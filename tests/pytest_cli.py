"""Integration tests for init command."""

import json
import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from .conftest import run_test_command_all_scopes_all_root

@pytest.mark.parametrize("scenario_commands,scenario_name", [
    (["init 0"], "init_0"),
    (["init 1"], "init_1"),
    (["init 1", "init_2"], "init_2"),
    (["init 2"], "missing_init_ip"),
    (["tf init"], "tf_init"),
    (["tf init", "tf apply"], "tf_apply"),
    (["tf apply"], "missing_tf_init"),
])
def test_cli_test_scenarii(scenario_commands, scenario_name):
    """Check CLI commands scenarii"""

    for command in scenario_commands:
        output = run_test_command_all_scopes_all_root(command, scenario_name)
