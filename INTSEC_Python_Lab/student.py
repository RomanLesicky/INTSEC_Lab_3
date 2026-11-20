from pathlib import Path
import csv
import hashlib
import sys


def file_hash(path):
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def folder_hashes(folder):
    if not folder.is_dir():
        raise ValueError(f"Missing folder: {folder}")
    hashes = {}
    for path in sorted(folder.iterdir()):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Expected an ordinary file: {path}")
        hashes[path.name] = file_hash(path)
    return hashes


def compare(before, after):
    """Return one result dictionary for every filename in either snapshot."""
    raise NotImplementedError("Complete compare()")


def status_counts(results):
    """Return counts for added, deleted, modified and unchanged files."""
    raise NotImplementedError("Complete status_counts()")


def load_events(path):
    columns = ["event_id", "timestamp", "account", "action", "path", "result"]
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError("Unexpected access.csv header")
        events = []
        for line, row in enumerate(reader, start=2):
            if None in row or any(not row[key] for key in columns):
                raise ValueError(f"Malformed log row {line}")
            events.append(row)
    return events


def successful_events_for(events, filename):
    """Return successful events for filename, in their original order."""
    raise NotImplementedError("Complete successful_events_for()")


def main():
    if len(sys.argv) not in (1, 2):
        raise SystemExit("Usage: python3 student.py [FILE]")

    case = Path(__file__).parent / "case"

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        events = load_events(case / "access.csv")
        print(f"ACCESS EVENTS FOR {filename}")
        for event in successful_events_for(events, filename):
            print(" | ".join(event.values()))
        return

    before = folder_hashes(case / "before")
    after = folder_hashes(case / "after")
    results = compare(before, after)
    counts = status_counts(results)

    print("SUMMARY")
    for status in ("added", "deleted", "modified", "unchanged"):
        print(f"{status}: {counts[status]}")

    print("\nCHANGED FILES")
    for row in results:
        if row["status"] != "unchanged":
            print(f"{row['file']}: {row['status']}")


if __name__ == "__main__":
    main()
