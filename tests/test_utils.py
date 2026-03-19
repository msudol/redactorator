import os
import sys
import unittest

_PRETTY_HEADER_PRINTED = False


class PrettyTestCase(unittest.TestCase):
    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
        self._patch_result(result)
        return super().run(result)

    def _patch_result(self, result):
        if getattr(result, "_pretty_patched", False):
            return

        result._pretty_patched = True
        stream = getattr(result, "stream", sys.stdout)

        def write(line):
            stream.write(line + "\n")
            stream.flush()

        def maybe_header():
            global _PRETTY_HEADER_PRINTED
            if not _PRETTY_HEADER_PRINTED:
                write("\n" + "=" * 72)
                write("🧪 Running redact.py regex tests")
                write("=" * 72)
                _PRETTY_HEADER_PRINTED = True

        original_start = result.startTest
        original_success = result.addSuccess
        original_failure = result.addFailure
        original_error = result.addError
        original_skip = result.addSkip

        def startTest(test):
            maybe_header()
            write(f"\n⏳ {test.id()}")
            original_start(test)

        def addSuccess(test):
            write("✅ Passed")
            original_success(test)

        def addFailure(test, err):
            write("❌ Failed")
            original_failure(test, err)

        def addError(test, err):
            write("💥 Error")
            original_error(test, err)

        def addSkip(test, reason):
            write(f"⏭️  Skipped: {reason}")
            original_skip(test, reason)

        result.startTest = startTest
        result.addSuccess = addSuccess
        result.addFailure = addFailure
        result.addError = addError
        result.addSkip = addSkip


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
