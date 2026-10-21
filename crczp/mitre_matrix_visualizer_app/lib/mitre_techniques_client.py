"""Client for fetching and caching MITRE ATT&CK tactics and techniques via TAXII2/STIX2."""

import logging
import pickle  # nosec B403 - data is written by this service from trusted MITRE sources
from functools import cached_property
from pathlib import Path
from typing import Any

from django.core.cache import cache
from stix2 import Filter, TAXIICollectionSource
from taxii2client.v21 import Collection

from crczp.mitre_matrix_visualizer_app.lib.technique import Technique

SOURCE_WEBSITE = 'https://attack-taxii.mitre.org/api/v21/collections/'
MATRIX_ID = 'x-mitre-collection--1f5f1533-f617-4ca8-9ab4-6a02367fa019'
MATRIX_NAME = 'Enterprise ATT&CK'
MITRE_CACHE_TIMEOUT = None  # No timeout - cache is updated manually
CACHE_KEYS = ('mitre_tactics', 'mitre_techniques', 'technique_index')
BACKUP_PATH = Path(__file__).resolve().parent.parent / 'templates' / 'mitre_attack_backup_data'
MatrixData = tuple[list[Any], list[Any], list[Any]]

LOG = logging.getLogger(__name__)


class MitreClient:
    """Retrieves MITRE ATT&CK tactics and techniques from the TAXII2 server or a local cache."""

    @cached_property
    def source(self) -> TAXIICollectionSource:
        """TAXII source of the matrix collection; connects to the server on first access."""
        return TAXIICollectionSource(Collection(SOURCE_WEBSITE + MATRIX_ID))

    def _get_matrix_tactics(self) -> list[Any]:
        """
        Gather tactics of MATRIX_NAME matrix.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        tactics = []
        matrices = self.source.query([
            Filter('type', '=', 'x-mitre-matrix'),
        ])

        for matrix in matrices:
            if matrix['name'] == MATRIX_NAME:
                for tactic_id in matrix['tactic_refs']:
                    tactics.append(self.source.get(tactic_id))
                break
        return tactics

    def _get_tactic_techniques(self, tactic: Any) -> Any:
        """
        Gather techniques assigned to  a single tactic.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        return self.source.query([
            Filter('type', '=', 'attack-pattern'),
            Filter('kill_chain_phases.phase_name', '=', tactic),
            Filter('kill_chain_phases.kill_chain_name', '=', 'mitre-attack'),
            Filter('x_mitre_is_subtechnique', '=', False),
        ])

    def _remove_revoked_deprecated(self, stix_objects: Any) -> list[Any]:
        """
        Remove revoked or deprecated STIX objects from list of STIX objects.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        return list(
            filter(
                lambda x: (
                    x.get('x_mitre_deprecated', False) is False and x.get('revoked', False) is False
                ),
                stix_objects,
            )
        )

    def _get_matrix_techniques(self, tactics: Any) -> tuple[list[Any], list[Any]]:
        """
        Gather techniques of matrix.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        all_techniques = []
        technique_index = []
        for tactic in tactics:
            tactic_techniques = self._get_tactic_techniques(tactic['x_mitre_shortname'])
            tactic_techniques = self._remove_revoked_deprecated(tactic_techniques)
            tactic_techniques.sort(key=lambda x: x['name'])

            for technique in tactic_techniques:
                technique_index_code = (
                    f'{tactic["external_references"][0]["external_id"]}.'
                    f'{technique["external_references"][0]["external_id"]}'
                )
                technique_index.append(Technique(technique_index_code, technique['name']))

            all_techniques.append(tactic_techniques)
        return all_techniques, technique_index

    @staticmethod
    def _read_backup() -> MatrixData:
        """Load the matrix data bundled with the service."""
        with open(BACKUP_PATH, 'rb') as backup:
            return pickle.load(backup)  # type: ignore[no-any-return]  # nosec B301

    @staticmethod
    def _read_cache() -> MatrixData | None:
        """Return the cached matrix data, or None when it is incomplete or the cache fails."""
        try:
            cached = cache.get_many(CACHE_KEYS)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            LOG.warning('Matrix cache read failed: %s', exc)
            return None
        values = [cached.get(key) for key in CACHE_KEYS]
        if not all(values):
            return None
        return values[0], values[1], values[2]

    @staticmethod
    def _write_cache(data: MatrixData) -> None:
        """Store the matrix data in the cache; a failing cache is logged and ignored."""
        try:
            cache.set_many(dict(zip(CACHE_KEYS, data, strict=True)), MITRE_CACHE_TIMEOUT)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            LOG.warning('Matrix cache write failed: %s', exc)

    def get_tactics_techniques(self) -> MatrixData:
        """
        Return tactics, techniques and technique index from the cache. When the cache is empty
        or unavailable, the bundled data is returned and stored in the cache.
        """
        data = self._read_cache()
        if data is None:
            data = self._read_backup()
            self._write_cache(data)
        return data

    def update_matrix_data(self) -> str:
        """
        Replace the cached data with the data of the official TAXII server. When the server
        cannot be used, the cached data stays in place, or is filled from the bundled data
        when the cache holds none.
        :return: Message stating whether the TAXII server data was stored.
        """
        try:
            print('Gathering matrix content:')
            tactics = self._get_matrix_tactics()
            (techniques, technique_index) = self._get_matrix_techniques(tactics)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            LOG.error('Matrix update failed: %s', exc, exc_info=True)
            self.get_tactics_techniques()
            return (
                'The tactics and techniques update failed. '
                'Keeping the cached or locally stored MITRE data.'
            )
        self._write_cache((tactics, techniques, technique_index))
        return 'Tactics and techniques were updated successfully.'
