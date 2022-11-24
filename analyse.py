import time
import numpy
import pandas as pd
import json 


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
函数名:readCsv
函数说明:读取对应交易对的CSV文件
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
df.to_csv('持仓明细.csv', encoding='utf_8_sig', index=None)

