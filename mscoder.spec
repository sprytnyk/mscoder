# -*- mode: python ; coding: utf-8 -*-
# Build with: uv run pyinstaller mscoder.spec --clean
# Linux and Windows get one file. macOS gets dist/MSCoder.app, which shows its icon in
# Finder and the Dock and opens without a Terminal window. MSCODER_TARGET_ARCH picks
# x86_64 or arm64 there (default: the interpreter's).
import os
import re
import sys
from pathlib import Path

MACOS = sys.platform == "darwin"

icon_file = "assets/icon.icns" if MACOS else "assets/icon.ico"
datas = [
    ("assets/icon.ico", "assets"),
]

a = Analysis(
    ["mscoder/__main__.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe_options = dict(
    name="mscoder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=not MACOS,  # UPX breaks the code signature macOS needs
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=os.environ.get("MSCODER_TARGET_ARCH") or None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

if MACOS:
    # PyInstaller warns against packing an .app into one file. It starts slower, and an
    # .app is a folder anyway. Finder shows one MSCoder.app either way.
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, **exe_options)
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="mscoder")
    init = Path("mscoder/__init__.py").read_text()
    version = re.search(r'__version__ = "(\d+(?:\.\d+)*)', init).group(1)
    app = BUNDLE(
        coll,
        name="MSCoder.app",
        icon=icon_file,
        bundle_identifier="dev.sprytnyk.mscoder",
        version=version,
        info_plist={
            "CFBundleVersion": version,
            "LSApplicationCategoryType": "public.app-category.utilities",
        },
    )
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], runtime_tmpdir=None, **exe_options)
