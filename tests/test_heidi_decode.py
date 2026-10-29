import unittest

import heidi_decode


class HeidiPasswordCodecTest(unittest.TestCase):
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
