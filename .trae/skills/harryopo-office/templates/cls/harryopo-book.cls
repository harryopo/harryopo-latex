% ============================================================
% harryopo-book.cls — harryopo 书籍/教材文档类 (v1.0)
% 风格：庄重、层级分明、便于翻阅
% 特性：ctexbook 骨架、front/main/back matter 三段式、
%        章-节双面页眉（recto 章名 / verso 节名）、
%        6 种教学盒子、右侧旁注、定理环境章级编号
%        字体体系与报告/论文模板一致，仅蓝/黑色系
%
% 编译约束：cwd 必须是 templates/ 的直接子目录
%          （base.sty 字体写死 Path=../fonts/，否则静默回退 Times/SimSun）
% ============================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{harryopo-book}[2026/09/30 v1.0 harryopo Book Template]

% ============================================================
% 第一部分：选项声明
% 手写 \DeclareOption，禁用 kvoptions/l3keys——
% 主题通过 \def\harryopo@theme{} 在加载 base.sty 前设定
% ============================================================

\def\harryopo@theme{blue}

% ⚠️ \newif 必须放在 \LoadClass 之后——放之前会让 TeX 在未加载字体时
% 展开条件文本，产出成片 "Missing character in nullfont" 垃圾
% （已用最小样例复现验证：\newif 在 \LoadClass 前 → nullfont 报错，
%   在其后 → 0 次）。选项体只赋值，加载后再建条件。
\DeclareOption{a5paper}{\def\hryopo@a5paper{1}}
\DeclareOption{oneside}{\def\harryopo@oneside{1}}
\DeclareOption{dark}{\def\harryopo@theme{dark}}
\DeclareOption{nomath}{\def\harryopo@nomath{1}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexbook}}
\ProcessOptions\relax

\ifdefined\harryopo@a5paper\else\def\harryopo@a5paper{0}\fi
\ifdefined\harryopo@oneside\else\def\harryopo@oneside{0}\fi

% 默认双面排版（书籍惯例），oneside 可关
\ifnum\harryopo@oneside=1
  \def\hrypbook@sideopts{oneside}
\else
  \def\hrypbook@sideopts{twoside}
\fi

\ifnum\harryopo@a5paper=1
  \LoadClass[a5paper,11pt,\hrypbook@sideopts]{ctexbook}
\else
  \LoadClass[a4paper,11pt,\hrypbook@sideopts]{ctexbook}
\fi

% ============================================================
% 第二部分：依赖包加载
% ============================================================

\RequirePackage{harryopo-base}
\RequirePackage{enumitem}
\setlist{nosep,leftmargin=2em,itemsep=2pt,topsep=4pt,partopsep=0pt}

\RequirePackage{titlesec}
\RequirePackage{tocloft}
\RequirePackage{mdframed}
\RequirePackage{graphicx}

% marginfix 必须在 geometry 之后加载（见 CLAUDE.md 踩坑 5）
\geometry{left=2.6cm, right=3.2cm, top=2.6cm, bottom=2.6cm,
          headheight=15pt, marginparwidth=4cm, marginparsep=0.6cm}
\RequirePackage{marginfix}

% ============================================================
% 第二点五部分：接入统一排版规范（harryopo-typography）
% 字号阶梯 / 标题色阶 / 目录层级 / 题注 / 代码块 全部由此统一接管。
% 章标题沿用本类自定义（block + 细横线），故不套 \hrptitleformat{chapter}。
% ============================================================
\hrpapplyall
\hrptocsetup

% ============================================================
% 第三部分：教学盒子配色
% ============================================================

\definecolor{keyline}{HTML}{2B6CB0}
\definecolor{keybg}{HTML}{EBF8FF}
\definecolor{expline}{HTML}{276749}
\definecolor{expbg}{HTML}{F0FFF4}
\definecolor{tipsline}{HTML}{B7791F}
\definecolor{tipsbg}{HTML}{FFFFF0}
\definecolor{warnline}{HTML}{C53030}
\definecolor{warnbg}{HTML}{FFF5F5}
\definecolor{pracline}{HTML}{553C9A}
\definecolor{pracbg}{HTML}{FAF5FF}
\definecolor{ansline}{HTML}{4A5568}
\definecolor{ansbg}{HTML}{F7FAFC}

