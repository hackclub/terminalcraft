$repoOwner = "frinshhd"
$repoName = "sumsnap"

# Support pre-release via environment variable
$Prerelease = $false
if ($env:SUMSNAP_PRERELEASE -eq "1") { $Prerelease = $true }

if ($Prerelease) {
  Write-Host "Downloading latest *pre-release* sumsnap for Windows..."
  $releases = Invoke-RestMethod "https://api.github.com/repos/$repoOwner/$repoName/releases"
  $pre = $releases | Where-Object { $_.prerelease } | Select-Object -First 1
  $asset = $pre.assets | Where-Object { $_.name -like "sumsnap-windows*" } | Select-Object -First 1
  $url = $asset.browser_download_url
} else {
  Write-Host "Downloading latest sumsnap for Windows..."
  $release = Invoke-RestMethod "https://api.github.com/repos/$repoOwner/$repoName/releases/latest"
  $asset = $release.assets | Where-Object { $_.name -like "sumsnap-windows*" } | Select-Object -First 1
  $url = $asset.browser_download_url
}

if (-not $url) {
  Write-Host "No suitable binary found!"
  exit 1
}

$destDir = "$env:USERPROFILE\AppData\Local\Programs\sumsnap"
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
Invoke-WebRequest -Uri $url -OutFile "$destDir\sumsnap.exe"

# Add to PATH if not already there
$userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$destDir*") {
    [System.Environment]::SetEnvironmentVariable("PATH", "$userPath;$destDir", "User")
    Write-Host "Added $destDir to your PATH. You may need to restart your terminal."
}

Write-Host "Installed! Run 'sumsnap' from anywhere."