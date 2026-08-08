% ============================================================
% harryopo-mathnotes.cls — 数理笔记文档类
% 风格：色块+侧边竖线定义块 / 方正字体 / XITS数学 / 宽边注
% 维护：harryopo
% ============================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{harryopo-mathnotes}[2026/06/21 v1.0 Harryopo Math Notes Template]

% ===================== 文档类 =====================
\LoadClass[a4paper,9pt,twoside]{extarticle}

% ===================== 基础宏包 =====================
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
\RequirePackage[scheme=plain,fontset=none]{ctex}
\RequirePackage{unicode-math}
\RequirePackage{amsmath}
\RequirePackage[svgnames,table]{xcolor}
\RequirePackage{graphicx}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{setspace}
\RequirePackage{calc}
\RequirePackage{indentfirst}
\RequirePackage{marginfix}          % 自动防边注重叠
\RequirePackage{mdframed}
\RequirePackage{framed}
\RequirePackage{adjustbox}
\RequirePackage{changepage}
\RequirePackage{tabularx}           % X 列类型（表格自动换行）
\RequirePackage{booktabs}           % 专业三线表
\RequirePackage[colorlinks,linkcolor=black]{hyperref}
\RequirePackage{amsthm}
\RequirePackage{geometry}
\RequirePackage{caption}
\RequirePackage[list=true]{subcaption}

% ===================== 页面几何 =====================
\newlength\leftblank
\newlength\rightblank
\newlength\topblank
\newlength\bottomblank
\setlength\leftblank{2.3cm}
\setlength\rightblank{6cm}
\setlength\topblank{3cm}
\setlength\bottomblank{2.5cm}

\geometry{
  a4paper,
  top=\topblank, bottom=\bottomblank,
  left=\leftblank, right=\rightblank,
  twoside,
  headheight=15pt,
  headsep=0.8cm,
  footskip=1.2cm
}

\setlength{\marginparwidth}{5.3cm}
\setlength{\marginparsep}{12pt}
\setlength{\marginparpush}{5pt}

% ===================== 西文字体（XITS + TeX Gyre Heros，优先 fonts/ 本地） =====================
% 三层回退：fonts/ 目录 → 系统字体名 → 通用回退

\IfFontExistsTF{XITS-Regular.otf}{%
  \setmainfont{XITS-Regular.otf}[
    Path=./fonts/,
    BoldFont=XITS-Bold.otf,
    ItalicFont=XITS-Italic.otf,
    BoldItalicFont=XITS-BoldItalic.otf,
  ]
}{%
  \IfFontExistsTF{XITS}{%
    \setmainfont{XITS}
  }{%
    \setmainfont{Times New Roman}
  }
}

\IfFontExistsTF{texgyreheros-regular.otf}{%
  \setsansfont{texgyreheros-regular.otf}[
    Path=./fonts/,
    BoldFont=texgyreheros-bold.otf,
    ItalicFont=texgyreheros-italic.otf,
    BoldItalicFont=texgyreheros-bolditalic.otf,
    Scale=0.91,
  ]
}{%
  \IfFontExistsTF{TeX Gyre Heros}{%
    \setsansfont{TeX Gyre Heros}[Scale=0.91]
  }{%
    \setsansfont{Arial}[Scale=0.91]
  }
}

\IfFontExistsTF{XITSMath-Regular.otf}{%
  \setmathfont{XITSMath-Regular.otf}[
    Path=./fonts/,
    BoldFont=XITSMath-Bold.otf,
  ]
}{%
  \IfFontExistsTF{XITS Math}{%
    \setmathfont{XITS Math}
  }{%
    \setmathfont{TeX Gyre Termes Math}
  }
}

\everymath{\displaystyle}       % 行内公式 Displaystyle（笔记风格）

% ===================== 中文字体（方正系列 + 系统回退） =====================
\xeCJKsetup{AutoFallBack=true}

