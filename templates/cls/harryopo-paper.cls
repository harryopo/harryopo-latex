% ============================================================
% harryopo-paper.cls — harryopo 学术论文通用文档类 (v4.0)
% 风格：学术规范、简洁大气、功能完备
% 特性：单栏/双栏切换、跨栏排版、算法伪代码、栏平衡
%        标题=小标宋、作者=楷体、层级字体区分清晰
%        XITS 数学/英文/数字，仅蓝/黑色系
% ============================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{harryopo-paper}[2026/06/21 v4.0 harryopo Paper Template]

% ============================================================
% 第一部分：选项声明（仅 blue / dark）
% ============================================================

\def\harryopo@theme{blue}
\newif\if@twocolumnmode \@twocolumnmodefalse
\DeclareOption{twocolumn}{\@twocolumnmodetrue}
\newif\if@govmode \@govmodefalse
\DeclareOption{gov}{\@govmodetrue}
\DeclareOption{dark}{\def\harryopo@theme{dark}}
\DeclareOption{nomath}{\def\harryopo@nomath{1}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexart}}
\ProcessOptions\relax

\if@twocolumnmode
    \LoadClass[a4paper,11pt,twocolumn]{ctexart}
\else
    \LoadClass[a4paper,11pt]{ctexart}
\fi

% ============================================================
% 第二部分：依赖包加载
% ============================================================

\RequirePackage{harryopo-base}
\RequirePackage{dblfloatfix}

\if@twocolumnmode
    \RequirePackage{flushend}
\fi

