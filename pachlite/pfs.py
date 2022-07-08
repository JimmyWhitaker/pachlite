from pathlib import Path
import os

PIPELINE_ENV_VAR = "_PACHYDERM_PIPELINE_CONTAINER"

def in_container() -> bool:
    return bool(os.environ.get(PIPELINE_ENV_VAR))

class PFS:

    @staticmethod
    def get(repo: str, out: bool = False) -> Path:
        if in_container():
            path = Path("/pfs", repo) if not out else Path("/pfs/out")
            if not path.exists():
                raise NotADirectoryError(path)
        else:
            raise NotImplementedError(
                "TODO: Add connection with mount extension for local development"
            )
        return path