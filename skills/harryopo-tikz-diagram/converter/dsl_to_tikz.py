"""
DSL 转 TikZ 主转换器
将 YAML 格式的结构化描述转换为 TikZ 代码

使用颜色名（PaperBorder/PaperFill 等）配合 Nature 风格配色使用
"""

try:
    from .schema import (
        LayeredArchConfig,
        FlowchartConfig,
        OrgTreeConfig,
        dict_to_layered_arch,
        dict_to_flowchart,
        dict_to_org_tree,
    )
except ImportError:
    from schema import (
        LayeredArchConfig,
        FlowchartConfig,
        OrgTreeConfig,
        dict_to_layered_arch,
        dict_to_flowchart,
        dict_to_org_tree,
    )


def generate_tikz(dsl: dict) -> str:
    """
    将 DSL 字典转换为 TikZ 代码字符串

    Args:
        dsl: 符合 schema 的字典

    Returns:
        TikZ 代码字符串（tikzpicture 环境）
    """
    diagram_type = dsl.get("type", "")

    if diagram_type == "layered-architecture":
        config = dict_to_layered_arch(dsl)
        return generate_layered_arch(config)
    elif diagram_type == "flowchart":
        config = dict_to_flowchart(dsl)
        return generate_flowchart(config)
    elif diagram_type == "org-tree":
        config = dict_to_org_tree(dsl)
        return generate_org_tree(config)
    else:
        raise ValueError(f"不支持的图类型: {diagram_type}")


# ============================================================
# 颜色名称映射（Nature 风格）
# ============================================================

MAIN = "PaperBorder"
SUB = "PaperMuted"
SMALL = "PaperLayerBorder"
TINY = "PaperLayerBg"
DARK = "PaperTitle"
ACCENT = "AccentOrange"
FILL = "PaperFill"


# ============================================================
# 分层架构图生成
# ============================================================

