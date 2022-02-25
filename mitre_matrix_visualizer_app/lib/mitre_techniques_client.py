from taxii2client.v20 import Collection
from stix2 import TAXIICollectionSource, Filter
from django.core.cache import cache

SOURCE_WEBSITE = "https://cti-taxii.mitre.org/stix/collections/"
MATRIX_ID = "95ecc380-afe9-11e4-9b6c-751b66dd541e"
MATRIX_NAME = "Enterprise ATT&CK"
MITRE_CACHE_TIMEOUT = 86400

def get_matrix_tactics(source: TAXIICollectionSource) -> list:
    """
    Gather tactics of MATRIX_NAME matrix based on code from MITRE ATTACK® official repository
    https://github.com/mitre/cti.
    """
    tactics = list()
    matrices = source.query([Filter('type', '=', 'x-mitre-matrix'), ])

    for matrix in matrices:
        if matrix["name"] == MATRIX_NAME:
            for tactic_id in matrix['tactic_refs']:
                tactics.append(source.get(tactic_id))
            break

    return tactics


def get_matrix_techniques(source: TAXIICollectionSource, tactic) -> list:
    """
    Gather techniques assigned to tactic based on code from MITRE ATTACK® official repository
    https://github.com/mitre/cti. Subtechniques aren't included!
    """
    return source.query([
        Filter('type', '=', 'attack-pattern'),
        Filter('kill_chain_phases.phase_name', '=', tactic),
        Filter('kill_chain_phases.kill_chain_name', '=', 'mitre-attack'),
        Filter('x_mitre_is_subtechnique', '=', False),
    ])


def get_mitre_techniques() -> (list, list):
    print("Gathering matrix content...")
    collection = Collection(SOURCE_WEBSITE + MATRIX_ID)
    src = TAXIICollectionSource(collection)
    # tactics = cache.get("mitre_tactics", None)
    # if not tactics:
    #     print("AAAAAAAAAAAAAAAAAAAAAAAAaa")
    #     tactics = get_matrix_tactics(src)
    #     cache.set("mitre_tactics", tactics, MITRE_CACHE_TIMEOUT)

    #
    # techniques = cache.get("mitre_techniques", None)
    # if not tactics:
    #     print("BBBBBBBBBBBBBBBBBbbbbbbbbb")
    #     tactics = get_matrix_techniques(src, tactics)
    #     cache.set("mitre_techniques", techniques, MITRE_CACHE_TIMEOUT)

    tactics = get_matrix_tactics(src)
    techniques = get_matrix_techniques(src, tactics)
    return tactics, techniques


def test_get_mitre():
    tactics, techniques = get_mitre_techniques()
    # print("\n\n\n\n\n\n\n\n>")
    # print(tactics)
    # print("\n\n\n\n\n\n\n\n>")
    # print(techniques)
