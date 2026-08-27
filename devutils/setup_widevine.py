#!/usr/bin/env python3

# Copyright 2026 The Zenium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Install Google Chrome's local Widevine CDM into a Zenium profile."""

import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

CHROME_WIDEVINE_DIRS = (
    Path('/opt/google/chrome/WidevineCdm'),
    Path('/opt/google/chrome-beta/WidevineCdm'),
    Path('/opt/google/chrome-unstable/WidevineCdm'),
)

PLATFORM_DIRECTORIES = {
    'aarch64': 'linux_arm64',
    'amd64': 'linux_x64',
    'arm64': 'linux_arm64',
    'x86_64': 'linux_x64',
}

ZENIUM_IMPORT_MARKER = 'zenium-imported-from-chrome'


def default_user_data_dir():
    """Returns Zenium's default Linux user data directory."""
    configured = os.environ.get('ZENIUM_USER_DATA_DIR')
    if configured:
        return Path(configured).expanduser()

    config_home = os.environ.get('CHROME_CONFIG_HOME') or os.environ.get('XDG_CONFIG_HOME')
    if config_home:
        return Path(config_home).expanduser() / 'net.zenium'
    return Path.home() / '.config' / 'net.zenium'


def find_chrome_widevine():
    """Finds Widevine in a standard Google Chrome installation."""
    configured = os.environ.get('CHROME_WIDEVINE_DIR')
    candidates = ((Path(configured).expanduser(), ) if configured else CHROME_WIDEVINE_DIRS)
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    raise FileNotFoundError('Google Chrome Widevine was not found. Pass --source or set '
                            'CHROME_WIDEVINE_DIR.')


def read_manifest(source_dir):
    """Reads and validates the fields needed to register Widevine."""
    manifest_path = source_dir / 'manifest.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise ValueError(f'Missing Widevine manifest: {manifest_path}') from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f'Invalid Widevine manifest: {manifest_path}') from exc

    required_fields = (
        'version',
        'x-cdm-module-versions',
        'x-cdm-interface-versions',
        'x-cdm-host-versions',
    )
    missing_fields = [field for field in required_fields if not manifest.get(field)]
    if missing_fields:
        raise ValueError('Widevine manifest is missing: ' + ', '.join(missing_fields))

    version_parts = str(manifest['version']).split('.')
    if not version_parts or not all(part.isdigit() for part in version_parts):
        raise ValueError(f"Invalid Widevine version: {manifest['version']}")
    return manifest


def platform_directory(machine=None):
    """Returns Chrome's platform-specific Widevine directory name."""
    machine = (machine or platform.machine()).lower()
    try:
        return PLATFORM_DIRECTORIES[machine]
    except KeyError as exc:
        raise ValueError(f'Unsupported Linux architecture: {machine}') from exc


def atomic_copy(source, destination):
    """Copies one file without exposing a partially written destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{destination.name}.',
                                                       dir=destination.parent)
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)
    try:
        shutil.copy2(source, temporary_path)
        os.chmod(temporary_path, 0o644)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def atomic_write_json(destination, value):
    """Writes compact JSON without exposing a partially written hint file."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{destination.name}.',
                                                       dir=destination.parent,
                                                       text=True)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as output:
            json.dump(value, output, separators=(',', ':'))
            output.write('\n')
        os.chmod(temporary_path, 0o644)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def atomic_write_text(destination, value):
    """Writes text without exposing a partially written destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{destination.name}.',
                                                       dir=destination.parent,
                                                       text=True)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as output:
            output.write(value)
        os.chmod(temporary_path, 0o644)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def install_widevine(source_dir, user_data_dir, machine=None):
    """Copies Chrome's Widevine files and returns the installed CDM path."""
    source_dir = source_dir.expanduser().resolve()
    user_data_dir = user_data_dir.expanduser().resolve()
    manifest = read_manifest(source_dir)
    platform_name = platform_directory(machine)
    library_relative_path = Path('_platform_specific') / platform_name / 'libwidevinecdm.so'
    library_path = source_dir / library_relative_path
    if not library_path.is_file():
        raise ValueError(f'Missing Widevine library: {library_path}')

    widevine_dir = user_data_dir / 'WidevineCdm'
    install_dir = widevine_dir / str(manifest['version'])
    atomic_copy(source_dir / 'manifest.json', install_dir / 'manifest.json')
    atomic_copy(library_path, install_dir / library_relative_path)

    license_path = source_dir / 'LICENSE'
    if license_path.is_file():
        atomic_copy(license_path, install_dir / 'LICENSE')

    atomic_write_text(install_dir / ZENIUM_IMPORT_MARKER, 'Imported by Zenium\n')

    hint_path = widevine_dir / 'latest-component-updated-widevine-cdm'
    atomic_write_json(hint_path, {'Path': str(install_dir)})
    return install_dir


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Copy Google Chrome's Widevine CDM into a Zenium profile.")
    parser.add_argument('--source',
                        type=Path,
                        help='Chrome WidevineCdm directory (detected automatically by default)')
    parser.add_argument('--user-data-dir',
                        type=Path,
                        default=default_user_data_dir(),
                        help='Zenium user data directory (default: %(default)s)')
    return parser.parse_args()


def main():
    """Installs Widevine and reports the required restart."""
    args = parse_args()
    try:
        source_dir = args.source or find_chrome_widevine()
        install_dir = install_widevine(source_dir, args.user_data_dir)
    except (OSError, ValueError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1

    print(f'Installed Widevine from {source_dir} to {install_dir}')
    print('Fully restart Zenium to enable protected media playback.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
