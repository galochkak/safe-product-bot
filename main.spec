# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['bot/main.py'],
    pathex=['C:\\Users\\User\\Desktop\\product_checker_bot'],
    binaries=[],
    datas=[
        ('data/banned_additives.json', 'data'),
        ('data/stats.json', 'data'),
        ('.env', '.')
    ],
    hiddenimports=[
        'utils.ocr',
        'pytesseract',
        'cv2',
        'PIL'],  # можно добавить: 'utils.ocr'
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='БезопасныйПродукт',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,           # Скрытое окно (без терминала)
    icon='icon.ico'          # Единственный и правильный путь к иконке
)