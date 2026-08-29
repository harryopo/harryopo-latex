// Preview.tsx — Markdown 实时预览（markdown-it + KaTeX）
import { useMemo } from 'react'
import MarkdownIt from 'markdown-it'
import katex from 'katex'

const mdIt = new MarkdownIt({ html: true, linkify: true, breaks: true })

/** 公式预处理：$$...$$ 块级 + $...$ 行内 → KaTeX HTML */
function renderWithMath(src: string): string {
  // 块级 $$...$$（单行或多行）
  let out = src.replace(/\$\$([\s\S]+?)\$\$/g, (_m, latex: string) =>
    katex.renderToString(latex.trim(), { displayMode: true, throwOnError: false }),
  )
  // 行内 $...$（避免与 $$ 残留冲突）
  out = out.replace(/(^|[^$])\$([^$\n]+?)\$(?![^$]*\$)/g, (_m, pre: string, latex: string) =>
    pre + katex.renderToString(latex.trim(), { displayMode: false, throwOnError: false }),
  )
  return mdIt.render(out)
}

export function Preview({ md }: { md: string }) {
  const html = useMemo(() => renderWithMath(md), [md])
  return (
    <div
      className="markdown-preview"
      style={{ padding: '16px 24px', fontSize: 15, lineHeight: 1.7 }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
