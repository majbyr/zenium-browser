<div align="center">
    <img src="resources/branding/app_icon/raw.png"
        title="Zenium" alt="Zenium logo" width="120" />
    <h1>Zenium Browser</h1>
    <p>
        A privacy-oriented Chromium browser with a Zen/Arc-inspired vertical
        workspace interface.
    </p>
</div>

> [!IMPORTANT]
> Zenium is an independent, experimental project in active development. It is
> not affiliated with Zen Browser, The Browser Company (Arc), Google, or the
> Helium project. There are currently no official stable Zenium releases.

## What Zenium is

Zenium starts from the open-source
[Helium](https://github.com/imputnet/helium) Chromium patch stack and retains
its ungoogled-chromium foundation, privacy-oriented defaults, and integrated
content blocking. Zenium then changes the browser interface and workflow to
focus on a compact vertical sidebar inspired by the interaction patterns of
Zen Browser and Arc.

This repository contains Zenium's Chromium patch stack and supporting build
resources. It is not a standalone copy of the Chromium source tree: the build
tools fetch a compatible Chromium source release and apply the patches in
[`patches/series`](patches/series).

## Current interface

The current development build includes:

- vertical tabs and Zen mode enabled by default;
- a unified sidebar containing navigation controls, the address field, browser
  actions, and the tab list;
- a pin control for switching between an auto-hiding sidebar and an
  always-visible sidebar;
- sidebar access in fullscreen mode;
- an expanded address/search popup designed for the narrow sidebar;
- Zen-like tab spacing, page framing, rounded corners, and compact controls;
- Chromium's normal tab, extension, profile, browsing-data, and web-platform
  behavior underneath the custom interface.

The design is inspired by Zen Browser and Arc, but Zenium is implemented as a
Chromium/Helium patch set. It does not use Firefox or Zen Browser as its code
base, and it is not intended to be an exact clone of either browser.

## Project status

Zenium is currently a development prototype. The main browser can be built and
run on Linux, and the sidebar workflow is functional, but packaging, updates,
cross-platform behavior, migration, accessibility, and long-term profile
compatibility still require more work. Expect bugs and breaking changes.

Do not rely on the project for high-risk browsing until it has received wider
testing and independent security review. Privacy-related behavior inherited
from upstream projects can also change as Chromium evolves.

## Building

Building Zenium is a full Chromium build and requires substantial disk space,
memory, and time. The patch stack currently tracks the Chromium version in
[`chromium_version.txt`](chromium_version.txt).

The repository retains Helium's download, patch, localization, and resource
generation utilities. Platform-specific packaging and a simpler reproducible
build guide are still being prepared for Zenium; contributors should treat the
existing scripts as development tooling rather than a supported end-user
installer.

## Upstream foundations and inspiration

Zenium exists because of the work of several projects:

- [Chromium](https://www.chromium.org/) provides the browser engine and web
  platform.
- [Helium](https://github.com/imputnet/helium) provides the immediate browser
  base, build tooling, privacy defaults, and many interface patches.
- [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium)
  provides much of the de-Googling foundation.
- [Zen Browser](https://github.com/zen-browser/desktop) and
  [Arc](https://arc.net/) inspired the vertical workspace and compact-sidebar
  design direction.

Additional imported patches retain their original attribution and are grouped
by source in the [`patches`](patches/) directory.

## Contributing

Issues and focused pull requests are welcome. When reporting an interface bug,
include the operating system, window-manager or desktop environment, whether a
system title bar is enabled, and a screenshot or short recording when useful.

## License

Zenium-specific code and modifications are licensed under GPL-3.0; see
[`LICENSE`](LICENSE). Imported code and patches retain their original licenses,
including the BSD-licensed material described in
[`LICENSE.ungoogled_chromium`](LICENSE.ungoogled_chromium).
