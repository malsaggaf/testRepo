#!/usb/bin/env python3

import json
import os
import subprocess
from datetime import date, datetime



class GitVersion:
    REVISION_SUFFIX_LENGTH = 8

    def __init__(self, source_dir):
        self.source_dir = source_dir

    def get_version_info(self):
        commit = (
            self._exec_git(f"rev-parse --short={self.REVISION_SUFFIX_LENGTH} HEAD")
            or "unknown"
        )

        dirty = False
        try:
            self._exec_git("diff --quiet")
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                dirty = True

        dirtyFiles = self._exec_git("status -s")


        # If WORKFLOW_BRANCH_OR_TAG is set in environment, is has precedence
        # (set by CI)
        # branch = (
        #     os.environ.get("WORKFLOW_BRANCH_OR_TAG", None)
        #     or self._exec_git("rev-parse --abbrev-ref HEAD")
        #     or "unknown"
        # )


        branch = self._exec_git("rev-parse --abbrev-ref HEAD")


        try:
            version = self._exec_git("describe --tags --abbrev=0") #latest version(tag) on the branch 
            distanceFromTag = self._exec_git("describe --tags") #number of commmits between the tag and HEAD

            try:
                distanceFromTag = distanceFromTag.split('-')[1]

            except IndexError:
                distanceFromTag = '0'


        except subprocess.CalledProcessError:
            version = "unknown"

        # if "SOURCE_DATE_EPOCH" in os.environ:
        #     commit_date = datetime.utcfromtimestamp(
        #         int(os.environ["SOURCE_DATE_EPOCH"])
        #     )
        # else:
            # commit_date = datetime.strptime(
            #     self._exec_git("log -1 --format=%cd").strip(),
            #     "%a %b %d %H:%M:%S %Y %z",
            # )

        commit_date = self._exec_git("--no-pager show -s --date=local --format='%ad' --date=format:%d/%m/%Y-%H:%M:%S")

        return {
            "GIT_COMMIT": commit,
            "GIT_BRANCH": branch,
            "VERSION": version,
            "TAG_DISTANCE_FROM_HEAD": distanceFromTag,
            "BUILD_DIRTY": dirty and 1 or 0,
            "DIRTY_FILES": dirtyFiles,
            "GIT_ORIGIN": ",".join(self._get_git_origins()),
            "GIT_COMMIT_DATE": commit_date,

        }

    def _get_git_origins(self):
        try:
            remotes = self._exec_git("remote -v")
        except subprocess.CalledProcessError:
            return set()
        origins = set()
        for line in remotes.split("\n"):
            if not line:
                continue
            _, destination = line.split("\t")
            url, _ = destination.split(" ")
            origins.add(url)
        return origins

    def _exec_git(self, args):
        cmd = ["git"]
        cmd.extend(args.split(" "))
        return (
            subprocess.check_output(cmd, cwd=self.source_dir, stderr=subprocess.STDOUT)
            .strip()
            .decode()
        )



if __name__ == "__main__":
    var = GitVersion(os.getcwd())
    print(var.get_version_info())
    

