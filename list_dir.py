from pathlib import Path
from os import listdir
import sys
import click

@click.command()
@click.option('--dir', type=click.Path(exists=True))
def run(dir):
    print(listdir(dir))

if __name__ == '__main__':
    run()