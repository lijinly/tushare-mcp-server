"""Tushare MCP Server 主服务"""

import os
import json
from typing import Any, Sequence
from datetime import datetime, timedelta

import tushare as ts
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp.server.models import InitializationOptions

# 创建MCP服务器
server = Server("tushare-mcp-server")

# 全局pro接口实例
ts_pro = None


def get_ts_pro():
    """获取Tushare pro接口实例"""
    global ts_pro
    if ts_pro is None:
        token = os.environ.get("TUSHARE_TOKEN")
        if not token:
            raise ValueError("TUSHARE_TOKEN environment variable is not set")
        ts_pro = ts.pro_api(token)
    return ts_pro


# ========== 工具定义 ==========

STOCK_BASIC_TOOL = Tool(
    name="stock_basic",
    description="获取股票基础信息，包括股票代码、名称、上市日期、所属行业等",
    inputSchema={
        "type": "object",
        "properties": {
            "exchange": {
                "type": "string",
                "description": "交易所代码，SSE为上交所，SZSE为深交所，BSE为北交所",
                "enum": ["", "SSE", "SZSE", "BSE"]
            },
            "list_status": {
                "type": "string",
                "description": "上市状态，L上市，D退市，P暂停上市",
                "enum": ["L", "D", "P"],
                "default": "L"
            },
            "fields": {
                "type": "string",
                "description": "需要返回的字段，用逗号分隔，默认返回所有字段"
            }
        }
    }
)

DAILY_QUOTE_TOOL = Tool(
    name="daily_quote",
    description="获取A股日线行情数据，包括开盘价、收盘价、最高价、最低价、成交量等",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如000001.SZ"
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

TRADE_CAL_TOOL = Tool(
    name="trade_cal",
    description="获取交易日历信息",
    inputSchema={
        "type": "object",
        "properties": {
            "exchange": {
                "type": "string",
                "description": "交易所，SSE为上交所，SZSE为深交所",
                "enum": ["SSE", "SZSE"],
                "default": "SSE"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "is_open": {
                "type": "string",
                "description": "是否交易，0休市，1交易",
                "enum": ["0", "1"]
            }
        }
    }
)

STOCK_COMPANY_TOOL = Tool(
    name="stock_company",
    description="获取上市公司基本信息",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "exchange": {
                "type": "string",
                "description": "交易所代码，SSE/SZSE",
                "enum": ["SSE", "SZSE"]
            }
        }
    }
)

