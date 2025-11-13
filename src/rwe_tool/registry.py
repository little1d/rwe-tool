"""工具注册与发现机制。"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - 仅用于类型提示
    from .base import BaseTool


@dataclass
class ToolDefinition:
    """记录工具类与其配置。"""

    name: str
    tool_type: str
    description: str
    parameter_schema: Dict
    tool_class: Type["BaseTool"]
    raw_config: Dict


_REGISTERED_TYPES: Dict[str, Type["BaseTool"]] = {}
_REGISTERED_TOOLS: Dict[str, ToolDefinition] = {}


def register_tool(tool_type_name: Optional[str] = None, *, config: Optional[Dict] = None):
    """装饰器：注册工具类型与其配置。"""

    if config is None:
        raise ValueError("register_tool 需要提供 config 参数")

    def decorator(cls: Type["BaseTool"]):
        nonlocal tool_type_name
        tool_type_name = tool_type_name or cls.__name__

        tool_name = config.get("name") or cls.__name__
        description = config.get("description", "")
        schema = config.get("parameter", {"type": "object", "properties": {}})

        definition = ToolDefinition(
            name=tool_name,
            tool_type=tool_type_name,
            description=description,
            parameter_schema=schema,
            tool_class=cls,
            raw_config=config,
        )

        if tool_name in _REGISTERED_TOOLS:
            raise ValueError(f"工具 {tool_name} 已存在，无法重复注册")

        _REGISTERED_TYPES[tool_type_name] = cls
        _REGISTERED_TOOLS[tool_name] = definition
        return cls

    return decorator


def list_tool_definitions() -> List[ToolDefinition]:
    """返回所有已注册的工具定义。"""

    return list(_REGISTERED_TOOLS.values())


def get_tool_definition(name: str) -> ToolDefinition:
    """根据工具名获取定义。"""

    if name not in _REGISTERED_TOOLS:
        raise KeyError(f"未找到工具: {name}")
    return _REGISTERED_TOOLS[name]
