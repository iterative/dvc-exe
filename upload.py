import argparse
import os
import posixpath
import sys
from glob import glob
from subprocess import STDOUT, CalledProcessError, check_output

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the executable to upload")
parser.add_argument("dest", help="destination S3 path")
args = parser.parse_args()

(path,) = glob(args.path)

dest = posixpath.join(args.dest, os.path.basename(path))

try:
    out = check_output(f"aws s3 cp {path} {dest}", stderr=STDOUT, shell=True)
except CalledProcessError as exc:
    print(f"failed to upload:\n{exc.output.decode()}", file=sys.stderr)
    raise
