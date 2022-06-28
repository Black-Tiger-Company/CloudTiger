""" Common Tools for CloudTiger."""
import json
import logging
import os
import shutil
import subprocess
import sys
from logging import Logger
import click
from collections import OrderedDict

import yaml
from jinja2 import Template


def merge_dictionaries(dict1: dict, dict2: dict) -> dict:

    """
    Recursive merge dictionaries.

    :param dict1: Base dictionary to merge.
    :param dict2: Dictionary to merge on top of base dictionary.

    :return: Merged dictionary
    """

    for key, val in dict1.items():
        if isinstance(val, dict):
            dict2_node = dict2.setdefault(key, {})
            merge_dictionaries(val, dict2_node)
        else:
            if key not in dict2:
                dict2[key] = val

    return dict2


def bash_source(logger: Logger, envfile: str):

    """ this function runs a 'source' on the dotenv file, and loads
    its content in os.environment

    :param logger: Logger, a Logger object to log details
    :param envfile: str, the path of the dotenv file to 'source'
    """

    logger.debug("Executing a source on dotenv file %s" % envfile)

    if os.path.isfile(envfile):
        command = format('env -i bash -c "source %s && env"' % envfile)
        for line in subprocess.getoutput(command).split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

def j2(logger: Logger, template_file: str, dictionary: dict, output_file: str):

    """ this function uses a 'template' j2 file, and use variables from 'dictionary'
    to dump the rendered 'output_file'

    :param logger: Logger, a Logger object to log details
    :param template_file: str, the path to the jinja2 template file
    :param dictionary: dict, the dictionary to use to interprete the jinja2 template
    :param output_file: str, the path to the interpreted output file
    """

    logger.debug("Rendering template file %s to output file %s with jinja2" 
                % (template_file, output_file))

    if not os.path.exists(template_file):
        err = format("Error : jinja template file %s does not exist" % template_file)
        logger.error(err)
        raise Exception(err)

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        logger.debug("Output folder %s does not exist, creating it" % output_dir)
        os.makedirs(output_dir, exist_ok=True)

    with open(template_file, 'r') as f:
        template = f.read()

    tm = Template(template)

    with open(output_file, "w") as f:
        f.write(tm.render(dictionary, env=os.environ))

    logger.debug("Rendering successful")


def load_json(logger: Logger, jsonfile: str) -> dict:

    """ this function loads a json file and returns the content as a dictionary

    :param logger: Logger, a Logger object to log details
    :param jsonfile: the path to the json file to load

    :return: content of the json file as a python dictionary
    """

    logger.debug("Loading json file %s as dictionary" % jsonfile)

    if os.path.exists(jsonfile):
        with open(jsonfile, 'r') as f:
            return json.load(f)

    else:
        raise Exception("Cannot read %s file : file does not exist" % jsonfile)


