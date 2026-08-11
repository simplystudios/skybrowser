# Sky Browser

A privacy-focused desktop browser built on Chromium (via Qt WebEngine) with built-in Tor routing, network-level ad blocking, and a forced dark theme.

> ⚠️ **Archived — Not Actively Maintained**
> Sky Browser was built in 2023 as a personal/learning project and hasn't been updated or contributed to since. Its dependencies — Qt WebEngine's bundled Chromium, `stem`, and the ad-block filter list it pulls from are outdated as a result. This repo is shared for portfolio/reference purposes only and is **not** recommended as a daily-driver privacy tool. For actual anonymous browsing, use the official [Tor Browser](https://www.torproject.org/download/).

## Overview

Sky Browser is a desktop browser built with Python and Qt, wrapping Chromium's rendering engine (via `QtWebEngine`) with automatic Tor routing. On launch, it spins up its own local Tor process, routes all traffic through it over SOCKS5, and verifies the connection against Tor's official exit node list — without the user needing to run Tor separately.

## Features

- **Built-in Tor routing** — launches and manages its own Tor process on startup (via the `stem` library) instead of requiring a separately-running Tor instance
- **Exit node verification** — checks the browser's outbound IP against the Tor Project's official Bulk Exit List on launch, to confirm traffic is actually routed through Tor
- **Network-level ad blocking** — intercepts every outbound request and blocks anything matching AdGuard's uBlock-optimized filter list
- **Forced dark mode** — dark theme applied at the Chromium engine level, not just the app chrome
- **Automatic GeoIP updates** — pulls the latest Tor GeoIP database from the Tor Project's repo on each launch, falling back to a local copy if offline
- **Standard browser chrome** — back/forward/refresh/home navigation, address bar, and a menu for settings/about/exit

## Screenshots
 <img width="1920" height="1044" alt="image" src="https://github.com/user-attachments/assets/426b4b71-6f69-452c-88e6-2c7ed2c8a7d3" />


## Tech Stack

- **Python 3**
- **PySide6** (Qt for Python) — UI framework and Chromium-based rendering via `QtWebEngine`
- **stem** — Tor process control and configuration
- **adblockparser** — parses and matches AdGuard/uBlock-style filter rules
- **requests** — filter list, GeoIP, and exit-node-list fetching

## How It Works

1. On launch, the app starts a local Tor process (`stem.process.launch_tor_with_config`) with its own SOCKS port (`9050`) and control port (`9051`), and downloads a fresh GeoIP file from the Tor Project's GitHub.
2. The app's `QNetworkProxy` is configured to route all traffic through that local Tor SOCKS5 proxy.
3. It confirms the connection is actually going through Tor by comparing the machine's public IP (via ipify) against Tor's official exit node list.
4. A `QWebEngineUrlRequestInterceptor` checks every outbound request against the AdGuard filter list and blocks matches before they load.
5. The browser opens to `ip-api.com/json` by default, so you can see your apparent (Tor-routed) IP and location immediately.

## Requirements

- Linux (the Tor binary path is currently hardcoded to `/usr/bin/tor`)
- Python 3.x
- Tor installed system-wide (e.g. `sudo apt install tor` on Debian/Ubuntu)
- Python packages: `PySide6`, `requests`, `stem`, `adblockparser`

## Setup & Running

1. Install Tor on your system:
   ```bash
   sudo apt install tor
   ```
2. Install Python dependencies:
   ```bash
   pip install PySide6 requests stem adblockparser
   ```
3. Make sure the icon assets referenced in the code (an `images/` folder plus a few icons in the root directory) are present alongside the script.
4. Run the app:
   ```bash
   python skybrowser.py
   ```
5. On first launch, the app bootstraps its own Tor circuit (can take a few seconds), verifies the connection, then opens the browser window.

## Known Limitations

- Tor binary path is hardcoded to `/usr/bin/tor` — Linux only as written.
- No specific Tor version is bundled or pinned; the app uses whatever Tor version is installed on the host.
- Settings currently opens a placeholder page rather than a built-out in-app settings panel.
- Built and tested in 2023 — not verified against current Qt WebEngine, Tor, or filter-list versions.
