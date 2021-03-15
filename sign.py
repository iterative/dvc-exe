import argparse
import base64
import os
import sys
import tempfile
from subprocess import STDOUT, check_call, check_output, CalledProcessError

CERT_ENV = "EXE_ITERATIVE_CERTIFICATE"
CERT_PASS_ENV = "EXE_ITERATIVE_CERTIFICATE_PASS"

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the executable to sign")
args = parser.parse_args()

cert = os.getenv(CERT_ENV)
if not cert:
    print(f"'{CERT_ENV}' env var is required", file=sys.stderr)
    exit(1)

cert_pass = os.getenv(CERT_PASS_ENV)
if not cert_pass:
    print(f"'{CERT_PASS_ENV}' env var is required", file=sys.stderr)
    exit(1)

if not os.path.exists(args.path):
    print(f"'{args.path}' doesn't exist", file=sys.stderr)
    exit(1)

try:
    out = check_output(
        [
            "powershell.exe",
            f"(Get-AuthenticodeSignature -FilePath {args.path}).SignerCertificate | Format-List",
        ],
        stderr=STDOUT,
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output}", file=sys.stderr)
    raise

# TODO: check that it is not signed yet
print(out)

with tempfile.NamedTemporaryFile() as tmp:
    tmp.write(base64.b64decode(cert))
    cmd = [
        "signtool.exe",
        f"/F {tmp.name}",
        f"/P {cert_pass}",
        "/T http://timestamp.digicert.com",
        args.path,
    ]
    check_call(cmd)

try:
    out = check_output(
        [
            "powershell.exe",
            f"(Get-AuthenticodeSignature -FilePath {args.path}).SignerCertificate | Format-List",
        ],
        stderr=STDOUT,
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output}", file=sys.stderr)
    raise

# TODO: check that it is signed
print(out)

print(f"successfully signed '{args.path}'")
