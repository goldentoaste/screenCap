# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['pynput.mouse._win32', 'screenCap.py'],
             pathex=['D:\\Python Project\\screenCap'],
             binaries=[],
             datas=[],
             hiddenimports=['pynput.keyboard._win32--hidden-import'],
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
          name='pynput.mouse',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
