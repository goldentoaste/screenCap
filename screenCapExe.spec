# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['screenCap.py'],
             pathex=['D:\\Python Project\\screenCap'],
             binaries=[],
             datas=[('icon.ico', '.'), ('bread.cur', '.')],
             hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32', 'pkg_resources', 'win32ui'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='screenCap',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='icon.ico' )
