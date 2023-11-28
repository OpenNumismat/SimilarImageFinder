# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/run.py'],
    pathex=['src'],
    binaries=[],
    datas=[("LICENSE", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)


import pyinstaller_versionfile
import src

VERSION = src.__version__
APP_NAME = "SimilarImageFinder"

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile.txt",
    version=VERSION,
    file_description=APP_NAME,
    internal_name=APP_NAME,
)


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='src/icons/binoculars.png',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="versionfile.txt",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)


import shutil

shutil.make_archive(f'{APP_NAME}-{VERSION}', 'zip', 'dist')
