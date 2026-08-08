"""
DSL 数据结构定义
定义三种图类型的配置数据类
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Module:
    """模块配置"""
    name: str
    desc: str = ""
    wide: bool = False


@dataclass
class Layer:
    """层配置"""
    name: str
    style: str = "medium"
    modules: List[Module] = field(default_factory=list)


@dataclass
class LayeredArchConfig:
    """分层架构图配置"""
    title: str = ""
    theme: str = "blue"
    layers: List[Layer] = field(default_factory=list)
    connections: List[dict] = field(default_factory=list)


@dataclass
class FlowNode:
    """流程节点"""
    id: str
    label: str
    type: str = "process"


@dataclass
class FlowEdge:
    """流程边"""
    from_id: str
    to_id: str
    label: str = ""


@dataclass
class FlowchartConfig:
    """流程图配置"""
    title: str = ""
    theme: str = "blue"
    direction: str = "TB"
    nodes: List[FlowNode] = field(default_factory=list)
    edges: List[FlowEdge] = field(default_factory=list)


@dataclass
class OrgNode:
    """组织节点"""
    name: str
    title: str = ""
    children: List["OrgNode"] = field(default_factory=list)


@dataclass
class OrgTreeConfig:
    """组织架构图配置"""
    title: str = ""
    theme: str = "blue"
    root: Optional[OrgNode] = None


def dict_to_layered_arch(data: dict) -> LayeredArchConfig:
    """将字典转换为分层架构图配置"""
    layers = []
    for layer_data in data.get("layers", []):
        modules = []
        for mod_data in layer_data.get("modules", []):
            modules.append(Module(
                name=mod_data.get("name", ""),
                desc=mod_data.get("desc", ""),
                wide=mod_data.get("wide", False)
            ))
        layers.append(Layer(
            name=layer_data.get("name", ""),
            style=layer_data.get("style", "medium"),
            modules=modules
        ))
    return LayeredArchConfig(
        title=data.get("title", ""),
        theme=data.get("theme", "blue"),
        layers=layers,
        connections=data.get("connections", [])
    )


def dict_to_flowchart(data: dict) -> FlowchartConfig:
    """将字典转换为流程图配置"""
    nodes = []
    for node_data in data.get("nodes", []):
        nodes.append(FlowNode(
            id=node_data.get("id", ""),
            label=node_data.get("label", ""),
            type=node_data.get("type", "process")
        ))
    edges = []
    for edge_data in data.get("edges", []):
        edges.append(FlowEdge(
            from_id=edge_data.get("from", ""),
            to_id=edge_data.get("to", ""),
            label=edge_data.get("label", "")
        ))
    return FlowchartConfig(
        title=data.get("title", ""),
        theme=data.get("theme", "blue"),
        direction=data.get("direction", "TB"),
        nodes=nodes,
        edges=edges
    )


def dict_to_org_node(data: dict) -> OrgNode:
    """递归将字典转换为组织节点"""
    children = []
    for child_data in data.get("children", []):
        children.append(dict_to_org_node(child_data))
    return OrgNode(
        name=data.get("name", ""),
        title=data.get("title", ""),
        children=children
    )


def dict_to_org_tree(data: dict) -> OrgTreeConfig:
    """将字典转换为组织架构图配置"""
    root = None
    root_data = data.get("root")
    if root_data:
        root = dict_to_org_node(root_data)
    return OrgTreeConfig(
        title=data.get("title", ""),
        theme=data.get("theme", "blue"),
        root=root
    )
