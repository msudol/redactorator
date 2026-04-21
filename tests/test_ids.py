import redactorator as redact
from test_utils import PrettyTestCase


class TestIdsRegex(PrettyTestCase):
    def setUp(self):
        self.group = redact.PATTERNS["ids"]

    def assert_match(self, text):
        self.assertTrue(self.group.contains(text), msg=f"Expected ID match for: {text}")
        self.assertGreater(len(self.group.find(text)), 0, msg=f"Expected IDs for: {text}")

    def assert_no_match(self, text):
        self.assertFalse(self.group.contains(text), msg=f"Expected NO ID match for: {text}")
        self.assertEqual(self.group.find(text), [], msg=f"Expected NO IDs for: {text}")

    # Verify labeled ID-like values are detected (ID, Passport, Member ID)
    def test_labeled_id_variants(self):
        self.assert_match("ID: ABC-12345")
        self.assert_match("Member ID: 123456789")
        self.assert_match("Passport: A1234567")
        self.assert_match("Driver's License: DL 987-654-321")
        result = redact.find_all("ID: ABC-12345")
        self.assertGreater(len(result["ids"]), 0)
        self.assertEqual(result["phones"], [])
        self.assertEqual(result["ssns"], [])

    # Ensure short/unrelated tokens do not produce false ID matches
    def test_non_id_text_does_not_match(self):
        self.assert_no_match("Ticket # 123-45-6789")
        self.assert_no_match("Order: 1234")
        self.assert_no_match("ID-like but no code")

    # Aggressive mode should match unlabeled long alphanumeric or numeric tokens
    def test_aggressive_id_mode(self):
        # Long alphanumeric token should match in aggressive mode
        self.assertTrue(self.group.contains("ABC12345678", mode="aggressive"))
        self.assertEqual(self.group.find("ABC12345678", mode="aggressive"), ["ABC12345678"])
        self.assertEqual(self.group.redact("ABC12345678", mode="aggressive"), "***")

        # Long numeric token
        self.assertTrue(self.group.contains("1234567", mode="aggressive"))
        self.assertEqual(self.group.find("1234567", mode="aggressive"), ["1234567"])

    # Strict mode must not match unlabeled tokens
    def test_strict_id_mode_requires_labels(self):
        self.assertFalse(self.group.contains("ABC12345678", mode="strict"))
        self.assertEqual(self.group.find("ABC12345678", mode="strict"), [])
        self.assertEqual(self.group.redact("ABC12345678", mode="strict"), "ABC12345678")

    # Redaction should keep the label and mask only the identifier value
    def test_redact_ids_preserves_label(self):
        self.assertEqual(self.group.redact("ID: ABC-12345"), "ID: ***")
        self.assertEqual(self.group.redact("Passport: A1234567", mask_mode="length"), "Passport: ********")
