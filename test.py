#!/usr/bin/env python3
"""基础测试：验证 rwe_echo 工具是否正常工作"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from rwe_tool import RWEUniverse  # noqa: E402

engine = RWEUniverse()
engine.load_tools()

result = engine.run({"name": "rwe_echo", "arguments": {"text": "Hello, RWE Tool!"}})

print("测试结果:")
print(result)
