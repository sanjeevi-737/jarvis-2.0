param(
    [switch]$Daemon,
    [switch]$Setup,
    [switch]$Help
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ScriptDir

if ($Help) {
    Write-Host "JARVIS PRIME 2.0 - Voice Assistant" -ForegroundColor Cyan
    Write-Host "Usage: .\run.ps1 [options]`n" -ForegroundColor Gray
    Write-Host "  -Daemon    Run in background (system tray)" -ForegroundColor Yellow
    Write-Host "  -Setup     First-time setup (register ATXP, check deps)" -ForegroundColor Yellow
    Write-Host "  -Help      Show this help`n" -ForegroundColor Yellow
    Write-Host "  (no flag)  Run in foreground CLI mode" -ForegroundColor Green
    exit 0
}

if (-not (Test-Path ".env")) {
    Write-Host "[!] No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[!] Edit .env with your OPENAI_API_KEY before running." -ForegroundColor Red
    if (-not $Setup) { exit 1 }
}

if ($Setup) {
    Write-Host "[*] JARVIS PRIME - First-Time Setup`n" -ForegroundColor Cyan
    Write-Host "[*] Checking Python dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
    Write-Host "[*] Registering ATXP agent identity..." -ForegroundColor Green
    npx atxp@latest agent register
    Write-Host "[*] Checking balance..." -ForegroundColor Green
    npx atxp@latest balance
    Write-Host "[*] Setup complete. Run .\run.ps1 to start." -ForegroundColor Cyan
    exit 0
}

if ($Daemon) {
    $logFile = Join-Path $ScriptDir "jarvis_daemon.log"
    Write-Host "[*] Starting JARVIS in background mode..." -ForegroundColor Cyan
    $job = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        python -m src.main --daemon
    } -ArgumentList $ScriptDir
    Write-Host "[*] Background PID: $($job.Id)" -ForegroundColor Green
    Write-Host "[*] Logs: $logFile" -ForegroundColor Gray
    Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-Job $job; Remove-Job $job } | Out-Null
} else {
    Write-Host "[*] JARVIS PRIME 2.0 - Initializing..." -ForegroundColor Cyan
    python -m src.main
}
