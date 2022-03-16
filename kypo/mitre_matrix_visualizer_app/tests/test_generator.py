from kypo.mitre_matrix_visualizer_app.lib.mitre_matrix_generator import MitreMatrixGenerator
import pytest
from collections import defaultdict
#from jinja2 import Template
#import jinja2


class TestClient:
    training_definition_data = [
        {"title": "a1", "id": "1", "played": False, "mitre_techniques": [1, 2]},
        {"title": "b2", "id": "2", "played": True, "mitre_techniques": []},
        {"title": "b3", "id": "3", "played": True, "mitre_techniques": [3]}
    ]

    @pytest.fixture
    def mitre_generator(self):
        return MitreMatrixGenerator()

    def test_generator_generate_comparison_techniques(self, mocker, mitre_generator):
        techniques = [['1.1', '1.2.1'], [], ['3.1']]
        result_techniques = defaultdict(lambda: defaultdict(lambda: set()))
        result_techniques['1']['1'].add(1)
        result_techniques['1']['2'].add(1)
        result_techniques['3']['1'].add(3)
        assert mitre_generator._generate_comparison_techniques(techniques) == result_techniques

    @pytest.fixture
    def setup_generate_matrix_all(self, mocker):
        mock_get_tactics_techniques = mocker.patch(
            'kypo.mitre_matrix_visualizer_app.lib.mitre_techniques_client.MitreClient.get_tactics_techniques')
        mock_get_tactics_techniques.return_value = ('a', 'b')
        mock_template = mocker.MagicMock()
        mock_template.render.return_value = 'r'
        mock_template_init = mocker.patch('jinja2.Template.__new__')
        mock_template_init.return_value = mock_template
        mock_data = mocker.patch('json.load')
        mock_data.return_value = self.training_definition_data
        mock_generate_comparison_techniques = mocker.patch(
            'kypo.mitre_matrix_visualizer_app.lib.mitre_matrix_generator.MitreMatrixGenerator._generate_comparison_techniques')
        mock_generate_comparison_techniques.return_value = 'd'
        return mock_template, mock_generate_comparison_techniques

    def test_generator_generate_matrix_all(self, setup_generate_matrix_all, mitre_generator):
        mock_template, mock_generate_comparison_techniques = setup_generate_matrix_all

        assert mitre_generator.generate_matrix(False) == 'r'
        mock_generate_comparison_techniques.assert_called_with([[1, 2], [], [3], [1, 2], [], [3]])
        mock_template.render.assert_called_with(tactics='a', techniques='b',
                                                game_names=['a1 (L1)', 'b2 (L2)', 'b3 (L3)',
                                                            'a1 (A1)', 'b2 (A2)', 'b3 (A3)'],
                                                technique_dict='d', single_color=False)

    def test_generator_generate_matrix_played(self, setup_generate_matrix_all, mitre_generator):
        mock_template, mock_generate_comparison_techniques = setup_generate_matrix_all

        assert mitre_generator.generate_matrix(True) == 'r'
        mock_generate_comparison_techniques.assert_called_with([[], [3], [], [3]])
        mock_template.render.assert_called_with(tactics='a', techniques='b',
                                                game_names=['b2 (L2)', 'b3 (L3)', 'b2 (A2)',
                                                            'b3 (A3)'],
                                                technique_dict='d', single_color=False)
