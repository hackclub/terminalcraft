
$DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition

$zfindScript = @"
cd $DIR
python -m venv "$DIR\venv"
& "$DIR\venv\Scripts\Activate.ps1"
pip install -r "$DIR\requirements.txt"
python "$DIR\zfind.py"
deactivate
"@

$zfindScript | Out-File -FilePath "$HOME\.zfind.ps1" -Encoding utf8

$env:Path += ";$HOME"

$shortcutPath = "$HOME\Desktop\zfind.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-File `"$HOME\.zfind.ps1`""
$shortcut.Save()

Write-Output "zfind installed successfully"
