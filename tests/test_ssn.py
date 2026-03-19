import redact
from test_utils import PrettyTestCase


class TestSsnRegex(PrettyTestCase):
    def setUp(self):
        self.group = redact.PATTERNS["ssns"]

    def assert_match(self, text):
        self.assertTrue(self.group.contains(text), msg=f"Expected SSN match for: {text}")
        self.assertGreater(len(self.group.find(text)), 0, msg=f"Expected SSNs for: {text}")

    def assert_no_match(self, text):
        self.assertFalse(self.group.contains(text), msg=f"Expected NO SSN match for: {text}")
        self.assertEqual(self.group.find(text), [], msg=f"Expected NO SSNs for: {text}")

    def test_labeled_ssn_variants(self):
        self.assert_match("SSN: 123-45-6789")
        self.assert_match("SSN 123456789")
        self.assert_match("SS # 123 45 6789")
        self.assert_match("Social Security Number: 123-45-6789")
        self.assert_match("Social Security # 123456789")
        result = redact.find_all("SSN: 123-45-6789")
        self.assertGreater(len(result["ssns"]), 0)
        self.assertEqual(result["dobs"], [])

    def test_non_ssn_text_does_not_match(self):
        self.assert_no_match("Ticket # 123-45-6789")
        self.assert_no_match("Phone: 123-456-7890")
        self.assert_no_match("SSN-ish 123-45-6789")
        self.assert_no_match("123-45-6789")

    def test_aggressive_ssn_mode(self):
        self.assertTrue(self.group.contains("123-45-6789", mode="aggressive"))
        self.assertEqual(
            self.group.find("123-45-6789", mode="aggressive"),
            ["123-45-6789"],
        )
        self.assertEqual(
            self.group.find("SSN: 123-45-6789", mode="aggressive"),
            ["SSN: 123-45-6789"],
        )
        self.assertEqual(
            self.group.redact("123-45-6789", mode="aggressive"),
            "***",
        )
        self.assertEqual(
            self.group.redact(
                "123-45-6789",
                mode="aggressive",
                mask_mode="length",
            ),
            "***********",
        )

    def test_strict_ssn_mode_requires_labels(self):
        self.assertFalse(self.group.contains("123-45-6789", mode="strict"))
        self.assertEqual(self.group.find("123-45-6789", mode="strict"), [])
        self.assertEqual(
            self.group.redact("123-45-6789", mode="strict"),
            "123-45-6789",
        )

    def test_redact_ssns_preserves_label(self):
        self.assertEqual(
            self.group.redact("SSN: 123-45-6789"),
            "SSN: ***",
        )
        self.assertEqual(
            self.group.redact("SS # 123 45 6789"),
            "SS # ***",
        )
        self.assertEqual(
            self.group.redact("Ticket # 123-45-6789"),
            "Ticket # 123-45-6789",
        )
        self.assertEqual(
            self.group.redact("SSN: 123-45-6789", mask_mode="length"),
            "SSN: ***********",
        )
        self.assertEqual(
            self.group.redact("SSN: 123-45-6789", mask_mode="length", mask_char="#"),
            "SSN: ###########",
        )

    def test_redact_all(self):
        self.assertEqual(
            redact.redact_all("DOB: 01/02/1980 and SSN: 123-45-6789"),
            "DOB: *** and SSN: ***",
        )
        self.assertEqual(
            redact.redact_all(
                "DOB: Jan 1 1980 and SSN: 123-45-6789",
                mask_mode="length",
            ),
            "DOB: ********** and SSN: ***********",
        )
