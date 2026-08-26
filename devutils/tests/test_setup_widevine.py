# Copyright 2026 The Zenium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Tests for setup_widevine."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import setup_widevine # pylint: disable=import-error

sys.path.pop(0)


def make_source(tmp_path, manifest=None):
    """Creates a minimal Chrome Widevine directory for a test."""
    source_dir = tmp_path / 'chrome' / 'WidevineCdm'
    library_path = source_dir / '_platform_specific' / 'linux_x64' / 'libwidevinecdm.so'
    library_path.parent.mkdir(parents=True)
    library_path.write_bytes(b'test-widevine-library')
    (source_dir / 'LICENSE').write_text('test license', encoding='utf-8')
    if manifest is None:
        manifest = {
            'version': '4.10.3050.0',
            'x-cdm-module-versions': '4',
            'x-cdm-interface-versions': '10',
            'x-cdm-host-versions': '10',
        }
    (source_dir / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return source_dir


def test_default_user_data_dir_follows_chromium_config_home(tmp_path, monkeypatch):
    """Uses the same config-home override as Zenium itself."""
    monkeypatch.delenv('ZENIUM_USER_DATA_DIR', raising=False)
    monkeypatch.setenv('CHROME_CONFIG_HOME', str(tmp_path))
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'ignored'))

    assert setup_widevine.default_user_data_dir() == tmp_path / 'net.zenium'


def test_install_widevine(tmp_path):
    """Copies the required files and points the hint at that version."""
    source_dir = make_source(tmp_path)
    user_data_dir = tmp_path / 'profile'

    install_dir = setup_widevine.install_widevine(source_dir, user_data_dir, machine='x86_64')

    assert install_dir == user_data_dir / 'WidevineCdm' / '4.10.3050.0'
    assert (install_dir / 'manifest.json').is_file()
    assert (install_dir / 'LICENSE').read_text(encoding='utf-8') == 'test license'
    assert (install_dir / '_platform_specific' / 'linux_x64' /
            'libwidevinecdm.so').read_bytes() == b'test-widevine-library'
    hint_path = user_data_dir / 'WidevineCdm' / 'latest-component-updated-widevine-cdm'
    assert json.loads(hint_path.read_text(encoding='utf-8')) == {'Path': str(install_dir)}


def test_install_rejects_incomplete_manifest(tmp_path):
    """Rejects CDM directories that Chromium cannot register."""
    source_dir = make_source(tmp_path, {'version': '4.10.3050.0'})

    with pytest.raises(ValueError, match='manifest is missing'):
        setup_widevine.install_widevine(source_dir, tmp_path / 'profile', machine='x86_64')


def test_install_rejects_missing_architecture(tmp_path):
    """Rejects a Chrome CDM without the current architecture library."""
    source_dir = make_source(tmp_path)

    with pytest.raises(ValueError, match='Missing Widevine library'):
        setup_widevine.install_widevine(source_dir, tmp_path / 'profile', machine='aarch64')