FINA_INDICATOR_TOOL = Tool(
    name="fina_indicator",
    description="获取上市公司财务指标数据，包括ROE、毛利率、净利率等",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "ann_date": {
                "type": "string",
                "description": "公告日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "period": {
                "type": "string",
                "description": "报告期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

INCOME_TOOL = Tool(
    name="income",
    description="获取上市公司利润表数据",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "ann_date": {
                "type": "string",
                "description": "公告日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "period": {
                "type": "string",
                "description": "报告期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

BALANCE_SHEET_TOOL = Tool(
    name="balance_sheet",
    description="获取上市公司资产负债表数据",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "ann_date": {
                "type": "string",
                "description": "公告日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "period": {
                "type": "string",
                "description": "报告期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

CASHFLOW_TOOL = Tool(
    name="cashflow",
    description="获取上市公司现金流量表数据",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "ann_date": {
                "type": "string",
                "description": "公告日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "period": {
                "type": "string",
                "description": "报告期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

DAILY_LIMIT_TOOL = Tool(
    name="daily_limit",
    description="获取每日涨跌停股票统计",
    inputSchema={
        "type": "object",
        "properties": {
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "limit_type": {
                "type": "string",
                "description": "涨跌停类型，U涨停，D跌停，Z炸板",
                "enum": ["U", "D", "Z"]
            }
        }
    }
)

MONEYFLOW_HSGT_TOOL = Tool(
    name="moneyflow_hsgt",
    description="获取沪深港通资金流向数据",
    inputSchema={
        "type": "object",
        "properties": {
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            }
        }
    }
)

MARGIN_TOOL = Tool(
    name="margin",
    description="获取融资融券交易汇总数据（按交易所），包括融资余额、融资买入额、融资偿还额、融券余额等",
    inputSchema={
        "type": "object",
        "properties": {
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "exchange_id": {
                "type": "string",
                "description": "交易所代码，SSE为上交所，SZSE为深交所，BSE为北交所",
                "enum": ["SSE", "SZSE", "BSE"]
            }
        }
    }
)

MARGIN_DETAIL_TOOL = Tool(
    name="margin_detail",
    description="获取融资融券交易明细数据（按股票代码），包括个股融资余额、融资买入额、融券余量等",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，支持多个，逗号分隔"
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            }
        }
    }
)

HOLDERS_TOOL = Tool(
    name="top10_holders",
    description="获取上市公司前十大股东数据",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            },
            "period": {
                "type": "string",
                "description": "报告期，格式YYYYMMDD"
            },
            "ann_date": {
                "type": "string",
                "description": "公告日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

CONCEPT_TOOL = Tool(
    name="concept",
    description="获取概念股分类列表",
    inputSchema={
        "type": "object",
        "properties": {
            "src": {
                "type": "string",
                "description": "来源，默认为ts"
            }
        }
    }
)

CONCEPT_DETAIL_TOOL = Tool(
    name="concept_detail",
    description="获取概念股明细",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "概念代码"
            },
            "concept_name": {
                "type": "string",
                "description": "概念名称"
            },
            "ts_code": {
                "type": "string",
                "description": "股票代码"
            }
        }
    }
)

INDEX_BASIC_TOOL = Tool(
    name="index_basic",
    description="获取指数基础信息",
    inputSchema={
        "type": "object",
        "properties": {
            "market": {
                "type": "string",
                "description": "市场，MSCI/CSI/SSE/SZSE/CICC/CSI/申万指数/SW",
                "enum": ["MSCI", "CSI", "SSE", "SZSE", "CICC", "申万指数", "SW"]
            },
            "publisher": {
                "type": "string",
                "description": "发布商"
            },
            "category": {
                "type": "string",
                "description": "指数类别"
            }
        }
    }
)

INDEX_DAILY_TOOL = Tool(
    name="index_daily",
    description="获取指数日线行情",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "指数代码，如000001.SH"
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            }
        },
        "required": ["ts_code"]
    }
)

FUTURE_BASIC_TOOL = Tool(
    name="future_basic",
    description="获取期货合约基础信息",
    inputSchema={
        "type": "object",
        "properties": {
            "exchange": {
                "type": "string",
                "description": "交易所代码，CFFEX/DCE/CZCE/SHFE/INE/GFEX"
            },
            "fut_type": {
                "type": "string",
                "description": "合约类型，1普通合约，2主力合约，3连续合约",
                "enum": ["1", "2", "3"]
            }
        }
    }
)

FUTURE_DAILY_TOOL = Tool(
    name="future_daily",
    description="获取期货日线行情",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "合约代码"
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "exchange": {
                "type": "string",
                "description": "交易所"
            }
        }
    }
)

DAILY_BASIC_TOOL = Tool(
    name="daily_basic",
    description="获取A股每日基本面指标，包括PE、PB、PS、总市值、流通市值等估值数据",
    inputSchema={
        "type": "object",
        "properties": {
            "ts_code": {
                "type": "string",
                "description": "股票代码，如000001.SZ"
            },
            "trade_date": {
                "type": "string",
                "description": "交易日期，格式YYYYMMDD"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期，格式YYYYMMDD"
            },
            "end_date": {
                "type": "string",
                "description": "结束日期，格式YYYYMMDD"
            },
            "fields": {
                "type": "string",
                "description": "需要返回的字段，用逗号分隔，可选字段包括：ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv"
            }
        },
        "required": ["ts_code"]
    }
)

# 工具映射表
TOOLS = [
    STOCK_BASIC_TOOL,
    DAILY_QUOTE_TOOL,
    TRADE_CAL_TOOL,
    STOCK_COMPANY_TOOL,
    FINA_INDICATOR_TOOL,
    INCOME_TOOL,
    BALANCE_SHEET_TOOL,
    CASHFLOW_TOOL,
    DAILY_LIMIT_TOOL,
    MONEYFLOW_HSGT_TOOL,
    MARGIN_TOOL,
    MARGIN_DETAIL_TOOL,
    HOLDERS_TOOL,
    CONCEPT_TOOL,
    CONCEPT_DETAIL_TOOL,
    INDEX_BASIC_TOOL,
    INDEX_DAILY_TOOL,
    FUTURE_BASIC_TOOL,
    FUTURE_DAILY_TOOL,
    DAILY_BASIC_TOOL,
]


