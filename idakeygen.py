# Made specifically for IDA 9.5
# May not work for other versions of this software including future ones

import json
import hashlib
import os
import argparse
import shutil
from datetime import datetime, timedelta
import sys


def sort(obj):
    """Recursive sorting into json string"""
    if isinstance(obj, list):
        return '[' + ','.join(sort(item) for item in obj) + ']'
    elif isinstance(obj, dict):
        keys = sorted(obj.keys())
        return '{' + ','.join(f'"{k}":{sort(obj[k])}' for k in keys) + '}'
    else:
        return json.dumps(obj)


# Constants for IDA 9.5
cModulus = bytes.fromhex("3f0307607fed562fd5a163adc40fcc603373caa28414e64cdc4552a555b13ad4b3ad0a812800a03195300fd71634b90edb0d69ea710efebb2b0b9e72da2effb149de70bcbfa94b86af01ce455dbbd5fa987207651c7b60c2e4cafd0654188d98c30f64dc084d8547f0ac32db91124af82b3b15bf922a31f1d5e332f27615cea7")
privateKey = bytes.fromhex("8b3f5fdfad7f87239734c530e2ecebeb4fa48d79518756c15fd54636801cf7ea6367100566bf8b52b16bec05258d8426ea94c15841ab2d37802c07349df4c208584e86d25a6bfb82966cb2ddcd3d654e9994e814ca470577362a937cc984e404a0b68d173aab3180130118e1b03ed209a9d8757560a85a3c9b0d3380e7907c4f")

V54 = 127
V56 = 95
PADKEY = bytes.fromhex("e2a7c300dfcc777f89b57500d8151c7fb1d97b3f9f170393311234ceeb9e377ae2a7c300dfcc777f89b57500d8151c7fb1d97b3f9f170393311234ceeb9e377ae2a7c300dfcc777f89b57500d8151c7fb1d97b3f9f170393311234ceeb9e377ae2a7c300dfcc777f89b57500d8151c7fb1d97b3f9f170393311234ceeb9e377ae2a7c300dfcc777f89b57500d8151c7fb1d97b3f9f170393311234ceeb9e37")


def json_stringify_alphabetical(obj: dict):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def buf_to_bigint(buf: bytes):
    return int.from_bytes(buf, byteorder="little")


def bigint_to_buf(i: int):
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder="little")


def bytes_to_bigint(data):
    """Convert bytes to big integer (little-endian)"""
    result = 0
    for b in reversed(data):
        result = (result << 8) | b
    return result


def bigint_to_bytes(n):
    """Convert big integer to bytes (little-endian)"""
    if n == 0:
        return b'\x00'
    result = []
    while n > 0:
        result.append(n & 0xFF)
        n >>= 8
    return bytes(result)


def encrypt(message):
    """RSA encryption"""
    modulus = bytes_to_bigint(cModulus)
    key = bytes_to_bigint(privateKey)

    reversed_msg = bytes(reversed(message))
    msg = bytes_to_bigint(reversed_msg)

    # RSA encryption: c = m^e mod n
    base = msg % modulus
    exponent = key
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        exponent >>= 1
        base = (base * base) % modulus

    return bigint_to_bytes(result)


def create_license(
    name: str,
    license_type: str,
    owner="hi@hex-rays.com",
    start_date: str | None = None,
    end_date: str | None = None,
):
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")

    if end_date is None:
        # Default to 10 years - 1 day from start date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=10 * 365 - 1)
        end_date = end_dt.strftime("%Y-%m-%d")

    id = "14-0000-FFFF-88"
    license = {
        "header": {"version": 1},
        "payload": {
            "name": "ntkey",
            "email": "admin@hex-rays.com",
            "licenses": [
                {
                    "description": "license",
                    "edition_id": "ida-pro",
                    "id": id,
                    "product_id": "IDAPRO",
                    "product_version": "9.5",
                    "license_type": license_type,
                    "product": "IDA",
                    "seats": 1,
                    "start_date": start_date + " 00:00:00",
                    "end_date": end_date + " 23:59:59",
                    "issued_on": f"{start_date} 00:00:00",
                    "owner": name,
                    "add_ons": get_addons(
                        owner=id,
                        start_date=start_date,
                        end_date=end_date,
                    ),
                    "features": [],
                }
            ],
        },
    }

    return license


