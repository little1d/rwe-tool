"""RWEUniverse 核心引擎，实现工具加载、列举与执行。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base import BaseTool, ToolError, ToolExecutionError
from .registry import list_tool_definitions, get_tool_definition, ToolDefinition


@dataclass
class ToolInstance:
    definition: ToolDefinition
    instance: BaseTool


class RWEUniverse:
    """最小可用的工具执行引擎。"""

    def __init__(self):
        self._loaded_tools: Dict[str, ToolInstance] = {}

    def load_tools(
        self,
        include_tools: Optional[List[str]] = None,
        exclude_tools: Optional[List[str]] = None,
    ) -> List[str]:
        """根据过滤条件实例化并缓存工具。"""

        self._loaded_tools.clear()
        include_set = set(include_tools) if include_tools else None
        exclude_set = set(exclude_tools) if exclude_tools else set()

        for definition in list_tool_definitions():
            name = definition.name
            if include_set and name not in include_set:
                continue
            if name in exclude_set:
                continue
            self._loaded_tools[name] = ToolInstance(
                definition=definition,
                instance=definition.tool_class(definition.raw_config),
            )
        return list(self._loaded_tools.keys())

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """返回当前实例化工具的元数据。"""

        return {
            name: {
                "description": entry.definition.description,
                "parameter": entry.definition.parameter_schema,
                "type": entry.definition.tool_type,
            }
            for name, entry in self._loaded_tools.items()
        }

    def ensure_loaded(self):
        if not self._loaded_tools:
            self.load_tools()

    def run(self, function_call: Dict[str, Any]) -> Any:
        """执行标准 function_call 字典（包含 name / arguments）。"""

        self.ensure_loaded()
        if "name" not in function_call:
            raise ToolError("function_call 需要包含 name 字段")

        tool_name = function_call["name"]
        arguments = function_call.get("arguments") or {}

        if tool_name not in self._loaded_tools:
            # 尝试懒加载单个工具
            try:
                definition = get_tool_definition(tool_name)
            except KeyError as exc:
                raise ToolError(f"未注册工具: {tool_name}") from exc
            instance = definition.tool_class(definition.raw_config)
            self._loaded_tools[tool_name] = ToolInstance(
                definition=definition, instance=instance
            )

        entry = self._loaded_tools[tool_name]
        validated_args = entry.instance.validate(arguments).arguments
        try:
            return entry.instance.run(validated_args)
        except ToolError:
            raise
        except Exception as exc:  # pragma: no cover - 真实执行时捕获
            raise ToolExecutionError(f"{tool_name} 执行失败: {exc}") from exc
