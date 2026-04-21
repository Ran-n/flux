[//]: # ( ---------------------------------------------------------------------- )
[//]: # (+ Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+ Created: 	2026/04/21 08:57:11.157825 )
[//]: # (+ Revised: 	2026/04/21 09:41:40.774566 )
[//]: # ( ---------------------------------------------------------------------- )

# flux

> *Flux* — from Latin *fluxus*, meaning flow. In physics, the measure of a field passing through a surface. Here: the passage of information across the gap between your devices.

Text lives on your screen. Flux lets it move.

Copy anything — a URL, a password, a note — and Flux renders it as a QR code, ready to be caught by whatever's on the other side. No cable, no account, no sync service. Just a pattern of light that carries meaning across the air.

The name fits the tool: one fluid motion from clipboard to phone, with nothing in between.

## Features

- Clipboard text hidden by default — toggle visibility with the eye button
- Right-click the eye button to view the full text in a popup
- Right-click the QR code to copy it to the clipboard as an image
- Auto-closes on focus loss

## Limits

QR codes have a hard data capacity ceiling (version 40, error correction M):

| Content type | Max |
|---|---|
| Numeric only | ~7,089 characters |
| Alphanumeric | ~4,296 characters |
| Binary / UTF-8 | ~2,953 bytes |

Text that exceeds these limits will show an error instead of a QR code.

## Setup

**uv**
```
uv sync
```

**pip**
```
pip install pyperclip qrcode Pillow pywin32
```

**pipenv**
```
pipenv install
```

> Linux requires `xclip` for image copy: `sudo apt install xclip`

## Usage

Use `pythonw` to launch without blocking the terminal (Windows — no console window):

**uv**
```
uv run pythonw flux.pyw
```

**pip / pipenv**
```
pythonw flux.pyw
```

> On Linux/macOS `python flux.pyw` works fine; the process detaches naturally via the event loop.

## TODO

- **`make_icon.py`** — verify that all sizes embed correctly in the `.ico` file; some Windows contexts (Explorer, taskbar, alt-tab) pick specific sizes and the current Pillow `save()` call may not embed them reliably. Investigate using an external tool (e.g. `magick convert` via ImageMagick) or a dedicated `.ico` library to guarantee all nine size frames are present and correct.
