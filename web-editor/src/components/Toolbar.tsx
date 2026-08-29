// Toolbar.tsx — 工具栏（标题/粗体/斜体/列表/引用/公式/表格/图片）
import type { Editor } from '@tiptap/react'

interface ToolbarProps {
  editor: Editor | null
}

export function Toolbar({ editor }: ToolbarProps) {
  if (!editor) return null

  const btn = (label: string, onClick: () => void, active = false) => (
    <button
      type="button"
      onClick={onClick}
      style={{
        padding: '4px 8px',
        marginRight: 4,
        border: active ? '1px solid #0969da' : '1px solid #d0d7de',
        background: active ? '#ddf4ff' : '#fff',
        borderRadius: 4,
        cursor: 'pointer',
        fontSize: 13,
      }}
    >
      {label}
    </button>
  )

  return (
    <div style={{ padding: '8px', borderBottom: '1px solid #d0d7de', background: '#f6f8fa' }}>
      {btn('H1', () => editor.chain().focus().toggleHeading({ level: 1 }).run(),
        editor.isActive('heading', { level: 1 }))}
      {btn('H2', () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
        editor.isActive('heading', { level: 2 }))}
      {btn('H3', () => editor.chain().focus().toggleHeading({ level: 3 }).run(),
        editor.isActive('heading', { level: 3 }))}
      {btn('B', () => editor.chain().focus().toggleBold().run(), editor.isActive('bold'))}
      {btn('I', () => editor.chain().focus().toggleItalic().run(), editor.isActive('italic'))}
      {btn('列表', () => editor.chain().focus().toggleBulletList().run(),
        editor.isActive('bulletList'))}
      {btn('引用', () => editor.chain().focus().toggleBlockquote().run(),
        editor.isActive('blockquote'))}
      {btn('公式', () => {
        editor.chain().focus().insertBlockMath({ latex: 'x^2' }).run()
      })}
      {btn('表格', () => {
        editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
      })}
      {btn('图片', () => {
        const url = window.prompt('图片 URL')
        if (url) editor.chain().focus().setImage({ src: url }).run()
      })}
    </div>
  )
}
