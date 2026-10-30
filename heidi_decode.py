import argparse
import re
import sys
from pathlib import Path


def decode_password(encoded_password=""):
    if encoded_password == "":
        return ""
    if not re.fullmatch(r"(?:[0-9a-fA-F]{2})*[0-9]", encoded_password):
        raise ValueError("Invalid encoded password format")
    decoded_password = ""
    shift = int(encoded_password[-1])
    encoded_password = encoded_password[:-1]
    for i in range(0, len(encoded_password), 2):
        value = int(encoded_password[i : i + 2], 16) - shift
        if value < 0:
            raise ValueError("Invalid encoded password format")
        decoded_password += chr(value)
    return decoded_password


def encode_password(s):
    shift = len(s) % 10
    hex_str = ""
    for c in s:
        hex_str += format(ord(c) + shift, "02x")
    hex_str += str(shift)
    return hex_str


def read_connection_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        settings = f.read()

    connections = []
    current_connection = {}

    for line in settings.split("\n"):
        if line.startswith("Servers\\"):
            subkeys = line.split("\\")
            conn_name = subkeys[1]
            line_details = subkeys[2].split("<|||>")

            try:
                key = line_details[0]
                value = line_details[2]
            except IndexError:
                continue

            if not current_connection or current_connection["name"] != conn_name:
                if current_connection:
                    connections.append(current_connection)
                current_connection = {"name": conn_name}
            current_connection[key.strip()] = value.strip()

    if current_connection:
        connections.append(current_connection)
    return connections


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Parse a HeidiSQL settings export and print connection settings."
    )
    parser.add_argument(
        "--show-passwords",
        action="store_true",
        help="Reveal encoded and decoded passwords in stdout; keep output private",
    )
    parser.add_argument(
        "export_file",
        nargs="?",
        default="export_heidi.txt",
        help="HeidiSQL export file (default: export_heidi.txt)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    export_path = Path(args.export_file)
    if not export_path.is_file():
        raise SystemExit(f"Input file not found: {export_path}")

    connections = read_connection_data(export_path)

    # Validate all requested decodes before emitting any connection or secret.
    decoded = []
    if args.show_passwords:
        print(
            "Warning: encoded and decoded passwords will be written to stdout. "
            "Do not share or log this output.",
            file=sys.stderr,
        )
        try:
            decoded = [decode_password(conn.get("Password", "")) for conn in connections]
        except ValueError:
            raise SystemExit("Cannot reveal passwords: invalid encoded password format") from None

    for index, conn in enumerate(connections):
        print(f"Connection name: {conn.get('name', '')}")
        print(f"Host: {conn.get('Host', '')}")
        print(f"Port: {conn.get('Port', '')}")
        print(f"User: {conn.get('User', '')}")
        print(
            f"Password (encoded): {conn.get('Password', '') if args.show_passwords else '[hidden]'}"
        )
        print(f"Password (decoded): {decoded[index] if args.show_passwords else '[hidden]'}")
        print(f"Library: {conn.get('Library', '')}")
        print(f"ServerVersion: {conn.get('ServerVersion', '')}")
        print(f"ServerVersionFull: {conn.get('ServerVersionFull', '')}")
        print()


if __name__ == "__main__":
    main()
