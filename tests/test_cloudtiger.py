# #!/usr/bin/env python

# """Tests for `cloudtiger` package."""

# import os
# import shutil
# import unittest
# import pkg_resources

# from click.testing import CliRunner

# from cloudtiger import cli, helper

# TEST_DATA_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests')
# TEST_FOLDER = pkg_resources.resource_filename('cloudtiger', '../tests/run')

# test_paths = {
#     "simple" : ".",
#     "absolute" : "/app/absolute_test_path",
#     "relative" : "./relative_test_path",
#     "absolute_with_whitespace" : "/app/absolute\ test\ path",
#     "relative_with_whitespace" : "./app/relative\ test\ path"
# }

# class TestCloudtiger(unittest.TestCase):
#     """Tests for `cloudtiger` package."""

#     def setUp(self):
#         """Set up test fixtures, if any."""
#         os.chdir(TEST_FOLDER)

#         # we create gitops folders using several pathes
#         gitops_test_folder = os.path.join(TEST_DATA_FOLDER, "gitops")
#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep:
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else :
#                 test_path = os.path.join(os.getcwd(), test_path)
#             print(test_path)
#             shutil.copytree(gitops_test_folder, test_path, dirs_exist_ok=True)

#     def tearDown(self):
#         """Tear down test fixtures, if any."""

#         # we delete test gitops folders
#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep:
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else :
#                 test_path = os.path.join(os.getcwd(), test_path)
#             test_path = os.path.join(test_path, "gitops")
#             if os.path.isdir(test_path):
#                 shutil.rmtree(test_path)

#     def test_command_line_interface(self):
#         """Test the CLI."""
#         runner = CliRunner()
#         result = runner.invoke(cli.main)
#         assert result.exit_code == 0
#         assert 'Cloud Tiger is a CLI tool' in result.output

#         help_result = runner.invoke(cli.main, ['--help'])
#         assert help_result.exit_code == 0
#         print(help_result.output)

#         assert helper.helpers["basic"] in help_result.output

#         argument_result = runner.invoke(cli.main, ['init', '--help'])
#         assert argument_result.exit_code == 0
#         print(argument_result.output)

#         argument_result = runner.invoke(cli.main, ['tf', '--help'])
#         assert argument_result.exit_code == 0
#         print(argument_result.output)

#         argument_result = runner.invoke(cli.main, ['ans', '--help'])
#         assert argument_result.exit_code == 0
#         print(argument_result.output)

#     def test_cli_init_0(self) :
#         """Test the 'init 0' command """
#         runner = CliRunner()
#         test_scopes = [
#             os.path.join("aws", "single_scope"),
#             os.path.join("aws", "networks"),
#             os.path.join("vsphere", "single_scope")
#         ]

#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep :
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else :
#                 test_path = os.path.join(os.getcwd(), test_path)


#             for test_scope in test_scopes:

#                 test_path = test_path.replace(' ', "WHITESPACE")
#                 command = format("--project-root %s --output-file"
#                                  " %s --error-file %s %s init 0" %
#                                  (test_path, 'cloudtiger_std.log',
#                                   'cloudtiger_stderr.log',test_scope))
#                 command = command.split(' ')
#                 command = [elt.replace("WHITESPACE", " ") for elt in command]

#                 result = runner.invoke(cli.main, command)
#                 print(result.output)
#                 assert result.exit_code == 0

#     def test_cli_init_1(self) :
#         """Test the 'init 1' command """
#         runner = CliRunner()
#         test_scopes = [
#             os.path.join("aws", "single_scope"),
#             os.path.join("vsphere", "single_scope").
#             os.path.join("nutanix", "single_scope")
#         ]

#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep:
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else :
#                 test_path = os.path.join(os.getcwd(), test_path)

#             for test_scope in test_scopes:

#                 test_path = test_path.replace(' ', "WHITESPACE")
#                 command = format("--project-root %s --output-file"
#                                  " %s --error-file %s %s init 1" %
#                                  (test_path, 'cloudtiger_std.log',
#                                   'cloudtiger_stderr.log',test_scope))
#                 command = command.split(' ')
#                 command = [elt.replace("WHITESPACE", " ") for elt in command]

#                 result = runner.invoke(cli.main, command)
#                 print(result.output)
#                 assert result.exit_code == 0

#     def test_cli_init_2(self) :
#         """Test the 'init 2' command """
#         runner = CliRunner()

#         libraries_path = pkg_resources.resource_filename('cloudtiger', 'libraries')

#         test_scopes = [
#             os.path.join("aws", "single_scope"),
#             os.path.join("vsphere", "single_scope"),
#             os.path.join("nutanix", "single_scope")
#         ]

#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep:
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else :
#                 test_path = os.path.join(os.getcwd(), test_path)

#             for test_scope in test_scopes:

#                 test_path = test_path.replace(' ', "WHITESPACE")
#                 command = format("--project-root %s --output-file"
#                                  "%s --error-file %s --l %s %s init 2" %
#                                  (test_path, 'cloudtiger_std.log',
#                                   'cloudtiger_stderr.log', libraries_path, test_scope))
#                 command = command.split(' ')
#                 command = [elt.replace("WHITESPACE", " ") for elt in command]

#                 result = runner.invoke(cli.main, command)
#                 print(result.output)
#                 assert result.exit_code == 0

#     def test_cli_tf_0(self) :
#         """Test the 'init 2' command """
#         runner = CliRunner()

#         libraries_path = pkg_resources.resource_filename('cloudtiger', 'libraries')

#         test_scopes = [
#             # os.path.join("aws", "single_scope"),
#             # os.path.join("vsphere", "single_scope"),
#             os.path.join("nutanix", "single_scope")
#         ]

#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep:
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else:
#                 test_path = os.path.join(os.getcwd(), test_path)

#             for test_scope in test_scopes:

#                 test_path = test_path.replace(' ', "WHITESPACE")
#                 command = format("--project-root %s --output-file %s --error-file"
#                                  "%s --l %s %s tf 0" % (test_path, 'cloudtiger_std.log',
#                                                         'cloudtiger_stderr.log',
#                                                         libraries_path, test_scope))
#                 command = command.split(' ')
#                 command = [elt.replace("WHITESPACE", " ") for elt in command]

#                 result = runner.invoke(cli.main, command)
#                 print(result.output)
#                 assert result.exit_code == 0

#     def test_cli_tf_generic(self) :
#         """Test the 'tf <TF_COMMAND>' command """
#         runner = CliRunner()

#         libraries_path = pkg_resources.resource_filename('cloudtiger', 'libraries')

#         test_scopes = [
#             # os.path.join("aws", "single_scope"),
#             # os.path.join("vsphere", "single_scope"),
#             os.path.join("nutanix", "single_scope")
#         ]

#         for _, test_path in test_paths.items():
#             if test_path[0] == os.path.sep:
#                 test_path = os.path.join(TEST_FOLDER, test_path[1:])
#             else:
#                 test_path = os.path.join(os.getcwd(), test_path)

#             for test_scope in test_scopes :

#                 test_path = test_path.replace(' ', "WHITESPACE")

#                 for tf_action in ["plan"]:
#                     command = format("--project-root %s --output-file"
#                                      "%s --error-file %s --l %s %s tf %s" %
#                                      (test_path, 'cloudtiger_std.log',
#                                       'cloudtiger_stderr.log',
#                                       libraries_path, test_scope, tf_action))
#                     command = command.split(' ')
#                     command = [elt.replace("WHITESPACE", " ") for elt in command]

#                     result = runner.invoke(cli.main, command)
#                     print(result.output)
#                     assert result.exit_code == 0
