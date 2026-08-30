# ============================================================
# build.ps1 — harryopo-mathnotes 模板编译脚本
# Usage:
#   .\build.ps1          # Build main.tex
#   .\build.ps1 -Clean   # Clean temp files
# ============================================================
param([switch]$Clean)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Test-XeLaTeX {
    try { $null = xelatex --version 2>&1; return $true } catch { return $false }
}

function Clear-TempFiles {
    $exts = @("aux","log","out","toc","nav","snm","vrb","bbl","blg","synctex.gz","fls","fdb_latexmk")
    Write-Host "[CLEAN] Removing temp files..." -ForegroundColor Yellow
    $n = 0
    Push-Location $root
    foreach ($ext in $exts) {
        $files = Get-ChildItem -Filter "*.$ext" -ErrorAction SilentlyContinue
        if ($files) { Remove-Item $files -Force; $n += $files.Count }
    }
    Pop-Location
    Write-Host "[CLEAN] Done. $n files removed." -ForegroundColor Green
}

Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  harryopo-mathnotes Template Builder" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

if (-not (Test-XeLaTeX)) {
    Write-Host "[ERROR] XeLaTeX not found" -ForegroundColor Red; exit 1
}

if ($Clean) { Clear-TempFiles; exit 0 }

Push-Location $root

$file = "main"
if (-not (Test-Path "$file.tex")) {
    Write-Host "[ERROR] $file.tex not found" -ForegroundColor Red
    Pop-Location; exit 1
}

Write-Host "`n[BUILD] $file.tex" -ForegroundColor Cyan
foreach ($ext in @("aux","log","out","toc","bbl","blg")) {
    Remove-Item "$file.$ext" -EA SilentlyContinue
}

$ok = $true
for ($i = 1; $i -le 3; $i++) {
    Write-Host "  Pass $i ..." -ForegroundColor Gray
    $r = xelatex -interaction=nonstopmode -file-line-error "$file.tex" 2>&1
    if ($LASTEXITCODE -ne 0) { $ok = $false }
}

if ($ok -and (Test-Path "$file.pdf")) {
    $sz = [math]::Round((Get-Item "$file.pdf").Length / 1KB, 2)
    $pm = $r | Select-String 'Output written on .* \((\d+) page'
    $pg = if ($pm) { $pm.Matches.Groups[1].Value } else { "?" }
    Write-Host "[OK] $file.pdf ($sz KB, $pg pages)" -ForegroundColor Green
} else {
    Write-Host "[FAIL] $file.pdf not generated. See $file.log" -ForegroundColor Red
    Pop-Location; exit 1
}

Pop-Location
Write-Host "`nDone." -ForegroundColor Green
