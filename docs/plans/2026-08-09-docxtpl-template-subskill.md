# docxtpl 模板填充子 skill（2026-08-09 完成）

> 归属：harryopo-office 办公超级 skill · Word 模板填充流程
> 对应路线图：阶段 1（docxtpl 模板填充 + 模板注册表）——本文件覆盖 docxtpl 部分

## 一、目标

解决"AI 不按用户模板来"的核心痛点：

- 用户用 Word 设计好模板（**所见即所得**，任意复杂样式：封面/表格/页眉页脚/合并单元格）
- AI 只产出结构化 JSON（data.json）填充，**格式 100% 保留用户模板**
- 中间态 JSON 用户可直接编辑，符合办公文档生成铁律（AI 只产结构化数据）

## 二、技术选型

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **docxtpl**（python-docx + jinja2） | 模板即 Word 文件，格式保真，支持循环/条件/合并 | 模板需人工插占位符 | ✅ 采用 |
| python-docx 直接生成 | 无模板依赖 | 样式全手写，丑且不按模板 | 弃用 |
| pandoc → docx | 跨平台 | 格式控制弱，难以精细排版 | 弃用 |

调研来源：docxtpl 官方文档（readthedocs）+ CSDN 深度指南 + GitHub python-docx-template 项目。

## 三、实现（`scripts/word/template/`）

```
template/
├── docx_template.py        # 主入口 CLI：extract / validate / render
├── schema_extractor.py     # 模板占位符扫描 + jinja2 作用域类型推断 → schema.json
├── template_render.py      # data.json → 保真 .docx（校验 + 图片 InlineImage）
└── examples/               # 示例全链路
    ├── make_example_template.py   # 生成示例模板（占位符/循环表格/图片）
    ├── template.docx / schema.json / data.json / output.docx / demo.png
```

### 工作流

```
用户模板 template.docx（含 {{ 占位符 }}）
  → extract  扫描正文/页眉/页脚/脚注占位符 → schema.json（字段清单+类型）
  → AI 阅读 schema 确认字段含义 → 产出 data.json（用户可编辑）
  → validate 对照 schema 校验（必填缺失/类型错误）
  → render   保真填充 → 输出 .docx
```

### schema 类型推断规则

| 模板写法 | schema 推断 |
|---------|------------|
| `{{ var }}` | string，必填 |
| `{% if var %}` | var 可选（required=false） |
| `{{ obj.field }}` | obj → object（fields 聚合） |
| `{%tr for x in items %}...{%tr endfor %}` | items → array；循环内 `x.field` → item object |
| `loop.index` / `range` 等 | jinja2 内建，排除 |

### 占位符能力

- 普通变量、对象字段、行内条件（`{% if %}`）
- 表格行循环 `{%tr %}`、列循环 `{%tc %}`、段落循环 `{%p %}`
- 合并单元格 `{% hm %}` / `{% vm %}`
- 图片：data.json 写 `{"image": "path.png", "width_mm": 30}` → 自动 InlineImage

## 四、端到端验证（11 项全通过）

示例 data：知行读书·多智能体知识服务平台（4 行任务表 + 对象 owner + 条件块 + 图片）。

- ✓ 普通变量替换（项目名称）
- ✓ 对象字段（owner.name / owner.phone）
- ✓ 条件块渲染（need_abstract=true）
- ✓ 循环表格 4 行数据填充
- ✓ 结尾变量 summary
- ✓ 无 `{{` / `{%` / endfor / task.name 残留
- ✓ 图片 1 张正确插入（InlineImage）

## 五、踩坑记录（已入 CLAUDE.md #25~28）

1. **`{%tr for %}` 与 `{%tr endfor %}` 必须各自独占一行**——docxtpl 按"整行含标签"机制处理，中间数据行被循环复制；塞同一行会导致整行被吞 + jinja2 `unknown tag 'endfor'`
2. **占位符不能跨 run**——Word 中加粗/改色会拆 run 导致占位符无法识别
3. **docxtpl 0.20+ 移除 `get_defined_variables()`**——schema 提取自研：扫 `<w:t>` 节点 + 正则 + jinja2 作用域栈；`{%tr` 前缀正则用 `(?:(?:tr|tc|p|r)\s+)?`
4. **图片字段校验**——string 分支需放行含 `image` 键的 dict

## 六、使用命令

```powershell
cd .trae/skills/harryopo-office/scripts/word/template
python docx_template.py extract 模板.docx -o schema.json
python docx_template.py validate data.json -s schema.json
python docx_template.py render 模板.docx -d data.json -o 输出.docx --check
```

## 七、后续路线图

- ⬜ 模板注册表 v1（manifest.json）：把用户中意的模板统一注册入库
- ⬜ 自动 schema 提取增强：RichText 富文本、嵌套表格、页眉页脚图片
- ⬜ docxtpl 与 md_to_word 双流程统一入口
