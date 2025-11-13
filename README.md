# RWE Tool

一个最小可用的 RWE（Real-World Evidence）tool universe，内置：

- 轻量级核心引擎 `RWEUniverse`
- 基础工具基类与装饰器式注册系统
- 基于 `fastmcp` 的 stdio MCP 服务器入口

## 安装

```bash
uv pip install -e .
```

（建议在 Conda/venv 中执行）

## 快速体验

### 1. Python 调用

```python
from rwe_tool import RWEUniverse

engine = RWEUniverse()
engine.load_tools()
print(engine.run({
    "name": "rwe_echo",
    "arguments": {"text": "Hello RWE"}
}))
```

### 2. 本地测试

```bash
uv run python test.py
```

输出应包含：

```
测试结果:
{'success': True, 'echo': 'Hello, RWE Tool!'}
```

### 3. MCP 服务器（stdio）

```bash
uv run rwe-mcp-server --include-tools rwe_echo --name "RWE MCP"
```

- `--include-tools`：只暴露列出的工具，可省略表示加载全部
- `--exclude-tools`：排除指定工具
- `--print-tools`：仅打印工具列表并退出（调试）

确认 MCP 正常可运行：

```bash
uv run rwe-mcp-server --print-tools
```

## Qwen Code 集成

1. 编辑 `~/.qwen/settings.json`（或项目内 `.qwen/settings.json`）
2. 添加 rwe-tool MCP 配置（使用 `uv run`）：

```json
{
  "mcpServers": {
    "rwe-mcp-servers": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/rwe-tool",
        "run",
        "rwe-mcp-server"
      ]
    }
  }
}
```

> 将 `/absolute/path/to/rwe-tool` 替换成本地仓库路径，可按需附加 `--include-tools ...`。

3. 启动 Qwen Code，输入 `/mcp`，应看到 `rwe-mcp-servers - Connected`
4. 提示词示例：“列出 rwe-tool 暴露的工具”“调用 rwe_echo 返回 hello world”

## 如何新增 Tool

### Step 1. 创建文件并注册

1. **创建工具文件**

   ```python
   from rwe_tool.base import BaseTool
   from rwe_tool.registry import register_tool


   @register_tool(
       "RWEUtility",
       config={
           "name": "rwe_demo",
           "description": "返回入参的简单统计",
           "parameter": {
               "type": "object",
               "properties": {
                   "values": {
                       "type": "array",
                       "items": {"type": "number"},
                       "description": "待统计的数值数组"
                   }
               },
               "required": ["values"]
           }
       },
   )
   class RWEDemoTool(BaseTool):
       def run(self, arguments=None, **_):
           values = arguments["values"]
           return {
               "count": len(values),
               "min": min(values),
               "max": max(values),
               "mean": sum(values) / len(values),
           }
   ```

2. **在 `src/rwe_tool/tools/__init__.py` 中导入**  
   `from .rwe_demo import RWEDemoTool`

3. **重新加载并验证**

   ```bash
   uv run python test.py
   uv run rwe-mcp-server --print-tools
   ```

`RWEUniverse` 会自动发现所有注册工具；需要按场景缩减时可配合 `--include-tools`/`--exclude-tools`。

## MCP 调试 Checklist

1. `uv run python test.py` —— 本地执行通过
2. `uv run rwe-mcp-server --print-tools` —— 正常输出工具清单
3. `uv run rwe-mcp-server` —— 看到 FastMCP Banner，保持运行
4. Qwen `/mcp` —— `rwe-mcp-servers` 状态为 Connected
