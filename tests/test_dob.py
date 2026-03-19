import redact
from test_utils import PrettyTestCase


class TestBirthdateRegex(PrettyTestCase):
    def setUp(self):
        self.group = redact.PATTERNS["dobs"]

    def assert_match(self, text):
        self.assertTrue(self.group.contains(text), msg=f"Expected match for: {text}")
        self.assertGreater(len(self.group.find(text)), 0, msg=f"Expected DOBs for: {text}")

    def assert_no_match(self, text):
        self.assertFalse(self.group.contains(text), msg=f"Expected NO match for: {text}")
        self.assertEqual(self.group.find(text), [], msg=f"Expected NO DOBs for: {text}")

    def test_labeled_birthdates(self):
        self.assert_match("DOB: 01/02/1980")
        self.assert_match("dob 1/2/80")
        self.assert_match("Date of Birth - Jan 1, 1980")
        self.assert_match("D.O.B. 1980-01-02")
        self.assert_match("Birth date: 1 Jan 1980")
        self.assert_match("Birthdate 01-02-1980")
        self.assert_match("Birthday - January 1st, 1980")
        result = redact.find_all("DOB: 01/02/1980")
        self.assertGreater(len(result["dobs"]), 0)
        self.assertEqual(result["ssns"], [])

    def test_born_phrases(self):
        self.assert_match("He was born on January 1, 1980 in Texas.")
        self.assert_match("She was born 02-03-79.")
        self.assert_match("Born on 1 Jan 1980.")
        self.assert_match("Born 1st Jan 1980.")

    def test_non_birth_dates_do_not_match(self):
        self.assert_no_match("Incident date: 01/02/1980")
        self.assert_no_match("Report created on Jan 1, 1980")
        self.assert_no_match("Appointment date 1 Jan 1980")

    def test_redact_dobs_preserves_label(self):
        self.assertEqual(
            self.group.redact("DOB: 01/02/1980"),
            "DOB: ***",
        )
        self.assertEqual(
            self.group.redact("Born on 1 Jan 1980."),
            "Born on ***.",
        )
        self.assertEqual(
            self.group.redact("Incident date: 01/02/1980"),
            "Incident date: 01/02/1980",
        )
        self.assertEqual(
            self.group.redact("DOB: Jan 1 1980", mask_mode="length"),
            "DOB: **********",
        )
        self.assertEqual(
            self.group.redact("Born on Jan 1 1980.", mask_mode="length", mask_char="#"),
            "Born on ##########.",
        )

    def test_aggressive_dob_mode(self):
        self.assertTrue(self.group.contains("01/02/1980", mode="aggressive"))
        self.assertEqual(
            self.group.find("01/02/1980", mode="aggressive"),
            ["01/02/1980"],
        )
        self.assertEqual(
            self.group.redact("01/02/1980", mode="aggressive"),
            "***",
        )

    def test_strict_dob_mode_requires_labels(self):
        self.assertFalse(self.group.contains("01/02/1980", mode="strict"))
        self.assertEqual(self.group.find("01/02/1980", mode="strict"), [])
        self.assertEqual(
            self.group.redact("01/02/1980", mode="strict"),
            "01/02/1980",
        )
