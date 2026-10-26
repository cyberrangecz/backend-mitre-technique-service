"""Tests that the matrix data is served from the bundle when TAXII or the cache is unavailable."""

from typing import Any

import django
import pytest
from django.conf import settings

from crczp.mitre_matrix_visualizer_app.lib import mitre_techniques_client
from crczp.mitre_matrix_visualizer_app.lib.mitre_techniques_client import MitreClient

CLIENT_MODULE = 'crczp.mitre_matrix_visualizer_app.lib.mitre_techniques_client'


@pytest.fixture  # type: ignore[untyped-decorator]
def taxii_source_class(mocker: Any) -> Any:
    """Patch the TAXII source class so that any connection attempt raises."""
    return mocker.patch(
        f'{CLIENT_MODULE}.TAXIICollectionSource',
        side_effect=ConnectionError('503 Service Unavailable'),
    )


@pytest.fixture  # type: ignore[untyped-decorator]
def cold_cache(mocker: Any) -> Any:
    """Patch the cache with an empty one and return the patched object."""
    patched = mocker.patch(f'{CLIENT_MODULE}.cache')
    patched.get_many.return_value = {}
    return patched


@pytest.fixture  # type: ignore[untyped-decorator]
def broken_cache(mocker: Any) -> Any:
    """Patch the cache so that every operation raises."""
    patched = mocker.patch(f'{CLIENT_MODULE}.cache')
    patched.get_many.side_effect = ConnectionError('redis down')
    patched.set_many.side_effect = ConnectionError('redis down')
    return patched


def test_cold_cache_is_served_from_bundle_and_filled(
    taxii_source_class: Any, cold_cache: Any
) -> None:
    """Test that an empty cache yields the bundled data, stores it and never opens TAXII."""
    tactics, techniques, technique_index = MitreClient().get_tactics_techniques()

    assert tactics and techniques and technique_index
    cold_cache.set_many.assert_called_once()
    taxii_source_class.assert_not_called()


def test_cache_with_missing_key_is_treated_as_cold(
    taxii_source_class: Any, cold_cache: Any
) -> None:
    """Test that a cache holding only some of the keys is refilled from the bundle."""
    cold_cache.get_many.return_value = {'mitre_tactics': ['tactic']}

    tactics, _, _ = MitreClient().get_tactics_techniques()

    assert tactics != ['tactic']
    taxii_source_class.assert_not_called()


def test_cache_backend_failure_is_served_from_bundle(
    taxii_source_class: Any, broken_cache: Any
) -> None:
    """Test that a raising cache backend still yields the bundled data."""
    tactics, techniques, technique_index = MitreClient().get_tactics_techniques()

    assert tactics and techniques and technique_index
    broken_cache.set_many.assert_called_once()
    taxii_source_class.assert_not_called()


def test_bundle_path_does_not_depend_on_working_directory(
    taxii_source_class: Any, cold_cache: Any, tmp_path: Any, monkeypatch: Any
) -> None:
    """Test that the bundled data loads when the working directory is elsewhere."""
    monkeypatch.chdir(tmp_path)

    assert MitreClient().get_tactics_techniques()[0]
    assert mitre_techniques_client.BACKUP_PATH.is_absolute()
    assert settings.CRCZP_CONFIG.file_storage_location.startswith('/')
    taxii_source_class.assert_not_called()


def test_failed_refresh_keeps_existing_cache(taxii_source_class: Any, mocker: Any) -> None:
    """Test that a failing refresh leaves a populated cache untouched."""
    patched_cache = mocker.patch(f'{CLIENT_MODULE}.cache')
    patched_cache.get_many.return_value = {
        'mitre_tactics': ['tactic'],
        'mitre_techniques': ['technique'],
        'technique_index': ['index'],
    }

    message = MitreClient().update_matrix_data()

    assert message.startswith('The tactics and techniques update failed')
    patched_cache.set_many.assert_not_called()
    taxii_source_class.assert_called_once()


def test_failed_refresh_on_cold_cache_fills_it_from_bundle(
    taxii_source_class: Any, cold_cache: Any
) -> None:
    """Test that a failing refresh with an empty cache stores the bundled data."""
    message = MitreClient().update_matrix_data()

    assert message.startswith('The tactics and techniques update failed')
    cold_cache.set_many.assert_called_once()
    taxii_source_class.assert_called_once()


def test_failed_refresh_with_broken_cache_does_not_raise(
    taxii_source_class: Any, broken_cache: Any
) -> None:
    """Test that a failing refresh does not raise when the cache backend raises as well."""
    message = MitreClient().update_matrix_data()

    assert message.startswith('The tactics and techniques update failed')
    taxii_source_class.assert_called_once()


def test_routes_answer_without_taxii_and_cache(taxii_source_class: Any, broken_cache: Any) -> None:
    """Test that the technique index and refresh routes answer 200 with TAXII and cache down."""
    django.setup()
    from rest_framework.test import APIClient  # pylint: disable=import-outside-toplevel

    client = APIClient()
    prefix = f'/{settings.URL_PREFIX}'

    index_response = client.get(f'{prefix}mitre-technique-index')
    update_response = client.put(f'{prefix}mitre-update-matrix-data')

    assert index_response.status_code == 200
    assert index_response.json()['techniques']
    assert update_response.status_code == 200
    taxii_source_class.assert_called_once()