def load_yaml(logger: Logger, yamlfile: str):

    """ this function loads a json file and returns the content as a dictionary

    :param logger: Logger, a Logger object to log details
    :param yamlfile: str, the path of the yaml file to load

    :return: dict, content of the yaml file as a python dictionary
    """

    logger.debug("Loading yaml file %s as dictionary" % yamlfile)

    if os.path.exists(yamlfile):
        with open(yamlfile, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    else:
        raise Exception("Cannot read %s file : file does not exist" % yamlfile)


def bash_action(logger: Logger,
                command: str,
                folder: str,
                env: dict,
                output=None,
                error=None,
                single_output=False,
                background=False,
                set_input=None):

    """ this function wraps a bash command 

    :param logger: Logger, a Logger object to log details
    :param command: str, the bash command as a string
    :param folder: str, the path to the folder where the command will be executed
    :param env: str, the environment to use for the execution
    :param output: str, the path to the file where the output will be dumped
    :param error: str, the path to the file where the errors will be dumped
    :param single_output: bool, set to True if you expect to erase previous outputs
    in the output file
    :param background: bool, set to True if you want to run the command in the
    background
    :param set_input: str, add a command to apply if the command is expect to prompt a question
    """

    logger.info("Bash action : %s" % command)

    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT

    if output is not None:
        logger.debug("Standard output sent to %s" % output)
        if single_output is False:
            stdout = open(output, "a")
        else: 
            logger.debug("Single output")
            stdout = open(output, "w")

    if error is not None:
        logger.debug("Standard error sent to %s" % output)
        stderr = open(error, "a")

    try:
        logger.info("Execution of command :\n%s > %s \nin folder %s\n" % (command, output, folder))
        if background is True:
            if set_input is not None:
                result = subprocess.Popen(command, env=env, cwd=folder, shell=True,
                                          stdin=subprocess.PIPE)
                result.stdin.write(set_input)
                result.communicate()
            else:
                subprocess.Popen(command, env=env, cwd=folder, shell=True)
        else:
            if set_input is not None:
                result = subprocess.Popen(command, env=env, cwd=folder,
                                          stdout=subprocess.PIPE, stderr=stderr,
                                          shell=True, text=True, stdin=subprocess.PIPE)
                result.communicate(input=set_input)
            else:
                result = subprocess.Popen(command, env=env, cwd=folder, stdout=stdout,
                                          stderr=stderr, shell=True, text=True)
            # we print output in console only if no output file has been specified
            if (output is None) & (result.stdout is not None) & (background is False):
                while True:
                    line = result.stdout.readline()
                    if not line:
                        break
                    else:
                        logger.info(line.replace('\r', '').replace('\n', ''))
            else:
                result.wait()
    except Exception as e:
        logger.error("Error in the execution of command :\n%s" % e)
        raise Exception(e)

    logger.info("Successful bash action")


def find_exec_path(executable):

    """ this function returns the path to the Terraform executable """

    exec_path = shutil.which(executable)

    return exec_path


def create_logger(logfile='', verbose=False):

    """ this function create a nice logger object """

    if logfile == '':
        logfile = os.getcwd()
        logfile = os.path.join(logfile, 'cloudtiger.log')

    logger = logging.getLogger(__name__)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler(logfile)
    if verbose:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    # create a console handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    if verbose:
        stdout_handler.setLevel(logging.DEBUG)
    else:
        stdout_handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(stdout_handler)

    logger.debug('Logger created')

    return logger


def create_ssh_keys(logger: Logger, private_ssh_folder: str, public_ssh_folder: str,
                    stdout_file=None, stderr_file=None, ssh_key_name="id_rsa"):

    """ this function creates a pair (public/private) of ssh keys """

    logger.debug("Creating folder %s" % private_ssh_folder)
    os.makedirs(private_ssh_folder, exist_ok=True)
    os.makedirs(public_ssh_folder, exist_ok=True)

    created_ssh_private_key = os.path.join(private_ssh_folder, ssh_key_name)
    created_ssh_public_key = os.path.join(private_ssh_folder, ssh_key_name + ".pub")

    dest_ssh_public_key = os.path.join(public_ssh_folder, ssh_key_name + ".pub")

    if (not os.path.exists(created_ssh_private_key)) | (not os.path.exists(dest_ssh_public_key)):
        logger.debug("Public or private key does not exist, let us create a new pair")

        if os.path.exists(created_ssh_private_key):
            os.remove(created_ssh_private_key)

        if os.path.exists(dest_ssh_public_key):
            os.remove(dest_ssh_public_key)

        logger.debug("Creating SSH key pair")
        env = {"PRIVATE_FOLDER": private_ssh_folder, "KEY_NAME": ssh_key_name}

        command = "ssh-keygen -q -t rsa -f $PRIVATE_FOLDER/$KEY_NAME -N ''"

        bash_action(logger, command, os.getcwd(), env, stdout_file, stderr_file)

        # ensure keys are created
        if not os.path.exists(created_ssh_private_key):
            err = format("The private ssh key pair %s has not been created : "
                         "error" % created_ssh_private_key)
            logger.error(err)
            raise Exception(err)

        if not os.path.exists(created_ssh_public_key):
            err = format("The public ssh key pair %s has not been created : "
                         "error" % created_ssh_public_key)
            logger.error(err)
            raise Exception(err)

        shutil.move(created_ssh_public_key, dest_ssh_public_key)
        logger.debug("SSH key pair moved successfully")

    else:
        logger.debug("An SSH key pair already exists")

def get_credentials(provider_helper, credential_dir, append=False):

    """ This function will use multiple prompt to collect credentials for the 
    chosen cloud provider

    :param str provider: Provider name
    """

    # set templates file
    for filename in provider_helper.get("templates", []):
        filename = os.path.join(credential_dir, filename)
        if len(filename) > 3:
            if filename[-4:] == ".tpl":
                if not os.path.exists(filename[:-4]):
                    shutil.copyfile(filename, filename[:-4])

    if "initial_helper" in provider_helper.keys():
        print(provider_helper["initial_helper"])

    dotenv_content = {}
    for variable in provider_helper["keys"]:
        dotenv_content[variable['name']] = click.prompt(
            variable['helper'],
            hide_input=variable.get("sensitive", False),
            default=variable.get("default", None)
            )
    dotenv_content = "\n".join(
        [format("export %s=%s" % (key, value)) for key, value in dotenv_content.items()])
    if len(dotenv_content) > 0:
        dotenv_content += "\n"

    if append:
        write_mode = "a"
    else:
        write_mode = "w"

    with open(os.path.join(credential_dir, ".env"), write_mode) as f:
        f.write(dotenv_content)

    if "final_helper" in provider_helper.keys():
        print(provider_helper["final_helper"])

def read_user_choice(var_name, options):
    """Prompt the user to choose from several options for the given variable.

    The first item will be returned if no input happens.

    :param str var_name: Variable as specified in the context
    :param list options: Sequence of options that are available to select from
    :return: Exactly one item of ``options`` that has been chosen by the user
    """
    choice_map = OrderedDict((f'{i}', value) for i, value in enumerate(options, 1))
    choices = choice_map.keys()
    default = '1'

    choice_lines = ['{} - {}'.format(*c) for c in choice_map.items()]
    prompt = '\n'.join(
        (
            f"Select {var_name}:",
            "\n".join(choice_lines),
            f"Choose from {', '.join(choices)}",
        )
    )

    user_choice = click.prompt(
        prompt, type=click.Choice(choices), default=default, show_choices=False
    )
    return choice_map[user_choice]
