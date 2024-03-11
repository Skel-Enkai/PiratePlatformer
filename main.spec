# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Game/src/main.py'],
    pathex=['/data','/game','/levels'],
    binaries=[],
    datas=[('Game/graphics', 'graphics'), ('Game/audio', 'audio'), ('Game/level_data', 'level_data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TreasureHunters',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
