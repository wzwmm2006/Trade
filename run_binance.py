import ccxt
import time
import numpy
import pandas as pd
import json 
import datetime
import matplotlib.pyplot as plt
import random

'''*****************************************************************************
函数名:setLeverage
说明:设置杠杆倍数
******************************************************************************'''
def setLeverage(list_token, leverage):
    timestamp =  cex_binance.milliseconds();
    for token in list_token:     
        cex_binance.fapiPrivatePostLeverage({"symbol":token, "leverage":leverage, "timestamp":timestamp});

'''*****************************************************************************
函数名:getPrecision
说明:获取交易对合约精度
(注意：现货精度与合约精度不同)
******************************************************************************'''
def getPrecision(list_token):
    qty_precision = {};
    price_precision = {};
    for token in list_token:
        info = cex_binance.fapiPublicGetExchangeInfo().get('symbols');
        info_symbol = {};
        for item in info:
            if(item['symbol'] == token):
                qty_precision[token] = item['quantityPrecision'];
                price_precision[token] = item['pricePrecision'];
                break;
    return qty_precision, price_precision;

'''*****************************************************************************
函数名:order
说明:合约交易下单
参数：
symbol:符号，比如 BTCUSDT
leverage: 杠杆
qty_u: 下单的金额(USDT)
******************************************************************************'''
def order(symbol, leverage, qty_u, side, position="BOTH", market="MARKET"):
    # 获取最新价格
    # free_balance = float(cex_binance.fetch_balance().get('USDT').get('free'));
    last_price = float(cex_binance.fetchTicker(symbol).get('last'));

    # 计算下单数量
    format = '%.'+str(g_qty_precision[symbol])+'f';
    qty = format % (leverage * qty_u / last_price);

    # 开仓
    timestamp =  cex_binance.milliseconds();
    response = cex_binance.fapiPrivatePostOrder({
        "symbol": symbol,
        "side": side,
        "positionSide": position,
        "type": market,
        "quantity": qty,
        "timestamp": timestamp});

'''*****************************************************************************
逻辑部分
******************************************************************************'''
# 全局变量
SIDE_BUY = "BUY";
SIDE_SELL = "SELL";

# Start
print('Start');
# 加载json文件
file = open('./Json/apikey.json') 
api = json.load(file)

#初始化binance api
cex_binance = ccxt.binance({
    'apiKey': api['Binance']['apiKey'],
    'secret': api['Binance']['secret'],
    # 'password' : okex独有参数
    'timeout': 30000,
    'enableRateLimit': True,
});
market = cex_binance.load_markets();


# 参数设置
listToken = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'MATICUSDT', 'LTCUSDT', 'DOGEUSDT', 'XRPUSDT', 'LINKUSDT', 'ATOMUSDT', 'ETCUSDT',
             'UNIUSDT', 'CRVUSDT', 'APEUSDT', 'OPUSDT', 'FILUSDT', 'ZENUSDT', 'STGUSDT', 'BANDUSDT', 'ENSUSDT', 'LDOUSDT'];

# 设置杠杆倍数
leverage = 10; # 杠杆
setLeverage(listToken, leverage);

N1 = 2; # 持仓周期
N2 = 3; # 代币列表中自动选取几个币持仓
time_interval = '1d'   # 获取日线数据

hold_token = [];
token_data = {};

# 获取合约交易精度：数量和价格
g_qty_precision, g_price_precision = getPrecision(listToken);

# 获取list代币涨跌幅
if cex_binance.has['fetchOHLCV']:
        #for symbol in cex_binance.markets:
        for symbol in listToken:
            print(symbol);
            time.sleep (cex_binance.rateLimit / 1000) # time.sleep wants seconds
            data = cex_binance.fetch_ohlcv(symbol, timeframe=time_interval, limit=2);

            # 涨跌幅
            token_data[symbol] = (data[0][4] - data[0][1]) / data[0][1];

# 根据涨跌幅选取三个币种开仓
sortedTokenChange = sorted(token_data.items(),key = lambda x:x[1], reverse=True);

# 先平仓前一轮持仓
# 撤销当前所有持仓
#cex_binance.fapiPrivateDeleteAllOpenOrders();

# 计算仓位
free_balance = float(cex_binance.fetch_balance().get('USDT').get('free'));
position_qty1 = free_balance / 3;
position_qty2 = free_balance / 3;
position_qty3 = free_balance / 3;

# 根据涨跌幅，开仓
#order('BTCUSDT', leverage, 20, SIDE_BUY);

'''     
# 仓位1
if(float(sortedTokenChange[0][1]) > 0):
    if (cex_binance.has['fetchTicker']):
        price = cex_binance.fetch_ticker(sortedTokenChange[0][0])['bid'];
    order(sortedTokenChange[0][0], leverage, position_qty1, SIDE_BUY);
# 仓位2
if(float(sortedTokenChange[1][1]) > 0):
    if (cex_binance.has['fetchTicker']):
        price = cex_binance.fetch_ticker(sortedTokenChange[1][0])['bid'];
    order(sortedTokenChange[1][0], leverage, position_qty2, SIDE_BUY);
# 仓位3
if(float(sortedTokenChange[2][1]) > 0):
    if (cex_binance.has['fetchTicker']):
        price = cex_binance.fetch_ticker(sortedTokenChange[2][0])['bid'];
    order(sortedTokenChange[2][0], leverage, position_qty3, SIDE_BUY);
'''   
# Finish
print('Finish');
