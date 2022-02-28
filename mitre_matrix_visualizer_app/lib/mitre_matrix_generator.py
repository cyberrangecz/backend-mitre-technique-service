from mitre_matrix_visualizer_app.lib.mitre_techniques_client import MitreClient
from jinja2 import Template
import json
from collections import defaultdict


class MitreMatrixGenerator:
    @staticmethod
    def get_level_techniques(level):
        """
        Extract attack techniques from game level.
        Exit if level does not contain 'MITRE_techniques' key.
            (dict of str: str): Dictionary mapping attack techniques identifiers to their names.
        """
        try:
            return level["MITRE_techniques"]
        except KeyError:
            print("Found a GAME_LEVEL in one of supplied definitions "
                  "without MITRE_techniques key.")
            print("Task aborted.")

    @staticmethod
    def gather_techniques_of_game(levels):
        """
           (set of str): Set of identifiers of attack techniques assigned to game.
        """
        techniques = set()
        for level in levels:
            if level["level_type"] != "GAME_LEVEL":
                continue

            level_techniques = MitreMatrixGenerator.get_level_techniques(level).keys()

            for technique in level_techniques:
                parts = technique.split(".")
                if len(parts) == 3:
                    parts.pop()
                technique = ".".join(parts)
                techniques.add(technique)

        return techniques

    @staticmethod
    def process_technique(technique, game, techniques):
        """
        Auxiliary function used to populate comparison dictionary based on attack techniques of games.
        """
        parts = technique.split('.')
        techniques[parts[0]][parts[1]].add(game)

    @staticmethod
    def compare_techniques(games_levels):
        """
            (defaultdict of str: defaultdict of str: set of int)
            Comparison dictionary of games. First layer key is tactic identifier, second layer key
            is technique identifier and if subtechnique is true, third layer key is
            subtechnique identifier. Final value is set of indices of games containing attack technique.
        """
        techniques = defaultdict(lambda: defaultdict(lambda: set()))

        for game_index, game_levels in enumerate(games_levels):
            for technique in MitreMatrixGenerator \
                    .gather_techniques_of_game(game_levels):
                MitreMatrixGenerator.process_technique(technique, game_index + 1, techniques)
        return techniques

    @staticmethod
    def load_game(file_path):
        try:
            input_file = open(file_path, "r")
            game = json.load(input_file)
            return game["title"], game["levels"]
        except OSError:
            print(f"{file_path} is invalid filename.")
            print("Task aborted.")
        except json.JSONDecodeError:
            print(f"{file_path} is not valid JSON file.")
            print("Task aborted.")

    @staticmethod
    def load_games(file_paths):
        titles = []
        levels = []
        for file_path in file_paths:
            game_title, game_levels = MitreMatrixGenerator.load_game(file_path)
            titles.append(game_title)
            levels.append(game_levels)
        return titles, levels


    @staticmethod
    def generate_matrix():
        # tactics, techniques = MitreClient.get_tactics_techniques() # this is done for now #TODO uncomment
        print("Generating output file...")
        with open("mitre_matrix_visualizer_app/templates/template.jinja2", "r") as file:
            template = Template(file.read())

        game_paths = ["mitre_matrix_visualizer_app/templates/Captain_Slovakistan_with_techniques.json", "mitre_matrix_visualizer_app/templates/Kobylka_with_techniques.json", "mitre_matrix_visualizer_app/templates/COVID-19_Truth_seeker_with_techniques.json"]
        titles, levels = MitreMatrixGenerator.load_games(game_paths)

        # TODO this is my json file, will be replaced by the json file coming from the endpoint - dunno what form it will have
        with open("mitre_matrix_visualizer_app/templates/test.json", "r") as file:
            data = json.load(file)
        #my_titles = [level['title'] for level in data]  #TODO this does not work
        #print(titles)
        #print(my_titles)

        #titles are list of level names   levels are all info of levels - that is a problem
        # - I need to convert the json I made to the defaultdict structure is possible

        with open("mitre_matrix_visualizer_app/templates/result.html", "w") as file:
            technique_dict = MitreMatrixGenerator.compare_techniques(levels)

            # print("\n\n\n\n\n\n\n\n\nX>>>>")
            # print(tactics)
            # print("\n\n\n")
            # print(techniques)
            # print("\n\n\n")
            # print(titles)
            # print("\n\n\n")
            # print(technique_dict)

            # print("\n\n\n")
            # print(technique_dict['TA0001'])
            # print(technique_dict[1])

            # file.write(template.render(tactics=tactics, techniques=techniques, game_names=titles,  #TODO uncomment
            #                            technique_dict=technique_dict, single_color=False))

    @staticmethod
    def test_generate():
        MitreMatrixGenerator.generate_matrix()

