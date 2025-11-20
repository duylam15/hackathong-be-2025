# PowerShell script to clean cache and restart server

Write-Host "🧹 Cleaning Python cache files..." -ForegroundColor Yellow

# Remove all __pycache__ directories
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove all .pyc files
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force

Write-Host "✅ Cache cleaned!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Starting server..." -ForegroundColor Cyan
Write-Host ""

# Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
