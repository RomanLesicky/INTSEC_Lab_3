"""Local check for the INTSEC Python lab. Run: python3 test_student.py

Part 1 tests your three functions on small separate examples.
Part 2 runs your functions on the real case and checks that they work there.
The test checks your code only. It does not tell you the conclusion of the
investigation, and it stores scrambled values rather than the results.
"""

import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

import student

EXPECTED = {
    "compare": "a4779f9a874f1b5c921c38545e6feeb2a4a4af672609e3278a021f9b4b0aa2ed",
    "status_counts": "4f414d6201c618eb7ceb692c7f43ceb8226cdeec8838839e99bca7c52012b762",
    "successful_events_for": "d7625e7d3244841f5b52dc0a8a44c54e503ed8eb16949bb2b4192254c101b1fb",
}


class StudentFunctionTests(unittest.TestCase):
    def completed(self, function_name, *args):
        try:
            return getattr(student, function_name)(*args)
        except NotImplementedError:
            self.fail(f"{function_name}() is not completed yet.")

    def test_compare_classifies_all_statuses_in_sorted_order(self):
        before = {"alpha.txt": "one", "bravo.txt": "old", "charlie.txt": "gone"}
        after = {"alpha.txt": "one", "bravo.txt": "new", "delta.txt": "added"}
        expected = [
            {"file": "alpha.txt", "status": "unchanged"},
            {"file": "bravo.txt", "status": "modified"},
            {"file": "charlie.txt", "status": "deleted"},
            {"file": "delta.txt", "status": "added"},
        ]
        self.assertEqual(
            self.completed("compare", before, after),
            expected,
            "compare() must include every filename, classify it correctly, and sort by filename.",
        )

    def test_compare_handles_empty_snapshots(self):
        self.assertEqual(self.completed("compare", {}, {}), [])

    def test_status_counts_includes_all_four_keys(self):
        rows = [
            {"file": "a", "status": "added"},
            {"file": "b", "status": "modified"},
            {"file": "c", "status": "modified"},
        ]
        expected = {"added": 1, "deleted": 0, "modified": 2, "unchanged": 0}
        self.assertEqual(
            self.completed("status_counts", rows),
            expected,
            "status_counts() must return all four status keys, including zero values.",
        )

    def test_successful_events_for_keeps_only_matching_successes(self):
        events = [
            {"event_id": "T01", "path": "report.txt", "result": "SUCCESS"},
            {"event_id": "T02", "path": "report.txt", "result": "DENIED"},
            {"event_id": "T03", "path": "other.txt", "result": "SUCCESS"},
            {"event_id": "T04", "path": "report.txt", "result": "SUCCESS"},
            {"event_id": "T05", "path": "report.txt.old", "result": "SUCCESS"},
        ]
        expected = [events[0], events[3]]
        self.assertEqual(
            self.completed("successful_events_for", events, "report.txt"),
            expected,
            "successful_events_for() must keep exact filename matches with SUCCESS, in their existing order.",
        )


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def check_case():
    case = Path(__file__).parent / "case"
    before = student.folder_hashes(case / "before")
    after = student.folder_hashes(case / "after")
    results = student.compare(before, after)
    events = student.load_events(case / "access.csv")
    filtered = {
        row["file"]: [
            event["event_id"]
            for event in student.successful_events_for(events, row["file"])
        ]
        for row in results
    }
    checks = {
        "compare": results,
        "status_counts": student.status_counts(results),
        "successful_events_for": filtered,
    }
    passed = True
    for name, value in checks.items():
        if fingerprint(value) == EXPECTED[name]:
            print(f"  PASS     {name}()")
        else:
            print(f"  NOT YET  {name}() gives a wrong result on the case")
            passed = False
    return passed


def main():
    print("PART 1: your functions on small examples")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(StudentFunctionTests)
    )
    if not result.wasSuccessful():
        print(stream.getvalue())
        print("NOT YET: correct the function named above, then run this test again.")
        return 1
    print("  PASS")

    print("\nPART 2: your functions on the real case")
    try:
        passed = check_case()
    except Exception as error:
        print(f"  NOT YET  your code stopped on the case: {error}")
        passed = False
    if not passed:
        print("\nNOT YET: correct your code. Also check that the case folder is unchanged.")
        return 1

    print("\nPASS: your code works on the small examples and on the real case.")
    print("Now run python3 student.py and investigate. The test does not check")
    print("your conclusions, so those are marked from the PDF you submit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
