from kypo.mitre_matrix_visualizer_app.lib.mitre_techniques_client import MitreClient
import pytest

from kypo.mitre_matrix_visualizer_app.lib.technique import Technique


class TestClient:
    @pytest.fixture
    def mitre_client(self):
        return MitreClient()

    def test_client_get_matrix_tactics(self, mocker, mitre_client):
        mitre_client.source.query = mocker.MagicMock()
        mitre_client.source.query.return_value = [{'name': 'x',
                                                   'tactic_refs': [1, 2, 3]},
                                                  {'name': 'Enterprise ATT&CK',
                                                   'tactic_refs': [4, 5, 6, 7]}]
        mitre_client.source.get = mocker.MagicMock()
        mitre_client.source.get.return_value = 9

        tactics = mitre_client._get_matrix_tactics()

        assert tactics == [9, 9, 9, 9]
        mitre_client.source.get.assert_any_call(4)
        mitre_client.source.get.assert_any_call(5)
        mitre_client.source.get.assert_any_call(6)
        mitre_client.source.get.assert_called_with(7)

    def test_remove_revoked_deprecated(self, mitre_client):
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

    def test_get_matrix_techniques(self, mocker, mitre_client):
        tactics = [{'x_mitre_shortname': 'a', 'external_references': [{'external_id': 'codeA'}]},
                   {'x_mitre_shortname': 'b', 'external_references': [{'external_id': 'codeB'}]}]
        mitre_client._get_tactic_techniques = mocker.MagicMock()
        mitre_client._get_tactic_techniques.return_value = 'c'
        mitre_client._remove_revoked_deprecated = mocker.MagicMock()
        mitre_client._remove_revoked_deprecated.return_value = [{'name': 'b',
                                                                 'external_references':
                                                                     [{'external_id': 'code1'}]},
                                                                {'name': 'a',
                                                                 'external_references':
                                                                     [{'external_id': 'code2'}]}]

        techniques, technique_index = mitre_client._get_matrix_techniques(tactics)

        mitre_client._get_tactic_techniques.assert_any_call('a')
        mitre_client._get_tactic_techniques.assert_called_with('b')
        mitre_client._remove_revoked_deprecated.assert_called_with('c')
        assert techniques == [[{'name': 'a', 'external_references': [{'external_id': 'code2'}]},
                               {'name': 'b', 'external_references': [{'external_id': 'code1'}]}],
                              [{'name': 'a', 'external_references': [{'external_id': 'code2'}]},
                               {'name': 'b', 'external_references': [{'external_id': 'code1'}]}]]
        assert technique_index[0].name == 'a' and technique_index[0].code == 'codeA.code2'
        assert technique_index[1].name == 'b' and technique_index[1].code == 'codeA.code1'
        assert technique_index[2].name == 'a' and technique_index[2].code == 'codeB.code2'
        assert technique_index[3].name == 'b' and technique_index[3].code == 'codeB.code1'

    def test_update_matrix_data(self, mocker, mitre_client):
        mitre_client._get_matrix_tactics = mocker.MagicMock()
        mitre_client._get_matrix_tactics.return_value = 'a'
        mitre_client._get_matrix_techniques = mocker.MagicMock()
        mitre_client._get_matrix_techniques.return_value = 'b', 'c'

        assert mitre_client.update_matrix_data() == "Tactics and techniques were updated successfully."
