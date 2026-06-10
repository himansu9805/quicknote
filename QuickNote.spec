# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/quicknote/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/quicknote/assets', 'quicknote/assets'),
    ],
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
    name='QuickNote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/quicknote/assets/app_icon.ico',
    version='version_info.txt',
    uac_admin=True,
)
