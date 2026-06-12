<#
.SYNOPSIS
    Updates live Dragon Lady Observatory data and rebuilds the viewer.

.DESCRIPTION
    Runs a fresh engine poll to generate new records (including alert_class tags),
    then rebuilds the Astro viewer so the globe and console reflect the latest live data.

    This is currently the required step to make the globe properly show bright/dim
    markers for conjunctions after a poll.

.EXAMPLE
    .\scripts\update-live.ps1
#>

Write-Host "=== Dragon Lady Observatory — Live Update ===" -ForegroundColor Cyan

# Move to repo root (this script lives in scripts/)
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "`n[1/2] Running engine poll..." -ForegroundColor Yellow
python -m engine.poll

if ($LASTEXITCODE -ne 0) {
    Write-Host "Poll failed. Aborting." -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/2] Rebuilding viewer..." -ForegroundColor Yellow
Set-Location "$repoRoot\viewer"
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Viewer build failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Done. Live data + rebuilt viewer should now reflect the latest poll (including alert_class glow on the globe)." -ForegroundColor Green
Write-Host "You can preview with: cd viewer; npm run preview" -ForegroundColor Gray