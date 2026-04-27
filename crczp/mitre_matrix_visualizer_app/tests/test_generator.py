"""Unit tests for MitreMatrixGenerator HTML matrix generation."""

from collections import defaultdict
from typing import Any

import pytest
from django.conf import settings

from crczp.mitre_matrix_visualizer_app.lib.mitre_matrix_generator import (
    TEMPLATE_HEADERS,
    MitreMatrixGenerator,
)


class TestGenerator:  # pylint: disable=protected-access
    """Tests for MitreMatrixGenerator comparison technique building and matrix rendering."""

    training_definition_data = [
        {'title': 'a1', 'id': '1', 'played': False, 'mitre_techniques': [1, 2]},
        {'title': 'b2', 'id': '2', 'played': True, 'mitre_techniques': []},
        {'title': 'b3', 'id': '3', 'played': True, 'mitre_techniques': [3]},
    ]
    headers = {**TEMPLATE_HEADERS, 'Authorization': 'token'}

    @pytest.fixture  # type: ignore[untyped-decorator]
    def mitre_generator(self) -> MitreMatrixGenerator:
        """Return a fresh MitreMatrixGenerator instance."""
        return MitreMatrixGenerator()

    def test_generator_generate_comparison_techniques(
        self, mitre_generator: MitreMatrixGenerator
    ) -> None:
        """Test that _generate_comparison_techniques builds the correct nested defaultdict."""
        techniques = [['1.1', '1.2.1'], [], ['3.1']]
        result_techniques: defaultdict[str, defaultdict[str, set[int]]] = defaultdict(
            lambda: defaultdict(set)
        )
        result_techniques['1']['1'].add(1)
        result_techniques['1']['2'].add(1)
        result_techniques['3']['1'].add(3)
        assert mitre_generator._generate_comparison_techniques(techniques) == result_techniques

    @pytest.fixture  # type: ignore[untyped-decorator]
    def setup_generate_matrix_all(self, mocker: Any) -> Any:
        """Patch external dependencies for generate_matrix tests."""
        mocker.patch(
            'crczp.mitre_matrix_visualizer_app.lib.mitre_techniques_client.TAXIICollectionSource'
        )
        mock_get_tactics_techniques = mocker.patch(
            'crczp.mitre_matrix_visualizer_app.lib'
            '.mitre_techniques_client.MitreClient.get_tactics_techniques'
        )
        mock_get_tactics_techniques.return_value = ('a', 'b', 'c')
        mock_template = mocker.MagicMock()
        mock_template.render.return_value = 'r'
        mock_template_init = mocker.patch('jinja2.Template.__new__')
        mock_template_init.return_value = mock_template

        mock_request_result = mocker.MagicMock()
        mock_request_result.json.return_value = self.training_definition_data
        mock_request = mocker.patch('requests.get')
        mock_request.return_value = mock_request_result
        mock_generate_comparison_techniques = mocker.patch(
            'crczp.mitre_matrix_visualizer_app.lib.mitre_matrix_generator'
            '.MitreMatrixGenerator._generate_comparison_techniques'
        )
        mock_generate_comparison_techniques.return_value = 'd'
        return mock_template, mock_generate_comparison_techniques, mock_request

    def test_generator_generate_matrix_all(
        self, setup_generate_matrix_all: Any, mitre_generator: MitreMatrixGenerator
    ) -> None:
        """Test generate_matrix returns rendered template when played=False."""
        mock_template, mock_generate_comparison_techniques, mock_request = setup_generate_matrix_all

        assert mitre_generator.generate_matrix('token', False) == 'r'

        mock_request.assert_any_call(
            settings.CRCZP_CONFIG.java_linear_training_mitre_endpoint,
            headers=self.headers,
            timeout=30,
        )
        mock_request.assert_called_with(
            settings.CRCZP_CONFIG.java_adaptive_training_mitre_endpoint,
            headers=self.headers,
            timeout=30,
        )

        mock_generate_comparison_techniques.assert_called_with([[1, 2], [], [3], [1, 2], [], [3]])
        mock_template.render.assert_called_with(
            tactics='a',
            techniques='b',
            linear_game_names=['a1 (1)', 'b2 (2)', 'b3 (3)'],
            adaptive_game_names=['a1 (1)', 'b2 (2)', 'b3 (3)'],
            technique_dict='d',
            single_color=False,
        )

    def test_generator_generate_matrix_played(
        self, setup_generate_matrix_all: Any, mitre_generator: MitreMatrixGenerator
    ) -> None:
        """Test generate_matrix filters training definitions by played=True."""
        mock_template, mock_generate_comparison_techniques, mock_request = setup_generate_matrix_all

        assert mitre_generator.generate_matrix('token', True) == 'r'

        mock_request.assert_any_call(
            settings.CRCZP_CONFIG.java_linear_training_mitre_endpoint,
            headers=self.headers,
            timeout=30,
        )
        mock_request.assert_called_with(
            settings.CRCZP_CONFIG.java_adaptive_training_mitre_endpoint,
            headers=self.headers,
            timeout=30,
        )

        mock_generate_comparison_techniques.assert_called_with([[], [3], [], [3]])
        mock_template.render.assert_called_with(
            tactics='a',
            techniques='b',
            linear_game_names=['b2 (2)', 'b3 (3)'],
            adaptive_game_names=['b2 (2)', 'b3 (3)'],
            technique_dict='d',
            single_color=False,
        )
