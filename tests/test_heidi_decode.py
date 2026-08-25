import unittest

import heidi_decode


class HeidiPasswordCodecTest(unittest.TestCase):
    def test_encode_decode_round_trip(self) -> None:
        self.assertEqual(
            heidi_decode.decode_password(heidi_decode.encode_password("p@ssword")), "p@ssword"
        )

    def test_empty_password_round_trip(self) -> None:
        self.assertEqual(heidi_decode.decode_password(heidi_decode.encode_password("")), "")


if __name__ == "__main__":
    unittest.main()
