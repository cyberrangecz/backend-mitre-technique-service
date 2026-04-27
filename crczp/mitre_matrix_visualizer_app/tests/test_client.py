"""Unit tests for the MitreClient TAXII2/STIX2 data-fetching logic."""

from typing import Any

import pytest

from crczp.mitre_matrix_visualizer_app.lib.mitre_techniques_client import MitreClient


class TestClient:  # pylint: disable=protected-access
    """Tests for MitreClient tactic and technique retrieval."""

    @pytest.fixture  # type: ignore[untyped-decorator]
    def mitre_client(self) -> MitreClient:
        """Return a fresh MitreClient instance."""
        return MitreClient()

    def test_client_get_matrix_tactics(self, mocker: Any, mitre_client: MitreClient) -> None:
        """Test that _get_matrix_tactics returns tactic objects for the Enterprise ATT&CK matrix."""
        mitre_client.source.query = mocker.MagicMock()
        mitre_client.source.query.return_value = [
            {'name': 'x', 'tactic_refs': [1, 2, 3]},
            {'name': 'Enterprise ATT&CK', 'tactic_refs': [4, 5, 6, 7]},
        ]
        mitre_client.source.get = mocker.MagicMock()
        mitre_client.source.get.return_value = 9

        tactics = mitre_client._get_matrix_tactics()

        assert tactics == [9, 9, 9, 9]
        mitre_client.source.get.assert_any_call(4)
        mitre_client.source.get.assert_any_call(5)
        mitre_client.source.get.assert_any_call(6)
        mitre_client.source.get.assert_called_with(7)

    def test_remove_revoked_deprecated(self, mitre_client: MitreClient) -> None:
        """Test that _remove_revoked_deprecated filters out revoked and deprecated techniques."""
        mitre_client = MitreClient()
        filtered = mitre_client._remove_revoked_deprecated([
            {'name': 'a', 'x_mitre_deprecated': True},
            {'name': 'b', 'revoked': True},
            {'name': 'c', 'x_mitre_deprecated': False},
            {'name': 'd', 'revoked': False},
            {'name': 'e'},
        ])
        for position, name in enumerate(['c', 'd', 'e']):
            assert filtered[position].get('name') == name

    def test_get_matrix_techniques(self, mocker: Any, mitre_client: MitreClient) -> None:
        """Test that _get_matrix_techniques returns correct technique lists and index."""
        tactics = [
            {'x_mitre_shortname': 'a', 'external_references': [{'external_id': 'codeA'}]},
            {'x_mitre_shortname': 'b', 'external_references': [{'external_id': 'codeB'}]},
        ]
        mock_tactic: Any = mocker.MagicMock()
        mitre_client._get_tactic_techniques = mock_tactic  # type: ignore[method-assign]
        mock_tactic.return_value = 'c'
        mock_revoked: Any = mocker.MagicMock()
        mitre_client._remove_revoked_deprecated = mock_revoked  # type: ignore[method-assign]
        mock_revoked.return_value = [
            {'name': 'b', 'external_references': [{'external_id': 'code1'}]},
            {'name': 'a', 'external_references': [{'external_id': 'code2'}]},
        ]

        techniques, technique_index = mitre_client._get_matrix_techniques(tactics)

        mock_tactic.assert_any_call('a')
        mock_tactic.assert_called_with('b')
        mock_revoked.assert_called_with('c')
        assert techniques == [
            [
                {'name': 'a', 'external_references': [{'external_id': 'code2'}]},
                {'name': 'b', 'external_references': [{'external_id': 'code1'}]},
            ],
            [
                {'name': 'a', 'external_references': [{'external_id': 'code2'}]},
                {'name': 'b', 'external_references': [{'external_id': 'code1'}]},
            ],
        ]
        assert technique_index[0].name == 'a' and technique_index[0].code == 'codeA.code2'
        assert technique_index[1].name == 'b' and technique_index[1].code == 'codeA.code1'
        assert technique_index[2].name == 'a' and technique_index[2].code == 'codeB.code2'
        assert technique_index[3].name == 'b' and technique_index[3].code == 'codeB.code1'

    def test_update_matrix_data(self, mocker: Any, mitre_client: MitreClient) -> None:
        """Test that update_matrix_data fetches tactics/techniques and returns success message."""
        mock_tactics: Any = mocker.MagicMock()
        mitre_client._get_matrix_tactics = mock_tactics  # type: ignore[method-assign]
        mock_tactics.return_value = 'a'
        mock_techniques: Any = mocker.MagicMock()
        mitre_client._get_matrix_techniques = mock_techniques  # type: ignore[method-assign]
        mock_techniques.return_value = 'b', 'c'

        assert (
            mitre_client.update_matrix_data() == 'Tactics and techniques were updated successfully.'
        )
