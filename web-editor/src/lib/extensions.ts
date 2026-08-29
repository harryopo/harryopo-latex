// extensions.ts — harryopo-web 编辑器扩展装配
import StarterKit from '@tiptap/starter-kit'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import Image from '@tiptap/extension-image'
import { Markdown } from '@tiptap/markdown'
import { HarryopoBlockMath, HarryopoInlineMath } from './math'
import { RawBlock, RawInline } from './raw'

/** 浏览器编辑器扩展（含 Markdown 扩展：编辑器内 MD 序列化） */
export const editorExtensions = [
  StarterKit.configure({ codeBlock: false }),
  Table.configure({ resizable: true }),
  TableRow,
  TableHeader,
  TableCell,
  Image,
  Markdown,
  HarryopoBlockMath,
  HarryopoInlineMath,
  RawBlock,
  RawInline,
]

/** headless 扩展（服务端/测试：MarkdownManager.parse/serialize，无需 Markdown 扩展） */
export const headlessExtensions = [
  StarterKit.configure({ codeBlock: false }),
  Table,
  TableRow,
  TableHeader,
  TableCell,
  Image,
  HarryopoBlockMath,
  HarryopoInlineMath,
  RawBlock,
  RawInline,
]
