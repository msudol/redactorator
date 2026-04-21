import redactorator as redact
from test_utils import PrettyTestCase


class TestPhoneRegex(PrettyTestCase):
    def setUp(self):
        self.group = redact.PATTERNS["phones"]

    def assert_match(self, text):
        self.assertTrue(self.group.contains(text), msg=f"Expected phone match for: {text}")
        self.assertGreater(len(self.group.find(text)), 0, msg=f"Expected phones for: {text}")

    def assert_no_match(self, text):
        self.assertFalse(self.group.contains(text), msg=f"Expected NO phone match for: {text}")
        self.assertEqual(self.group.find(text), [], msg=f"Expected NO phones for: {text}")

    # Verify common labeled phone formats are detected (various separators)
    def test_labeled_phone_variants(self):
        self.assert_match("Phone: 123-456-7890")
        self.assert_match("Phone # (123) 456-7890")
        self.assert_match("Telephone: 123.456.7890")
        self.assert_match("Tel: 123 456 7890")
        self.assert_match("Mobile 1234567890")
        result = redact.find_all("Phone: 123-456-7890")
        self.assertGreater(len(result["phones"]), 0)
        self.assertEqual(result["dobs"], [])
        self.assertEqual(result["ssns"], [])

    # Ensure numbers in non-phone contexts are not matched as phones
    def test_non_phone_text_does_not_match(self):
        self.assert_no_match("Ticket # 123-456-7890")
        self.assert_no_match("SSN: 123-45-6789")

    # Redaction should keep the label and mask the phone value
    def test_redact_phones_preserves_label(self):
        self.assertEqual(
            self.group.redact("Phone: 123-456-7890"),
            "Phone: ***",
        )
        self.assertEqual(
            self.group.redact("Tel: (123) 456-7890", mask_mode="length"),
            "Tel: **************",
        )

    # Aggressive mode should match unlabeled phone numbers
    def test_aggressive_phone_mode(self):
        self.assertTrue(self.group.contains("123-456-7890", mode="aggressive"))
        self.assertEqual(
            self.group.find("123-456-7890", mode="aggressive"),
            ["123-456-7890"],
        )
        self.assertEqual(
            self.group.redact("123-456-7890", mode="aggressive"),
            "***",
        )

    # Strict mode should only match labeled phone numbers
    def test_strict_phone_mode_requires_labels(self):
        self.assertFalse(self.group.contains("123-456-7890", mode="strict"))
        self.assertEqual(self.group.find("123-456-7890", mode="strict"), [])
        self.assertEqual(
            self.group.redact("123-456-7890", mode="strict"),
            "123-456-7890",
        )