def get_addons(owner: str, start_date: str, end_date: str) -> list[dict]:
    addons = [
        'LUMINA', 'TEAMS',
        'HEXX86', 'HEXX64', 'HEXARM', 'HEXARM64',
        'HEXMIPS', 'HEXMIPS64', 'HEXPPC', 'HEXPPC64',
        'HEXRV', 'HEXRV64', 'HEXARC', 'HEXARC64',
        'HEXV850', 'HEXDALVIK'
    ]

    result = []

    for i, addon in enumerate(addons):
        result.append(
            {
                "id": f"48-1337-B00B-{i + 1:02d}",
                "code": addon,
                "owner": owner,
                "start_date": start_date + " 00:00:00",
                "end_date": end_date + " 23:59:59",
            }
        )
    return result


def generate_license_file(license_data, filename="idapro.hexlic"):
    license_data["signature"] = sign(license_data["payload"])

    # Use indented formatting for output to improve readability
    serialized = json.dumps(license_data, indent=2, sort_keys=True)

    with open(filename, "w") as f:
        f.write(serialized)

    print(f"Saved new license to {filename}!")
    return True


# IDA 9.5 patch bytes
PATCH_SEARCH = bytes.fromhex("29f4481f796f9f66f2ff13cc4ab5b54f60845db603ba2c0bac8a9bc4b6cbdefc5c62bfc2f5ee850ac45ea97ad347e8b56dba5085af8c8aad9cc2ec626ca78a068006d658f68651da31a0a77c65a70ed73a40d53b08edd403c095aa0bcffa52f313ebcacaaa2ce5024a4e2b9aa70fc6092f38ae094d71e43f7690b5ddd3e9e4f7")
PATCH_REPLACE = bytes.fromhex("a107b71c8a08ba5350934f7cf6e81be3a24dc2e35f7200d80cbd70b37ed6811dd2146d3cb7e20ad19b2544c0ef14c5c66ffbbdf226ec3f3d544c04385303ca4a7179299340022f5d50948bcf8a60307e2c196329e51a5296dc419e40fef3ef7c6f015a09ebd979e79615338985643e666c14897f9f597e11f44341f496d56861")


def patch_ida_files(apply=False):
    """Patch all IDA files"""
    files_to_patch = [
        "ida32.dll",
        "ida.dll",
        "libida32.so",
        "libida.so",
        "libida32.dylib",
        "libida.dylib",
    ]

    success_count = 0
    for filename in files_to_patch:
        if generate_patched_dll(filename, apply):
            success_count += 1

    if apply:
        # if we're on macOS, try to run codesign
        if sys.platform == "darwin":
            parent_path = os.path.abspath(os.curdir)
            if not parent_path.endswith("Contents/MacOS"):
                print(
                    "Error: Unexpected path structure. In order to re-sign the bundle, this script should be run from xxx.app/Contents/MacOS/"
                )
                return success_count

            bundle_dir = os.path.abspath(os.path.join(parent_path, "../.."))

            try:
                result = os.system(f"xattr -c '{bundle_dir}'")
                if result != 0:
                    print(
                        "Error: Failed to clear extended attributes on the IDA bundle."
                    )
            except Exception as e:
                print(f"Error while trying to clear extended attributes: {e}")

            try:
                result = os.system(f"codesign --verbose -f -s - --deep '{bundle_dir}'")
                if result != 0:
                    print("Error: Failed to re-sign the IDA bundle.")
            except Exception as e:
                print(f"Error while trying to re-sign the IDA bundle: {e}")

    return success_count


def sign(payload):
    """Create signature"""
    data_str = sort({"payload": payload})
    hash_val = hashlib.sha256(data_str.encode()).digest()

    U = bytearray(V54)
    U[V56:V56+32] = hash_val  # Copy the hash to the location starting at V56 in U

    block = bytearray(V54)
    for i in range(V54):
        block[i] = U[i] ^ PADKEY[i]

    if block[0] == 0:
        block[0] ^= 1

    sig = encrypt(bytes(block))
    out = bytearray(128)
    out[:len(sig)] = sig
    return bytes(out).hex().upper()


# Alias for backward compatibility
def sign_hexlic(payload: dict) -> str:
    return sign(payload)