\IfFontExistsTF{FZSSJW.TTF}{%
  % --- 有方正字体：最佳排版效果 ---
  \setCJKmainfont[BoldFont={FZHTJW.TTF},ItalicFont={FZKTJW.TTF}]{FZSSJW.TTF}
  \setCJKfamilyfont{zhsong}{FZSSJW.TTF}
  \setCJKfamilyfont{zhhei}{FZHTJW.TTF}
  \setCJKfamilyfont{zhkai}{FZKTJW.TTF}
  \setCJKfamilyfont{zhfs}{FZFSJW.TTF}
  \setCJKfamilyfont{zhli}{FZLSJW.TTF}
  \newCJKfontfamily\fzdbs{FZDBSJW.TTF}
  \newCJKfontfamily\fzht{FZHTJW.TTF}
  \newCJKfontfamily\fzkt{FZKTJW.TTF}
  \newCJKfontfamily\fzfs{FZFSJW.TTF}
  \newCJKfontfamily\fzxbs{FZXBSJW.TTF}
}{%
  % --- 无方正字体：系统回退 ---
  \setCJKmainfont[BoldFont={SimHei},ItalicFont={KaiTi}]{SimSun}
  \setCJKfamilyfont{zhsong}{SimSun}
  \setCJKfamilyfont{zhhei}{SimHei}
  \setCJKfamilyfont{zhkai}{KaiTi}
  \setCJKfamilyfont{zhfs}{FangSong}
  \setCJKfamilyfont{zhli}{STLiti}
  \newCJKfontfamily\fzdbs{SimHei}
  \newCJKfontfamily\fzht{SimHei}
  \newCJKfontfamily\fzkt{KaiTi}
  \newCJKfontfamily\fzfs{FangSong}
  \newCJKfontfamily\fzxbs{SimHei}
}

% ===================== 浮动体路径 & Captions =====================
\graphicspath{{./image/}{./images/}{./figures/}{./fig/}}

