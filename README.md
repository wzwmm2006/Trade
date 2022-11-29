# Trade
some trade samples

1、import ccxt
--概述：
通过ccxt库实现从cex获取交易数据。
--核心逻辑：
使用fetchOHLCV()接口获取OHLCV烛线图数据
OHLCV烛线图数据结构：
[
    [
        1504541580000, // UTC 时间戳，单位：毫秒
        4235.4,        // (O)开盘价格, float
        4240.6,        // (H)最高价格, float
        4230.0,        // (L)最低价格, float
        4230.7,        // (C)收盘价格, float
        37.72941911    // (V)交易量，以基准货币计量， float
    ],
    ...
]
注意事项：
fetchOHLCV (symbol, timeframe = '1m', since = None, limit = None, params = {})
单次调用能够从cex获取的数据是有限制的，如果需要获取截止到当前时间的所有数据，需要用循环的方式获取。

2、import pandas
--概述：
通过pandas库进行数据的处理、分析、读取存入csv；
--核心逻辑：
根据step1获取的BTCUSDT/ETHUSDT的日线数据，计算最近N天日线级别涨跌幅
getChange()
                            ||
根据最近N天日线级别涨跌幅，通过BTC/ETH换仓策略(待优化),计算当日的持仓币种/持仓币种数量/持仓价值U
calHold()
                            ||
计算每年涨幅/年华收益率/最大回撤/净值/等需要的数据（N份数据）
backTest()
                            ||
遍历N，获取最优策略(截至目前净值增长最高)
getSumData()
                            ||
绘制最优策略的数据

3、import matplotlib.pyplot as plt
--概述
通过matplotlib进行折线图绘制，主要绘制最优策略的净值变化趋势
--核心逻辑
plt.annotate()进行注释箭头

