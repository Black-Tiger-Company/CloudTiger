"""pytest fixtures which are globally available throughout the suite."""
import os
import shutil

import pytest
from click.testing import CliRunner

from cloudtiger.cli import main

@pytest.fixture(scope='session')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(command:str):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, command.split())

    return cli_main