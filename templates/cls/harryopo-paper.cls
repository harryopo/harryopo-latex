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

% 使用基础包中的统一页眉配置
\harryopo@setup@header{sectionmark}

% ============================================================
% 第五部分：正文标题层级
% ============================================================

% 一级标题 section：方正大标宋 + 蓝色
\titleformat{\section}
    {\Large\fzdbs\color{MainColor}}
    {\rmfamily\bfseries\thesection}{1em}{}
\titlespacing{\section}{0pt}{16pt}{10pt}

% 二级标题 subsection：黑体 + 辅色
\titleformat{\subsection}
    {\large\bfseries\color{SubColor}}
    {\rmfamily\bfseries\thesubsection}{1em}{}
\titlespacing{\subsection}{1em}{12pt}{6pt}

% 三级标题 subsubsection：方正楷体 + 略深辅色
\titleformat{\subsubsection}
    {\normalsize\fzkt\color{MainColor!80!black}}
    {\rmfamily\bfseries\thesubsubsection}{1em}{}
\titlespacing{\subsubsection}{2em}{8pt}{4pt}

% 括号式小标题：\subhead{标题名} → （标题名）黑体后接正文
\newcommand{\subhead}[1]{%
    \par\vspace{6pt}\noindent
    {\bfseries\fzht\color{SubColor}（#1）}\hspace{0.5em}%
}

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
        {\huge\fzxb\color{DarkColor}\@title\par}
        \vspace{0.8cm}
        {\large\fzkt\@author\par}
        \vspace{0.6cm}
    \end{center}
}

% ============================================================
% 第八部分：摘要与关键词（缩进2em，标签=黑体，内容=楷体）
% ============================================================

\renewenvironment{abstract}{%
    \list{}{\leftmargin=2em \rightmargin=0em \topsep=0.5cm \parsep=0pt \itemsep=0pt}\item\relax
    {\fzht\color{MainColor} 摘\quad 要：}%
    \fzkt
}{%
    \endlist
}

\newcommand{\keywords}[1]{%
    \list{}{\leftmargin=2em \rightmargin=0em \topsep=0pt \parsep=0pt \itemsep=0pt}\item\relax
    {\fzht\color{MainColor} 关键词：}\fzkt #1%
    \endlist
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
            \vspace{0.5cm}
            \noindent{\small\color{gray}\@fundproject\par}
        \fi
    \fi
}

% ============================================================
% 第十三部分：作者简介
% ============================================================

\newcommand{\printauthorbio}{%
    \ifdefined\@authorbio\relax
        \ifx\@authorbio\@empty\else
            \vspace{0.5cm}
            \noindent{\bfseries\color{MainColor} 作者简介：}\par
            \noindent{\small\@authorbio\par}
        \fi
    \fi
}

\endinput