\DeclareCaptionFont{fzfsfont}{\fzfs}
\DeclareCaptionLabelFormat{zhlabel}{{\fzht #1 #2}\;}
\captionsetup{
  labelformat=zhlabel,
  labelsep=quad,
  font={footnotesize,fzfsfont},
  skip=6pt
}
\captionsetup[table]{
  position=bottom                % 表格标题默认在表格下方
}
\captionsetup[subfigure]{
  labelformat=simple,
  labelsep=space,
  font={scriptsize,fzfsfont}
}

% ===================== 颜色定义 =====================
\definecolor{formalshade}{rgb}{0.95,0.95,0.95}
\definecolor{defbar}{gray}{0.55}
\definecolor{answerbg}{rgb}{0.90,0.96,1.0}

% 标注蓝色系（RGB 精确定义，R=0 杜绝偏紫）
\definecolor{attnline}{RGB}{0, 130, 215}     % 注意：深天蓝
\definecolor{attnbg}{RGB}{228, 242, 255}     % 注意：极淡蓝底
\definecolor{tipsline}{RGB}{60, 165, 230}    % 提示：中天蓝
\definecolor{tipsbg}{RGB}{238, 249, 255}     % 提示：微蓝底
\definecolor{warnsline}{RGB}{135, 200, 240}  % 警告：浅天蓝
\definecolor{warnsbg}{RGB}{245, 251, 255}    % 警告：近乎白底

% ===================== 脚注样式 =====================
\setlength{\footnotesep}{0.5em}

% ===================== 页眉页脚 =====================
% 智能页眉：奇数页右下 = 节标题，偶数页左下 = 子节标题；无横线
\pagestyle{fancy}
\fancyhf{}
\fancyhead[RO]{\fzkt\rightmark}      % 奇数页右侧：当前 subsection
\fancyhead[LE]{\fzkt\leftmark}       % 偶数页左侧：当前 section
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}

% ===================== 标题字体大小 =====================
\newcommand*{\TitleFont}{%
  \usefont{\encodingdefault}{\rmdefault}{m}{n}%
  \fontsize{34}{20}\selectfont}
\newcommand*{\TitleFontb}{%
  \usefont{\encodingdefault}{\rmdefault}{m}{n}%
  \fontsize{30}{20}\selectfont}
\newcommand*{\TitleFontc}{%
  \usefont{\encodingdefault}{\rmdefault}{m}{n}%
  \fontsize{23}{20}\selectfont}

% ===================== 节标题格式 =====================
% section: "一、标题"（中文编号 + 顿号）
\titleformat{\section}
  {\normalfont\TitleFontc\fzdbs\color{DeepSkyBlue}}
  {\fzht \chinese{section}、}
  {0.5em}
  {}
\renewcommand{\thesection}{\arabic{section}}

% subsection: "1.1 标题"（阿拉伯数字）
\titleformat{\subsection}
  {\normalfont\huge\fzxbs\color{DeepSkyBlue}}
  {\thesubsection}
  {1em}
  {}
\titlespacing*{\subsection}{0pt}{12pt}{6pt}

% subsubsection: "1.1.1 标题"（阿拉伯数字，黑体）
\titleformat{\subsubsection}
  {\normalfont\Large\fzht}
  {\thesubsubsection}
  {1em}
  {}
\titlespacing*{\subsubsection}{0pt}{10pt}{4pt}

\setcounter{tocdepth}{2}

% ===================== 色块+侧边竖线 环境 =====================
\newenvironment{formal}{%
  \def\FrameCommand{%
    \hspace{2pt}%
    {\color{defbar}\vrule width 2pt}%
    {\color{formalshade}\vrule width 3pt}%
    \colorbox{formalshade}%
  }%
  \MakeFramed{\advance\hsize-\width\FrameRestore}%
  \noindent\hspace{-5pt}%
  \begin{adjustwidth}{}{7pt}%
  \vspace{2pt}%
}{%
  \vspace{2pt}%
  \end{adjustwidth}%
  \endMakeFramed%
}

% ===================== 定理类环境 =====================
\theoremstyle{definition}
\newtheorem{theorem}{定理}[section]
\newtheorem{definition}[theorem]{定义}
\newtheorem{lemma}[theorem]{性质}
\newtheorem{corollary}[theorem]{推论}
\newtheorem{example}{例}

% 解答环境：淡蓝背景
\newmdenv[
  backgroundcolor=answerbg,
  linecolor=white,
  innertopmargin=6pt,
  innerbottommargin=6pt,
  innerleftmargin=8pt,
  innerrightmargin=8pt,
]{answer}

% ===================== 习题环境 =====================
\newcounter{exercisecnt}[section]
\renewcommand{\theexercisecnt}{\thesection.\arabic{exercisecnt}}

\newenvironment{exercise}[1][]{%
  \refstepcounter{exercisecnt}%
  \par\medskip\noindent%
  {\color{DeepSkyBlue}\fzht 习题~\theexercisecnt%
  \if\relax\detokenize{#1}\relax\else\quad #1\fi}
  \par\vspace{4pt}\noindent\ignorespaces
}{%
  \par\medskip%
}

% ===================== 注解标注环境 =====================
% 注意（深天蓝竖线 + 淡蓝背景）
\newmdenv[
  hidealllines=true,
  leftline=true,
  linecolor=attnline,
  linewidth=2.5pt,
  leftmargin=0pt,
  rightmargin=0pt,
  innerleftmargin=10pt,
  innerrightmargin=8pt,
  innertopmargin=6pt,
  innerbottommargin=6pt,
  backgroundcolor=attnbg,
  skipabove=10pt,
  skipbelow=10pt,
]{mdfattention}
\newenvironment{attention}{%
  \begin{mdfattention}%
    \textbf{\color{attnline}\fzht 注意：}~
}{%
  \end{mdfattention}%
}

% 提示（中天蓝竖线 + 微蓝背景）
\newmdenv[
  hidealllines=true,
  leftline=true,
  linecolor=tipsline,
  linewidth=2.5pt,
  leftmargin=0pt,
  rightmargin=0pt,
  innerleftmargin=10pt,
  innerrightmargin=8pt,
  innertopmargin=6pt,
  innerbottommargin=6pt,
  backgroundcolor=tipsbg,
  skipabove=10pt,
  skipbelow=10pt,
]{mdftip}
\newenvironment{tips}{%
  \begin{mdftip}%
    \textbf{\color{tipsline}\fzht 提示：}~
}{%
  \end{mdftip}%
}

% 警告（浅天蓝竖线 + 近乎白背景）
\newmdenv[
  hidealllines=true,
  leftline=true,
  linecolor=warnsline,
  linewidth=2.5pt,
  leftmargin=0pt,
  rightmargin=0pt,
  innerleftmargin=10pt,
  innerrightmargin=8pt,
  innertopmargin=6pt,
  innerbottommargin=6pt,
  backgroundcolor=warnsbg,
  skipabove=10pt,
  skipbelow=10pt,
]{mdfwarn}
\newenvironment{warns}{%
  \begin{mdfwarn}%
    \textbf{\color{warnsline}\fzht 警告：}~
}{%
  \end{mdfwarn}%
}

% ===================== 侧边注解命令 =====================
% 通用边注格式设置
\newcommand{\harryopo@marginfmt}{%
  \raggedright%
  \footnotesize%
  \setlength{\parskip}{2pt}%
  \setlength{\lineskip}{1pt}%
  \linespread{1.1}\selectfont%
}

\newcommand{\bianzhu}[2][]{%
  \marginpar{%
    \harryopo@marginfmt%
    \if\relax\detokenize{#1}\relax\else%
      {\color{DeepSkyBlue}\fzht #1}\\[4pt]%
    \fi%
    \fzfs #2%
  }%
}

\newcommand{\bianzhutu}[3][]{%
  \marginpar{%
    \harryopo@marginfmt%
    \if\relax\detokenize{#1}\relax\else%
      {\color{DeepSkyBlue}\fzht #1}\\[4pt]%
    \fi%
    \includegraphics[width=0.88\marginparwidth]{#2}\\[4pt]%
    \fzfs #3%
  }%
}

% ===================== 封面命令 =====================
% 用户可重新定义 \mathtitle, \mathauthor, \mathaffiliation, \mathinfo
\newcommand{\mathtitle}{数理笔记}
\newcommand{\mathauthor}{作者姓名}
\newcommand{\mathaffiliation}{单位名称}
\newcommand{\mathinfo}{}

\renewcommand{\maketitle}{%
  \begin{titlepage}
    \setlength{\parindent}{0pt}
    \raggedleft
    \vspace*{3cm}

    \hfill
    \begin{minipage}[t]{0.6\textwidth}
      \raggedleft
      {\TitleFont\fzdbs\mathtitle}

      \vspace{1.2cm}
      \hfill{\color{DeepSkyBlue}\rule{5cm}{1.5pt}}

      \vspace{1cm}
      {\Huge\fzfs 编著\quad\mathauthor}

      \vspace{2.5cm}
      {\large\fzfs\mathinfo}
    \end{minipage}

    \vfill
    {\Large\fzfs\mathaffiliation}

    \vspace{0.5cm}
    {\normalsize\fzfs 版权所有\quad 侵权必究\par\copyright\ \the\year}
  \end{titlepage}
}

% ===================== 附录 =====================
\let\oldappendix\appendix
\renewcommand{\appendix}{%
  \oldappendix
  \renewcommand{\thesection}{\chinese{section}}
  \titleformat{\section}
    {\normalfont\TitleFontc\fzdbs\color{DeepSkyBlue}}
    {\fzht 附录\chinese{section}}
    {0.5em}
    {}
  \renewcommand{\theexercisecnt}{\chinese{section}.\arabic{exercisecnt}}
}

\endinput
