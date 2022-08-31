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
