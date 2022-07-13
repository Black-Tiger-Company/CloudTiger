"""Integration tests for init command."""

import json
import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

@pytest.fixture(params=['-v', '--version'])
def version_cli_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param

def test_cli_version(cli_runner, version_cli_flag):
    """Verify CloudTiger version output by `cloudtiger --v` on cli invocation."""
    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith('cloudtiger, version')