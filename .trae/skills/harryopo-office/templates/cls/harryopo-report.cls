% ============================================================
% harryopo-report.cls — harryopo 学术报告通用文档类 (v4.0)
% 风格：正式、结构清晰、层级分明
% 特性：封面页、目录、章节结构、摘要
%        字体体系与论文模板一致，无需横线，仅蓝/黑色系
% ============================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{harryopo-report}[2026/06/21 v4.0 harryopo Report Template]

% ============================================================
% 第一部分：选项声明（仅 blue / dark）
% ============================================================

\def\harryopo@theme{blue}
\DeclareOption{dark}{\def\harryopo@theme{dark}}
\DeclareOption{nomath}{\def\harryopo@nomath{1}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexrep}}
\ProcessOptions\relax

\LoadClass[a4paper,12pt]{ctexrep}

% ============================================================
% 第二部分：依赖包加载
% ============================================================

\RequirePackage{harryopo-base}
\RequirePackage{enumitem}
\setlist{nosep,leftmargin=2em,itemsep=2pt,topsep=4pt,partopsep=0pt}

% 报告常用
\RequirePackage{tocloft}
\RequirePackage[titletoc]{appendix}

% ============================================================
% 第三部分：页面布局
% ============================================================

\geometry{left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm, headheight=15pt}

% ============================================================
% 第四部分：页眉页脚（无横线）
% ============================================================

% 使用基础包中的统一页眉配置
\harryopo@setup@header{chaptermark}
% 报告模板覆盖章节标记格式（在统一配置之后，否则会被覆盖）
\renewcommand{\chaptermark}[1]{\markboth{第\thechapter 章\quad #1}{}}

% ============================================================
% 第五部分：章标题格式
% ============================================================

% 章标题：大号小标宋 + 深色
\titleformat{\chapter}[hang]
    {\huge\fzxb\color{DarkColor}}
    {第\thechapter 章}{1em}{}
\titlespacing{\chapter}{0pt}{20pt}{16pt}

% 节标题：方正大标宋 + 蓝色
\titleformat{\section}
    {\Large\fzdbs\color{MainColor}}
    {\thesection}{1em}{}
\titlespacing{\section}{0pt}{16pt}{10pt}

% 小节标题：黑体 + 辅色
\titleformat{\subsection}
    {\large\bfseries\color{SubColor}}
    {\thesubsection}{1em}{}
\titlespacing{\subsection}{1em}{12pt}{6pt}

% 小小节标题：方正楷体
\titleformat{\subsubsection}
    {\normalsize\fzkt\color{MainColor!80!black}}
    {\thesubsubsection}{1em}{}
\titlespacing{\subsubsection}{2em}{8pt}{4pt}

% 括号式小标题：\subhead{标题名}
\newcommand{\subhead}[1]{%
    \par\vspace{6pt}\noindent
    {\bfseries\fzht\color{SubColor}（#1）}\hspace{0.5em}%
}

% ============================================================
% 第六部分：报告信息命令
% ============================================================

\newcommand{\subtitle}[1]{\def\@subtitle{#1}}
\newcommand{\@subtitle}{}
\newcommand{\institute}[1]{\def\@institute{#1}}
\newcommand{\@institute}{}
\newcommand{\fundproject}[1]{\def\@fundproject{#1}}
\newcommand{\@fundproject}{}

% ============================================================
% 第七部分：封面
% ============================================================

\renewcommand{\maketitle}{%
    \begin{titlepage}
        \centering
        \vspace*{3cm}

        % 报告标题：超大号小标宋
        {\Huge\fzxb\color{DarkColor}\@title\par}

        \ifdefined\@subtitle\relax
            \ifx\@subtitle\@empty\else
                \vspace{0.8cm}
                {\Large\fzkt\color{SubColor}\@subtitle\par}
            \fi
        \fi

        \vspace{2cm}

        % 作者：楷体
        {\large\fzkt\@author\par}

        \vspace{0.5cm}

        % 机构
        \ifdefined\@institute\relax
            \ifx\@institute\@empty\else
                {\normalsize\fzfs\color{gray}\@institute\par}
            \fi
        \fi

        \vspace{1cm}

        % 日期
        {\normalsize\fzfs\color{gray}\@date\par}

        \vfill

    \end{titlepage}
}

% ============================================================
% 第八部分：摘要（居中标题，缩进2em，标签=黑体，内容=楷体）
% ============================================================

\renewenvironment{abstract}{%
    \clearpage
    \thispagestyle{plain}
    \vspace*{2cm}
    \begin{center}
    {\LARGE\fzxb\color{DarkColor} 摘\quad 要\par}
    \end{center}
    \addcontentsline{toc}{chapter}{摘要}
    \vspace{0.8cm}
    \fzkt
    \list{}{\leftmargin=2em \rightmargin=0em \topsep=0pt \parsep=0pt \itemsep=0pt}\item\relax
}{%
    \endlist
    \clearpage
}

% ============================================================
% 第九部分：引言命令
% ============================================================

\newcommand{\introduction}{%
    \clearpage
    \thispagestyle{plain}
    \vspace*{2cm}
    \begin{center}
    {\LARGE\fzxb\color{DarkColor} 引\quad 言\par}
    \end{center}
    \addcontentsline{toc}{chapter}{引言}
    \vspace{0.8cm}
}

% ============================================================
% 第十部分：目录配置
% ============================================================

\renewcommand{\contentsname}{目\quad 录}
\renewcommand{\cfttoctitlefont}{\hfill\LARGE\fzxb\color{DarkColor}}
\renewcommand{\cftaftertoctitle}{\hfill}
\renewcommand{\cftchapfont}{\large\fzht}
\renewcommand{\cftsecfont}{\large}
\renewcommand{\cftsubsecfont}{\large}
\renewcommand{\cftchappagefont}{\large}
\renewcommand{\cftdotsep}{1}

% --- 插图/表格目录融入目录（降级为节标题） ---
\let\harryopo@oldlistoffigures\listoffigures
\renewcommand{\listoffigures}{%
    \section*{插图目录}%
    \addcontentsline{toc}{section}{插图目录}%
    \@starttoc{lof}%
}
\let\harryopo@oldlistoftables\listoftables
\renewcommand{\listoftables}{%
    \section*{表格目录}%
    \addcontentsline{toc}{section}{表格目录}%
    \@starttoc{lot}%
}

% 目录后强制分页（含插图/表格目录）
\let\harryopo@oldtableofcontents\tableofcontents
\renewcommand{\tableofcontents}{%
    \harryopo@oldtableofcontents
    \bigskip
    \listoffigures
    \bigskip
    \listoftables
    \clearpage
}

% ============================================================
% 第十一部分：参考文献
% ============================================================

\newcommand{\bibfile}[1]{\def\@bibfile{#1}}
\def\@bibfile{references}

\newcommand{\printbib}{%
    \bibliographystyle{unsrt}
    \bibliography{\@bibfile}
}

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

\endinput
