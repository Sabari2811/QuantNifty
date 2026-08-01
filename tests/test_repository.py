from recording.snapshot_repository import SnapshotRepository

repo = SnapshotRepository()

sessions = repo.list_recordings()

print()

print("=" * 60)

print("Replay Sessions")

print("=" * 60)

for s in sessions:

    print(

        s.display_name,

        "|",

        "Complete" if s.complete else "Legacy"

    )