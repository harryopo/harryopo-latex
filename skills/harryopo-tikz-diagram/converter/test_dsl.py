"""
DSL 转换器测试用例
测试三种图类型的基本生成、主题切换和边界情况
"""

import pytest
from dsl_to_tikz import generate_tikz


# ============================================================
# 分层架构图测试
# ============================================================

class TestLayeredArchitecture:
    """分层架构图测试"""

    def test_basic_generation(self):
        """测试基本分层架构图生成"""
        dsl = {
            "type": "layered-architecture",
            "title": "测试架构图",
            "theme": "blue",
            "layers": [
                {
                    "name": "前端层",
                    "modules": [
                        {"name": "Web 页面", "desc": "Vue"},
                        {"name": "移动端", "desc": "React Native"}
                    ]
                },
                {
                    "name": "后端层",
                    "modules": [
                        {"name": "API 服务", "desc": "FastAPI"}
                    ]
                }
            ]
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "\\end{tikzpicture}" in result
        assert "harryopo-module" in result
        assert "arch-layerbox" in result
        assert "前端层" in result
        assert "后端层" in result
        assert "Web 页面" in result
        assert "API 服务" in result

    def test_theme_green(self):
        """测试绿色主题——验证使用颜色名系统"""
        dsl = {
            "type": "layered-architecture",
            "theme": "green",
            "layers": [
                {
                    "name": "层1",
                    "modules": [{"name": "模块1"}]
                }
            ]
        }
        result = generate_tikz(dsl)
        assert "MainColor" in result
        assert "SubColor" in result
        assert "TinyColor" in result

    def test_theme_orange(self):
        """测试橙色主题——验证使用颜色名系统"""
        dsl = {
            "type": "layered-architecture",
            "theme": "orange",
            "layers": [
                {
                    "name": "层1",
                    "modules": [{"name": "模块1"}]
                }
            ]
        }
        result = generate_tikz(dsl)
        assert "MainColor" in result
        assert "SubColor" in result
        assert "TinyColor" in result

    def test_minimal_layers(self):
        """测试边界情况：最少层数（2层）"""
        dsl = {
            "type": "layered-architecture",
            "layers": [
                {
                    "name": "层1",
                    "modules": [{"name": "模块1"}]
                },
                {
                    "name": "层2",
                    "modules": [{"name": "模块2"}]
                }
            ]
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "层1" in result
        assert "层2" in result

    def test_wide_module(self):
        """测试宽模块"""
        dsl = {
            "type": "layered-architecture",
            "layers": [
                {
                    "name": "数据层",
                    "modules": [
                        {"name": "数据库", "wide": True}
                    ]
                }
            ]
        }
        result = generate_tikz(dsl)
        assert "harryopo-module-wide" in result

    def test_connections(self):
        """测试连接箭头"""
        dsl = {
            "type": "layered-architecture",
            "layers": [
                {
                    "name": "上层",
                    "modules": [{"name": "模块A"}]
                },
                {
                    "name": "下层",
                    "modules": [{"name": "模块B"}]
                }
            ],
            "connections": [
                {"from": "0/0", "to": "1/0", "label": "调用"}
            ]
        }
        result = generate_tikz(dsl)
        assert "\\draw[->" in result
        assert "调用" in result


# ============================================================
# 流程图测试
# ============================================================

class TestFlowchart:
    """流程图测试"""

    def test_basic_generation(self):
        """测试基本流程图生成"""
        dsl = {
            "type": "flowchart",
            "title": "测试流程",
            "theme": "blue",
            "direction": "TB",
            "nodes": [
                {"id": "start", "label": "开始", "type": "start"},
                {"id": "process", "label": "处理", "type": "process"},
                {"id": "end", "label": "结束", "type": "end"}
            ],
            "edges": [
                {"from": "start", "to": "process"},
                {"from": "process", "to": "end"}
            ]
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "\\end{tikzpicture}" in result
        assert "flow-start" in result
        assert "flow-process" in result
        assert "flow-end" in result
        assert "开始" in result
        assert "结束" in result

    def test_direction_lr(self):
        """测试 LR 方向"""
        dsl = {
            "type": "flowchart",
            "direction": "LR",
            "nodes": [
                {"id": "a", "label": "节点A", "type": "process"},
                {"id": "b", "label": "节点B", "type": "process"}
            ],
            "edges": [
                {"from": "a", "to": "b"}
            ]
        }
        result = generate_tikz(dsl)
        assert "right=of" in result

    def test_direction_tb(self):
        """测试 TB 方向"""
        dsl = {
            "type": "flowchart",
            "direction": "TB",
            "nodes": [
                {"id": "a", "label": "节点A", "type": "process"},
                {"id": "b", "label": "节点B", "type": "process"}
            ],
            "edges": [
                {"from": "a", "to": "b"}
            ]
        }
        result = generate_tikz(dsl)
        assert "below=of" in result

    def test_decision_node(self):
        """测试判断节点"""
        dsl = {
            "type": "flowchart",
            "nodes": [
                {"id": "check", "label": "是否通过", "type": "decision"}
            ],
            "edges": []
        }
        result = generate_tikz(dsl)
        assert "flow-decision" in result

    def test_io_node(self):
        """测试输入输出节点"""
        dsl = {
            "type": "flowchart",
            "nodes": [
                {"id": "input", "label": "输入数据", "type": "io"}
            ],
            "edges": []
        }
        result = generate_tikz(dsl)
        assert "flow-io" in result

    def test_edge_labels(self):
        """测试连线标签"""
        dsl = {
            "type": "flowchart",
            "nodes": [
                {"id": "a", "label": "A", "type": "process"},
                {"id": "b", "label": "B", "type": "process"}
            ],
            "edges": [
                {"from": "a", "to": "b", "label": "是"}
            ]
        }
        result = generate_tikz(dsl)
        assert "是" in result

    def test_theme_green(self):
        """测试绿色主题流程图——验证使用颜色名系统"""
        dsl = {
            "type": "flowchart",
            "theme": "green",
            "nodes": [
                {"id": "n", "label": "节点", "type": "process"}
            ],
            "edges": []
        }
        result = generate_tikz(dsl)
        assert "MainColor" in result
        assert "SubColor" in result

    def test_minimal_nodes(self):
        """测试边界情况：最少节点数（2个）"""
        dsl = {
            "type": "flowchart",
            "nodes": [
                {"id": "start", "label": "开始", "type": "start"},
                {"id": "end", "label": "结束", "type": "end"}
            ],
            "edges": [
                {"from": "start", "to": "end"}
            ]
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "开始" in result
        assert "结束" in result


# ============================================================
# 组织架构树测试
# ============================================================

class TestOrgTree:
    """组织架构树测试"""

    def test_basic_generation(self):
        """测试基本组织树生成"""
        dsl = {
            "type": "org-tree",
            "title": "测试组织架构",
            "theme": "blue",
            "root": {
                "name": "张总",
                "title": "总经理",
                "children": [
                    {"name": "李经理", "title": "技术部经理"},
                    {"name": "王经理", "title": "产品部经理"}
                ]
            }
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "\\end{tikzpicture}" in result
        assert "org-person" in result
        assert "org-person-root" in result
        assert "张总" in result
        assert "李经理" in result
        assert "总经理" in result

    def test_deep_tree(self):
        """测试深层嵌套树"""
        dsl = {
            "type": "org-tree",
            "root": {
                "name": "CEO",
                "children": [
                    {
                        "name": "CTO",
                        "children": [
                            {
                                "name": "Tech Lead",
                                "children": [
                                    {"name": "Developer"}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "CEO" in result
        assert "CTO" in result
        assert "Tech Lead" in result
        assert "Developer" in result

    def test_minimal_tree(self):
        """测试边界情况：最少节点（只有根节点）"""
        dsl = {
            "type": "org-tree",
            "root": {
                "name": "光杆司令",
                "title": "创始人"
            }
        }
        result = generate_tikz(dsl)
        assert "\\begin{tikzpicture}" in result
        assert "光杆司令" in result
        assert "创始人" in result

    def test_theme_orange(self):
        """测试橙色主题组织树——验证使用颜色名系统"""
        dsl = {
            "type": "org-tree",
            "theme": "orange",
            "root": {
                "name": "老大",
                "children": [
                    {"name": "小弟"}
                ]
            }
        }
        result = generate_tikz(dsl)
        assert "MainColor" in result
        assert "SmallColor" in result

    def test_connections_exist(self):
        """测试连接线存在"""
        dsl = {
            "type": "org-tree",
            "root": {
                "name": "父节点",
                "children": [
                    {"name": "子节点"}
                ]
            }
        }
        result = generate_tikz(dsl)
        assert "\\draw[-" in result


# ============================================================
# 通用错误处理测试
# ============================================================

class TestErrorHandling:
    """错误处理测试"""

    def test_unknown_type(self):
        """测试未知图类型抛出异常"""
        dsl = {
            "type": "unknown-type"
        }
        with pytest.raises(ValueError, match="不支持的图类型"):
            generate_tikz(dsl)

    def test_default_theme(self):
        """测试默认主题（不指定 theme 时使用颜色名系统，默认 blue 由 theme-loader 处理）"""
        dsl = {
            "type": "layered-architecture",
            "layers": [
                {
                    "name": "层1",
                    "modules": [{"name": "模块1"}]
                }
            ]
        }
        result = generate_tikz(dsl)
        assert "MainColor" in result
        assert "SubColor" in result
        assert "TinyColor" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
