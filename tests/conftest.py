"""pytest fixtures which are globally available throughout the suite."""

import pytest
from click.testing import CliRunner

from cloudtiger.cli import main

@pytest.fixture()
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(command:list):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, command)

    return cli_main

@pytest.fixture(params=['--version'])
def cli_version_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param

# @pytest.fixture()
# def test_scopes():
#     """Fixture that provide a list of test scopes"""
#     get_test_scopes = [
#         os.path.join("aws", "single_scope"),
#         os.path.join("vsphere", "single_scope"),
#         os.path.join("nutanix", "single_scope")
#     ]

#     return get_test_scopes



# @pytest.fixture()
# def root_folders():
#     return [
#     ("simple", "."),
#     ("absolute", "/app/absolute_root_folder"),
#     ("relative", "./relative_root_folder"),
#     ("absolute_with_whitespace", "/app/absolute\ test\ path"),
#     ("relative_with_whitespace", "./app/relative\ test\ path")
#     ]
    
# root_folders = [
#     ("simple", "."),
#     ("absolute", "/app/absolute_root_folder"),
#     ("relative", "./relative_root_folder"),
#     ("absolute_with_whitespace", "/app/absolute\ test\ path"),
#     ("relative_with_whitespace", "./app/relative\ test\ path")
#     ]

# @pytest.fixture()
# def run_test_command(root_folder, scope, command):
#     """Fixture that runs a command on a scope in a root folder"""

#     # if root_folder[0] == os.path.sep :
#     #     root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
#     # else :
#     #     root_folder = os.path.join(os.getcwd(), root_folder)

#     # we use 'WHITESPACE' as a placeholder for whitespaces in the project root
#     # because we will split the command input afterwards using whitespaces
#     # too
#     root_folder = root_folder.replace(' ', "WHITESPACE")

#     # the command must be fed as a list of parameters
#     command = format("--project-root %s --output-file"
#                 "%s --error-file %s %s %s" %
#                 (root_folder, 'cloudtiger_std.log',
#                 'cloudtiger_stderr.log', scope, command))
#     command = command.split()
#     command = [elt.replace("WHITESPACE", " ") for elt in command]

#     result = cli_runner(command)
#     return result.output
#     # print(result.output)
#     # assert result.output == expected_outputs[scenario_name]

# @pytest.fixture()
# def run_test_command_all_scopes(root_folder, command, scenario_name):
#     """Fixture that runs a command on all test scopes in a root folder"""
#     for test_scope in test_scopes() :
#         run_test_command(command, scenario_name)

# @pytest.fixture()
# def run_test_command_all_scopes_all_root(command, scenario_name):
#     """Fixture that runs a command on all test scopes in a root folder"""
#     for root_folder in root_folders() :
#         run_test_command_all_scopes(root_folder, command, scenario_name)