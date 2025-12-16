#!/usr/bin/env python3
"""
Bump version in pyproject.toml and src/demix/__init__.py
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def validate_version(version: str) -> bool:
    """Validate semantic version format (e.g., 1.0.0, 2.1.3)."""
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def update_pyproject_toml(version: str, dry_run: bool = False) -> bool:
    """Update version in pyproject.toml."""
    filepath = Path('pyproject.toml')
    if not filepath.exists():
        print(f"Error: {filepath} not found")
        return False

    content = filepath.read_text()
    pattern = r'^version = "[^"]+"$'
    replacement = f'version = "{version}"'

    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        print(f"Error: Could not find version line in {filepath}")
        return False

    if dry_run:
        print(f"Would update {filepath}")
    else:
        filepath.write_text(new_content)
        print(f"Updated {filepath}")

    return True


def update_init_py(version: str, dry_run: bool = False) -> bool:
    """Update version in src/demix/__init__.py."""
    filepath = Path('src/demix/__init__.py')
    if not filepath.exists():
        print(f"Error: {filepath} not found")
        return False

    content = filepath.read_text()
    pattern = r'^__version__ = "[^"]+"$'
    replacement = f'__version__ = "{version}"'

    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        print(f"Error: Could not find __version__ line in {filepath}")
        return False

    if dry_run:
        print(f"Would update {filepath}")
    else:
        filepath.write_text(new_content)
        print(f"Updated {filepath}")

    return True


def get_current_version() -> Optional[str]:
    """Get current version from pyproject.toml."""
    filepath = Path('pyproject.toml')
    if not filepath.exists():
        return None

    content = filepath.read_text()
    match = re.search(r'^version = "([^"]+)"$', content, flags=re.MULTILINE)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(
        description='Bump version in pyproject.toml and src/demix/__init__.py'
    )
    parser.add_argument(
        'version',
        help='New version number (e.g., 1.0.4)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )

    args = parser.parse_args()

    if not validate_version(args.version):
        print(f"Error: Invalid version format '{args.version}'. Use semantic versioning (e.g., 1.0.4)")
        sys.exit(1)

    current = get_current_version()
    if current:
        print(f"Current version: {current}")
    print(f"New version: {args.version}")

    if args.dry_run:
        print("\n[Dry run mode - no changes will be made]\n")

    success = True
    success = update_pyproject_toml(args.version, args.dry_run) and success
    success = update_init_py(args.version, args.dry_run) and success

    if success:
        print(f"\nVersion bumped to {args.version}")
    else:
        print("\nVersion bump failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
