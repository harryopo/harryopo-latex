<#
  harryopo-mathnotes MD->LaTeX Converter
  Dependency: Pandoc, XeLaTeX
  Usage: .\md2latex.ps1 example-note.md [-Clean] [-TexOnly]
#>

param(
  [Parameter(Mandatory=$true, Position=0)]
  [string]$InputFile,

  [switch]$TexOnly,

  [switch]$Clean
)

$ErrorActionPreference = "Stop"

# ---- Check dependencies ----
$pandoc = Get-Command "pandoc" -ErrorAction SilentlyContinue
if (-not $pandoc) {
  Write-Host "[ERROR] Pandoc not found: https://pandoc.org/installing.html" -ForegroundColor Red
  exit 1
}

if (-not (Test-Path $InputFile)) {
  Write-Host "[ERROR] Input file not found: $InputFile" -ForegroundColor Red
  exit 1
}

# ---- Paths ----
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseName  = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$TexFile   = Join-Path $ScriptDir "$BaseName.tex"
$PdfFile   = Join-Path $ScriptDir "$BaseName.pdf"
$Template  = Join-Path $ScriptDir "pandoc\mathnotes-template.latex"
$LuaFilter = Join-Path $ScriptDir "pandoc\mathnotes-table.lua"

if (-not (Test-Path $Template)) {
  Write-Host "[ERROR] Template not found: $Template" -ForegroundColor Red
  exit 1
}

Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  harryopo-mathnotes MD -> LaTeX Converter" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# ---- Step 1: MD -> LaTeX (Pandoc) ----
Write-Host "[1/3] Markdown -> LaTeX ..." -ForegroundColor Yellow

$luaArgs = @()
if (Test-Path $LuaFilter) {
  $luaArgs = @("--lua-filter=$LuaFilter")
}

$pandocCmd = "pandoc `"$InputFile`" --from=markdown+smart+auto_identifiers --to=latex --template=`"$Template`" --pdf-engine=xelatex $luaArgs --output=`"$TexFile`" -M lang=zh-CN 2>&1"
$pandocResult = cmd /c $pandocCmd 2>&1

if (Test-Path $TexFile) {
  Write-Host "  [OK] $TexFile" -ForegroundColor Green
} else {
  Write-Host "  [FAIL] LaTeX generation failed" -ForegroundColor Red
  Write-Host $pandocResult
  exit 1
}

# ---- Step 2: LaTeX -> PDF (XeLaTeX x3) ----
if ($TexOnly) {
  Write-Host ""
  Write-Host "[2/3] Skipped PDF build (--TexOnly)"
  Write-Host ""
  Write-Host "Done. LaTeX source: $TexFile" -ForegroundColor Green
  exit 0
}

Write-Host ""
Write-Host "[2/3] LaTeX -> PDF (xelatex x3) ..." -ForegroundColor Yellow

for ($i = 1; $i -le 3; $i++) {
  Write-Host "  Pass $i ..."
  $xelatexResult = & xelatex -interaction=nonstopmode -output-directory="$ScriptDir" $TexFile 2>&1
}

if (Test-Path $PdfFile) {
  $size = (Get-Item $PdfFile).Length
  $sizeKB = [math]::Round($size / 1024, 1)
  Write-Host "  [OK] $BaseName.pdf ($sizeKB KB)" -ForegroundColor Green
} else {
  Write-Host "  [FAIL] PDF build failed. Check $BaseName.log" -ForegroundColor Red
  exit 1
}

# ---- Step 3: Clean ----
Write-Host ""
Write-Host "[3/3] Clean temp files ..." -ForegroundColor Yellow

if ($Clean) {
  $exts = @("aux", "log", "out", "toc", "lot", "lof", "bbl", "blg", "thm")
  foreach ($ext in $exts) {
    Remove-Item (Join-Path $ScriptDir "$BaseName.$ext") -ErrorAction SilentlyContinue
  }
  Write-Host "  [OK] Temp files removed" -ForegroundColor Green
} else {
  Write-Host "  [INFO] Temp files kept ($BaseName.tex/.log/.aux/.toc)"
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  Conversion complete!" -ForegroundColor Green
Write-Host "    PDF: $PdfFile" -ForegroundColor Green
Write-Host "    TEX: $TexFile" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
