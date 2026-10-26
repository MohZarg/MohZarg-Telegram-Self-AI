"""Safe SQLite backup and restore helpers with integrity checks and atomic replacement."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sqlite3
import tempfile


def _check_integrity(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    with sqlite3.connect(str(path)) as db:
        result = db.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise ValueError(f"SQLite integrity check failed for: {path}")


def _copy_database(source: str | Path, destination: str | Path, *, overwrite: bool) -> Path:
    src = Path(source).expanduser().resolve()
    dst = Path(destination).expanduser().resolve()
    if src == dst:
        raise ValueError("Source and destination must be different paths")
    if not src.is_file():
        raise FileNotFoundError(f"SQLite database not found: {src}")
    if dst.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dst}; pass --overwrite to replace it")
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{dst.name}.", suffix=".tmp", dir=str(dst.parent))
    os.close(fd)
    temporary = Path(temp_name)
    try:
        with sqlite3.connect(str(src)) as source_db, sqlite3.connect(str(temporary)) as target_db:
            source_db.backup(target_db)
            result = target_db.execute("PRAGMA integrity_check").fetchone()
            if not result or result[0] != "ok":
                raise ValueError("SQLite integrity check failed after copy")
        os.chmod(temporary, 0o600)
        os.replace(temporary, dst)
        return dst
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def backup_database(source: str | Path, destination: str | Path) -> Path:
    """Create a consistent online SQLite backup; refuse to overwrite an existing backup."""
    return _copy_database(source, destination, overwrite=False)


def restore_database(backup: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
    """Restore a verified backup atomically; stop app/worker before replacing a live database."""
    _check_integrity(Path(backup).expanduser().resolve())
    return _copy_database(backup, destination, overwrite=overwrite)


def main() -> int:
    parser = argparse.ArgumentParser(description="Back up or restore a SQLite scheduler database")
    subparsers = parser.add_subparsers(dest="command", required=True)
    backup_parser = subparsers.add_parser("backup", help="create a consistent database backup")
    backup_parser.add_argument("source")
    backup_parser.add_argument("destination")
    restore_parser = subparsers.add_parser("restore", help="restore a verified backup")
    restore_parser.add_argument("source")
    restore_parser.add_argument("destination")
    restore_parser.add_argument("--overwrite", action="store_true", help="replace an existing destination")
    args = parser.parse_args()
    if args.command == "backup":
        result = backup_database(args.source, args.destination)
    else:
        result = restore_database(args.source, args.destination, overwrite=args.overwrite)
    print(f"SQLite {args.command} completed: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