# ========== 工具处理函数 ==========

def df_to_json(df) -> str:
    """将DataFrame转换为JSON字符串"""
    if df is None or df.empty:
        return json.dumps({"data": [], "count": 0})
    
    # 处理日期时间类型
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    result = {
        "data": df.to_dict(orient='records'),
        "count": len(df),
        "columns": list(df.columns)
    }
    return json.dumps(result, ensure_ascii=False, default=str)


async def handle_stock_basic(args: dict) -> list:
    """处理股票基础信息查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'exchange' in args and args['exchange']:
        params['exchange'] = args['exchange']
    if 'list_status' in args:
        params['list_status'] = args['list_status']
    if 'fields' in args and args['fields']:
        params['fields'] = args['fields']
    
    df = pro.stock_basic(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_daily_quote(args: dict) -> list:
    """处理日线行情查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    
    df = pro.daily(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_trade_cal(args: dict) -> list:
    """处理交易日历查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'exchange' in args:
        params['exchange'] = args['exchange']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'is_open' in args and args['is_open']:
        params['is_open'] = args['is_open']
    
    df = pro.trade_cal(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_stock_company(args: dict) -> list:
    """处理上市公司信息查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'ts_code' in args and args['ts_code']:
        params['ts_code'] = args['ts_code']
    if 'exchange' in args and args['exchange']:
        params['exchange'] = args['exchange']
    
    df = pro.stock_company(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_fina_indicator(args: dict) -> list:
    """处理财务指标查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'ann_date' in args and args['ann_date']:
        params['ann_date'] = args['ann_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'period' in args and args['period']:
        params['period'] = args['period']
    
    df = pro.fina_indicator(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_income(args: dict) -> list:
    """处理利润表查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'ann_date' in args and args['ann_date']:
        params['ann_date'] = args['ann_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'period' in args and args['period']:
        params['period'] = args['period']
    
    df = pro.income(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_balance_sheet(args: dict) -> list:
    """处理资产负债表查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'ann_date' in args and args['ann_date']:
        params['ann_date'] = args['ann_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'period' in args and args['period']:
        params['period'] = args['period']
    
    df = pro.balancesheet(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_cashflow(args: dict) -> list:
    """处理现金流量表查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'ann_date' in args and args['ann_date']:
        params['ann_date'] = args['ann_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'period' in args and args['period']:
        params['period'] = args['period']
    
    df = pro.cashflow(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_daily_limit(args: dict) -> list:
    """处理涨跌停统计查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'ts_code' in args and args['ts_code']:
        params['ts_code'] = args['ts_code']
    if 'limit_type' in args and args['limit_type']:
        params['limit_type'] = args['limit_type']
    
    df = pro.limit_list(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_moneyflow_hsgt(args: dict) -> list:
    """处理沪深港通资金流向查询"""
    pro = get_ts_pro()

    params = {}
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']

    df = pro.moneyflow_hsgt(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_margin(args: dict) -> list:
    """处理融资融券交易汇总查询"""
    pro = get_ts_pro()

    params = {}
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'exchange_id' in args and args['exchange_id']:
        params['exchange_id'] = args['exchange_id']

    df = pro.margin(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_margin_detail(args: dict) -> list:
    """处理融资融券交易明细查询"""
    pro = get_ts_pro()

    params = {}
    if 'ts_code' in args and args['ts_code']:
        params['ts_code'] = args['ts_code']
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']

    df = pro.margin_detail(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_holders(args: dict) -> list:
    """处理前十大股东查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'period' in args and args['period']:
        params['period'] = args['period']
    if 'ann_date' in args and args['ann_date']:
        params['ann_date'] = args['ann_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    
    df = pro.top10_holders(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_concept(args: dict) -> list:
    """处理概念股分类查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'src' in args and args['src']:
        params['src'] = args['src']
    
    df = pro.concept(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_concept_detail(args: dict) -> list:
    """处理概念股明细查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'id' in args and args['id']:
        params['id'] = args['id']
    if 'concept_name' in args and args['concept_name']:
        params['concept_name'] = args['concept_name']
    if 'ts_code' in args and args['ts_code']:
        params['ts_code'] = args['ts_code']
    
    df = pro.concept_detail(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_index_basic(args: dict) -> list:
    """处理指数基础信息查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'market' in args and args['market']:
        params['market'] = args['market']
    if 'publisher' in args and args['publisher']:
        params['publisher'] = args['publisher']
    if 'category' in args and args['category']:
        params['category'] = args['category']
    
    df = pro.index_basic(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_index_daily(args: dict) -> list:
    """处理指数日线行情查询"""
    pro = get_ts_pro()
    
    params = {'ts_code': args['ts_code']}
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    
    df = pro.index_daily(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_future_basic(args: dict) -> list:
    """处理期货基础信息查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'exchange' in args and args['exchange']:
        params['exchange'] = args['exchange']
    if 'fut_type' in args and args['fut_type']:
        params['fut_type'] = args['fut_type']
    
    df = pro.fut_basic(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_future_daily(args: dict) -> list:
    """处理期货日线行情查询"""
    pro = get_ts_pro()
    
    params = {}
    if 'ts_code' in args and args['ts_code']:
        params['ts_code'] = args['ts_code']
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'exchange' in args and args['exchange']:
        params['exchange'] = args['exchange']
    
    df = pro.fut_daily(**params)
    return [TextContent(type="text", text=df_to_json(df))]


async def handle_daily_basic(args: dict) -> list:
    """处理每日基本面指标查询（PE/PB/PS/市值等）"""
    pro = get_ts_pro()

    params = {'ts_code': args['ts_code']}
    if 'trade_date' in args and args['trade_date']:
        params['trade_date'] = args['trade_date']
    if 'start_date' in args and args['start_date']:
        params['start_date'] = args['start_date']
    if 'end_date' in args and args['end_date']:
        params['end_date'] = args['end_date']
    if 'fields' in args and args['fields']:
        params['fields'] = args['fields']

    df = pro.daily_basic(**params)
    return [TextContent(type="text", text=df_to_json(df))]


# 工具处理函数映射
TOOL_HANDLERS = {
    "stock_basic": handle_stock_basic,
    "daily_quote": handle_daily_quote,
    "trade_cal": handle_trade_cal,
    "stock_company": handle_stock_company,
    "fina_indicator": handle_fina_indicator,
    "income": handle_income,
    "balance_sheet": handle_balance_sheet,
    "cashflow": handle_cashflow,
    "daily_limit": handle_daily_limit,
    "moneyflow_hsgt": handle_moneyflow_hsgt,
    "margin": handle_margin,
    "margin_detail": handle_margin_detail,
    "top10_holders": handle_holders,
    "concept": handle_concept,
    "concept_detail": handle_concept_detail,
    "index_basic": handle_index_basic,
    "index_daily": handle_index_daily,
    "future_basic": handle_future_basic,
    "future_daily": handle_future_daily,
    "daily_basic": handle_daily_basic,
}


# ========== MCP Server 事件处理 ==========

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """处理工具调用"""
    if name not in TOOL_HANDLERS:
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        handler = TOOL_HANDLERS[name]
        return await handler(arguments)
    except Exception as e:
        error_msg = json.dumps({"error": str(e)}, ensure_ascii=False)
        return [TextContent(type="text", text=error_msg)]


# ========== 主入口 ==========

async def main():
    """服务器主入口"""
    # 验证token是否配置
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        print("Error: TUSHARE_TOKEN environment variable is not set", flush=True)
        print("Please set your Tushare API token: export TUSHARE_TOKEN=your_token", flush=True)
        return 1
    
    # 测试连接
    try:
        pro = get_ts_pro()
        # 简单测试查询
        test_df = pro.trade_cal(exchange='SSE', limit=1)
        print(f"Tushare MCP Server started successfully", flush=True)
        print(f"Available tools: {len(TOOLS)}", flush=True)
    except Exception as e:
        print(f"Error connecting to Tushare API: {e}", flush=True)
        return 1
    
    # 启动stdio服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tushare-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )
    
    return 0


if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main()))
