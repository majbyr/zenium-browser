## About

Zenium is an experimental browser built on the
[Helium](https://github.com/imputnet/helium) Chromium patch stack. It combines
Helium's privacy features with a compact vertical workspace.

Current features include:

- vertical tabs and Zen mode by default;
- navigation, address bar, browser actions, and tabs in one sidebar;
- auto-hide and always-visible sidebar modes;
- sidebar access in fullscreen;
- compact spacing, controls, and rounded page framing.

Zenium is an independent project inspired by Zen Browser and Arc. It is not a
fork of Zen Browser and is not affiliated with Zen, Arc, Google, or Helium.

## Status

Zenium is an early development prototype. Expect bugs, incomplete packaging,
and breaking changes. There are no official stable releases yet.

This repository contains a Chromium patch stack, not the Chromium source code.
Building it requires downloading and compiling the compatible Chromium version.

## DRM

Widevine is not redistributed with Zenium. On Linux, an existing Google Chrome
installation can be used to enable protected media:

```sh
python3 devutils/setup_widevine.py
```

Restart Zenium completely after running the command. Use `--user-data-dir` when
Zenium is launched with a custom profile directory.

## License

Zenium-specific changes are licensed under [GPL-3.0](LICENSE). Imported code and
patches retain their original licenses and attribution.
