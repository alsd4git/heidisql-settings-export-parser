import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import heidi_decode


class HeidiPasswordCodecTest(unittest.TestCase):
    def run_export(self, password, *options):
        with TemporaryDirectory() as directory:
            export = Path(directory) / "synthetic.txt"
            export.write_text(
                "Servers\\demo\\Host<|||>1<|||>demo.invalid\n"
                f"Servers\\demo\\Password<|||>1<|||>{password}\n",
                encoding="utf-8",
            )
            out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                heidi_decode.main([str(export), *options])
            return out.getvalue(), err.getvalue()

    def test_passwords_hidden_by_default(self):
        secret = "synthetic-secret"
        encoded = heidi_decode.encode_password(secret)
        out, err = self.run_export(encoded)
        self.assertNotIn(secret, out + err)
        self.assertNotIn(encoded, out + err)
        self.assertIn("Host: demo.invalid", out)
        self.assertIn("Password (encoded): [hidden]", out)
        self.assertIn("Password (decoded): [hidden]", out)
        self.assertEqual(err, "")

    def test_explicit_reveal_warns_without_logging_passwords(self):
        secret = "synthetic-secret"
        encoded = heidi_decode.encode_password(secret)
        out, err = self.run_export(encoded, "--show-passwords")
        self.assertIn(f"Password (encoded): {encoded}", out)
        self.assertIn(f"Password (decoded): {secret}", out)
        self.assertIn("Warning:", err)
        self.assertNotIn(secret, err)
        self.assertNotIn(encoded, err)

    def test_invalid_password_not_decoded_by_default(self):
        out, err = self.run_export("invalid-private-value")
        self.assertNotIn("invalid-private-value", out + err)

    def test_invalid_reveal_does_not_echo_input(self):
        with TemporaryDirectory() as directory:
            export = Path(directory) / "synthetic.txt"
            export.write_text(
                "Servers\\first\\Password<|||>1<|||>"
                + heidi_decode.encode_password("synthetic-secret")
                + "\nServers\\second\\Password<|||>1<|||>invalid-private-value\n",
                encoding="utf-8",
            )
            out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                with self.assertRaises(SystemExit) as raised:
                    heidi_decode.main([str(export), "--show-passwords"])
        self.assertEqual(out.getvalue(), "")
        for secret in ("invalid-private-value", "synthetic-secret"):
            self.assertNotIn(secret, str(raised.exception) + err.getvalue())
        self.assertIn("invalid encoded password", str(raised.exception))

    def test_invalid_encodings_have_sanitized_errors(self):
        for value in ("odd00", "aaX", "abc1", "001", "secret9"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "^Invalid encoded password format$"):
                    heidi_decode.decode_password(value)

    def test_default_export_filename(self) -> None:
        self.assertEqual(heidi_decode.parse_args([]).export_file, "export_heidi.txt")

    def test_explicit_export_filename(self) -> None:
        self.assertEqual(heidi_decode.parse_args(["custom.txt"]).export_file, "custom.txt")

    def test_missing_export_has_actionable_error(self) -> None:
        with self.assertRaisesRegex(SystemExit, "Input file not found"):
            heidi_decode.main(["tests/does-not-exist.txt"])

    def test_encode_decode_round_trip(self) -> None:
        self.assertEqual(
            heidi_decode.decode_password(heidi_decode.encode_password("p@ssword")), "p@ssword"
        )

    def test_empty_password_round_trip(self) -> None:
        self.assertEqual(heidi_decode.decode_password(heidi_decode.encode_password("")), "")


if __name__ == "__main__":
    unittest.main()
