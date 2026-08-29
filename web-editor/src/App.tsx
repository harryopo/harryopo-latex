// App.tsx — harryopo-web 主界面（文件树 + 编辑 + 预览 + 导出 + 模板新建）
import { useCallback, useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { Editor } from './components/Editor'
import { Preview } from './components/Preview'
import { FileTree } from './components/FileTree'
import { TemplateModal } from './components/TemplateModal'

const API = ''

interface TreeNode {
  name: string
  path: string
  type: 'dir' | 'md'
  children?: TreeNode[]
}

interface ExportFile {
  name: string
  url: string
}

export default function App() {
  const [tree, setTree] = useState<TreeNode[]>([])
  const [current, setCurrent] = useState<string>('')
  const [md, setMd] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState('')
  const [exports, setExports] = useState<ExportFile[]>([])
  const [exporting, setExporting] = useState(false)
  const [tplOpen, setTplOpen] = useState(false)
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const refreshTree = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/tree`)
      const d = await r.json()
      setTree(d.tree || [])
    } catch {
      /* server 未启动 */
    }
  }, [])

  // 加载文档（path）
  const loadDoc = useCallback(async (path: string) => {
    try {
      const r = await fetch(`${API}/api/doc?path=${encodeURIComponent(path)}`)
      const d = await r.json()
      setMd(d.content ?? '')
      setCurrent(path)
      setExports([])
    } catch {
      /* ignore */
    }
  }, [])

  // 保存（debounce）
  const saveDoc = useCallback(async (path: string, content: string) => {
    setSaving(true)
    try {
      await fetch(`${API}/api/doc`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, content }),
      })
      setSavedAt(new Date().toLocaleTimeString())
    } finally {
      setSaving(false)
    }
  }, [])

  const handleChange = useCallback(
    (content: string) => {
      setMd(content)
      if (saveTimer.current) clearTimeout(saveTimer.current)
      saveTimer.current = setTimeout(() => {
        if (current) saveDoc(current, content)
      }, 600)
    },
    [current, saveDoc],
  )

  // 新建文档
  const newDoc = useCallback(async () => {
    const name = window.prompt('新文档名（含 .md，支持子目录如 报告/周报.md）')
    if (!name) return
    const r = await fetch(`${API}/api/file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: name }),
    })
    if (r.ok) {
      await refreshTree()
      loadDoc(name)
    } else {
      alert((await r.json()).error || '创建失败')
    }
  }, [refreshTree, loadDoc])

  // 删除文档
  const deleteDoc = useCallback(async (path: string) => {
    const r = await fetch(`${API}/api/file?path=${encodeURIComponent(path)}`, { method: 'DELETE' })
    if (r.ok) {
      await refreshTree()
      if (current === path) {
        setCurrent('')
        setMd(null)
      }
    }
  }, [refreshTree, current])

  // 导出
  const doExport = useCallback(async (format: string) => {
    if (!current) return
    setExporting(true)
    setExports([])
    try {
      const r = await fetch(`${API}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: current, format }),
      })
      const d = await r.json()
      if (d.ok) setExports(d.files)
      else alert(`导出失败：${d.log || ''}`)
    } catch (e) {
      alert(`导出请求失败：${e}`)
    } finally {
      setExporting(false)
    }
  }, [current])

  useEffect(() => {
    refreshTree()
  }, [refreshTree])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* 顶栏 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderBottom: '1px solid #d0d7de', background: '#f6f8fa' }}>
        <strong>harryopo-web</strong>
        <span style={{ flex: 1, color: '#57606a', fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {current || '（未打开文档）'}
        </span>
        <span style={{ color: saving ? '#0969da' : '#57606a', fontSize: 12 }}>
          {saving ? '保存中…' : savedAt ? `已保存 ${savedAt}` : ''}
        </span>
        <button onClick={() => setTplOpen(true)} style={btnStyle}>从模板新建</button>
        <button onClick={() => doExport('word')} disabled={exporting} style={btnStyle}>
          {exporting ? '导出中…' : '导出 Word'}
        </button>
        <button onClick={() => doExport('paper')} disabled={exporting} style={btnStyle}>
          导出 PDF
        </button>
        <button onClick={() => doExport('word,paper')} disabled={exporting} style={btnStyle}>
          全部
        </button>
      </div>

      {/* 主区：文件树 | 编辑 | 预览 */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div style={{ width: 200, borderRight: '1px solid #d0d7de', overflow: 'auto', background: '#f6f8fa' }}>
          <FileTree
            tree={tree}
            current={current}
            onOpen={loadDoc}
            onNew={newDoc}
            onDelete={deleteDoc}
          />
        </div>
        <div style={{ flex: 1, borderRight: '1px solid #d0d7de' }}>
          <Editor value={md} onChange={handleChange} />
        </div>
        <div style={{ flex: 1, overflow: 'auto', background: '#fff' }}>
          <Preview md={md ?? ''} />
        </div>
      </div>

      {/* 导出产物 */}
      {exports.length > 0 && (
        <div style={{ padding: '8px 16px', borderTop: '1px solid #d0d7de', background: '#f6f8fa' }}>
          导出完成：
          {exports.map((f) => (
            <a key={f.name} href={`${API}${f.url}`} download={f.name} style={{ marginRight: 12, color: '#0969da' }}>
              {f.name}
            </a>
          ))}
        </div>
      )}

      {/* 从模板新建 */}
      {tplOpen && <TemplateModal onClose={() => setTplOpen(false)} />}
    </div>
  )
}

const btnStyle: CSSProperties = {
  padding: '5px 10px',
  border: '1px solid #d0d7de',
  background: '#fff',
  borderRadius: 4,
  cursor: 'pointer',
}
