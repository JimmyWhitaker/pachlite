from pathlib import Path
from os import listdir
import sys
import click

@click.command()
@click.option('--dir')
# @click.option('--dir', type=click.Path(exists=True))
def run(dir):
    tmp_dir = '/Users/jimmy/pfs/images/'
    print(listdir(tmp_dir))

if __name__ == '__main__':
    run()