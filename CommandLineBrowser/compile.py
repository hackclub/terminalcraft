import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=terminal_craft',
    '--add-data=visuals:visuals',  # Include the visuals directory
    '--hidden-import=selenium',
    '--hidden-import=webdriver_manager',
    '--hidden-import=requests',
    '--hidden-import=beautifulsoup4',
    '--hidden-import=readability',
    '--hidden-import=textwrap',
    '--hidden-import=random',
    '--hidden-import=re',
])
