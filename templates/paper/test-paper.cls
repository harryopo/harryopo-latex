\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{test-paper}[2026/06/22 test]
\def\harryopo@theme{blue}
\newif\if@twocolumnmode \@twocolumnmodetrue
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexart}}
\ProcessOptions\relax
\LoadClass[a4paper,11pt,twocolumn]{ctexart}
\RequirePackage{harryopo-base}
\RequirePackage{dblfloatfix}
\RequirePackage{cuted}
\RequirePackage{flushend}
\endinput
