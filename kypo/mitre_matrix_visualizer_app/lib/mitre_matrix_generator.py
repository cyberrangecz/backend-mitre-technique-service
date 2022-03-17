from kypo.mitre_matrix_visualizer_app.lib.mitre_techniques_client import MitreClient
from jinja2 import Template
import json
from collections import defaultdict


class MitreMatrixGenerator:
    @staticmethod
    def _generate_comparison_techniques(training_techniques):
        """
            Comparison dictionary of games. First layer key is tactic identifier, second layer key
            is technique identifier. Final value is set of indices of games containing attack
            technique.
        """
        techniques = defaultdict(lambda: defaultdict(lambda: set()))

        for level_index, level_techniques in enumerate(training_techniques):
            for technique in level_techniques:
                if len(technique.split('.')) > 2:
                    technique = technique.split('.')[0] + '.' + technique.split('.')[1]
                parts = technique.split('.')
                techniques[parts[0]][parts[1]].add(level_index + 1)
        return techniques

    # noinspection PyMethodMayBeStatic
    def generate_matrix(self, played: bool):
        tactics, techniques = MitreClient().get_tactics_techniques()

        print("Generating output file...")
        with open("kypo/mitre_matrix_visualizer_app/templates/template.jinja2", "r") as file:
            template = Template(file.read())

        # TODO this is loading json file, will be replaced by the json file coming from the endpoint
        with open("kypo/mitre_matrix_visualizer_app/templates/test_linear.json", "r") as file:
            data_linear = json.load(file)
        titles_linear = [training_definition.get("title") + " (L"
                         + str(training_definition.get("id")) + ")" for training_definition
                         in data_linear if not played or training_definition.get("played")]

        with open("kypo/mitre_matrix_visualizer_app/templates/test_adaptive.json", "r") as file:
            data_adaptive = json.load(file)
        titles_adaptive = [training_definition.get("title") + " (A" +
                           str(training_definition.get("id")) + ")" for training_definition
                           in data_adaptive if not played or training_definition.get("played")]

        data = data_linear + data_adaptive
        titles = titles_linear + titles_adaptive

        training_techniques = [training_definition.get("mitre_techniques") for training_definition
                               in data if not played or training_definition.get("played")]
        training_technique_dict = self._generate_comparison_techniques(training_techniques)

        # TODO this is generating the matrix into file for testing purposes
        with open("kypo/mitre_matrix_visualizer_app/templates/result.html", "w") as file:
            file.write(template.render(tactics=tactics, techniques=techniques, game_names=titles,
                                       technique_dict=training_technique_dict, single_color=False))

        with open("kypo/mitre_matrix_visualizer_app/templates/template2.jinja2", "r") as file2:
            template2 = Template(file2.read())

        return template2.render(tactics=tactics, techniques=techniques, game_names=titles,
                                technique_dict=training_technique_dict, single_color=False)
