from taxii2client.v20 import Collection
from stix2 import TAXIICollectionSource, Filter
from django.core.cache import cache

from kypo.mitre_matrix_visualizer_app.lib.technique import Technique

SOURCE_WEBSITE = "https://cti-taxii.mitre.org/stix/collections/"
MATRIX_ID = "95ecc380-afe9-11e4-9b6c-751b66dd541e"
MATRIX_NAME = "Enterprise ATT&CK"
MITRE_CACHE_TIMEOUT = 86400


class MitreClient:
    technique_index = []

    def __init__(self):
        collection = Collection(SOURCE_WEBSITE + MATRIX_ID)
        self.source = TAXIICollectionSource(collection)

    def _get_matrix_tactics(self) -> list:
        """
        Gather tactics of MATRIX_NAME matrix.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        tactics = []
        matrices = self.source.query([Filter('type', '=', 'x-mitre-matrix'), ])

        for matrix in matrices:
            if matrix["name"] == MATRIX_NAME:
                for tactic_id in matrix['tactic_refs']:
                    tactics.append(self.source.get(tactic_id))
                break
        return tactics

    def _get_tactic_techniques(self, tactic):
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

    def _remove_revoked_deprecated(self, stix_objects):
        """
        Remove revoked or deprecated STIX objects from list of STIX objects.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        return list(
            filter(
                lambda x: x.get("x_mitre_deprecated", False) is False and
                x.get("revoked", False) is False,
                stix_objects
            )
        )

    def _get_matrix_techniques(self, tactics) -> list:
        """
        Gather techniques of matrix.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        all_techniques = []
        self.technique_index = []
        for tactic in tactics:
            tactic_techniques = self._get_tactic_techniques(tactic["x_mitre_shortname"])
            tactic_techniques = self._remove_revoked_deprecated(tactic_techniques)
            tactic_techniques.sort(key=lambda x: x["name"])

            for technique in tactic_techniques:
                technique_index_code = f"{tactic['external_references'][0]['external_id']}." \
                                       f"{technique['external_references'][0]['external_id']}"
                self.technique_index.append(Technique(technique_index_code, technique["name"]))

            all_techniques.append(tactic_techniques)
        return all_techniques

    def get_tactics_techniques(self) -> (list, list):
        print("Gathering matrix content:")
        tactics = cache.get("mitre_tactics", None)
        if not tactics:
            tactics = self._get_matrix_tactics()
            cache.set("mitre_tactics", tactics, MITRE_CACHE_TIMEOUT)

        techniques = cache.get("mitre_techniques", None)
        if not techniques:
            techniques = self._get_matrix_techniques(tactics)
            cache.set("mitre_techniques", techniques, MITRE_CACHE_TIMEOUT)

        return tactics, techniques