def generate_layered_arch(config: LayeredArchConfig) -> str:
    """
    生成分层架构图 TikZ 代码

    Args:
        config: 分层架构图配置

    Returns:
        TikZ 代码字符串
    """
    lines = []

    # 主题切换命令
    theme_cmd = f"\\loadtikzsiztheme{{{config.theme}}}"

    # 开始 tikzpicture
    lines.append("\\begin{tikzpicture}[")
    lines.append("    >=Stealth,")
    lines.append("    node distance=0.8cm and 0.6cm,")
    lines.append("    harryopo-module/.style={")
    lines.append("        rectangle,")
    lines.append(f"        draw={MAIN},")
    lines.append(f"        fill={FILL},")
    lines.append("        line width=0.8pt,")
    lines.append("        text width=4.5cm,")
    lines.append("        align=left,")
    lines.append("        minimum height=1.7cm,")
    lines.append("        font=\\small\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        rounded corners=4pt,")
    lines.append("        inner sep=5pt,")
    lines.append("    },")
    lines.append("    harryopo-module-wide/.style={")
    lines.append("        harryopo-module,")
    lines.append("        text width=14cm,")
    lines.append("        minimum height=0.95cm,")
    lines.append("    },")
    lines.append("    arch-layerbox/.style={")
    lines.append(f"        draw={SMALL},")
    lines.append(f"        fill={TINY},")
    lines.append("        line width=0.6pt,")
    lines.append("        dashed,")
    lines.append("        dash pattern=on 4pt off 3pt,")
    lines.append("        rounded corners=6pt,")
    lines.append("        inner xsep=16pt,")
    lines.append("        inner ysep=14pt,")
    lines.append("    },")
    lines.append("    arch-layertitle/.style={")
    lines.append("        font=\\normalsize\\bfseries\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        fill=white,")
    lines.append("        inner xsep=4pt,")
    lines.append("        inner ysep=1pt,")
    lines.append("        anchor=south west,")
    lines.append("    },")
    lines.append("]")

    # 生成模块节点
    module_positions = {}

    for layer_idx, layer in enumerate(config.layers):
        layer_modules = layer.modules
        if not layer_modules:
            continue

        module_names = []

        for mod_idx, module in enumerate(layer_modules):
            node_id = f"layer{layer_idx}_mod{mod_idx}"
            style = "harryopo-module-wide" if module.wide else "harryopo-module"

            if layer_idx == 0 and mod_idx == 0:
                if module.desc:
                    lines.append(
                        f"    \\node[{style}] ({node_id}) at (0,0) "
                        f"{{\\textbf{{{module.name}}}\\\\[2pt]\\footnotesize{{{module.desc}}}}};"
                    )
                else:
                    lines.append(f"    \\node[{style}] ({node_id}) at (0,0) {{{module.name}}};")
            elif mod_idx == 0:
                prev_layer_ref = f"layer{layer_idx-1}_mod0"
                if module.desc:
                    lines.append(
                        f"    \\node[{style}, below=1.2cm of {prev_layer_ref}] ({node_id}) "
                        f"{{\\textbf{{{module.name}}}\\\\[2pt]\\footnotesize{{{module.desc}}}}};"
                    )
                else:
                    lines.append(
                        f"    \\node[{style}, below=1.2cm of {prev_layer_ref}] ({node_id}) "
                        f"{{{module.name}}};"
                    )
            else:
                prev_node = f"layer{layer_idx}_mod{mod_idx-1}"
                if module.desc:
                    lines.append(
                        f"    \\node[{style}, right=of {prev_node}] ({node_id}) "
                        f"{{\\textbf{{{module.name}}}\\\\[2pt]\\footnotesize{{{module.desc}}}}};"
                    )
                else:
                    lines.append(
                        f"    \\node[{style}, right=of {prev_node}] ({node_id}) "
                        f"{{{module.name}}};"
                    )

            module_positions[(layer_idx, mod_idx)] = node_id
            module_names.append(node_id)

        # 生成层背景框
        if module_names:
            fit_nodes = " ".join([f"({n})" for n in module_names])
            lines.append("    \\begin{scope}[on background layer]")
            lines.append(
                f"        \\node[arch-layerbox, fit={{{fit_nodes}}}, "
                f"label={{[arch-layertitle]north west:{{{layer.name}}}}}] "
                f"(layer{layer_idx}_box) {{}};"
            )
            lines.append("    \\end{scope}")

    # 生成连接箭头
    for conn in config.connections:
        from_ref = conn.get("from", "")
        to_ref = conn.get("to", "")
        label = conn.get("label", "")

        from_node = _resolve_module_ref(from_ref, config, module_positions)
        to_node = _resolve_module_ref(to_ref, config, module_positions)

        if from_node and to_node:
            if label:
                lines.append(
                    f"    \\draw[-{{Stealth}}, line width=1.4pt, {MAIN}] "
                    f"({from_node}.south) -- node[midway, right=4pt, fill=white, inner sep=2pt, font=\\footnotesize\\sffamily, text={SUB}] {{{label}}} "
                    f"({to_node}.north);"
                )
            else:
                lines.append(
                    f"    \\draw[-{{Stealth}}, line width=1.4pt, {MAIN}] "
                    f"({from_node}.south) -- ({to_node}.north);"
                )

    # 标题
    if config.title:
        lines.append(
            f"    \\node[font=\\bfseries\\Large\\sffamily, text={MAIN}, "
            f"above=0.5cm of layer0_mod0.north] (title) {{{config.title}}};"
        )

    lines.append("\\end{tikzpicture}")

    return "\n".join(lines)


def _resolve_module_ref(ref: str, config: LayeredArchConfig, positions: dict) -> str:
    """
    解析模块引用

    支持格式：
    - "layerName/moduleName"
    - "0/0" (层索引/模块索引)
    """
    if "/" in ref:
        parts = ref.split("/", 1)
        layer_ref, mod_ref = parts[0], parts[1]

        if layer_ref.isdigit() and mod_ref.isdigit():
            layer_idx = int(layer_ref)
            mod_idx = int(mod_ref)
            return positions.get((layer_idx, mod_idx), "")

        for layer_idx, layer in enumerate(config.layers):
            if layer.name == layer_ref:
                for mod_idx, module in enumerate(layer.modules):
                    if module.name == mod_ref:
                        return positions.get((layer_idx, mod_idx), "")

    return ""


# ============================================================
# 流程图生成
# ============================================================