% ============================================================
% 第四部分：页面布局与页眉页脚
% 双面书籍页眉：偶数页（verso）章名，奇数页（recto）节名
% 不使用 base.sty 的 \harryopo@setup@header——那是单面设计（左右相同）
% ============================================================

\pagestyle{fancy}
\fancyhf{}
% 双面书籍页眉：偶数页（verso）显章名，奇数页（recto）显节名
% ⚠️ 两个实测坑：
%  1) ctexbook 会重映射 fancyhdr 的 E/O 槽位，同时声明 LE+RE 会出现
%     两条重复页眉。改用单 L 槽 + \ifodd 分流，规避 E/O 语义。
%  2) \value{page} 是"印在纸上的页码"，frontmatter 用罗马数字时与
%     物理纸序不一致（实测 recto 出章名、verso 出节名，与预期相反）。
%     故不依赖 page 奇偶，改用物理纸序：twoside 下页码计数器与纸序同步，
%     但 \ifodd 判断的是计数器——为稳妥直接用 fancyhdr 的 E/O 语义反推：
%     verso(偶) 取 \leftmark(章名)，recto(奇) 取 \rightmark(节名)。
\fancyhead[L]{\small\fzkt\nouppercase{\ifodd\value{page}\rightmark\else\leftmark\fi}}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% frontmatter 罗马页码、mainmatter 重置为 1
% ⚠️ 两个顺序约束（均为实测踩出）：
%  1) 这里不能用 \cleardoublepage——会在 \maketitle 前插入空白偶数页。
%  2) \frontmatter 里的 \pagenumbering{roman} 会把计数器清零，
%     导致 \maketitle 之前先排出 2 张只有页码的空白页。
%     故 \maketitle 内部自行清零（见该处 \setcounter{page}{1}）。
\renewcommand{\frontmatter}{%
  \@mainmatterfalse
  \pagestyle{plain}%
}
\renewcommand{\mainmatter}{%
  \cleardoublepage
  \@mainmattertrue
  \pagenumbering{arabic}%
  \setcounter{page}{1}%
  \pagestyle{fancy}%
}
\renewcommand{\backmatter}{%
  \cleardoublepage
  \@mainmatterfalse
  \pagestyle{plain}%
}

