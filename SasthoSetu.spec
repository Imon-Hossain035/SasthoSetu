# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    "customtkinter",
    "dotenv",
    "sqlite3",
    "hashlib",
    "core",
    "database",
    "services",
    "ui",
    "utils",
]

# Collect all assets, fonts, and themes for customtkinter
ctk_ret = collect_all("customtkinter")
datas += ctk_ret[0]
binaries += ctk_ret[1]
hiddenimports += ctk_ret[2]

# Collect google.genai dependencies if present
try:
    genai_ret = collect_all("google.genai")
    datas += genai_ret[0]
    binaries += genai_ret[1]
    hiddenimports += genai_ret[2]
except Exception:
    pass

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SasthoSetu",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
