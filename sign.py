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

print("=== checking for existing signature")

try:
    out = check_output(
        [
            "powershell.exe",
            f"(Get-AuthenticodeSignature -FilePath {args.path}).SignerCertificate | Format-List",
        ],
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output}", file=sys.stderr)
    raise

# TODO: check that it is not signed yet
print(out)

print("=== checking available SDKs")
sdks_path = "C:\Program Files (x86)\Microsoft SDKs\Windows"
sdks = os.listdir(sdks_path)
if not sdks:
    print("no SDKs found", file=sys.stderr)
print("\n".join(sdks))
sdk = sdks[0]
sdk_bin = os.path.join(sdks_path, sdk, "bin")
print(f"using {sdk}")
path = os.pathsep.join(
    [
        sdk_bin,
        os.environ.get("PATH", os.defpath),
    ],
)
env = dict(os.environ, PATH=path)
print("\n".join(os.listdir(sdk_bin)))

print(f"=== signing {args.path}")

with tempfile.NamedTemporaryFile() as tmp:
    tmp.write(base64.b64decode(cert))
    try:
        check_call(
            [
                "C:\\Program Files (x86)\\Windows Kits\\10\\App Certification Kit\\signtool.exe",
                "sign",
                f"/F {tmp.name}",
                f"/P {cert_pass}",
                "/T http://timestamp.digicert.com",
                args.path,
            ],
            stderr=STDOUT, shell=True, env=env,
        )
    except CalledProcessError as exc:
        print(f"failed to sign:\n{exc.output}", file=sys.stderr)
        raise

print("=== checking signed executable")

try:
    out = check_output(
        [
            "powershell.exe",
            f"(Get-AuthenticodeSignature -FilePath {args.path}).SignerCertificate | Format-List",
        ],
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output}", file=sys.stderr)
    raise

# TODO: check that it is signed
print(out)

print(f"=== successfully signed '{args.path}'")