def generate_patched_dll(filename, apply=False):
    if not os.path.exists(filename):
        # print(f"Didn't find {filename}, skipping patch generation")
        return False

    with open(filename, "rb") as f:
        data = f.read()

        if data.find(PATCH_REPLACE) != -1:
            print(f"{filename} looks to be already patched :)")
            return True

        if data.find(PATCH_SEARCH) == -1:
            print(f"{filename} doesn't contain the original pattern.")
            return False

        data = data.replace(PATCH_SEARCH, PATCH_REPLACE)

        patched_filename = f"{filename}.patched"
        with open(patched_filename, "wb") as f:
            f.write(data)

        print(f"Generated patch: {patched_filename}")

    if apply:
        # Check if file is writable
        try:
            with open(filename, "r+b"):
                pass
        except Exception:
            print(f"Error: {filename} is not writable. Cannot swap files.")
            return False

        backup_filename = f"{filename}.bak"
        try:
            if not os.path.exists(backup_filename):
                shutil.copy2(filename, backup_filename)
                print(f"Created backup: {backup_filename}")
            else:
                print(
                    f"Backup already exists: {backup_filename}, skipping backup creation."
                )

            # Replace original with patched
            shutil.move(patched_filename, filename)
            print(f"Swapped {filename} with patched version")
            return True
        except Exception as e:
            print(f"Error swapping files: {e}")
            return False
    else:
        print(
            "To apply the patch, replace the original files with the patched files"
        )
        return True


class ArgumentParserWithHelp(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def main():
    parser = ArgumentParserWithHelp(
        description="IDA Pro 9.x keygen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --patch                   : Generate .patched files only
  %(prog)s --patch --apply           : Generate patches and apply them to current IDA installation
                                     : on macOS attempts to also re-sign the bundle
  %(prog)s --license                 : Generate license only
  %(prog)s --oneshot                 : Patch IDA then generate license - equivalent to running --patch --apply then --license
  %(prog)s --license --name "bnuuy"  : Custom name
  %(prog)s --oneshot --license-type floating --end-date 2030-12-31

How to use:
  1. Place this script in the directory where IDA is installed and all .dll/.so/.dylib files are located.
     On Windows it's C:\\Program Files\\IDA Professional 9.x\\
     On Linux it's ~/ida-pro-9.x/
     On macOS it's /Applications/IDA Professional 9.x.app/Contents/MacOS/
  2. You most likely just want to run the script with --oneshot option, which will do everything automatically.
  3. If you want run individual steps, see the options above.

Note: This version of the keygen uses a different modulus patch than the previous version.
      See the source code in case you want to use the old patch.
        """,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--patch", action="store_true", help="Generate patched DLL files"
    )
    mode_group.add_argument(
        "--license", action="store_true", help="Generate license file only"
    )
    mode_group.add_argument(
        "--oneshot", action="store_true", help="Patch IDA files and generate license"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply patches to original files (creates .bak backups)",
    )

    parser.add_argument(
        "--name",
        # idgaf what you do, but if you republish this script as your own without
        # any meaningful changes, you're just a skid
        default="ntkey",
        help="License holder name (default: %(default)s)",
    )
    parser.add_argument(
        "--license-type",
        choices=["named", "floating", "computer"],
        default="named",
        help="License type (default: %(default)s)",
    )
    parser.add_argument(
        "--start-date", help="License start date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--end-date",
        help="License end date (YYYY-MM-DD, default: 10 years from start date)",
    )

    args = parser.parse_args()

    args.apply = args.apply or args.oneshot

    # Validate date format if provided
    for date_arg in [args.start_date, args.end_date]:
        if date_arg:
            try:
                datetime.strptime(date_arg, "%Y-%m-%d")
            except ValueError:
                print(
                    f"Error: Invalid date format '{date_arg}'. Use YYYY-MM-DD format."
                )
                return 1

    # end date must not be before start date and must not be more than 10 years from start date
    if args.start_date and args.end_date:
        start_dt = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(args.end_date, "%Y-%m-%d")

        if end_dt < start_dt:
            print("Error: End date must not be before start date.")
            return 1

        if (end_dt - start_dt).days >= 3650:
            print("Error: End date must not be more than 10 years from start date.")
            return 1

    success = True

    if args.patch or args.oneshot:
        success_count = patch_ida_files(args.apply)
        success = success_count > 0

        if success_count == 0:
            print(
                "No files were patched. Ensure that you run this script from the IDA installation directory."
            )
            parser.print_help()
            return 1

    if args.license or args.oneshot:
        print("Generating license...")
        license_data = create_license(
            name=args.name,
            license_type=args.license_type,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        success = generate_license_file(license_data)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())