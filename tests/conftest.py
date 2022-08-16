"""pytest fixtures which are globally available throughout the suite."""
import os
import shutil

import pytest
import pkg_resources
from click.testing import CliRunner

from tests.expected_outputs import expected_outputs
from cloudtiger.cli import main

TEST_DATA_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests')
TEST_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests/run')

root_folders = {
    "simple" : ".",
    "absolute" : "/app/absolute_root_folder",
    "relative" : "./relative_root_folder",
    "absolute_with_whitespace" : "/app/absolute\ test\ path",
    "relative_with_whitespace" : "./app/relative\ test\ path"
}

@pytest.fixture(scope='environment')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(command:list):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, command)

    return cli_main

@pytest.fixture(scope='environment')
def create_gitops_folders():
    """Fixture that create gitops folders using several pathes"""
    os.chdir(TEST_FOLDER)

    gitops_test_folder = os.path.join(TEST_DATA_FOLDER, "gitops")
    for _, root_folder in root_folders.items():
        if root_folder[0] == os.path.sep:
            root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
        else :
            root_folder = os.path.join(os.getcwd(), root_folder)

        shutil.copytree(gitops_test_folder, root_folder, dirs_exist_ok=True)

@pytest.fixture(scope='environment')
def delete_gitops_folders():
    """Fixture that delete test gitops folders."""
    for _, root_folder in root_folders.items():
        if root_folder[0] == os.path.sep:
            root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
        else :
            root_folder = os.path.join(os.getcwd(), root_folder)
        root_folder = os.path.join(root_folder, "gitops")
        if os.path.isdir(root_folder):
            shutil.rmtree(root_folder)

@pytest.fixture(scope='environment')
def get_test_scopes():
    """Fixture that provide a list of test scopes"""
    test_scopes = [
        os.path.join("aws", "single_scope"),
        os.path.join("vsphere", "single_scope").
        os.path.join("nutanix", "single_scope")
    ]

    return test_scopes

@pytest.fixture(scope='environment')
def run_test_command(root_folder, scope, command, scenario_name):
    """Fixture that runs a command on a scope in a root folder"""

    if root_folder[0] == os.path.sep :
        root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
    else :
        root_folder = os.path.join(os.getcwd(), root_folder)

    # we use 'WHITESPACE' as a placeholder for whitespaces in the project root
    # because we will split the command input afterwards using whitespaces
    # too
    root_folder = root_folder.replace(' ', "WHITESPACE")

    # the command must be fed as a list of parameters
    command = command.split()
    command = [elt.replace("WHITESPACE", " ") for elt in command]

    result = cli_runner(command)
    print(result.output)
    assert result.output == expected_outputs[scenario_name]

@pytest.fixture(scope='environment')
def run_test_command_all_scopes(test_scopes, root_folder, command, scenario_name):
    """Fixture that runs a command on all test scopes in a root folder"""
    for test_scope in test_scopes :
        run_test_command(root_folder, test_scope, command, scenario_name)

@pytest.fixture(scope='environment')
def run_test_command_all_scopes_all_root(test_scopes, root_folders, command, scenario_name):
    """Fixture that runs a command on all test scopes in a root folder"""
    for root_folder in root_folders :
        run_test_command_all_scopes(test_scopes, root_folder, command, scenario_name)