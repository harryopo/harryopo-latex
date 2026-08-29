// raw.ts — RawBlock / RawInline 兜底节点（借鉴 Oleafly packages/wysiwyg）
//
// 原则（呼应"AI 只产结构化数据"铁律）：语义节点只覆盖已知结构，
// 未识别结构（LaTeX 片段、特殊语法等）原样保存在 attrs.source，
// 可视化只做展示，序列化时原样回写，保证内容零丢失。
import { mergeAttributes, Node } from '@tiptap/core'
import { ReactNodeViewRenderer, type NodeViewProps } from '@tiptap/react'
import type { CSSProperties } from 'react'

// ---------- RawBlock：块级兜底 ----------

export const RawBlock = Node.create({
  name: 'rawBlock',
  group: 'block',
  atom: true,

  addAttributes() {
    return {
      source: { default: '' },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="raw-block"]' }]
  },

  renderHTML({ HTMLAttributes, node }) {
    return [
      'div',
      mergeAttributes(HTMLAttributes, { 'data-type': 'raw-block' }),
      node.attrs.source,
    ]
  },

  renderMarkdown({ node }) {
    return node.attrs?.source || ''
  },

  addNodeView() {
    return ReactNodeViewRenderer(RawBlockView)
  },
})

// ---------- RawInline：行内兜底 ----------

export const RawInline = Node.create({
  name: 'rawInline',
  group: 'inline',
  inline: true,
  atom: true,

  addAttributes() {
    return {
      source: { default: '' },
    }
  },

  parseHTML() {
    return [{ tag: 'span[data-type="raw-inline"]' }]
  },

  renderHTML({ HTMLAttributes, node }) {
    return [
      'span',
      mergeAttributes(HTMLAttributes, { 'data-type': 'raw-inline' }),
      node.attrs.source,
    ]
  },

  renderMarkdown(node: { attrs?: { source?: string } }) {
    return node.attrs?.source || ''
  },
})

// ---------- NodeView（MVP 只读展示） ----------

function RawBlockView(props: NodeViewProps) {
  const source = props.node.attrs.source || ''
  const preview = source.length > 120 ? source.slice(0, 120) + '…' : source
  return <div style={RAW_STYLE}>{preview}</div>
}

const RAW_STYLE: CSSProperties = {
  margin: '0.5em 0',
  padding: '0.4em 0.6em',
  background: '#f6f8fa',
  borderLeft: '3px solid #c9d1d9',
  fontFamily: 'monospace',
  fontSize: '0.85em',
  whiteSpace: 'pre-wrap',
  color: '#57606a',
}
