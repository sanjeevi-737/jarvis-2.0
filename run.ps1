param(
    [switch]$Daemon,
    [switch]$Setup,
    [switch]$Help
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ScriptDir

# ── Help ──────────────────────────────────────────────────
if ($Help) {
    Write-Host "JARVIS PRIME 2.0 - Voice Assistant" -ForegroundColor Cyan
    Write-Host "Usage: .\run.ps1 [options]`n" -ForegroundColor Gray
    Write-Host "  -Daemon    Run in background (system tray, stops when terminal closes)" -ForegroundColor Yellow
    Write-Host "  -Setup     First-time setup (register ATXP, check deps)" -ForegroundColor Yellow
    Write-Host "  -Help      Show this help`n" -ForegroundColor Yellow
    Write-Host "  (no flag)  Run in foreground CLI mode" -ForegroundColor Green
    exit 0
}

# ── Prerequisites ─────────────────────────────────────────
$MissingDeps = @()

if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    $MissingDeps += "Python 3.13+ (https://www.python.org/downloads/)"
}

if (-not (Get-Command "npx" -ErrorAction SilentlyContinue)) {
    $MissingDeps += "Node.js / npm (https://nodejs.org/) - required for ATXP phone/SMS/email"
}

if ($MissingDeps.Count -gt 0) {
    Write-Host "[!] Missing prerequisites:" -ForegroundColor Red
    $MissingDeps | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
    if (-not $Setup) { exit 1 }
}

# ── Environment ───────────────────────────────────────────
if (-not (Test-Path ".env")) {
    Write-Host "[!] No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[!] Edit .env with your OPENAI_API_KEY before running." -ForegroundColor Red
    if (-not $Setup) { exit 1 }
}

# ── Setup ─────────────────────────────────────────────────
if ($Setup) {
    Write-Host "[*] JARVIS PRIME - First-Time Setup`n" -ForegroundColor Cyan
    Write-Host "[*] Installing Python dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] pip install failed. Check requirements.txt." -ForegroundColor Red
        exit 1
    }
    $useAtxp = (Select-String -Path ".env" -Pattern "^USE_ATXP=1" -Quiet)
    if ($useAtxp) {
        Write-Host "[*] Registering ATXP agent identity..." -ForegroundColor Green
        npx atxp@latest agent register
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[!] ATXP registration failed. Check your network and npm." -ForegroundColor Red
        }
        Write-Host "[*] Checking ATXP balance..." -ForegroundColor Green
        npx atxp@latest balance
    } else {
        Write-Host "[*] Skipping ATXP setup (USE_ATXP=0). LLM + shell commands will work." -ForegroundColor Yellow
    }
    Write-Host "[*] Setup complete. Run .\run.ps1 to start." -ForegroundColor Cyan
    exit 0
}

# ── Daemon Mode ───────────────────────────────────────────
if ($Daemon) {
    $logFile = Join-Path $ScriptDir "jarvis_daemon.log"
    $pidFile = Join-Path $ScriptDir "jarvis_daemon.pid"
    Write-Host "[*] Starting JARVIS in background mode..." -ForegroundColor Cyan
    Write-Host "[*] Logs: $logFile" -ForegroundColor Gray
    Write-Host "[*] Note: Process stops when this terminal closes." -ForegroundColor Yellow
    Write-Host "[*] Use Task Scheduler for persistent boot-time daemon." -ForegroundColor Gray
    $job = Start-Job -Name "JarvisDaemon" -ScriptBlock {
        param($dir)
        Set-Location $dir
        $env:PYTHONUNBUFFERED = "1"
        python -m src.main --daemon *>&1 | ForEach-Object {
            "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $_"
        }
    } -ArgumentList $ScriptDir
    $job.Id | Out-File -FilePath $pidFile -Encoding utf8
    Wait-Job $job | Out-Null
    exit 0
}

# ── Foreground Mode ──────────────────────────────────────
Write-Host "[*] JARVIS PRIME 2.0 - Initializing..." -ForegroundColor Cyan
python -m src.main
