import argparse
import base64
import os
import sys
from glob import glob
from subprocess import STDOUT, CalledProcessError, check_call, check_output

CERT_ENV = "EXE_ITERATIVE_CERTIFICATE"
CERT_PASS_ENV = "EXE_ITERATIVE_CERTIFICATE_PASS"
SIGNTOOL = (
    "C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit\\signtool.exe"
)

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the executable to sign")
args = parser.parse_args()

(path,) = glob(args.path)

cert = os.getenv(CERT_ENV)
if not cert:
    print(f"'{CERT_ENV}' env var is required", file=sys.stderr)
    exit(1)

cert_path = "cert.pfx"
with open(cert_path, "wb") as fobj:
    fobj.write(base64.b64decode(cert))

cert_pass = os.getenv(CERT_PASS_ENV)
if not cert_pass:
    print(f"'{CERT_PASS_ENV}' env var is required", file=sys.stderr)
    exit(1)

if not os.path.exists(path):
    print(f"'{path}' doesn't exist", file=sys.stderr)
    exit(1)

print("=== checking for existing signature")

# https://github.com/PowerShell/PowerShell/issues/18530#issuecomment-1325691850
os.environ["PSModulePath"] = ""

try:
    out = check_output(
        [
            "powershell.exe",
            f"(Get-AuthenticodeSignature -FilePath {path}).SignerCertificate | Format-List",
        ],
        stderr=STDOUT,
        shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output.decode()}", file=sys.stderr)
    raise

# TODO: check that it is not signed yet
print(out.decode())

print(f"=== signing {path}")

try:
    check_call(
        [
            SIGNTOOL,
            "sign",
            "/fd",
            "SHA256",
            "/F",
            cert_path,
            "/P",
            cert_pass,
            "/T",
            "http://timestamp.digicert.com",
            path,
        ],
        stderr=STDOUT,
        shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

print("=== verifying signed executable")

try:
    out = check_output(
        [
            "powershell.exe",
            f"(Get-AuthenticodeSignature -FilePath {path}).SignerCertificate | Format-List",
        ],
        stderr=STDOUT,
        shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output.decode()}", file=sys.stderr)
    raise

# TODO: check that it is properly signed
print(out.decode())

print(f"=== successfully signed '{path}'")
