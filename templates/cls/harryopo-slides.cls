%%
%% harryopo-slides.cls — harryopo 演示文稿文档类（PDF 交付）
%% 基于 ctexbeamer：学术答辩(blue) / 作品路演(dark) / 商务汇报(plain) 三主题
%% 编译：xelatex ×2，cwd 须为 templates/ 子目录（字体 Path=../fonts/ 约定，同 base.sty）
%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{harryopo-slides}[2026/09/18 v1.0 harryopo slides (ctexbeamer, blue/dark/plain)]

% ============================================================
% 主题选项：blue（默认）/ dark / plain；其余选项透传 ctexbeamer
% 布尔开关而非字符串比较：\ifstrequal 不展开宏参数（实测踩坑）
% ============================================================
\newif\ifhrypslides@dark
\newif\ifhrypslides@plain
\DeclareOption{dark}{\hrypslides@darktrue}
\DeclareOption{plain}{\hrypslides@plaintrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexbeamer}}
\ProcessOptions\relax

\LoadClass[aspectratio=169,11pt]{ctexbeamer}

% ============================================================
% 字体（方正内嵌，相对编译 cwd 的 ../fonts/，与 base.sty 同款语法）
%   正文 书宋 · 标题 黑体 · 大标题 小标宋 · 数学 XITS Math
% beamer 默认强制 sans，这里恢复 roman 正文（中文书宋更适合阅读）
% ============================================================
\usefonttheme{professionalfonts}
\setCJKmainfont[
    Extension = .TTF,
    BoldFont = FZHTJW,
    ItalicFont = FZKTJW,
    Path = ../fonts/
]{FZSSJW}
\setCJKsansfont[
    Extension = .TTF,
    Path = ../fonts/
]{FZHTJW}
\newCJKfontfamily\hrypxb{FZXBSJW}[Extension=.TTF, Path=../fonts/]
\newCJKfontfamily\hrypht{FZHTJW}[Extension=.TTF, Path=../fonts/]
\newCJKfontfamily\hrypkai{FZKTJW}[Extension=.TTF, Path=../fonts/]
\newCJKfontfamily\hrypfs{FZFSJW}[Extension=.TTF, Path=../fonts/]
% 与 base.sty 同名快捷命令（声明式，{\fzht 文字} 分组调用）——convert.py 行内转换复用
\providecommand{\fzht}{\hrypht}
\providecommand{\fzkt}{\hrypkai}
\providecommand{\fzfs}{\hrypfs}
\providecommand{\fzxb}{\hrypxb}
\providecommand{\fzdbs}{\hrypxb}
\AtBeginDocument{\renewcommand{\familydefault}{\rmdefault}\selectfont}
\setmainfont{XITS}[Extension=.otf, UprightFont=*-Regular, BoldFont=*-Bold,
                  ItalicFont=*-Italic, Path=../fonts/]
\usepackage{unicode-math}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{multirow}
\setmathfont{XITSMath}[
    Extension = .otf,
    UprightFont = *-Regular,
    BoldFont = *-Bold,
    Path = ../fonts/
]

% ============================================================
% 主题色板（色值与 harryopo-base.sty 完全一致，保证全家桶同一血统）
% ============================================================
\definecolor{MainColor}{HTML}{1A365D}
\definecolor{SubColor}{HTML}{2B6CB0}
\definecolor{SmallColor}{HTML}{4299E1}
\definecolor{TinyColor}{HTML}{EBF8FF}
\definecolor{DarkColor}{HTML}{1A202C}
\definecolor{AccentColor}{HTML}{C53030}
\definecolor{InkColor}{HTML}{111827}
\definecolor{MuteColor}{HTML}{6B7280}
\definecolor{PaperColor}{HTML}{FFFFFF}
\definecolor{GoldColor}{HTML}{E69A2D}

\ifhrypslides@dark
    % 深色路演：黑底白字（投影场景）
    \definecolor{DarkAccentColor}{HTML}{805AD5}
    \setbeamercolor{normal text}{bg=DarkColor, fg=PaperColor}
    \setbeamercolor{alerted text}{fg=GoldColor}
    \setbeamercolor{structure}{fg=DarkAccentColor}
    \setbeamercolor{frametitle}{fg=PaperColor, bg=DarkColor}
    \setbeamercolor{title}{fg=PaperColor}
    \setbeamercolor{subtitle}{fg=DarkAccentColor}
    \setbeamercolor{author}{fg=PaperColor}
    \setbeamercolor{date}{fg=MuteColor}
    \setbeamercolor{block title}{use=structure, fg=PaperColor, bg=DarkAccentColor}
    \setbeamercolor{block body}{fg=PaperColor, bg=DarkColor}
    \setbeamercolor{footline}{fg=MuteColor}
    \definecolor{FrameLineColor}{HTML}{805AD5}