def generate_flowchart(config: FlowchartConfig) -> str:
    """
    生成流程图 TikZ 代码

    Args:
        config: 流程图配置

    Returns:
        TikZ 代码字符串
    """
    lines = []

    # 开始 tikzpicture
    lines.append("\\begin{tikzpicture}[")
    lines.append("    >=Stealth,")
    lines.append("    node distance=1.2cm,")
    lines.append("    flow-startend/.style={")
    lines.append("        rectangle,")
    lines.append(f"        draw={ACCENT},")
    lines.append(f"        fill={ACCENT}!10,")
    lines.append("        line width=1.2pt,")
    lines.append("        rounded corners=18pt,")
    lines.append("        text width=120pt,")
    lines.append("        minimum height=36pt,")
    lines.append("        align=center,")
    lines.append("        font=\\small\\bfseries\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        inner sep=8pt,")
    lines.append("    },")
    lines.append("    flow-process/.style={")
    lines.append("        rectangle,")
    lines.append(f"        draw={MAIN},")
    lines.append(f"        fill={FILL},")
    lines.append("        line width=0.8pt,")
    lines.append("        rounded corners=4pt,")
    lines.append("        text width=120pt,")
    lines.append("        minimum height=36pt,")
    lines.append("        align=center,")
    lines.append("        font=\\small\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        inner sep=6pt,")
    lines.append("    },")
    lines.append("    flow-decision/.style={")
    lines.append("        diamond,")
    lines.append(f"        draw={MAIN},")
    lines.append(f"        fill={TINY},")
    lines.append("        line width=0.8pt,")
    lines.append("        aspect=1.3,")
    lines.append("        minimum width=60pt,")
    lines.append("        align=center,")
    lines.append("        font=\\small\\bfseries\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        inner sep=4pt,")
    lines.append("    },")
    lines.append("    flow-io/.style={")
    lines.append("        trapezium,")
    lines.append("        trapezium left angle=70,")
    lines.append("        trapezium right angle=110,")
    lines.append(f"        draw={MAIN},")
    lines.append(f"        fill={FILL},")
    lines.append("        line width=0.8pt,")
    lines.append("        text width=120pt,")
    lines.append("        minimum height=36pt,")
    lines.append("        align=center,")
    lines.append("        font=\\small\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        inner sep=6pt,")
    lines.append("    },")
    lines.append("]")

    # 构建节点索引
    node_names = {}
    for i, node in enumerate(config.nodes):
        node_names[node.id] = f"node{i}"

    # 布局方向
    direction = config.direction.upper()

    # 生成节点
    for i, node in enumerate(config.nodes):
        node_name = node_names[node.id]
        node_type = node.type
        if node_type in ("start", "end"):
            node_type = "startend"
        style = f"flow-{node_type}"

        if i == 0:
            lines.append(f"    \\node[{style}] ({node_name}) at (0,0) {{{node.label}}};")
        else:
            prev_node_name = node_names[config.nodes[i - 1].id]
            if direction == "LR":
                lines.append(f"    \\node[{style}, right=of {prev_node_name}] ({node_name}) {{{node.label}}};")
            else:
                lines.append(f"    \\node[{style}, below=of {prev_node_name}] ({node_name}) {{{node.label}}};")

    # 生成边
    for edge in config.edges:
        from_name = node_names.get(edge.from_id, "")
        to_name = node_names.get(edge.to_id, "")

        if from_name and to_name:
            if edge.label:
                if direction == "LR":
                    lines.append(
                        f"    \\draw[-{{Stealth}}, line width=1.5pt, {MAIN}] "
                        f"({from_name}) -- node[midway, above=3pt, fill=white, inner sep=2pt, font=\\footnotesize\\sffamily, text={SUB}] {{{edge.label}}} "
                        f"({to_name});"
                    )
                else:
                    lines.append(
                        f"    \\draw[-{{Stealth}}, line width=1.5pt, {MAIN}] "
                        f"({from_name}) -- node[midway, right=4pt, fill=white, inner sep=2pt, font=\\footnotesize\\sffamily, text={SUB}] {{{edge.label}}} "
                        f"({to_name});"
                    )
            else:
                lines.append(
                    f"    \\draw[-{{Stealth}}, line width=1.5pt, {MAIN}] "
                    f"({from_name}) -- ({to_name});"
                )

    # 标题
    if config.title and config.nodes:
        first_node = node_names[config.nodes[0].id]
        lines.append(
            f"    \\node[font=\\bfseries\\Large\\sffamily, text={MAIN}, "
            f"above=0.5cm of {first_node}.north] (title) {{{config.title}}};"
        )

    lines.append("\\end{tikzpicture}")

    return "\n".join(lines)


# ============================================================
# 组织架构树生成
# ============================================================

