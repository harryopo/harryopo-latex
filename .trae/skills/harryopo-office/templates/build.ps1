# ============================================================
# build.ps1 - harryopo LaTeX Template Build Script (v4.2)
# Usage: .\build.ps1 [-Category paper|report] [-Clean] [-NoMath]
# ============================================================
param([string]$Category="", [switch]$Clean, [switch]$NoMath)
$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClsDir   = Join-Path $ScriptDir "cls"
$FontsDir = Join-Path $ScriptDir "fonts"

# ============================================================
# 环境检查（快速失败，不让用户等 1 小时才发现缺工具）
# ============================================================
function Test-Prerequisites {
    $ok = $true

    # 1. xelatex
    if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
        Write-Host "[FATAL] xelatex not found. Install TeX Live or MiKTeX." -ForegroundColor Red
        $ok = $false
    }

    # 2. cls 目录
    if (-not (Test-Path $ClsDir)) {
        Write-Host "[FATAL] cls/ directory not found at $ClsDir" -ForegroundColor Red
        $ok = $false
    }

    # 3. fonts 目录
    if (-not (Test-Path $FontsDir)) {
        Write-Host "[FATAL] fonts/ directory not found at $FontsDir" -ForegroundColor Red
        $ok = $false
    }

    # 4. 关键字体文件
    $criticalFonts = @("FZSSJW.TTF","FZKTJW.TTF","FZHTJW.TTF","XITS-Regular.otf","XITSMath-Regular.otf")
    foreach ($f in $criticalFonts) {
        $p = Join-Path $FontsDir $f
        if (-not (Test-Path $p)) {
            Write-Host "[FATAL] Missing font: fonts/$f" -ForegroundColor Red
            $ok = $false
        }
    }

    # 5. XITSMath.otf（unicode-math SizeFeatures 需要无 -Regular 后缀的副本）
    $mathOtf = Join-Path $FontsDir "XITSMath.otf"
    $mathReg = Join-Path $FontsDir "XITSMath-Regular.otf"
    if ((Test-Path $mathReg) -and (-not (Test-Path $mathOtf))) {
        Copy-Item $mathReg $mathOtf -Force
        Write-Host "[AUTO] Created XITSMath.otf from XITSMath-Regular.otf" -ForegroundColor Yellow
    }

    # 6. .cls 文件
    foreach ($cls in @("harryopo-paper.cls","harryopo-report.cls","harryopo-base.sty")) {
        $p = Join-Path $ClsDir $cls
        if (-not (Test-Path $p)) {
            Write-Host "[FATAL] Missing: cls/$cls" -ForegroundColor Red
            $ok = $false
        }
    }

    if (-not $ok) {
        Write-Host "`n[ABORT] Environment check failed. Fix the above issues and retry." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Environment check passed." -ForegroundColor Green
}

# ============================================================
# TEXINPUTS 设置
# ============================================================
# cls;fonts;.; 让 xelatex 在 templates/cls 找 .cls/.sty，在 templates/fonts 找字体
$env:TEXINPUTS = "$ClsDir;$FontsDir;.;"

$TempExts = @("aux","log","out","toc","nav","snm","vrb","bbl","blg","synctex.gz","fls","fdb_latexmk","listing","lof","lot")

function Clear-TempFiles([string]$Dir) {
    foreach ($ext in $TempExts) {
        Get-ChildItem $Dir -Filter "*.$ext" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

function Build-File([string]$TexPath) {
    $Name = [System.IO.Path]::GetFileNameWithoutExtension($TexPath)
    $Dir  = Split-Path -Parent $TexPath
    Write-Host "`n[BUILD] $Name.tex" -ForegroundColor Cyan
    Push-Location $Dir
    Clear-TempFiles $Dir

    for ($i=1; $i -le 3; $i++) {
        Write-Host "  Pass $i/3 ..." -ForegroundColor Gray
        $result = xelatex -interaction=nonstopmode -file-line-error "$Name.tex" 2>&1
        # 首 pass 检查致命错误
        if ($i -eq 1) {
            $fatal = $result | Select-String "Fatal error|No pages of output"
            if ($fatal) {
                Write-Host "  [FATAL] Compilation failed on pass 1:" -ForegroundColor Red
                $fatal | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
                # 提取关键错误行
                $errors = Get-Content "$Name.log" -ErrorAction SilentlyContinue | Select-String "! |fontspec error|Missing" | Select-Object -First 5
                if ($errors) { $errors | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow } }
                Pop-Location
                return $false
            }
        }
    }

    $pdf = Join-Path $Dir "$Name.pdf"
    if (Test-Path $pdf) {
        $sz = [math]::Round((Get-Item $pdf).Length/1KB, 2)
        # 从最后一次 pass 的日志提取页数（不再额外跑 xelatex）
        $pg = "?"
        $logContent = Get-Content "$Name.log" -ErrorAction SilentlyContinue
        if ($logContent) {
            $match = $logContent | Select-String 'Output written on .* \((\d+) page'
            if ($match -and $match.Matches.Count -gt 0) {
                $pg = $match.Matches[0].Groups[1].Value
            }
        }
        Write-Host "[OK]   $Name.pdf — ${sz}KB  ${pg}pages" -ForegroundColor Green
        Pop-Location
        return $true
    } else {
        Write-Host "[FAIL] $Name — no PDF produced" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

# ============================================================
# 主流程
# ============================================================
Write-Host ("="*60) -ForegroundColor Cyan
Write-Host "  harryopo LaTeX Builder v4.2" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan

Test-Prerequisites

if ($NoMath) {
    $env:HARRYOP_NOMATH = "1"
    Write-Host "[INFO] --NoMath: unicode-math disabled, using amsmath/amssymb" -ForegroundColor Yellow
}

$Targets = @()
if ($Category) {
    $Dir = Join-Path $ScriptDir $Category
    if (Test-Path $Dir) { Get-ChildItem $Dir -Filter "*.tex" | %{ $Targets += $_.FullName } }
} else {
    foreach ($cat in @("paper","report")) {
        $Dir = Join-Path $ScriptDir $cat
        if (Test-Path $Dir) { Get-ChildItem $Dir -Filter "*.tex" | %{ $Targets += $_.FullName } }
    }
}

# Dedup
$Targets = $Targets | Select-Object -Unique

if ($Clean) {
    Write-Host "[CLEAN] Removing all temp files..." -ForegroundColor Yellow
    foreach ($cat in @("paper","report")) {
        $Dir = Join-Path $ScriptDir $cat
        if (Test-Path $Dir) { Clear-TempFiles $Dir }
    }
    $old = Join-Path $ScriptDir "examples"
    if (Test-Path $old) { Clear-TempFiles $old }
    Write-Host "[CLEAN] Done." -ForegroundColor Green
    if (-not $Targets) { exit 0 }
}

if ($Targets.Count -eq 0) {
    Write-Host "[ERROR] No .tex files found." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] $($Targets.Count) tex file(s) found" -ForegroundColor White
$ok=0; $fail=0
foreach ($t in $Targets) {
    if (Build-File $t) { $ok++ } else { $fail++ }
}
Write-Host "`n"+"="*60 -ForegroundColor Cyan
Write-Host "[SUMMARY] OK=$ok FAIL=$fail" -ForegroundColor $(if($fail){"Red"}else{"Green"})
if ($fail) { exit 1 }