\else\ifhrypslides@plain
    % 极简商务：黑白灰 + 朱红点缀
    \setbeamercolor{normal text}{bg=PaperColor, fg=InkColor}
    \setbeamercolor{alerted text}{fg=AccentColor}
    \setbeamercolor{structure}{fg=InkColor}
    \setbeamercolor{frametitle}{fg=InkColor, bg=PaperColor}
    \setbeamercolor{title}{fg=InkColor}
    \setbeamercolor{subtitle}{fg=MuteColor}
    \setbeamercolor{author}{fg=InkColor}
    \setbeamercolor{date}{fg=MuteColor}
    \setbeamercolor{block title}{fg=PaperColor, bg=InkColor}
    \setbeamercolor{block body}{fg=InkColor, bg=InkColor!4}
    \setbeamercolor{footline}{fg=MuteColor}
    \definecolor{FrameLineColor}{HTML}{111827}
\else
    % blue 学术（默认）：藏蓝主色白底
    \setbeamercolor{normal text}{bg=PaperColor, fg=InkColor}
    \setbeamercolor{alerted text}{fg=AccentColor}
    \setbeamercolor{structure}{fg=SubColor}
    \setbeamercolor{frametitle}{fg=MainColor, bg=PaperColor}
    \setbeamercolor{title}{fg=MainColor}
    \setbeamercolor{subtitle}{fg=SubColor}
    \setbeamercolor{author}{fg=InkColor}
    \setbeamercolor{date}{fg=MuteColor}
    \setbeamercolor{block title}{use=structure, fg=PaperColor, bg=SubColor}
    \setbeamercolor{block body}{fg=InkColor, bg=TinyColor}
    \setbeamercolor{footline}{fg=MuteColor}
    \definecolor{FrameLineColor}{HTML}{2B6CB0}
\fi\fi

% ============================================================
% 字号与字形：标题黑体、封面题小标宋
% ============================================================
\setbeamerfont{title}{size=\huge, family=\hrypxb, series=\bfseries}
\setbeamerfont{subtitle}{size=\large, family=\hrypkai}
\setbeamerfont{author}{size=\normalsize, family=\hrypkai}
\setbeamerfont{date}{size=\small}
\setbeamerfont{frametitle}{size=\Large, family=\hrypht, series=\bfseries}
\setbeamerfont{block title}{size=\normalsize, family=\hrypht, series=\bfseries}
\setbeamerfont{footline}{size=\tiny}

% ============================================================
% 版式：frame 标题左置 + 彩色下划线；页脚 左短题 · 右页码；圆角 block
% ============================================================
\setbeamertemplate{frametitle}{%
    \nointerlineskip%
    \begin{beamercolorbox}[wd=\paperwidth, leftskip=0.55cm, rightskip=0.55cm, sep=0.3cm, left]{frametitle}%
        \usebeamerfont*{frametitle}\usebeamercolor[fg]{frametitle}%
        \insertframetitle\hfill{\footnotesize\usebeamercolor[fg]{structure}\insertframenumber/\inserttotalframenumber}%
    \end{beamercolorbox}%
    \nointerlineskip{\color{FrameLineColor}\rule{\paperwidth}{1.2pt}}%
}
\setbeamertemplate{footline}{%
    \leavevmode\hbox to \paperwidth{%
        \hspace{0.55cm}{\color{MuteColor}\tiny\quad\insertshorttitle}%
        \hfill%
        \hspace{0.55cm}{\color{MuteColor}\tiny\insertframenumber\,/\,\inserttotalframenumber}\quad%
    }%
    \vskip2pt%
}
\setbeamertemplate{itemize items}[circle]
\setbeamertemplate{enumerate items}[default]
\setbeamertemplate{blocks}[rounded][shadow=false]
\setbeamertemplate{navigation symbols}{}
\setbeamersize{text margin left=0.9cm, text margin right=0.9cm}

% 封面：留白 + 主色细线
\setbeamertemplate{title page}{%
    \vbox{}\vskip-2ex%
    \vfill
    \begin{center}
        {\usebeamerfont{title}\usebeamercolor[fg]{title}\inserttitle\par}%
        \vskip1.2em%
        {\color{FrameLineColor}\rule{0.28\paperwidth}{1.6pt}}\par%
        \vskip1em%
        {\usebeamerfont{subtitle}\usebeamercolor[fg]{subtitle}\insertsubtitle\par}%
        \vskip2.5em%
        {\usebeamerfont{author}\usebeamercolor[fg]{author}\insertauthor\par}%
        \vskip1.2em%
        {\usebeamerfont{institute}\usebeamercolor[fg]{date}\insertinstitute\par}%
        \vskip0.8em%
        {\usebeamerfont{date}\usebeamercolor[fg]{date}\insertdate\par}%
    \end{center}
    \vfill
}

% 目录与节页：紧凑、主色编号
\setbeamertemplate{section in toc}{%
    {\color{structure.fg}\inserttocsectionnumber.}\ \inserttocsection\par}
\setbeamertemplate{subsection in toc}{%
    \hspace{1.2em}{\color{MuteColor}\bullet}\ \inserttocsubsection\par}

% 演讲者备注在 note 页正常排版（）
\mode<handout>{%
    \setbeameroption{show notes on second screen}
}

\endinput
