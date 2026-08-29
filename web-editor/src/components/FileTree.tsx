// FileTree.tsx — 多文档文件树（递归目录 + 新建/删除）
import { useState } from 'react'
import type { CSSProperties } from 'react'

interface TreeNode {
  name: string
  path: string
  type: 'dir' | 'md'
  children?: TreeNode[]
}

interface FileTreeProps {
  tree: TreeNode[]
  current: string
  onOpen: (path: string) => void
  onNew: () => void
  onDelete: (path: string) => void
}

export function FileTree({ tree, current, onOpen, onNew, onDelete }: FileTreeProps) {
  return (
    <div style={{ padding: '8px', fontSize: 13, userSelect: 'none' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <strong>文档</strong>
        <button onClick={onNew} style={miniBtn}>+ 新建</button>
      </div>
      {tree.map((node) => (
        <TreeNodeItem
          key={node.path}
          node={node}
          depth={0}
          current={current}
          onOpen={onOpen}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}

function TreeNodeItem({ node, depth, current, onOpen, onDelete }: {
  node: TreeNode
  depth: number
  current: string
  onOpen: (path: string) => void
  onDelete: (path: string) => void
}) {
  const [open, setOpen] = useState(true)
  const pad = { paddingLeft: depth * 14 + 4 }

  if (node.type === 'dir') {
    return (
      <div>
        <div
          style={{ ...pad, cursor: 'pointer', fontWeight: 600, color: '#24292f' }}
          onClick={() => setOpen(!open)}
        >
          {open ? '📂' : '📁'} {node.name}
        </div>
        {open && node.children?.map((c) => (
          <TreeNodeItem
            key={c.path}
            node={c}
            depth={depth + 1}
            current={current}
            onOpen={onOpen}
            onDelete={onDelete}
          />
        ))}
      </div>
    )
  }

  const active = node.path === current
  return (
    <div
      style={{
        ...pad,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        background: active ? '#ddf4ff' : 'transparent',
        borderRadius: 4,
        paddingTop: 2,
        paddingBottom: 2,
      }}
    >
      <span
        onClick={() => onOpen(node.path)}
        style={{ flex: 1, color: active ? '#0969da' : '#24292f' }}
      >
        📄 {node.name.replace(/\.md$/, '')}
      </span>
      <button
        onClick={() => {
          if (window.confirm(`删除 ${node.path}？`)) onDelete(node.path)
        }}
        style={{ ...miniBtn, color: '#d1242f' }}
        title="删除"
      >
        ✕
      </button>
    </div>
  )
}

const miniBtn: CSSProperties = {
  border: 'none',
  background: 'transparent',
  cursor: 'pointer',
  fontSize: 12,
  color: '#0969da',
  padding: '1px 4px',
}
