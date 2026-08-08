# ============================================================
# build.ps1 — 蒸馏区参赛说明书 LaTeX 一键编译脚本
# 适用：competition-statement-template.tex
#
# 流程：
#   1. 环境检查（xelatex、cls、fonts、关键字体）
#   2. 设置 TEXINPUTS 让 xelatex 找到 templates/cls/ 和 templates/fonts/
#   3. 编译 3 遍（确保目录稳定）
#   4. 错误诊断：首遍检测 fatal，二/三遍检测 overfull
#
# 用法：
#   .\build.ps1                    # 编译默认模板
#   .\build.ps1 -Clean             # 清理临时文件
#   .\build.ps1 -Name mypaper      # 编译指定文件
# ============================================================
param(
    [switch]$Clean,
    [string]$Name = "competition-statement-template"
)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClsDir    = Join-Path $ScriptDir "templates\cls"
$FontsDir  = Join-Path $ScriptDir "templates\fonts"

# ============================================================
# 环境检查
# ============================================================
function Test-Prerequisites {
    $ok = $true

    if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
        Write-Host "[FATAL] xelatex 未安装。请安装 TeX Live 或 MiKTeX。" -ForegroundColor Red
        $ok = $false
    }

    if (-not (Test-Path $ClsDir)) {
        Write-Host "[FATAL] 缺少目录：templates/cls/" -ForegroundColor Red
        $ok = $false
    }

    if (-not (Test-Path $FontsDir)) {
        Write-Host "[FATAL] 缺少目录：templates/fonts/" -ForegroundColor Red
        $ok = $false
    }

    $criticalFonts = @("FZSSJW.TTF","FZKTJW.TTF","FZHTJW.TTF","FZXBSJW.TTF","XITS-Regular.otf")
    foreach ($f in $criticalFonts) {
        $p = Join-Path $FontsDir $f
        if (-not (Test-Path $p)) {
            Write-Host "[FATAL] 缺少字体：templates/fonts/$f" -ForegroundColor Red
            $ok = $false
        }
    }

    $mathOtf = Join-Path $FontsDir "XITSMath.otf"
    $mathReg = Join-Path $FontsDir "XITSMath-Regular.otf"
    if ((Test-Path $mathReg) -and (-not (Test-Path $mathOtf))) {
        Copy-Item $mathReg $mathOtf -Force
        Write-Host "[AUTO] 已从 XITSMath-Regular.otf 创建 XITSMath.otf 副本" -ForegroundColor Yellow
    }

    $clsFiles = @("harryopo-base.sty","harryopo-report.cls")
    foreach ($cls in $clsFiles) {
        $p = Join-Path $ClsDir $cls
        if (-not (Test-Path $p)) {
            Write-Host "[FATAL] 缺少：templates/cls/$cls" -ForegroundColor Red
            $ok = $false
        }
    }

    if (-not $ok) {
        Write-Host "`n[ABORT] 环境检查未通过，请先修复上述问题。" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] 环境检查通过。" -ForegroundColor Green
}

# ============================================================
# TEXINPUTS 设置
# ============================================================
# 让 xelatex 在 templates/cls 找 .cls/.sty，templates/fonts 找字体
# 注意：fontspec 的 Path 是相对工作目录的，所以字体路径已硬编码为 ../fonts/
# 必须从 templates/ 目录编译（详见脚本的 Push-Location）
$env:TEXINPUTS = "$ClsDir;$FontsDir;.;"

$TempExts = @("aux","log","out","toc","nav","snm","vrb","bbl","blg","synctex.gz","fls","fdb_latexmk","listing","lof","lot")

