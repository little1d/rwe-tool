"""最小 MCP 服务器封装，基于 fastmcp 暴露 RWE 工具。"""

from __future__ import annotations

import argparse
import json
from typing import List, Optional
import keyword

try:  # pragma: no cover - 运行时依赖
    from fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "fastmcp 未安装，无法启动 MCP 服务器。请运行 `pip install fastmcp`。"
    ) from exc

from .engine import RWEUniverse


def _build_tool_function(engine: RWEUniverse, tool_name: str, schema: dict):
    """根据 JSON schema 构造具有显式参数的 handler。"""

    properties = schema.get("properties") or {}
    required = set(schema.get("required") or [])

    if not properties:
        async def handler():
            return engine.run({"name": tool_name, "arguments": {}})

        return handler

    # 如果存在非法 Python 标识符，退化为单个 dict 参数
    if any(
        (not name.isidentifier()) or keyword.iskeyword(name) for name in properties.keys()
    ):
        async def handler(arguments: dict):
            if not isinstance(arguments, dict):
                raise ValueError("arguments 参数必须是字典")
            return engine.run({"name": tool_name, "arguments": arguments})

        return handler

    param_defs = []
    for name in properties.keys():
        if name in required:
            param_defs.append(name)
        else:
            param_defs.append(f"{name}=None")

    params_str = ", ".join(param_defs)
    lines = []
    if params_str:
        lines.append(f"async def generated({params_str}):")
    else:
        lines.append("async def generated():")
    lines.append("    arguments = {}")
    for name in properties.keys():
        lines.append(f"    if {name} is not None:")
        lines.append(f"        arguments['{name}'] = {name}")
    lines.append(
        f"    return engine.run({{'name': '{tool_name}', 'arguments': arguments}})"
    )

    local_ns = {"engine": engine}
    exec("\n".join(lines), local_ns)
    return local_ns["generated"]


def _attach_tools(server: FastMCP, engine: RWEUniverse):
    """将当前加载的工具注册到 fastmcp 实例。"""

    for tool_name, meta in engine.list_tools().items():
        parameter_schema = meta.get("parameter", {"type": "object"})
        description = meta.get("description", "")

        handler_fn = _build_tool_function(engine, tool_name, parameter_schema)

        server.tool(
            name=tool_name,
            description=description,
            annotations={"parameters": parameter_schema},
        )(handler_fn)


def build_server(
    *,
    include_tools: Optional[List[str]] = None,
    exclude_tools: Optional[List[str]] = None,
    name: str = "RWE MCP Server",
) -> FastMCP:
    """根据过滤条件构建 fastmcp 服务器。"""

    engine = RWEUniverse()
    engine.load_tools(include_tools=include_tools, exclude_tools=exclude_tools)
    server = FastMCP(name=name)
    _attach_tools(server, engine)
    return server


def run_server(
    *,
    include_tools: Optional[List[str]] = None,
    exclude_tools: Optional[List[str]] = None,
    name: str = "RWE MCP Server",
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """启动 fastmcp 服务器。"""

    server = build_server(
        include_tools=include_tools, exclude_tools=exclude_tools, name=name
    )
    transport_kwargs = {}
    if transport != "stdio":
        transport_kwargs = {"host": host, "port": port}
    server.run(transport=transport, **transport_kwargs)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RWE MCP 服务器")
    parser.add_argument(
        "--include-tools",
        nargs="+",
        help="仅暴露指定工具（默认全部）",
    )
    parser.add_argument(
        "--exclude-tools",
        nargs="+",
        help="排除指定工具",
    )
    parser.add_argument("--name", default="RWE MCP Server", help="服务器名称")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="MCP 传输方式（默认 stdio）",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP 监听地址")
    parser.add_argument("--port", type=int, default=8000, help="HTTP 监听端口")
    parser.add_argument(
        "--print-tools",
        action="store_true",
        help="仅打印可用工具并退出",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None):
    args = parse_args(argv)
    engine = RWEUniverse()
    loaded = engine.load_tools(
        include_tools=args.include_tools, exclude_tools=args.exclude_tools
    )
    if args.print_tools:
        print(
            json.dumps(
                {
                    "name": args.name,
                    "total": len(loaded),
                    "tools": engine.list_tools(),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    server = build_server(
        include_tools=args.include_tools,
        exclude_tools=args.exclude_tools,
        name=args.name,
    )
    transport_kwargs = {}
    if args.transport != "stdio":
        transport_kwargs = {"host": args.host, "port": args.port}
    server.run(transport=args.transport, **transport_kwargs)


if __name__ == "__main__":
    main()
