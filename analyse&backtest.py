import time
import numpy
import pandas as pd
import json 
import matplotlib.pyplot as plt


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

'''***************************************************
函数名:getChange
函数说明:获取涨跌幅
输入: 
None
输出: pandas change_dict
*******************************************************'''
def getChange(listToken):
    #计算最近N天的涨跌幅
    N =1 
    #集合存储结果
    change_dict = {}
    for symbol in listToken:
        #获取数据
        df = readCsv(symbol)
        #df 我们需要 时间，开盘价，收盘价 这三个参数
        df['最近N天涨跌幅'] = df['收盘价格'].pct_change(N)
        # 获取所有1天涨跌幅
        change_dict[symbol] = df[['UTC+8时间', '最近N天涨跌幅']]
    return change_dict

'''***************************************************
函数名:calHold
函数说明:根据涨跌幅计算持仓
输入: change_dist
输出: pandas hold_result
*******************************************************'''
def calHold(change_dict):
    # 计算持仓
    hold_result = {}
    hold_index = 0
    for index in range(len(change_dict['BTCUSDT'])):
        BTCChange = change_dict['BTCUSDT'].iloc[index]['最近N天涨跌幅']
        ETHChange = change_dict['ETHUSDT'].iloc[index]['最近N天涨跌幅']
        date = change_dict['BTCUSDT'].iloc[index]['UTC+8时间']

        if BTCChange is None or ETHChange is None:
            continue

        # =====判断操作：待细化
        if BTCChange > ETHChange:
            #print('买入比特币')
            hold_result[hold_index] = [date, 'BTCUSDT']
        # 并非两者都<0时，且以太坊涨得多
        elif BTCChange < ETHChange:
            #print('买入以太坊')
            hold_result[hold_index] = [date, 'ETHUSDT']
        hold_index += 1

    return hold_result

'''***************************************************
函数名:backTest
函数说明:根据持仓回测收益
输入: init_U, listToken
输出: pandas hold_result
*******************************************************'''
def backTest(init_U, listToken):
    market = {};

    hold = pd.read_csv('../database/持仓明细.csv');
    hold['持仓数量'] = 0;
    hold['持仓U'] = 0;
    for symbol in listToken:
        market[symbol] = readCsv(symbol);

    # 首日
    hold.at[0,'持仓U'] = init_U;
    if(hold['持仓'][0] == 'BTCUSDT'):
        # 购入BTC
        hold.at[0,'持仓数量'] = init_U / market['BTCUSDT'].iloc[1]['开盘价格'];
    elif(hold['持仓'][0] == 'ETHUSDT'):
        #购入ETH
        hold.at[0,'持仓数量'] = init_U / market['ETHUSDT'].iloc[1]['开盘价格'];

    for index in range(1,len(hold)):
        # 与前一轮持仓相同，不交易
        if(hold['持仓'][index] == hold['持仓'][index-1]): 
            hold.at[index,'持仓U'] = hold['持仓U'][index-1];
            hold.at[index,'持仓数量'] = hold['持仓数量'][index-1];
            continue;

        # 需要换仓，则交易
        if(hold['持仓'][index] == 'BTCUSDT'):
            # 以当日开盘价格卖出ETH
            hold.at[index,'持仓U'] = hold['持仓数量'][index-1] * market['ETHUSDT'].iloc[index]['开盘价格'];
            # 以当日开盘价格购入BTC
            hold.at[index,'持仓数量'] = hold['持仓U'][index] / market['BTCUSDT'].iloc[index]['开盘价格'];
        elif(hold['持仓'][index] == 'ETHUSDT'):
            #卖出BTC
            hold.at[index,'持仓U'] = hold['持仓数量'][index-1] * market['BTCUSDT'].iloc[index]['开盘价格'];
            #购入ETH
            hold.at[index,'持仓数量'] = hold['持仓U'][index] / market['ETHUSDT'].iloc[index]['开盘价格'];

    return hold;



'''***************************************************
函数名:drawPlot
函数说明:根据回测收益绘制折线图
输入: hold_backtest
输出: None
*******************************************************'''
def drawPlot(hold_backtest):
    x = hold_backtest.loc[:, 'UTC+8时间'];
    y = hold_backtest.loc[:, '持仓U'];
    l = plt.plot(x,y, 'g--',label='backtest');
    plt.title('backtest');
    plt.xlabel('UTC+8');
    plt.ylabel('USDT');
    plt.legend();
    plt.show();


'''*****************************************************************************
逻辑部分
******************************************************************************'''
listToken = ['BTCUSDT', 'ETHUSDT']

# 计算涨跌幅
change = getChange(listToken)

# 根据涨跌幅计算持仓
hold = calHold(change)

# 写数据到csv
df = pd.DataFrame(hold).T
df.columns = ['UTC+8时间','持仓']
df.to_csv('../database/持仓明细.csv', encoding='utf_8_sig', index=None)

# 回测
init_U = 10000;   # 初始资金
hold_backtest = backTest(init_U, listToken);

# 存入数据到csv
df = pd.DataFrame(hold_backtest);
df.columns = ['UTC+8时间','持仓','持仓数量','持仓U'];
df.to_csv('../database/持仓明细_回测收益.csv', encoding='utf_8_sig', index=None)

# 绘制回测收益折线图
drawPlot(hold_backtest);





