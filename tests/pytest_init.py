"""Integration tests for init command."""

import json
import os
import re
from pathlib import Path
from cloudtiger import helper

import pytest
from click.testing import CliRunner

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
    assert result.output.startswith('cloudtiger, version')

def test_cli_helper(cli_runner, cli_main_helper):
    """Check main helper"""
    result = cli_runner(cli_main_helper)
    assert result.exit_code == 0
    assert result.output == helper.helpers["basic"]

def test_cli_init_folder(cli_runner):
    """Check init folder command"""
    