import argparse
from subprocess import STDOUT, check_call, check_output, CalledProcessError

DEST = "s3://dvc-public/dvc-pkgs/exe/"

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the executable to upload")
args = parser.parse_args()

try:
    out = check_output(
        [
            "aws", "s3", "cp", args.path, DEST, "--acl", "public-read",
        ],
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to upload:\n{exc.output.decode()}", file=sys.stderr)
    raise