def generate_org_tree(config: OrgTreeConfig) -> str:
    """
    生成组织架构树 TikZ 代码

    使用相对定位方式构建树，结构清晰可靠

    Args:
        config: 组织架构图配置

    Returns:
        TikZ 代码字符串
    """
    lines = []

    # 开始 tikzpicture
    lines.append("\\begin{tikzpicture}[")
    lines.append("    >=Stealth,")
    lines.append("    org-person/.style={")
    lines.append("        rectangle,")
    lines.append(f"        draw={MAIN},")
    lines.append(f"        fill={FILL},")
    lines.append("        line width=0.8pt,")
    lines.append("        text width=90pt,")
    lines.append("        align=center,")
    lines.append("        minimum height=50pt,")
    lines.append("        font=\\small\\sffamily,")
    lines.append(f"        text={DARK},")
    lines.append("        rounded corners=4pt,")
    lines.append("        inner sep=5pt,")
    lines.append("    },")
    lines.append("    org-person-root/.style={")
    lines.append("        rectangle,")
    lines.append(f"        draw={MAIN},")
    lines.append(f"        fill={DARK},")
    lines.append(f"        text={FILL},")
    lines.append("        line width=0.8pt,")
    lines.append("        rounded corners=6pt,")
    lines.append("        text width=120pt,")
    lines.append("        align=center,")
    lines.append("        minimum height=50pt,")
    lines.append("        font=\\small\\bfseries\\sffamily,")
    lines.append("        inner sep=6pt,")
    lines.append("    },")
    lines.append("]")

    # 使用相对定位方式构建树
    if config.root:
        lines.extend(_generate_org_tree_positioned(config.root))

    # 标题
    if config.title:
        lines.append(
            f"    \\node[font=\\bfseries\\Large\\sffamily, text={MAIN}, "
            f"above=0.5cm of root.north] (title) {{{config.title}}};"
        )

    lines.append("\\end{tikzpicture}")

    return "\n".join(lines)


def _generate_org_tree_positioned(root) -> list:
    """
    使用相对定位方式生成组织树

    采用层序遍历，手动布局节点，确保结构清晰可靠

    Args:
        root: 根节点

    Returns:
        TikZ 代码行列表
    """
    lines = []

    # 深度优先遍历，收集所有节点信息
    all_nodes = []
    node_info = {}

    def collect_nodes(node, level, parent_id, child_index):
        node_id = len(all_nodes)
        all_nodes.append(node)
        node_info[node_id] = {
            "node": node,
            "level": level,
            "parent_id": parent_id,
            "child_index": child_index,
        }
        for i, child in enumerate(node.children):
            collect_nodes(child, level + 1, node_id, i)

    collect_nodes(root, 0, -1, 0)

    # 按层级分组
    levels = {}
    for nid, info in node_info.items():
        lvl = info["level"]
        if lvl not in levels:
            levels[lvl] = []
        levels[lvl].append(nid)

    # 生成节点名称映射
    node_names = {}

    # 逐层生成节点
    for level in sorted(levels.keys()):
        level_nodes = levels[level]

        for idx, nid in enumerate(level_nodes):
            info = node_info[nid]
            node = info["node"]

            if level == 0:
                name = "root"
            else:
                name = f"l{level}_n{idx}"
            node_names[nid] = name

            style = "org-person-root" if level == 0 else "org-person"

            if node.title:
                node_text = f"\\textbf{{{node.name}}}\\\\[2pt]\\footnotesize{{{node.title}}}"
            else:
                node_text = node.name

            if level == 0:
                lines.append(f"    \\node[{style}] ({name}) at (0,0) {{{node_text}}};")
            else:
                parent_id = info["parent_id"]
                parent_name = node_names[parent_id]

                parent_info = node_info[parent_id]
                parent_children = parent_info["node"].children
                num_children = len(parent_children)
                child_idx = info["child_index"]

                if num_children == 1:
                    xshift = "0cm"
                else:
                    total_width = (num_children - 1) * 3.5
                    start_offset = -total_width / 2
                    xshift_val = start_offset + child_idx * 3.5
                    xshift = f"{xshift_val}cm"

                lines.append(
                    f"    \\node[{style}, below=1.8cm of {parent_name}, xshift={xshift}] "
                    f"({name}) {{{node_text}}};"
                )

    # 生成连接线
    for nid, info in node_info.items():
        if info["level"] == 0:
            continue

        parent_id = info["parent_id"]
        parent_name = node_names[parent_id]
        child_name = node_names[nid]

        lines.append(
            f"    \\draw[-, line width=1.2pt, {MAIN}] "
            f"({parent_name}.south) -- ({child_name}.north);"
        )

    return lines
