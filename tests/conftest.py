"""pytest fixtures which are globally available throughout the suite."""
import os
import shutil

import pytest
import pkg_resources
from click.testing import CliRunner

from cloudtiger.cli import main

TEST_DATA_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests')
TEST_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests/run')

@pytest.fixture()
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(command:list):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, command)

    return cli_main

@pytest.fixture()
def create_gitops_folders():
    """Fixture that create gitops folders using several pathes"""
    os.chdir(TEST_FOLDER)

    gitops_test_folder = os.path.join(TEST_DATA_FOLDER, "gitops")
    for _, root_folder in root_folders:
        if root_folder[0] == os.path.sep:
            root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
        else :
            root_folder = os.path.join(os.getcwd(), root_folder)

        shutil.copytree(gitops_test_folder, root_folder, dirs_exist_ok=True)

@pytest.fixture()
def delete_gitops_folders():
    """Fixture that delete test gitops folders."""
    for _, root_folder in root_folders:
        if root_folder[0] == os.path.sep:
            root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
        else :
            root_folder = os.path.join(os.getcwd(), root_folder)
        root_folder = os.path.join(root_folder, "gitops")
        if os.path.isdir(root_folder):
            shutil.rmtree(root_folder)

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
# def run_test_command_all_scopes(command, scenario_name):
#     """Fixture that runs a command on all test scopes in a root folder"""
#     for test_scope in test_scopes :
#         run_test_command(command, scenario_name)

# @pytest.fixture()
# def run_test_command_all_scopes_all_root(command, scenario_name):
#     """Fixture that runs a command on all test scopes in a root folder"""
#     for root_folder in root_folders :
#         run_test_command_all_scopes(command, scenario_name)