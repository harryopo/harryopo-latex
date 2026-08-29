// TemplateModal.tsx — 从模板新建：模板列表 → schema 动态表单 → docxtpl 渲染
import { useCallback, useEffect, useState } from 'react'
import type { CSSProperties } from 'react'

interface TplInfo { id: string; name: string; category: string }
interface FieldSpec {
  type: string
  required?: boolean
  description?: string
  fields?: Record<string, FieldSpec>
  item?: { type: string; fields?: Record<string, FieldSpec> }
}
type KeyedField = { key: string } & FieldSpec

export function TemplateModal({ onClose }: { onClose: () => void }) {
  const [templates, setTemplates] = useState<TplInfo[]>([])
  const [selected, setSelected] = useState<string>('')
  const [schema, setSchema] = useState<KeyedField[]>([])
  const [data, setData] = useState<Record<string, unknown>>({})
  const [rendering, setRendering] = useState(false)
  const [resultUrl, setResultUrl] = useState<string>('')

  // 模板列表
  useEffect(() => {
    fetch('/api/templates').then((r) => r.json()).then((d) => {
      setTemplates(d.templates || [])
      if (d.templates?.length) setSelected(d.templates[0].id)
    })
  }, [])

  // 选中模板 → 拉 schema → 初始化 data
  const loadSchema = useCallback(async (id: string) => {
    const r = await fetch(`/api/templates/${id}/schema`)
    const s = await r.json()
    const fields = Object.entries(s.fields || {}).map(([k, v]) => ({ key: k, ...(v as FieldSpec) }))
    setSchema(fields)
    setData(initData(fields))
    setResultUrl('')
  }, [])

  useEffect(() => {
    if (selected) loadSchema(selected)
  }, [selected, loadSchema])

  // 初始化默认值
  const initData = (fields: Array<{ key: string; type: string; item?: { type?: string } }>): Record<string, unknown> => {
    const d: Record<string, unknown> = {}
    for (const f of fields) {
      if (f.type === 'object') d[f.key] = {}
      else if (f.type === 'array') d[f.key] = []
      else d[f.key] = ''
    }
    return d
  }

  // 渲染提交
  const doRender = async () => {
    if (!selected) return
    setRendering(true)
    try {
      const r = await fetch(`/api/templates/${selected}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data }),
      })
      const d = await r.json()
      if (d.ok) setResultUrl(d.url)
      else alert(`渲染失败：${d.log || ''}`)
    } finally {
      setRendering(false)
    }
  }

  return (
    <div style={overlay} onClick={onClose}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>
        <h3 style={{ marginTop: 0 }}>从模板新建</h3>
        <div style={{ marginBottom: 10 }}>
          <select value={selected} onChange={(e) => setSelected(e.target.value)} style={inputStyle}>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>{t.name}（{t.category}）</option>
            ))}
          </select>
        </div>

        <div style={{ maxHeight: '50vh', overflow: 'auto', marginBottom: 12 }}>
          {schema.map((f) => (
            <FieldEditor key={f.key} field={f} value={data[f.key]} onChange={(v) => setData({ ...data, [f.key]: v })} />
          ))}
        </div>

        {resultUrl && (
          <div style={{ marginBottom: 10, color: '#0969da' }}>
            渲染完成：
            <a href={resultUrl} download style={{ color: '#0969da' }}>下载 docx</a>
          </div>
        )}

        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button onClick={onClose} style={btnStyle}>关闭</button>
          <button onClick={doRender} disabled={rendering} style={{ ...btnStyle, background: '#0969da', color: '#fff' }}>
            {rendering ? '渲染中…' : '渲染 docx'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ---------- 字段编辑器（string / object / array） ----------

function FieldEditor({ field, value, onChange }: {
  field: { key: string; type: string; required?: boolean; description?: string; fields?: Record<string, FieldSpec>; item?: FieldSpec }
  value: unknown
  onChange: (v: unknown) => void
}) {
  const label = `${field.key}${field.required ? '*' : ''}`

  if (field.type === 'object') {
    const obj = (value as Record<string, unknown>) || {}
    const sub = Object.entries(field.fields || {}).map(([k, v]) => ({ key: k, ...v }))
    return (
      <fieldset style={fieldsetStyle}>
        <legend>{label}</legend>
        {sub.map((s) => (
          <FieldEditor key={s.key} field={s} value={obj[s.key]} onChange={(v) => onChange({ ...obj, [s.key]: v })} />
        ))}
      </fieldset>
    )
  }

  if (field.type === 'array') {
    const arr = (value as Array<Record<string, unknown>>) || []
    const itemFields = Object.entries(field.item?.fields || {}).map(([k, v]) => ({ key: k, ...v }))
    return (
      <fieldset style={fieldsetStyle}>
        <legend>{label}（列表）</legend>
        {arr.map((row, i) => (
          <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 4, alignItems: 'center' }}>
            {itemFields.map((f) => (
              <input
                key={f.key}
                placeholder={f.key}
                value={String(row[f.key] ?? '')}
                onChange={(e) => {
                  const next = arr.map((r, j) => (j === i ? { ...r, [f.key]: e.target.value } : r))
                  onChange(next)
                }}
                style={{ ...inputStyle, flex: 1 }}
              />
            ))}
            <button
              onClick={() => onChange(arr.filter((_, j) => j !== i))}
              style={{ ...miniBtn, color: '#d1242f' }}
            >✕</button>
          </div>
        ))}
        <button
          onClick={() => onChange([...arr, {}])}
          style={miniBtn}
        >+ 添加行</button>
      </fieldset>
    )
  }

  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      <div style={{ fontSize: 12, color: '#57606a', marginBottom: 2 }}>{label}</div>
      <input
        value={(value as string) ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={field.description || ''}
        style={{ ...inputStyle, width: '100%' }}
      />
    </label>
  )
}

const overlay: CSSProperties = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
}
const modal: CSSProperties = {
  background: '#fff', borderRadius: 8, padding: 20, width: 480,
  boxShadow: '0 8px 30px rgba(0,0,0,0.15)', maxHeight: '80vh', overflow: 'auto',
}
const inputStyle: CSSProperties = {
  padding: '5px 8px', border: '1px solid #d0d7de', borderRadius: 4, fontSize: 13,
}
const fieldsetStyle: CSSProperties = {
  border: '1px solid #d0d7de', borderRadius: 6, margin: '0 0 10px', padding: '8px 10px',
}
const btnStyle: CSSProperties = {
  padding: '5px 12px', border: '1px solid #d0d7de', background: '#fff', borderRadius: 4, cursor: 'pointer',
}
const miniBtn: CSSProperties = {
  border: 'none', background: 'transparent', cursor: 'pointer', color: '#0969da', fontSize: 12, padding: '2px 6px',
}
