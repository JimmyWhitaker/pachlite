"""Functionality for interacting with the pachctl mount-server."""
import logging
import subprocess
import urllib.parse
from dataclasses import dataclass
from subprocess import Popen
from time import sleep
from typing import Dict, Literal, Optional

import requests
from requests import get, put, RequestException

logger = logging.getLogger(__name__)


@dataclass
class Mount:
    """Mount object from the mount-server response."""
    name: str
    mode: str
    state: str
    status: str
    mountpoint: str

    @classmethod
    def from_dict(cls, data: Dict) -> "Mount":
        return cls(
            name=data['name'],
            mode=data['mode'],
            state=data['state'],
            status=data['status'],
            mountpoint=data['mountpoint'],
        )


@dataclass
class Branch:
    """Branch object from the mount-server response."""
    name: str
    mount: Mount

    @classmethod
    def from_dict(cls, data: Dict) -> "Branch":
        return cls(
            name=data['name'],
            mount=Mount.from_dict(data['mount'][0]),
        )


@dataclass
class Repo:
    """Repo object from the mount-server response."""
    name: str
    branches: Dict[str, Branch]

    @classmethod
    def from_dict(cls, data: Dict) -> "Repo":
        return cls(
            name=data['name'],
            branches={
                name: Branch.from_dict(branch)
                for name, branch in data['branches'].items()
            },
        )

class MountServer(object):
    MOUNT_MODE = Literal["r", "rw"]
    
    def __init__(self, mount_dir:str):
        self.HEADERS = {'Accept': '*/*', 'Accept-Encoding': ''}
        self.MOUNT_SERVER_URL = "http://localhost:9002"
        self._mount_process: Optional[Popen] = None
        self.mount_dir = mount_dir

    def get_config(self) -> Dict:
        """Returns the JSON response from GET /config"""
        response = get(f"{self.MOUNT_SERVER_URL}/config")
        response.raise_for_status()
        return response.json()


    def get_repos(self) -> Dict[str, "Repo"]:
        """Returns the deserialized response from GET /repos"""
        response = get(f"{self.MOUNT_SERVER_URL}/repos")
        response.raise_for_status()
        return {
            name: Repo.from_dict(repo)
            for name, repo in response.json().items()
        }


    def mount_repo(self,
        repo: str, branch: str, mode: MOUNT_MODE = 'r', name: Optional[str] = None
    ) -> str:
        """Mount the specified branch of the specified pachyderm repository"""
        name = name or f"{repo}@{branch}"
        url = f"{self.MOUNT_SERVER_URL}/repos/{repo}/{branch}/_mount"
        params = urllib.parse.urlencode(dict(name=name, mode=mode), safe='@')
        response = requests.put(url, params=params)
        response.raise_for_status()

        return name


    def unmount_repo(self, repo: str, branch: str, name: Optional[str] = None) -> None:
        """Unmount the specified branch of the specified pachyderm repository"""
        name = name or f"{repo}@{branch}"
        url = f"{self.MOUNT_SERVER_URL}/repos/{repo}/{branch}/_unmount"
        put(url, params=dict(name=name)).raise_for_status()


    def safe_start_mount_server(self, *, wait: int = 30) -> None:
        """Start the mount-server if it is not already started."""
        mount_dir = "/Users/jimmy/pfs"
        
        try:
            subprocess.run(
                    ["bash", "-c", f"umount {mount_dir}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            self.get_config()
        except RequestException:
            self._mount_process = Popen(["/usr/local/bin/pachctl", "mount-server", "--mount-dir",mount_dir])
            for _ in range(wait):
                try:
                    self.get_config()
                    return
                except RequestException:
                    sleep(1)
            raise TimeoutError("Failed to start pachctl mount-server")
        
    def safe_stop_mount_server(self):
        try:
            subprocess.run(
                    ["bash", "-c", f"umount {self.mount_dir}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        except:
            pass