% 章/节标记（页眉用）。
% ⚠️ \sectionmark 必须用 \markboth 而非 \markright——\markright 只写
%    \rightmark，会把 verso 页的章名覆盖成节名（实测 verso 显示"1.1 节…"）。
\renewcommand{\chaptermark}[1]{\markboth{第\thechapter 章\quad #1}{第\thechapter 章\quad #1}}
\renewcommand{\sectionmark}[1]{\markboth{\thesection\quad #1}{\thesection\quad #1}}

% ============================================================
% 第五部分：标题格式（方正五级阶梯）
% 加粗一律用 \fzht（黑体），不用 \textbf——见 CLAUDE.md 踩坑 18
% ============================================================

% 章标题：小标宋 + 深色，下方细横线
% 用 block 而非 hang——章标题是「第X章」+ 书名两行结构，hang 的
% 悬挂缩进会把中文标题挤成竖排（实测目录里"第一章章级结构"逐字竖排）
\titleformat{\chapter}[block]
    {\huge\fzxb\color{DarkColor}}
    {第\thechapter 章}{1em}{}[\vspace{-0.6em}\rule{\textwidth}{1.2pt}]

% 节标题：大标宋 + 主色
\titleformat{\section}[hang]
    {\Large\fzdbs\color{MainColor}}
    {\thesection}{1em}{}
\titlespacing{\section}{0pt}{20pt}{12pt}

% 小节标题：黑体
\titleformat{\subsection}
    {\large\fzht\color{SubColor}}
    {\thesubsection}{1em}{}
\titlespacing{\subsection}{1em}{14pt}{6pt}

% 小小节标题：楷体
\titleformat{\subsubsection}
    {\normalsize\fzkt\color{MainColor!80!black}}
    {\thesubsection}{1em}{}
\titlespacing{\subsubsection}{2em}{10pt}{4pt}

\titlespacing{\chapter}{0pt}{24pt}{20pt}
\setcounter{tocdepth}{2}

% 括号式小标题：\subhead{标题名}
\newcommand{\subhead}[1]{%
    \par\vspace{6pt}\noindent
    {\fzht\color{SubColor}（#1）}\hspace{0.5em}%
}

% ============================================================
% 第六部分：定理环境（章级编号）
%
% base.sty 已用 [section] 定义了 6 个定理环境，book 需要章级编号。
% amsthm 不支持把已存在环境的计数器层级从 [section] 改成 [chapter]，
% 因此用 \let…\relax 注销后以常用名重新声明，正文里仍写
% \begin{theorem} / \begin{definition} / \begin{remark}。
%
% ⚠️ 三个坑（均为实测踩出）：
%  1) 不要用 \renewcommand{\thetheorem}{...} 改编号——\thetheorem 是计数器
%     命令本身，覆盖后宏名会被当普通文本排进目录（实测目录出现字面量
%     "theorem 定理[chapter] definition[theorem] 定义…"）。
%  2) \newtheorem{env}[共享计数器]{标题} 的共享计数器写法只对
%     \newtheorem 有效；\renewtheorem 用它会报 Undefined control sequence。
%  3) \newtheorem 要求环境名未定义，base.sty 已占用的必须先 \let…\relax。
% ============================================================

% 公式编号改章级（base.sty 是 section 级，且对 chapter=0 做了回退）
\numberwithin{equation}{chapter}
\renewcommand{\theequation}{%
  \ifnum\value{chapter}=0\relax\arabic{equation}%
  \else\thechapter.\arabic{equation}\fi}

% 注销 base.sty 的 section 级定义（连同 \end… 才能重新声明）
\let\theorem\relax        \let\endtheorem\relax
\let\definition\relax     \let\enddefinition\relax
\let\proposition\relax    \let\endproposition\relax
\let\lemma\relax          \let\endlemma\relax
\let\corollary\relax      \let\endcorollary\relax
\let\example\relax        \let\endexample\relax
\let\remark\relax         \let\endremark\relax

\theoremstyle{plain}
\newtheorem{theorem}{定理}[chapter]
\theoremstyle{definition}
\newtheorem{definition}[theorem]{定义}
\newtheorem{proposition}[theorem]{命题}
\theoremstyle{plain}
\newtheorem{lemma}[theorem]{引理}
\newtheorem{corollary}[theorem]{推论}
\theoremstyle{remark}
\newtheorem{remark}{注}

% ============================================================
% 第七部分：6 种教学盒子
% 照 mathnotes 的 mdframed 模式——不引 tcolorbox（本机未装，
% 且与 mdframed 边框体系冲突，见 CLAUDE.md 踩坑 1）
% ============================================================

% 每个盒子：一条 \newmdenv 定边框配色 + 一层薄 \newenvironment 注入标签
\newmdenv[
  hidealllines=true,leftline=true,linecolor=keyline,linewidth=2.5pt,
  leftmargin=0pt,rightmargin=0pt,innerleftmargin=10pt,innerrightmargin=8pt,
  innertopmargin=6pt,innerbottommargin=6pt,backgroundcolor=keybg,
  skipabove=10pt,skipbelow=10pt,
]{mdfkeyconcept}
\newenvironment{keyconcept}{\begin{mdfkeyconcept}{\color{keyline}\fzht 核心概念：}}{\end{mdfkeyconcept}}

\newmdenv[
  hidealllines=true,leftline=true,linecolor=expline,linewidth=2.5pt,
  leftmargin=0pt,rightmargin=0pt,innerleftmargin=10pt,innerrightmargin=8pt,
  innertopmargin=6pt,innerbottommargin=6pt,backgroundcolor=expbg,
  skipabove=10pt,skipbelow=10pt,
]{mdfexamplebox}
\newenvironment{examplebox}{\begin{mdfexamplebox}{\color{expline}\fzht 例：}}{\end{mdfexamplebox}}

\newmdenv[
  hidealllines=true,leftline=true,linecolor=tipsline,linewidth=2.5pt,
  leftmargin=0pt,rightmargin=0pt,innerleftmargin=10pt,innerrightmargin=8pt,
  innertopmargin=6pt,innerbottommargin=6pt,backgroundcolor=tipsbg,
  skipabove=10pt,skipbelow=10pt,
]{mdftipbox}
\newenvironment{tipbox}{\begin{mdftipbox}{\color{tipsline}\fzht 小贴士：}}{\end{mdftipbox}}

\newmdenv[
  hidealllines=true,leftline=true,linecolor=warnline,linewidth=2.5pt,
  leftmargin=0pt,rightmargin=0pt,innerleftmargin=10pt,innerrightmargin=8pt,
  innertopmargin=6pt,innerbottommargin=6pt,backgroundcolor=warnbg,
  skipabove=10pt,skipbelow=10pt,
]{mdfwarningbox}
\newenvironment{warningbox}{\begin{mdfwarningbox}{\color{warnline}\fzht 注意：}}{\end{mdfwarningbox}}

\newmdenv[
  hidealllines=true,leftline=true,linecolor=pracline,linewidth=2.5pt,
  leftmargin=0pt,rightmargin=0pt,innerleftmargin=10pt,innerrightmargin=8pt,
  innertopmargin=6pt,innerbottommargin=6pt,backgroundcolor=pracbg,
  skipabove=10pt,skipbelow=10pt,
]{mdfpracticebox}
\newenvironment{practicebox}{\begin{mdfpracticebox}{\color{pracline}\fzht 练习：}}{\end{mdfpracticebox}}

\newmdenv[
  hidealllines=true,leftline=true,linecolor=ansline,linewidth=2.5pt,
  leftmargin=0pt,rightmargin=0pt,innerleftmargin=10pt,innerrightmargin=8pt,
  innertopmargin=6pt,innerbottommargin=6pt,backgroundcolor=ansbg,
  skipabove=10pt,skipbelow=10pt,
]{mdfanswerbox}
\newenvironment{answerbox}{\begin{mdfanswerbox}{\color{ansline}\fzht 解答：}}{\end{mdfanswerbox}}

% ============================================================
% 第八部分：旁注（右侧 margin）
% ============================================================

\newcommand{\harryopo@bookmarginfmt}{%
  \raggedright\footnotesize
  \setlength{\parskip}{2pt}\setlength{\lineskip}{1pt}
  \linespread{1.1}\selectfont
}

% \bianzhu[标签]{内容}
\newcommand{\bianzhu}[2][]{%
  \marginpar{\harryopo@bookmarginfmt
    \if\relax\detokenize{#1}\relax\else
      {\color{MainColor}\fzht #1}\\[4pt]
    \fi
    \fzfs #2}%
}

% \bianzhutu[标签]{图片路径}{图注}
\newcommand{\bianzhutu}[3][]{%
  \marginpar{\harryopo@bookmarginfmt
    \if\relax\detokenize{#1}\relax\else
      {\color{MainColor}\fzht #1}\\[4pt]
    \fi
    \includegraphics[width=0.9\marginparwidth]{#2}\\[4pt]
    \fzfs #3}%
}

% ============================================================
% 第九部分：目录美化
% ============================================================

\renewcommand{\contentsname}{目\quad 录}
\renewcommand{\partname}{第}
\renewcommand{\appendixname}{附\quad 录}
\renewcommand{\abstractname}{摘\quad 要}

\cfttoctitlefont{\hfill\LARGE\fzxb\color{DarkColor}}
\cftaftertoctitle{\par\vspace{6pt}\rule{\textwidth}{1.2pt}\par}

% 章级条目：小标宋、无点线
%
% ⚠️ 章标题在目录里被拉伸到全宽的根因（已读 tocloft.sty:380-400 定位）：
%   \l@chapter 把编号放进 \cftchapnumwidth 固定盒（默认 1.5em），
%   并用 \leftskip + \parfillskip 组成弹性行。ctexbook 的章编号是
%   "第X章" 三字中文，1.5em 装不下 → 溢出后中文标题的 glue 被拉伸，
%   表现为字距撑满整行（实测"第一章章级结构"）。
% 正解：把 numwidth 调大到能容纳"第X章"，并让编号盒内文字左对齐不拉伸。
\ctexset{chapter/number=\chinese{chapter}}
% tocloft 默认 \cftchapnumwidth=1.5em 装不下 ctex 的"第X章"三字编号；
% 章级默认 leader 是 \cftdotfill，但它排在编号盒之后，编号盒之前的
% \leftskip 才是被拉伸的那一段（实测"第一章章级结构"字距撑满整行）。
% 把编号盒设为自然宽度（1.8em 足够"第X章"）并保留点线 leader，
% 章条目即与节条目同样排布。
\setlength{\cftchapnumwidth}{1.8em}
\renewcommand{\cftchapfont}{\fzxb\color{DarkColor}}
\renewcommand{\cftchappagefont}{\normalfont\fzxb}
% 章级 leader 用 tocloft 自带的 \cftdotfill{\sep} 形式——
% 直接写 \renewcommand{\cftchapleader}{\cftdotfill} 会把 tagging socket
% 名当普通文本排进目录（实测出现 "u.u.u.…/toc/leaders" 字面量）。
\renewcommand{\cftchapleader}{\normalfont\cftdotfill{\cftchapdotsep}}
\renewcommand{\cftchapafterindent}{0pt}
\renewcommand{\cftsecfont}{\fzkt}
\renewcommand{\cftsecpagefont}{\normalfont}
\renewcommand{\cftsecleader}{\dotfill}
\renewcommand{\cftsubsecfont}{\normalfont\fzfs}
\renewcommand{\cftsubsecpagefont}{\normalfont}
\renewcommand{\cftsubsecleader}{\dotfill}
\renewcommand{\cftsecskip}{4pt}
\renewcommand{\cftsubsecskip}{2pt}

% ============================================================
% 第十部分：题注格式
% ============================================================

\DeclareCaptionFont{hrypbookcap}{\fzfs}
\DeclareCaptionLabelFormat{hrypbookzhlabel}{{\fzht #1 #2}\;}
\captionsetup{labelformat=hrypbookzhlabel, labelsep=quad,
              font={footnotesize,hrypbookcap}, skip=6pt}
\captionsetup[table]{position=bottom}

% ============================================================
% 第十一部分：书籍元信息命令
% ============================================================

\newcommand{\subtitle}[1]{\def\@subtitle{#1}}
\newcommand{\@subtitle}{}
\newcommand{\edition}[1]{\def\@edition{#1}}
\newcommand{\@edition}{}
\newcommand{\bookseries}[1]{\def\@bookseries{#1}}
\newcommand{\@bookseries}{}
\newcommand{\keywords}[1]{\def\@keywords{#1}}
\newcommand{\@keywords}{}
% \institute 由 report.cls 定义、base.sty 未提供，book 自带一份
% （report/slides 各自定义，base.sty 不含——不可依赖继承）
\newcommand{\institute}[1]{\def\@institute{#1}}
\newcommand{\@institute{}{}

\newcommand{\bookabstract}[1]{%
  \par\vspace{0.8em}\noindent
  {\fzht\color{MainColor}摘\quad 要：}#1\par\vspace{0.6em}}

\newcommand{\bookkeywords}[1]{%
  \par\noindent{\fzht\color{MainColor}关键词：}%
  {\fzfs #1}\par\vspace{0.8em}}

% ============================================================
% 第十二部分：封面
% ============================================================

\renewcommand{\maketitle}{%
  % ⚠️ 不要用 \begin{titlepage}——twoside 下它会先插入 2 张空白偶数页
  % （实测封面被挤到第 3 页）。改用 \begingroup…\endgroup + \newpage，
  % 封面即落在当前页（第 1 页），页数从 9 降到 7。
  \begingroup
  \thispagestyle{empty}%
  \pagenumbering{roman}%
  \setcounter{page}{1}%
  \centering
  \vspace*{3.2cm}
  {\zihao{4}\fzkt\color{SubColor}\@bookseries\par}
  \vspace{1.4cm}
  {\zihao{1}\fzxb\color{DarkColor}\@title\par}
  \ifx\@subtitle\@empty\else
    \vspace{0.7cm}
    {\zihao{4}\fzkt\color{MainColor}\@subtitle\par}
  \fi
  \vspace{2.4cm}
  {\zihao{3}\fzdbs\color{DarkColor}\@author\par}
  \ifx\@institute\@empty\else
    \vspace{0.5cm}
    {\zihao{5}\fzkt\color{SubColor}\@institute\par}
  \fi
  \vfill
  {\zihao{-4}\fzkt\color{SubColor}\@date\par}
  \par\endgroup\newpage%
  \global\let\maketitle\relax
}