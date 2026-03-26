"""Tushare MCP Server 入口模块"""

import asyncio
import sys
from .server import main

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
