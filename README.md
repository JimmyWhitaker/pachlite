# PachLite
The PachLite is a hack project to simplify a couple of convenience functions. 

## Install
The project uses `poetry`:

```bash
poetry shell
poetry install
```

## Using the CLI

```
$ pachlite
Usage: pachlite [OPTIONS] COMMAND [ARGS]...

  PyPach Utilities for developing Pachyderm pipelines locally.

Options:
  --help  Show this message and exit.

Commands:
  build  Build pachyderm pipeline
  run    Run python file locally as if it were a pipeline
```

```
$ pachlite build --help
Usage: pachlite build [OPTIONS] [ENTRYPOINT_ARGS]...

  Build pachyderm pipeline

Options:
  -n, --name TEXT         Name of pipeline
  -d, --description TEXT  Description of pipeline
  --image TEXT            Name of docker image to be used for the entrypoint
  -i, --input_repo TEXT   Input repo(s) - format repo@branch
  --entrypoint PATH
  --help                  Show this message and exit.
```

```
pachlite run --help
Usage: pachlite run [OPTIONS] ENTRYPOINT [ENTRYPOINT_ARGS]...

  Run python file locally as if it were a pipeline

Options:
  -i, --input TEXT  Input repo(s) - format repo@branch
  --help            Show this message and exit.
```

