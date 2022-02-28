from taxii2client.v20 import Collection
from stix2 import TAXIICollectionSource, Filter
from django.core.cache import cache

SOURCE_WEBSITE = "https://cti-taxii.mitre.org/stix/collections/"
MATRIX_ID = "95ecc380-afe9-11e4-9b6c-751b66dd541e"
MATRIX_NAME = "Enterprise ATT&CK"
MITRE_CACHE_TIMEOUT = 86400


class MitreClient:
    @staticmethod
    def get_matrix_tactics(source: TAXIICollectionSource) -> list:
        """
        Gather tactics of MATRIX_NAME matrix.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        tactics = list()
        matrices = source.query([Filter('type', '=', 'x-mitre-matrix'), ])

        for matrix in matrices:
            if matrix["name"] == MATRIX_NAME:
                for tactic_id in matrix['tactic_refs']:
                    tactics.append(source.get(tactic_id))
                break

        return tactics

    @staticmethod
    def get_tactic_techniques(source, tactic):
        """
        Gather techniques assigned to  a single tactic.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        return source.query([
            Filter('type', '=', 'attack-pattern'),
            Filter('kill_chain_phases.phase_name', '=', tactic),
            Filter('kill_chain_phases.kill_chain_name', '=', 'mitre-attack'),
            Filter('x_mitre_is_subtechnique', '=', False),
        ])

    @staticmethod
    def remove_revoked_deprecated(stix_objects):
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

    @staticmethod
    def get_matrix_techniques(source: TAXIICollectionSource, tactics) -> list:
        """
        Gather techniques of matrix.
        Based on code from MITRE ATTACK® official repository https://github.com/mitre/cti.
        """
        techniques = []
        for tactic in tactics:
            lst = MitreClient.get_tactic_techniques(source, tactic["x_mitre_shortname"])
            lst = MitreClient.remove_revoked_deprecated(lst)
            lst.sort(key=lambda x: x["name"])
            techniques.append(lst)
        return techniques

    @staticmethod
    def get_tactics_techniques() -> (list, list):
        print("Gathering matrix content:")
        collection = Collection(SOURCE_WEBSITE + MATRIX_ID)
        src = TAXIICollectionSource(collection)
        tactics = cache.get("mitre_tactics", None)
        if not tactics:
            tactics = MitreClient.get_matrix_tactics(src)
            cache.set("mitre_tactics", tactics, MITRE_CACHE_TIMEOUT)

        techniques = cache.get("mitre_techniques", None)
        if not techniques:
            techniques = MitreClient.get_matrix_techniques(src, tactics)
            cache.set("mitre_techniques", techniques, MITRE_CACHE_TIMEOUT)

        return tactics, techniques
