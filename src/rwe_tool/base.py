"""基础工具抽象与通用异常。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


class ToolError(Exception):
    """所有工具相关异常的基类。"""


class ToolValidationError(ToolError):
    """参数校验失败。"""


class ToolExecutionError(ToolError):
    """工具执行过程中出现的错误。"""


@dataclass
class ValidationResult:
    """参数校验结果，便于后续扩展。"""

    arguments: Dict[str, Any]


class BaseTool:
    """所有 RWE 工具的基类，封装公共配置与校验逻辑。"""

    def __init__(self, tool_config: Optional[Dict[str, Any]] = None):
        self.tool_config = tool_config or {}

    def validate(self, arguments: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """根据 JSON schema 中的 required 字段做最小校验。"""
        arguments = arguments or {}
        schema = self.tool_config.get("parameter", {})
        required_fields = schema.get("required", [])
        missing = [field for field in required_fields if field not in arguments]
        if missing:
            raise ToolValidationError(f"缺少必要参数: {', '.join(missing)}")
        return ValidationResult(arguments=arguments)

    def run(self, arguments: Optional[Dict[str, Any]] = None, **_) -> Any:  # pragma: no cover - 抽象方法
        """子类必须实现的核心逻辑。"""
        raise NotImplementedError("工具需要实现 run 方法")
