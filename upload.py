import os
import sys
import posixpath
import argparse

from glob import glob
from subprocess import STDOUT, check_call, check_output, CalledProcessError


DEST = "s3://dvc-public/dvc-pkgs/exe/"

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the executable to upload")
args = parser.parse_args()

path, = glob(args.path)

dest = posixpath.join(DEST, os.path.basename(path))

try:
    out = check_output(
        f"aws s3 cp {path} {dest}",
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to upload:\n{exc.output.decode()}", file=sys.stderr)
    raise
