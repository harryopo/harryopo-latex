// md.test.ts — round-trip 幂等测试（核心护栏）
// MD → parse → JSONContent → serialize → MD'，断言结构零丢失
import { describe, expect, it } from 'vitest'
import { createManager, isRoundTripStable, mdToJson, jsonToMd } from './md'
import { headlessExtensions } from './extensions'

const manager = createManager(headlessExtensions)

describe('harryopo MD 约定 round-trip', () => {
  it('单行块级公式 $$...$$ 往返', () => {
    const md = '公式：\n\n$$E = mc^2$$\n\n正文。'
    const json = mdToJson(manager, md)
    const out = jsonToMd(manager, json)
    expect(out).toContain('$$E = mc^2$$')
  })

  it('多行块级公式往返', () => {
    const md = '$$\n\\int_0^1 x^2\\,dx = \\frac{1}{3}\n$$'
    const out = jsonToMd(manager, mdToJson(manager, md))
    expect(out.replace(/\s+/g, ' ').trim()).toContain('$$')
    expect(out.replace(/\s+/g, '')).toContain('\\frac{1}{3}')
  })

  it('行内公式 $...$ 往返', () => {
    const md = '质能方程 $E=mc^2$ 是核心。'
    const out = jsonToMd(manager, mdToJson(manager, md))
    expect(out).toContain('$E=mc^2$')
  })

  it('GFM 表格往返', () => {
    const md = '| 项目 | 数值 |\n| --- | --- |\n| A | 1 |\n| B | 2 |'
    const out = jsonToMd(manager, mdToJson(manager, md))
    // 表格序列化可能列对齐（| 项目  | 数值  |），宽松断言内容保留
    expect(out).toContain('项目')
    expect(out).toContain('数值')
    expect(out).toContain('| A')
    expect(out).toContain('| B')
  })

  it('标题层级往返', () => {
    const md = '# 主标题\n\n## 一、引言\n\n### 1.1 小节'
    const out = jsonToMd(manager, mdToJson(manager, md))
    expect(out).toContain('# 主标题')
    expect(out).toContain('## 一、引言')
    expect(out).toContain('### 1.1 小节')
  })

  it('引用注释往返', () => {
    const md = '正文。\n\n> 注：这是注释。\n\n继续。'
    const out = jsonToMd(manager, mdToJson(manager, md))
    expect(out).toContain('> 注：这是注释。')
  })

  it('图片往返', () => {
    const md = '![图1：架构](figures/arch.png)'
    const out = jsonToMd(manager, mdToJson(manager, md))
    expect(out).toContain('![图1：架构](figures/arch.png)')
  })

  it('round-trip 幂等稳定（二次序列化不变）', () => {
    const md = '# 报告\n\n## 一、简介\n\n公式 $$x^2$$ 与表格：\n\n| a | b |\n| - | - |\n| 1 | 2 |'
    const { stable, first, second } = isRoundTripStable(manager, md)
    expect(stable).toBe(true)
    expect(first).toBe(second)
  })
})
