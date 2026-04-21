#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/04/21 13:15:54.371216
Revised: 2026/04/21 13:15:54.371216
"""

import os
import subprocess
import sys
import tomllib

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(here, "pyproject.toml"), "rb") as f:
        version = tomllib.load(f)["project"]["version"]

    exe_name = f"flux-{version}"

    for ext in (".pyw", ".py"):
        candidate = os.path.join(here, "flux" + ext)
        if os.path.exists(candidate):
            script = candidate
            break
    else:
        print("Error: flux.pyw or flux.py not found.")
        sys.exit(1)

    build = os.path.join(here, "build", "temp")
    dist = os.path.join(here, "build", "dist")
    ico = os.path.join(here, "media", "icon.ico")

    os.makedirs(build, exist_ok=True)
    os.makedirs(dist, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--icon={ico}",
        f"--name={exe_name}",
        f"--distpath={dist}",
        f"--workpath={build}",
        f"--specpath={build}",
        "--exclude-module=PyQt5",
        "--hidden-import=qrcode.image.pil",
        script,
    ]

    print("Running PyInstaller...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"\nDone ->  {dist}\\{exe_name}.exe")
    else:
        print("\nBuild failed.")
        sys.exit(result.returncode)
