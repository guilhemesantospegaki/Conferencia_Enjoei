# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/Mono Pegaki_Fundo escuro.png', 'assets'),
        ('assets/Pegaki_Fundo branco.png', 'assets'),
        ('assets/Conferencia_Enjoei.ico', 'assets'),
        ('validacao_icon.svg', '.'),
        ('log_icon.svg', '.'),
        ('download_icon.svg', '.'),
        ('reset_icon.svg', '.'),
        ('.env', '.')
    ],
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
    name='Conferência Enjoei',
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
    icon=['assets/Conferencia_Enjoei.ico'],
)
