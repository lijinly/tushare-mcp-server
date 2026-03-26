# Tushare MCP Server

基于Tushare金融数据API的MCP (Model Context Protocol) Server。

## 功能

提供以下金融数据查询工具：

- **股票基础数据**: 股票列表、交易日历
- **行情数据**: 日线、周线、月线行情
- **财务数据**: 利润表、资产负债表、现金流量表
- **市场数据**: 涨跌停、龙虎榜、资金流向
- **宏观数据**: 经济数据、利率、汇率

## 安装

```bash
pip install -e .
```

## 配置

在使用前需要配置Tushare的API Token。可以通过以下方式设置：

### 环境变量
```bash
export TUSHARE_TOKEN="your_token_here"
```

### MCP配置
在Claude Desktop或其他MCP客户端的配置中添加：

```json
{
  "mcpServers": {
    "tushare": {
      "command": "python",
      "args": ["-m", "tushare_mcp_server"],
      "env": {
        "TUSHARE_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 使用

启动服务器：
```bash
python -m tushare_mcp_server
```

## 依赖

- Python >= 3.10
- tushare >= 1.4.0
- mcp >= 1.0.0
- pandas >= 2.0.0

## 许可证

MIT
