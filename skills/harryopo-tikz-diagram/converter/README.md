# DSL 转换器使用说明

harryopo-tikz-diagram Skill 的 DSL 转换器，用于将 YAML 格式的结构化描述转换为 TikZ 代码。

## 功能介绍

- **分层架构图** (layered-architecture)：自动生成多层架构图，支持模块、层背景框、连接箭头
- **流程图** (flowchart)：支持多种节点类型（开始/处理/判断/输入输出/结束），支持 TB/LR 方向
- **组织架构树** (org-tree)：递归生成组织架构树，支持职位和姓名

## 安装依赖

```bash
pip install pyyaml
```

## 快速开始

```python
import yaml
from dsl_to_tikz import generate_tikz

# 从 YAML 文件读取
with open("example.yaml", "r", encoding="utf-8") as f:
    dsl = yaml.safe_load(f)

# 生成 TikZ 代码
tikz_code = generate_tikz(dsl)
print(tikz_code)
```

## 使用示例

### 1. 分层架构图

```yaml
type: layered-architecture
title: 系统分层架构图
theme: blue
layers:
  - name: 表现层
    style: light
    modules:
      - name: Web 前端
        desc: Vue.js
      - name: 移动 App
        desc: React Native
  - name: 业务层
    style: medium
    modules:
      - name: 用户服务
        desc: 用户管理
      - name: 订单服务
        desc: 订单处理
      - name: 支付服务
        desc: 在线支付
  - name: 数据层
    style: dark
    modules:
      - name: MySQL
        wide: true
connections:
  - from: "表现层/Web 前端"
    to: "业务层/用户服务"
    label: "调用"
```

### 2. 流程图

```yaml
type: flowchart
title: 用户登录流程
theme: green
direction: TB
nodes:
  - id: start
    label: 开始
    type: start
  - id: input
    label: 输入用户名密码
    type: io
  - id: check
    label: 验证信息
    type: decision
  - id: success
    label: 登录成功
    type: process
  - id: end
    label: 结束
    type: end
edges:
  - from: start
    to: input
  - from: input
    to: check
  - from: check
    to: success
    label: 是
  - from: success
    to: end
```

### 3. 组织架构树

```yaml
type: org-tree
title: 公司组织架构
theme: orange
root:
  name: 张总
  title: 总经理
  children:
    - name: 李经理
      title: 技术部经理
      children:
        - name: 王工
          title: 高级工程师
        - name: 刘工
          title: 工程师
    - name: 陈经理
      title: 产品部经理
      children:
        - name: 赵产品
          title: 产品经理
```

## DSL 格式说明

### 通用字段

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 图类型：`layered-architecture` / `flowchart` / `org-tree` |
| title | string | 图标题（可选） |
| theme | string | 主题：`blue` / `green` / `orange`，默认 `blue` |

### 分层架构图 (layered-architecture)

```yaml
type: layered-architecture
layers:
  - name: 层名称
    style: light/medium/dark
    modules:
      - name: 模块名称
        desc: 模块描述（可选）
        wide: true/false（是否宽模块，可选）
connections:
  - from: "层名/模块名"
    to: "层名/模块名"
    label: 箭头标签（可选）
```

### 流程图 (flowchart)

```yaml
type: flowchart
direction: TB/LR  # 自上而下/自左而右
nodes:
  - id: 节点ID
    label: 显示文字
    type: start/process/decision/io/end
edges:
  - from: 起始节点ID
    to: 目标节点ID
    label: 连线标签（可选）
```

### 组织架构树 (org-tree)

```yaml
type: org-tree
root:
  name: 姓名
  title: 职位（可选）
  children:
    - name: 子节点姓名
      title: 子节点职位
      children: [...]  # 递归嵌套
```

## 输出说明

生成的 TikZ 代码包含：
- 完整的 `tikzpicture` 环境
- 预定义的样式（遵循 `harryopo-` / `arch-` / `flow-` / `org-` 命名前缀）
- 自动计算的节点位置
- 中文支持（需配合 XeLaTeX 编译器）

## 依赖的 TikZ 库

在 LaTeX 文档中需要加载以下库：

```latex
\usepackage{tikz}
\usetikzlibrary{
  positioning,
  fit,
  backgrounds,
  arrows.meta,
  shapes.geometric,
  shapes.misc
}
```