\RequirePackage[ruled,vlined,linesnumbered]{algorithm2e}
\newcounter{chapter}
\renewcommand{\algorithmcfname}{算法}
\SetKwInput{KwIn}{输入}
\SetKwInput{KwOut}{输出}
\SetKwInput{KwData}{数据}
\SetKwInput{KwResult}{结果}
\SetKwProg{Fn}{函数}{}{}
\SetKwComment{Comment}{// }{}

% ============================================================
% 第三部分：页面布局
% ============================================================

\if@twocolumnmode
    \geometry{left=2.2cm, right=2.2cm, top=2.2cm, bottom=2.2cm,
              columnsep=0.8cm, headheight=15pt}
\else
    \geometry{left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm,
              headheight=15pt}
\fi

% ============================================================
% 第四部分：页眉页脚（无横线）
% ============================================================

% 正文页眉：左=日期 · 节标题（楷体），右=页码
\fancypagestyle{fancy}{
    \fancyhf{}
    \fancyhead[L]{\small\fzkt\@date\quad\ifx\leftmark\@empty\else\textperiodcentered\quad\leftmark\fi}
    \fancyhead[R]{\small\thepage}
    \renewcommand{\headrulewidth}{0pt}
}
% 首页页眉：左=日期，右=页码
\fancypagestyle{plain}{
    \fancyhf{}
    \fancyhead[L]{\small\fzkt\@date}
    \fancyhead[R]{\small\thepage}
    \renewcommand{\headrulewidth}{0pt}
}
\renewcommand{\sectionmark}[1]{\markboth{#1}{}}
\pagestyle{fancy}

% ============================================================
% 第五部分：正文标题层级
% ============================================================

% 隐藏 section/subsection/subsubsection 自动编号（不显示 0.1/0.2 等）
% convert.py 已用 \section* 系列；此处保险起见也覆盖手动写 \section 的情况
\renewcommand{\thesection}{}
\renewcommand{\thesubsection}{}
\renewcommand{\thesubsubsection}{}

% 一级标题 section：方正大标宋 + 黑色
\titleformat{\section}
    {\Large\fzdbs\bfseries}
    {}{0pt}{}
\titlespacing{\section}{0pt}{16pt}{10pt}

% 二级标题 subsection：方正黑体 + 黑色
\titleformat{\subsection}
    {\large\bfseries\fzht}
    {}{0pt}{}
\titlespacing{\subsection}{1em}{12pt}{6pt}

% 三级标题 subsubsection：方正楷体 + 黑色
\titleformat{\subsubsection}
    {\normalsize\fzkt\bfseries}
    {}{0pt}{}
\titlespacing{\subsubsection}{2em}{8pt}{4pt}

% 四级标题 paragraph：方正黑体 + 黑色（公文 ① 层级）
\renewcommand{\theparagraph}{}
\titleformat{\paragraph}
    {\normalsize\bfseries\fzht}
    {}{0pt}{}
\titlespacing{\paragraph}{2em}{6pt}{2pt}

% 括号式小标题：\subhead{标题名} → （标题名）黑体后接正文
% 注意：不再使用 \noindent，保证后续段落正常段首缩进 2 字符
\newcommand{\subhead}[1]{%
    \par\vspace{6pt}%
    {\bfseries\fzht\color{SubColor}（#1）}\hspace{0.5em}%
}

% ============================================================
% 第五部分半：GB/T 9704-2012 公文模式（\documentclass[gov]{harryopo-paper}）
% ============================================================
% 页边距：上37 下35 左28 右26 mm；正文三号仿宋（16pt）；行距 28 磅
%（baselineskip = 16pt × 1.2 × 1.46 ≈ 28pt，版心 225mm 恰排 22 行）
% 层级标题（GB/T 9704 惯例）：一、黑体 ｜（一）楷体 ｜ 1. 仿宋加粗 ｜ （1）仿宋
\if@govmode
    \geometry{left=2.8cm, right=2.6cm, top=3.7cm, bottom=3.5cm, headheight=15pt}
    \zihao{3}                       % 正文三号 16pt（仿宋，base.sty 已设 CJK 主字体）
    \linespread{1.46}\selectfont    % 28 磅行距
    % 文件标题：二号小标宋居中（覆盖 \maketitle）
    \renewcommand{\maketitle}{%
        \begin{center}
            {\zihao{2}\fzdbs\color{DarkColor}\@title\par}
            \vspace{0.6cm}
        \end{center}}
    % 层级标题覆盖（GB/T 9704 分级字体）
    \titleformat{\section}
        {\zihao{3}\fzht}
        {}{0pt}{}
    \titlespacing{\section}{0pt}{8pt}{4pt}
    \titleformat{\subsection}
        {\zihao{3}\fzkt}
        {}{0pt}{}
    \titlespacing{\subsection}{0pt}{4pt}{2pt}
    \titleformat{\subsubsection}
        {\zihao{3}\bfseries\fzfs}
        {}{0pt}{}
    \titlespacing{\subsubsection}{0pt}{2pt}{2pt}
    \titleformat{\paragraph}
        {\zihao{3}\fzfs}
        {}{0pt}{}
    \titlespacing{\paragraph}{0pt}{2pt}{0pt}
\fi

% ============================================================
% 第六部分：论文信息命令
% ============================================================

\newcommand{\fundproject}[1]{\def\@fundproject{#1}}
\newcommand{\@fundproject}{}
\newcommand{\authorbio}[1]{\def\@authorbio{#1}}
\newcommand{\@authorbio}{}

% ============================================================
% 第七部分：标题页（无横线）
% ============================================================

\renewcommand{\maketitle}{%
    \begin{center}
        {\huge\fzdbs\color{DarkColor}\@title\par}
        \vspace{0.7cm}
        {\Large\fzkt\@author\par}
        \ifx\@date\@empty\else
        \vspace{0.3cm}
        {\normalsize\fzfs\@date\par}
        \fi
        \vspace{0.5cm}
    \end{center}
}

% ============================================================
% 第八部分：摘要与关键词（缩进2em，标签=黑体，内容=楷体）
% ============================================================

\renewenvironment{abstract}{%
    \list{}{\leftmargin=2em \rightmargin=0em \topsep=0.5cm \parsep=0pt \itemsep=0pt}\item\relax
    {\bfseries\fzht 摘\quad 要：}%
    \fzkt
}{%
    \endlist
}

% 关键：必须用 \begingroup...\endgroup 包裹 \list...\endlist
% 因为 \list 是底层命令，会把 \parindent 改为 \listparindent(0pt)
% 而 \endlist 不恢复 \parindent，导致后续所有段落失去首行缩进
\newcommand{\keywords}[1]{%
    \begingroup
    \list{}{\leftmargin=2em \rightmargin=0em \topsep=0pt \parsep=0pt \itemsep=0pt}\item\relax
    {\bfseries\fzht 关键词：}\fzkt #1%
    \endlist
    \endgroup
    \setlength{\parindent}{2em}% 双保险：确保 \parindent 恢复
    \par\vspace{0.3cm}
}

% ============================================================
% 第九部分：跨栏排版（双栏模式）
% ============================================================

\newcommand{\maketitlewithabstract}{%
    \if@twocolumnmode
        % 用 \twocolumn[] 而非 strip 环境，避免与 booktabs 冲突
        \twocolumn[%
            \maketitle
            \begin{abstract}
                \@abstractcontent
            \end{abstract}
            \keywords{\@keywordscontent}
            \vspace{0.5cm}
        ]%
    \else
        \maketitle
        \begin{abstract}
            \@abstractcontent
        \end{abstract}
        \keywords{\@keywordscontent}
    \fi
}

\newcommand{\abstractcontent}[1]{\def\@abstractcontent{#1}}
\newcommand{\@abstractcontent}{}
\newcommand{\keywordscontent}[1]{\def\@keywordscontent{#1}}
\newcommand{\@keywordscontent}{}

% ============================================================
% 第十部分：跨栏浮动体
% ============================================================

\renewenvironment{figure*}[1][tbp]
    {\@dblfloat{figure}[#1]}
    {\end@dblfloat}

\renewenvironment{table*}[1][tbp]
    {\@dblfloat{table}[#1]}
    {\end@dblfloat}

% ============================================================
% 第十一部分：上标引用
% ============================================================

\newcommand{\upcite}[1]{\textsuperscript{\cite{#1}}}

% ============================================================
% 第十二部分：基金信息
% ============================================================

\newcommand{\printfunding}{%
    \ifdefined\@fundproject\relax
        \ifx\@fundproject\@empty\else
            \vspace{0.5cm}\par
            \begingroup
                \small
                \parindent=2em\relax
                \indent{\color{gray}\@fundproject}\par
            \endgroup
        \fi
    \fi
}

% ============================================================
% 第十三部分：作者简介
% ============================================================

\newcommand{\printauthorbio}{%
    \ifdefined\@authorbio\relax
        \ifx\@authorbio\@empty\else
            \vspace{0.5cm}\par
            \begingroup
                \bfseries
                \parindent=2em\relax
                \indent{\color{MainColor}作者简介：}\par
            \endgroup
            \begingroup
                \small
                \parindent=2em\relax
                \indent\@authorbio\par
            \endgroup
        \fi
    \fi
}

\endinput