function Clear-TempFiles {
    param([string]$Dir)
    foreach ($ext in $TempExts) {
        Get-ChildItem $Dir -Filter "*.$ext" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

# ============================================================
# 编译流程
# ============================================================
function Build-Tex {
    param([string]$TexFile)
    if (-not (Test-Path $TexFile)) {
        Write-Host "[FATAL] 找不到文件：$TexFile" -ForegroundColor Red
        return $false
    }
    $Name = [System.IO.Path]::GetFileNameWithoutExtension($TexFile)
    $FullPath = (Resolve-Path $TexFile).Path
    $SourceDir = Split-Path -Parent $FullPath
    Write-Host "`n[BUILD] $Name.tex" -ForegroundColor Cyan

    # 关键修复：xelatex 在 Windows 上对中文路径 putenv 失败（致命错误）。
    # 解决方案：把 templates 复制到 d:\ai\latex\tmp-distill-build\（纯英文路径），
    # xelatex 在那里编译（写入 PDF / log），编译完再把 PDF 复制回 SourceDir。
    $TmpBuildRoot = "d:\ai\latex\tmp-distill-build"
    if (Test-Path $TmpBuildRoot) {
        Remove-Item $TmpBuildRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TmpBuildRoot -Force | Out-Null

    # 复制 templates/ 到临时根（纯英文路径）
    Copy-Item (Join-Path $ScriptDir "templates") (Join-Path $TmpBuildRoot "templates") -Recurse -Force

    # 复制 .tex 到临时根
    Copy-Item $FullPath (Join-Path $TmpBuildRoot $Name.tex) -Force

    # 复制 figures/ 到临时根
    if (Test-Path (Join-Path $SourceDir "figures")) {
        Copy-Item (Join-Path $SourceDir "figures") (Join-Path $TmpBuildRoot "figures") -Recurse -Force
    }

    # 关键修复：xelatex 在 templates/ 子目录编译时（cwd=templates/），
    # .tex 中 \includegraphics{figures/img_NNN.png} 会按 cwd 找 templates/figures/。
    # 解决方案：在 templates/ 下创建 junction "figures" 指向根目录的 figures/。
    # 这样 \graphicspath 不用改、.tex 不用改、fontspec Path=fonts/ 仍正确。
    $JunctionPath = Join-Path (Join-Path $TmpBuildRoot "templates") "figures"
    $JunctionTarget = Join-Path $TmpBuildRoot "figures"
    if (Test-Path $JunctionTarget) {
        # 清理可能存在的旧 junction 或同名的真实目录
        if (Test-Path $JunctionPath) {
            cmd /c rmdir "$JunctionPath" 2>&1 | Out-Null
        }
        # 创建 junction（需要绝对路径形式）
        $JunctionTargetAbs = (Resolve-Path $JunctionTarget).Path
        cmd /c mklink /J "$JunctionPath" "$JunctionTargetAbs" 2>&1 | Out-Null
        if (Test-Path $JunctionPath) {
            Write-Host "  [JUNCTION] templates/figures/ -> $JunctionTargetAbs" -ForegroundColor DarkGray
        } else {
            Write-Host "  [WARN] junction 创建失败，回退为目录符号链接" -ForegroundColor Yellow
            New-Item -ItemType SymbolicLink -Path $JunctionPath -Target $JunctionTargetAbs -Force | Out-Null
        }
    }

    # TEXINPUTS 用临时根的纯英文路径
    $TmpBuildRootUnix = $TmpBuildRoot -replace '\\', '/'
    $TmpTemplatesUnix = (Join-Path $TmpBuildRoot "templates") -replace '\\', '/'
    $TmpCls = "$TmpTemplatesUnix/cls"
    $TmpFonts = "$TmpTemplatesUnix/fonts"
    $env:TEXINPUTS = "$TmpCls;$TmpFonts;.;"

    # 从临时 templates/ 编译（cwd=templates/，fontspec Path=fonts/ 解析正确）
    $TmpTemplates = Join-Path $TmpBuildRoot "templates"
    Push-Location $TmpTemplates

    # 清理 .tex 所在目录的临时文件
    foreach ($ext in $TempExts) {
        Get-ChildItem $SourceDir -Filter "$Name.$ext" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    }

    $TmpTexPath = "$TmpBuildRootUnix/$Name.tex"

    $fatal = $false
    for ($i=1; $i -le 3; $i++) {
        Write-Host "  Pass $i/3 ..." -ForegroundColor Gray
        $output = xelatex -interaction=nonstopmode -file-line-error "$TmpTexPath" 2>&1

        if ($i -eq 1) {
            # 致命错误：图片 division by 0、文件缺失、无法加载等
            $errLines = $output | Select-String "Fatal error|No pages of output|No output PDF|Division by 0|file not found|Unable to load" | Select-Object -First 5
            if ($errLines) {
                Write-Host "  [FATAL] 第 1 遍编译出现致命错误：" -ForegroundColor Red
                $errLines | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
                $fatal = $true
                break
            }
        }
    }

    # 把 PDF 和 log 从临时根复制回 SourceDir
    # cwd 是 templates/，所以 PDF 输出在 templates/ 目录
    $tmpPdf = Join-Path $TmpTemplates "$Name.pdf"
    $tmpLog = Join-Path $TmpTemplates "$Name.log"
    if (Test-Path $tmpPdf) {
        Copy-Item $tmpPdf "$SourceDir\$Name.pdf" -Force
    }
    if (Test-Path $tmpLog) {
        Copy-Item $tmpLog "$SourceDir\$Name.log" -Force
    }

    Pop-Location

    # 清理临时目录
    Remove-Item $TmpBuildRoot -Recurse -Force -ErrorAction SilentlyContinue

    if ($fatal) {
        Write-Host "[FAIL] 编译失败，请查看日志：$SourceDir\$Name.log" -ForegroundColor Red
        return $false
    }

    $pdf = Join-Path $SourceDir "$Name.pdf"
    if (Test-Path $pdf) {
        $sz = [math]::Round((Get-Item $pdf).Length/1KB, 2)
        $pg = "?"
        $logContent = Get-Content "$SourceDir\$Name.log" -ErrorAction SilentlyContinue
        if ($logContent) {
            $match = $logContent | Select-String 'Output written on .* \((\d+) page'
            if ($match -and $match.Matches.Count -gt 0) {
                $pg = $match.Matches[0].Groups[1].Value
            }
        }
        # 统计 overfull 警告
        $overfull = ($logContent | Select-String "Overfull \\\\hbox" | Measure-Object).Count
        $warnColor = if ($overfull -gt 0) { "Yellow" } else { "Green" }
        Write-Host "[OK]   $Name.pdf — ${sz}KB  ${pg}页  overfull=$overfull" -ForegroundColor Green
        if ($overfull -gt 0) {
            Write-Host "       ⚠️  存在 $overfull 个 overfull 警告（视觉略宽）" -ForegroundColor Yellow
        }
        return $true
    } else {
        Write-Host "[FAIL] 未生成 PDF" -ForegroundColor Red
        return $false
    }
}

# ============================================================
# 主流程
# ============================================================
Write-Host ("="*60) -ForegroundColor Cyan
Write-Host "  蒸馏区参赛说明书 LaTeX Builder v1.0" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan

Test-Prerequisites

$TexFile = Join-Path $ScriptDir "$Name.tex"

if ($Clean) {
    Write-Host "[CLEAN] 清理临时文件..." -ForegroundColor Yellow
    Clear-TempFiles $ScriptDir
    Write-Host "[CLEAN] 完成。" -ForegroundColor Green
    if (-not (Test-Path $TexFile)) { exit 0 }
}

if (-not (Test-Path $TexFile)) {
    Write-Host "[ERROR] 找不到模板文件：$TexFile" -ForegroundColor Red
    exit 1
}

$result = Build-Tex $TexFile
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
if ($result) {
    Write-Host "[SUCCESS] 编译成功！输出：$Name.pdf" -ForegroundColor Green
} else {
    Write-Host "[FAILED] 编译失败" -ForegroundColor Red
    exit 1
}
