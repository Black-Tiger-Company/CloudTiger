"""Integration tests for CLI commands."""

import json
import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.expected_outputs import expected_outputs
from cloudtiger import helper

@pytest.fixture(params=['--version'])
def cli_version_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param

@pytest.fixture(params=['-h', '--help'])
def cli_main_helper(request):
    """Pytest fixture return both helper options."""
    return request.param

@pytest.fixture(params=['-r', '--recursive'])
def cli_recursive_option(request):
    """Pytest fixture recursive."""
    return request.param

def test_cli_version(cli_runner, cli_version_flag):
    """Verify CloudTiger version output by `cloudtiger --v` on cli invocation."""
    result = cli_runner(cli_version_flag)
    assert result.exit_code == 0
    assert ', version' in result.output
    # assert result.output.startswith('cloudtiger, version')

test_scopes = [
        os.path.join("aws", "single_scope"),
        os.path.join("vsphere", "single_scope"),
        os.path.join("nutanix", "single_scope")
    ]

root_folders = [
    ("simple", "."),
    ("absolute", "/app/absolute_root_folder"),
    ("relative", "./relative_root_folder"),
    ("absolute_with_whitespace", "/app/absolute\ test\ path"),
    ("relative_with_whitespace", "./app/relative\ test\ path")
    ]

# def test_cli_helper(cli_runner, cli_main_helper):
#     """Check main helper"""
#     result = cli_runner(cli_main_helper)
#     assert result.exit_code == 0
#     print(result.output)
#     assert result.output == helper.helpers["basic"]

# def run_test_command(root_folder, scope, command, scenario_name):
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
#                 "%s --error-file %s %s" %
#                 (root_folder, 'cloudtiger_std.log',
#                 'cloudtiger_stderr.log', command))
#     command = command.split()
#     command = [elt.replace("WHITESPACE", " ") for elt in command]

#     result = cli_runner(command)
#     print(result.output)
#     assert result.output == expected_outputs[scenario_name]

# @pytest.mark.usefixtures("run_test_command_all_scopes_all_root")
@pytest.mark.parametrize("scenario_commands,scenario_name", [
    (["init 0"], "init_0"),
    (["init 1"], "init_1"),
    (["init 1", "init_2"], "init_2"),
    (["init 2"], "missing_init_ip"),
    (["tf init"], "tf_init"),
    (["tf init", "tf apply"], "tf_apply"),
    (["tf apply"], "missing_tf_init"),
])
def test_cli_test_scenarii(create_gitops_folders, delete_gitops_folders, cli_runner, scenario_commands, scenario_name):
    """Check CLI commands scenarii"""
    
    for root_folder in root_folders:
        print(root_folders)
        for scope in test_scopes:
            create_gitops_folders()
            for command in scenario_commands:
                # output = run_test_command(root_folder, scope, command, scenario_name)
                command = format("--project-root %s --output-file"
                            "%s --error-file %s %s" %
                            (root_folder, 'cloudtiger_std.log',
                            'cloudtiger_stderr.log', command))
                command = command.split()
                command = [elt.replace("WHITESPACE", " ") for elt in command]
                
                result = cli_runner(command)
                print(result.output)
                assert result.output == expected_outputs[scenario_name]
                
            delete_gitops_folders()
