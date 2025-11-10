from rwe_tool.base import BaseTool
from rwe_tool.registry import register_tool


@register_tool(
    "RWEUtility",
    config={
        "name": "rwe_echo",
        "description": "Echo back the input text for connectivity tests.",
        "parameter": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "text to echo"}
            },
            "required": ["text"],
        },
    },
)
class RWEEchoTool(BaseTool):
    def run(self, arguments=None, **kwargs):
        arguments = arguments or kwargs or {}
        text = arguments.get("text", "")
        return {
            "success": True,
            "echo": text,
        }
