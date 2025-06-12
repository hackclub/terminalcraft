# Simple PowerShell script to start The Signal Cartographer
Write-Host "Starting The Signal Cartographer..." -ForegroundColor Cyan

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Check if activation worked
if ($LASTEXITCODE -eq 0) {
    Write-Host "Virtual environment activated successfully!" -ForegroundColor Green
    
    # Start the game
    Write-Host "Launching AetherTap interface..." -ForegroundColor Yellow
    python main.py
} else {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "Try running: .venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host "Then: python main.py" -ForegroundColor Yellow
} 