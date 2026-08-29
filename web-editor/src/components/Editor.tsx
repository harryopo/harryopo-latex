// Editor.tsx — TipTap 编辑器（harryopo MD 双向）
import { useEffect, useMemo, useRef } from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import { editorExtensions } from '../lib/extensions'
import { createManager, editorToMd, loadMdIntoEditor } from '../lib/md'
import { Toolbar } from './Toolbar'

interface EditorProps {
  /** 外部传入的 MD 内容（首次/切换文档时加载） */
  value: string | null
  /** 编辑器内容变化（MD）回调 */
  onChange: (md: string) => void
}

export function Editor({ value, onChange }: EditorProps) {
  const manager = useMemo(() => createManager(editorExtensions), [])
  const lastSyncedRef = useRef<string | null>(null)

  const editor = useEditor({
    extensions: editorExtensions,
    content: '',
    onUpdate: ({ editor }) => {
      const md = editorToMd(editor)
      // 标记已同步（防回环：编辑器产出 → onChange → value → 不再重载）
      lastSyncedRef.current = md
      onChange(md)
    },
  })

  // 外部 value 变化（文档切换/首次）→ 加载进编辑器（仅当与上次同步值不同）
  useEffect(() => {
    if (editor && value != null && lastSyncedRef.current !== value) {
      lastSyncedRef.current = value
      loadMdIntoEditor(editor, manager, value)
    }
  }, [value, editor, manager])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar editor={editor} />
      <div style={{ flex: 1, overflow: 'auto', padding: '0 16px' }}>
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
