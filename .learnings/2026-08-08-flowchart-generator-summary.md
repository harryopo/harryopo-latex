---

## 2026-08-08: flowchart-generator 工作总结

### 完成的工作
1. **移除 style19 流程图** — skill 不适合做复杂流程图，专注架构/时序图
2. **修复时序图路径冗余点** — `L{bend},{my} L{bend},{my}` → 直接 `L{tx-12},{my}`
3. **修复 PNG 导出** — playwright 改用临时 HTML 文件方案
4. **修复 style13 `len(nodes)` bug** — 改为 `len(layers)`
5. **修复 infer_style 误推 style16** — 插入 `nodes+edges → style16` 检查

### 最终 6 个样式
| Style | 名称 | 擅长场景 |
|-------|------|---------|
| 13 | Compact Architecture | 系统架构图 |
| 14 | Agent Orchestration | 智能体编排 |
| 15 | Pipeline Flow | 数据管线 |
| 16 | Data Flow | 数据流图 |
| 17 | Skill Workflow | 泳道图 |
| 18 | Sequence Diagram | 时序图 |

### 定位
- **擅长**：架构/组织/时序/管线/数据流/泳道图
- **不做**：复杂流程图（用 TikZ）
