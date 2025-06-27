# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['code\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('venv\\Lib\\site-packages\\tabula\\tabula-1.0.5-jar-with-dependencies.jar', 'tabula'), ('code\\src\\env\\', 'src\\env'), ('code\\src\\imgs\\', 'src\\imgs'), ('code\\src\\drivers\\', 'src\\drivers'), ('code\\src\\html\\', 'src\\html')],
    hiddenimports=[],
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
    name='Cobrança Automática',
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
    icon=['code\\src\\imgs\\mail-icon.ico'],
)
