// math.ts — harryopo 公式约定定制（@tiptap/extension-mathematics 扩展）
//
// harryopo MD 约定（convert.py / tex2md.py 输出）：
//   块级公式：单行 `$$...$$`（同行）—— 官方 BlockMath 只认 `$$\n...\n$$` 多行，需定制
//   行内公式：`$...$`（单美元）
import { BlockMath, InlineMath } from '@tiptap/extension-mathematics'

export const KATEX_OPTIONS = { throwOnError: false }

// 块级公式：支持单行 `$$...$$`（harryopo 主约定）+ 多行 `$$\n...\n$$`
export const HarryopoBlockMath = BlockMath.extend({
  renderMarkdown(node: { attrs?: { latex?: string } }) {
    // 统一输出单行（与 convert.py / tex2md 输出一致）
    return `$$${node.attrs?.latex || ''}$$`
  },
  markdownTokenizer: {
    name: 'blockMath',
    level: 'block' as const,
    start(src: string) {
      return /^\$\$/.test(src) ? 0 : -1
    },
    tokenize(src: string) {
      const single = /^\$\$(.+?)\$\$(?=\r?\n|$)/s.exec(src)
      if (single) {
        return { type: 'blockMath', raw: single[0], latex: single[1].trim() }
      }
      const multi = /^\$\$\r?\n([\s\S]+?)\r?\n\$\$/.exec(src)
      if (multi) {
        return { type: 'blockMath', raw: multi[0], latex: multi[1].trim() }
      }
      return undefined
    },
  },
}).configure({ katexOptions: { ...KATEX_OPTIONS, displayMode: true } })

// 行内公式：`$...$`（单美元，harryopo 约定）
export const HarryopoInlineMath = InlineMath.extend({
  renderMarkdown(node: { attrs?: { latex?: string } }) {
    return `$${node.attrs?.latex || ''}$`
  },
  markdownTokenizer: {
    name: 'inlineMath',
    level: 'inline' as const,
    start(src: string) {
      return src.indexOf('$')
    },
    tokenize(src: string) {
      const m = /^\$([^$\n]+?)\$/.exec(src)
      if (!m) return undefined
      return { type: 'inlineMath', raw: m[0], latex: m[1].trim() }
    },
  },
}).configure({ katexOptions: { ...KATEX_OPTIONS, displayMode: false } })
