import time
import numpy
import pandas as pd
import json 
import datetime
import matplotlib.pyplot as plt
import random


'''***************************************************
函数名:readCsv
函数说明:读取对应交易对的CSV文件
输入: 
symbol - 交易对名,比如BTCUSDT
输出: pandas df
*******************************************************'''
def readCsv(symbol):
    csvFile = "../database/" + symbol + ".csv"
    df = pd.read_csv(csvFile)
    return df

def boll_standard(df, n=20, std=2):
        # 计算布林线：
        # 布林线中轨：
        df['median'] = df['收盘价格'].rolling(n, min_periods=1).mean();
        #标准差：
        df['std'] = df['收盘价格'].rolling(n, min_periods=1).std(ddof=0); #ddof为标准差的自由度
        #布林线上轨：
        df['upper'] = df['median'] + std * df['std'];
        # 布林线下轨：
        df['lower'] = df['median'] - std * df['std'];
        print(df);

def ma_standard(df, n1=20, n2=40, n3=60):
    # 计算MA：
    # ma20：
    df['ma20'] = df['收盘价格'].rolling(20, min_periods=1).mean();
    #ma40：
    df['ma40'] = df['收盘价格'].rolling(40, min_periods=1).mean();
    #ma60:
    df['ma60'] = df['收盘价格'].rolling(60, min_periods=1).mean();


def trade():
    #找到信号
    df['signal'] = 0;
    #a。找到做多信号，买入，之后等待平仓信号
    #买入: 超买-K线向上穿越上轨
    condition1 = df['开盘价格'] > df['upper']; #当前k线收盘价大于上轨
    condition2 = df['开盘价格'].shift(1) <= df['upper'].shift(1); #之前k线收盘价小于等于上轨
    df.loc[condition1 & condition2, 'signal'] = 1; #将满足condition1 & condition2条件行的signal_long设置为1，signal long为新增列，代表坐多信号

    #平仓
    #condition1 = df['收盘价格'] < df['median'] #当前收盘价小于中轨
    #condition2 = df['收盘价格'].shift(1) >= df['median'].shift(1); #前一天收盘价大于等于中轨
    #df.loc[condition1 & condition2, 'signal_long'] = 0; #将满足条件的行 signal_long设置为0

    # b。找到做空信号，卖出，之后等待平仓信号
    #卖出: 超跌-K线向下穿越下轨
    condition1 = df['开盘价格'] < df['lower']; #当前k线收盘价小于下轨
    condition2 = df['开盘价格'].shift(1) >= df['lower'].shift(1); #之前k线收盘价大等于下轨
    df.loc[condition1 & condition2, 'signal'] = -1; #将满足condition1 & condition2条件行的signal_short设置为-1，signal short为新增列，代表做空信号

    #平仓
    #condition1 = df['收盘价格'] > df['median'] #当前收盘价大于中轨
    #condition2 = df['收盘价格'].shift(1) <= df['median'].shift(1); #前一天收盘价小于等于中轨

    condition_boll_down = df['收盘价格'].shift() > df['upper'].shift();
    df.loc[(condition_boll_down), 'signal'] = 1;

    condition_boll_down1 = df['收盘价格'].shift() < df['lower'].shift();
    df.loc[(condition_boll_down1), 'signal'] = -1;

    df['signal'].fillna(value=0, inplace=True);

    # 累加
    df['合约当日收益'] = df['signal'] * (df['收盘价格'] / df['开盘价格'] - 1) - abs(df['signal']) * gasfee - abs(df['signal']) * rate_fee * 3;
    df['总值U'] = df['合约当日收益'].cumsum();

    # 累乘
    df['合约当日收益'] = 1 + df['signal'] * (df['收盘价格'] / df['开盘价格'] - 1) - abs(df['signal']) * gasfee - abs(df['signal']) * rate_fee * 3;
    df['总值U'] = df['合约当日收益'].cumprod();

        
def drawPlot2():
    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

    # 创建图形
    plt.figure();
    #设置网格，途中红色虚线
    #plt.grid(linestyle=":", color ="red")

    # 持仓收益变化
    x = df.loc[:, 'UTC+8时间'];
    y1 = df.loc[:, '总值U'];
    plt.plot(x, y1);
    l1 = plt.plot(x, y1, 'blue', label='bolling');

    plt.title(u'布林策略');
    plt.xlabel(u'UTC+8时间');
    plt.ylabel('价格');
    plt.legend();
    plt.show();

'''*****************************************************************************
逻辑部分
******************************************************************************'''
# Start
print('Start');

listToken = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'MATICUSDT', 'LTCUSDT', 'DOGEUSDT', 'XRPUSDT', 'LINKUSDT', 'ATOMUSDT', 'ETCUSDT'];
selectedToken = [];

market = {};
hold_backtest = {};
back_sum = {};
max_N = {};
gasfee = 0.0002;
init_U = 10000;
leverage = 10; # 杠杆
rate = 0.1 # 每次开仓资金比例
rate_fee = 0.0001; #资金费率


# 回测收益
N1 = 21; # 持仓周期
N2 = 3; # 代币列表中自动选取几个币持仓
#for N in range(1, N1):
#    if(N != 20):continue;
    
for symbol in listToken:
    # 读取交易对数据
    df = readCsv(symbol);
    boll_standard(df, 20);

    # 写数据到csv
    csv = '../database/布林数据_'+symbol+'.csv';
    #csv = '../database/ma.csv';
    df = pd.DataFrame(df);
    # 布林
    df.columns = ['UTC+8时间','开盘价格','最高价格','最低价格', '收盘价格', '交易量', '净值', 'median', 'std', 'upper', 'lower'];
    # ma
    #df.columns = ['UTC+8时间','开盘价格','最高价格','最低价格', '收盘价格', '交易量', '净值', 'ma20', 'ma40', 'ma60'];
    df.to_csv(csv, encoding='utf_8_sig', index=None);

    trade();

    # 写数据到csv
    csv = '../database/回测_'+symbol+'.csv';
    df = pd.DataFrame(df, columns=['UTC+8时间','开盘价格', 'signal', '总值U', '持仓数量']);
    df.to_csv(csv, encoding='utf_8_sig', index=None);

    if(symbol == 'BTCUSDT'):
        drawPlot2();

# 绘制最优收益的回测收益折线图
#drawPlot(hold_backtest[max_N['最优N']], back_sum[max_N['最优N']], max_N['最优N'], ['BTCUSDT', 'ETHUSDT']);

# Finish
print('Finish');



