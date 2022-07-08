from email.mime import multipart
from pachlite.mount_server import *

import click
import logging
from pathlib import Path
from os import listdir
from time import sleep
import json

from lightning_app.components.python import PopenPythonScript
from lightning_app.components.python import TracerPythonScript

logger = logging.getLogger(__name__)
MOUNT_SERVER = MountServer("/Users/jimmy/pfs/")


@click.group()
def cli():
    """PyPach
    Utilities for developing Pachyderm pipelines locally.
    """
    pass


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option(
    "-i",
    "--input",
    prompt="Input(s)",
    help="Input repo(s) - format repo@branch",
    multiple=True,
)
@click.argument("entrypoint", type=click.Path(exists=True))
@click.argument("entrypoint_args", nargs=-1, type=click.UNPROCESSED)
def run(entrypoint, input, entrypoint_args):
    """Run python file locally as if it were a pipeline"""
    # Start mount server
    MOUNT_SERVER.safe_start_mount_server()

    # Mount Repos
    for i in input:
        repo, branch = i.split("@")
        name = repo
        logger.info(MOUNT_SERVER.mount_repo(repo, branch, name=name))

    python_script = PopenPythonScript(
        entrypoint, list(entrypoint_args)
    )  # TODO Change to TracerPythonScript in the future?
    python_script.run()

    # Unmount Repos
    for i in input:
        repo, branch = i.split("@")
        name = repo
        logger.info(MOUNT_SERVER.unmount_repo(repo, branch, name=name))

    # Stop mount server
    MOUNT_SERVER.safe_stop_mount_server()


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option("-n", "--name", prompt="Pipeline Name", help="Name of pipeline")
@click.option(
    "-d", "--description", prompt="Pipeline Description", help="Description of pipeline"
)
@click.option(
    "--image",
    prompt="Docker Image",
    help="Name of docker image to be used for the entrypoint",
)
@click.option(
    "-i", "--input_repo", help="Input repo(s) - format repo@branch", multiple=True
)
@click.option("--entrypoint", type=click.Path(exists=True))
@click.argument("entrypoint_args", nargs=-1, type=click.UNPROCESSED)
def build(name, description, image, input_repo, entrypoint, entrypoint_args):
    """Build pachyderm pipeline"""
    if not name:
        click.echo(f"Enter pipeline name (ex. 'hello'): {name}")
    if not input_repo:
        input_repo = input(
            "Enter input repos (ex. images@master labels@master) : "
        ).split()
        
    cmd = ("python "
            + str(entrypoint)
            + " "
            + str(" ".join(list(entrypoint_args)))).split()

    pipeline = {
        "pipeline": {"name": name},
        "description": description,
        "input": {},
        "transform": {
            "image": image,
            "cmd": cmd,
        },
    }

    pipeline_inputs = []
    for i in input_repo:
        print(i)
        repo, branch = i.split("@")
        pipeline_inputs.append({"pfs": {"repo": repo, "branch": branch, "glob": "/"}})

    if len(input_repo) > 1:
        pipeline["input"] = {"cross": pipeline_inputs}
    else:
        pipeline["input"] = pipeline_inputs[0]

    print(json.dumps(pipeline, sort_keys=True, indent=4, separators=(",", ": ")))


cli.add_command(run)
cli.add_command(build)
