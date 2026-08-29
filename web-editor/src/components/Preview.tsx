// Preview.tsx — Markdown 实时预览（markdown-it + KaTeX + mermaid）
import { useEffect, useMemo, useRef } from 'react'
import MarkdownIt from 'markdown-it'
import katex from 'katex'
import mermaid from 'mermaid'

const mdIt = new MarkdownIt({ html: true, linkify: true, breaks: true })

/** 公式预处理：$$...$$ 块级 + $...$ 行内 → KaTeX HTML */
function renderWithMath(src: string): string {
  let out = src.replace(/\$\$([\s\S]+?)\$\$/g, (_m, latex: string) =>
    katex.renderToString(latex.trim(), { displayMode: true, throwOnError: false }),
  )
  out = out.replace(/(^|[^$])\$([^$\n]+?)\$(?![^$]*\$)/g, (_m, pre: string, latex: string) =>
    pre + katex.renderToString(latex.trim(), { displayMode: false, throwOnError: false }),
  )
  return mdIt.render(out)
}

export function Preview({ md }: { md: string }) {
  const html = useMemo(() => renderWithMath(md), [md])
  const ref = useRef<HTMLDivElement>(null)

  // mermaid 渲染（预览中的 ```mermaid 代码块）
  useEffect(() => {
    if (!ref.current) return
    try {
      mermaid.initialize({ startOnLoad: false, theme: 'default' })
      mermaid.run({ nodes: Array.from(ref.current.querySelectorAll('.language-mermaid')) })
    } catch {
      /* 渲染失败时保留源码 */
    }
  }, [html])

  return (
    <div
      ref={ref}
      className="markdown-preview"
      style={{ padding: '16px 24px', fontSize: 15, lineHeight: 1.7 }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
