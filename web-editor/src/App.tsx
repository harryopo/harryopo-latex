// App.tsx — harryopo-web 主界面（文档管理 + 编辑 + 预览 + 导出）
import { useCallback, useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { Editor } from './components/Editor'
import { Preview } from './components/Preview'

const API = ''

interface ExportFile {
  name: string
  url: string
}

export default function App() {
  const [docs, setDocs] = useState<string[]>([])
  const [current, setCurrent] = useState<string>('')
  const [md, setMd] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState<string>('')
  const [exports, setExports] = useState<ExportFile[]>([])
  const [exporting, setExporting] = useState(false)
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // 文档列表
  const refreshDocs = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/docs`)
      const data = await r.json()
      setDocs(data.docs || [])
      if (!current && data.docs?.length) {
        const first = data.docs[0].replace(/\.md$/, '')
        setCurrent(first)
        loadDoc(first)
      }
    } catch {
      /* server 未启动时静默 */
    }
  }, [current])

  // 加载文档
  const loadDoc = useCallback(async (name: string) => {
    try {
      const r = await fetch(`${API}/api/doc?name=${encodeURIComponent(name)}`)
      const data = await r.json()
      setMd(data.content ?? '')
      setCurrent(name)
      setExports([])
    } catch {
      /* ignore */
    }
  }, [])

  // 保存（debounce 600ms）
  const saveDoc = useCallback(async (name: string, content: string) => {
    setSaving(true)
    try {
      await fetch(`${API}/api/doc`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, content }),
      })
      setSavedAt(new Date().toLocaleTimeString())
    } finally {
      setSaving(false)
    }
  }, [])

  // 编辑器变化 → debounce 保存
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
  const newDoc = useCallback(() => {
    const name = window.prompt('新文档名（不含 .md）')
    if (!name) return
    setCurrent(name)
    setMd('# 新文档\n\n## 一、\n\n正文。')
    setExports([])
  }, [])

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
      const data = await r.json()
      if (data.ok) setExports(data.files)
      else alert(`导出失败：${data.log || ''}`)
    } catch (e) {
      alert(`导出请求失败：${e}`)
    } finally {
      setExporting(false)
    }
  }, [current])

  useEffect(() => {
    refreshDocs()
  }, [refreshDocs])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'system-ui, sans-serif' }}>
      {/* 顶栏 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderBottom: '1px solid #d0d7de', background: '#f6f8fa' }}>
        <strong>harryopo-web</strong>
        <select
          value={current}
          onChange={(e) => loadDoc(e.target.value)}
          style={{ padding: '4px 8px' }}
        >
          {docs.map((d) => (
            <option key={d} value={d.replace(/\.md$/, '')}>{d}</option>
          ))}
        </select>
        <button onClick={newDoc} style={btnStyle}>新建</button>
        <span style={{ color: saving ? '#0969da' : '#57606a', fontSize: 12 }}>
          {saving ? '保存中…' : savedAt ? `已保存 ${savedAt}` : ''}
        </span>
        <span style={{ flex: 1 }} />
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

      {/* 主区：编辑 + 预览 */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
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
            <a
              key={f.name}
              href={`${API}${f.url}`}
              download={f.name}
              style={{ marginRight: 12, color: '#0969da' }}
            >
              {f.name}
            </a>
          ))}
        </div>
      )}
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
