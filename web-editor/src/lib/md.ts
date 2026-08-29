// md.ts — Markdown 中间态 ↔ ProseMirror JSON 双向工具（@tiptap/markdown）
//
// - 服务端/测试：MarkdownManager.parse(md) → JSONContent；serialize(json) → MD
// - 编辑器内：setContent(json)；getMarkdown()
import { MarkdownManager } from '@tiptap/markdown'
import type { Editor, Extensions, JSONContent } from '@tiptap/core'

/** 创建 MarkdownManager（服务端/测试用） */
export function createManager(extensions: Extensions): MarkdownManager {
  return new MarkdownManager({ extensions })
}

/** MD → JSONContent */
export function mdToJson(manager: MarkdownManager, md: string): JSONContent {
  return manager.parse(md) as JSONContent
}

/** JSONContent → MD */
export function jsonToMd(manager: MarkdownManager, json: JSONContent): string {
  return manager.serialize(json)
}

/** 编辑器当前内容 → MD（编辑器内保存） */
export function editorToMd(editor: Editor): string {
  const storage = editor.storage as unknown as {
    markdown?: { getMarkdown?: () => string }
  }
  return storage.markdown?.getMarkdown?.() ?? ''
}

/** 加载 MD 到编辑器（先 parse 成 JSON 再 setContent，保证类型安全） */
export function loadMdIntoEditor(editor: Editor, manager: MarkdownManager, md: string): void {
  const json = mdToJson(manager, md)
  editor.commands.setContent(json, { emitUpdate: false })
}

/** round-trip 幂等：serialize(parse(serialize(parse(x)))) === serialize(parse(x)) */
export function isRoundTripStable(
  manager: MarkdownManager,
  md: string,
): { stable: boolean; first: string; second: string } {
  const first = jsonToMd(manager, mdToJson(manager, md))
  const second = jsonToMd(manager, mdToJson(manager, first))
  return { stable: first === second, first, second }
}
