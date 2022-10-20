"""Integration tests for CLI commands."""

import os
import shutil

import pytest
import pkg_resources

from tests.expected_outputs import expected_outputs

TEST_DATA_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests')
TEST_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests/run')

root_folders = [
    ("simple", "."),
    ("absolute", "/app/absolute_root_folder"),
    ("relative", "./relative_root_folder"),
    ("absolute_with_whitespace", '/app/absolute test path'),
    ("relative_with_whitespace", './app/relative test path')
    ]

test_scopes = [
    os.path.join("aws", "single_scope"),
    os.path.join("vsphere", "single_scope"),
    os.path.join("nutanix", "single_scope")
]

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

def create_gitops_folder(root_folder):
    """Fixture that create gitops folders using several pathes"""
    os.chdir(TEST_FOLDER)

    gitops_test_folder = os.path.join(TEST_DATA_FOLDER, "gitops")

    if root_folder[0] == os.path.sep:
        root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
    else :
        root_folder = os.path.join(os.getcwd(), root_folder)

    try :
        shutil.copytree(gitops_test_folder, root_folder, dirs_exist_ok=True)
    except :
        print("Error in the test gitops folder creation")

def delete_gitops_folder(root_folder):
    """Fixture that delete test gitops folders."""

    if os.path.isdir(root_folder):
        try :
            shutil.rmtree(root_folder)
        except :
            print("Failed to delete the test gitops folder creation")

@pytest.mark.parametrize("scenario_commands,scenario_name", [
    (["init 0"], "init_0"),
    (["init 1"], "init_1"),
    (["init 1", "init 2"], "init_2"),
    (["init 2"], "missing_init_ip"),
    (["init 1", "init 2", "tf init"], "tf_init"),
    (["init 1", "init 2", "tf init", "tf plan"], "tf_plan"),
    (["tf apply"], "missing_tf_init"),
])
def test_cli_test_scenarii(cli_runner, scenario_commands, scenario_name):
    """Check CLI commands scenarii"""
    results = {}
    multiple_roots_expected_outputs = {}

    for key_root_folder, root_folder in root_folders:
        # key_root_folder = root_folder
        root_folder = root_folder.replace(' ', '\ ')
        create_gitops_folder(root_folder)

        results[key_root_folder] = {}
        if root_folder[0] == os.path.sep:
            root_folder = os.path.join(TEST_FOLDER, root_folder[1:])
        else :
            root_folder = os.path.join(os.getcwd(), root_folder)

        for scope in test_scopes:
            results[key_root_folder][scope] = ""
            for command in scenario_commands:
                # output = run_test_command(root_folder, scope, command, scenario_name)
                ws_root_folder = root_folder.replace(' ', "WHITESPACE")
                command = (f"--project-root {ws_root_folder} --output-file "
                           f"cloudtiger_std.log --error-file cloudtiger_stderr.log "
                           f"{scope} {command}")
                command = command.split()
                command = [elt.replace("WHITESPACE", " ") for elt in command]

                result = cli_runner(command)
                print(result.output)
                results[key_root_folder][scope] += result.output.replace("\\\\", "\\")

        delete_gitops_folder(root_folder)

        multiple_roots_expected_outputs[key_root_folder] = {}
        multiple_roots_expected_outputs[key_root_folder][scope] = expected_outputs
        [scenario_name][scope].replace('PROJECT_ROOT', root_folder)

    assert results == multiple_roots_expected_outputs
