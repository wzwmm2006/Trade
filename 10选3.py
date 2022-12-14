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

'''***************************************************
函数名:getChange
函数说明:获取涨跌幅
输入: 
None
输出: pandas change_dict
*******************************************************'''
def getChange(listToken, N, N2):
    #集合存储结果
    change_dict = {}
    for symbol in listToken:
        #获取数据
        df = readCsv(symbol)
        #df 我们需要 时间，开盘价，收盘价 这三个参数
        df['最近N天涨跌幅'] = df['开盘价格'].pct_change(N)
        # 获取所有1天涨跌幅
        change_dict[symbol] = df[['UTC+8时间', '最近N天涨跌幅']]

    # 计算持仓
    hold_result = {}
    TokenChange = {};
    hold_result['UTC+8时间'] = df['UTC+8时间'];
    for index in range(0,N2):
        df['selectedToken'+str(index)] = 'USDT';
        df['change'+str(index)] = 0;
        hold_result['selectedToken'+str(index)] = df['selectedToken'+str(index)];
        hold_result['change'+str(index)] = df['change'+str(index)];

   # print(hold_result);
    for index in range(len(change_dict[listToken[0]])):

        for index2 in range(len(listToken)):
            TokenChange[listToken[index2]] = change_dict[listToken[index2]].iloc[index]['最近N天涨跌幅'];
        sortedTokenChange = sorted(TokenChange.items(),key = lambda x:x[1], reverse=True);

        for index3 in range(0,N2):
            [selectedToken, change] = sortedTokenChange[index3];
            #print(change)
            if(numpy.isnan(change)):
                hold_result['selectedToken'+str(index3)][index] = 'USDT';
                hold_result['change'+str(index3)][index] = 0;
            if(change > 0):
                hold_result['selectedToken'+str(index3)][index] = selectedToken;
                hold_result['change'+str(index3)][index] = change;
    #print(hold_result);
    return hold_result;

'''***************************************************
函数名:backTest
函数说明:根据持仓回测收益
输入: init_U, listToken, N
输出: pandas hold_result
*******************************************************'''
def backTest(init_U, listToken, csv, gasfee):
    market = {};
    for symbol in listToken:
        market[symbol] = readCsv(symbol);

    hold = pd.read_csv(csv);
    hold['持仓数量_1'] = 0;
    hold['持仓数量_2'] = 0;
    hold['持仓数量_3'] = 0;
    hold['持仓U_1'] = 0;
    hold['持仓U_2'] = 0;
    hold['持仓U_3'] = 0;
    hold['持仓净值'] = 0;

    # 首日
    hold.at[0,'持仓U_1'] = init_U / 3;
    hold.at[0,'持仓U_2'] = init_U / 3;
    hold.at[0,'持仓U_3'] = init_U / 3;
    hold.at[0,'持仓净值'] = 1;

    for index in range(1,len(hold)):
        # ----卖出
        # 仓位1
        if(hold['持仓_1'][index-1] != 'USDT'):
            hold.at[index,'持仓U_1']  = hold['持仓数量_1'][index-1] * market[hold['持仓_1'][index-1]].iloc[index]['开盘价格'];
            hold.at[index,'持仓U_1'] = hold['持仓U_1'][index] * (1 - gasfee);
            hold.at[index,'持仓数量_1'] = 0;
        else:
            hold.at[index,'持仓U_1']  = hold['持仓U_1'][index-1];
            hold.at[index,'持仓数量_1']  = hold['持仓数量_1'][index-1];
        # 仓位2
        if(hold['持仓_2'][index-1] != 'USDT'):
            hold.at[index,'持仓U_2']  = hold['持仓数量_2'][index-1] * market[hold['持仓_2'][index-1]].iloc[index]['开盘价格'];
            hold.at[index,'持仓U_2'] = hold['持仓U_2'][index] * (1 - gasfee);
            hold.at[index,'持仓数量_2'] = 0;
        else:
            hold.at[index,'持仓U_2']  = hold['持仓U_2'][index-1];
            hold.at[index,'持仓数量_2']  = hold['持仓数量_2'][index-1];
        # 仓位3
        if(hold['持仓_3'][index-1] != 'USDT'):
            hold.at[index,'持仓U_3']  = hold['持仓数量_3'][index-1] * market[hold['持仓_3'][index-1]].iloc[index]['开盘价格'];
            hold.at[index,'持仓U_3'] = hold['持仓U_3'][index] * (1 - gasfee);
            hold.at[index,'持仓数量_3'] = 0;
        else:
            hold.at[index,'持仓U_3']  = hold['持仓U_3'][index-1];
            hold.at[index,'持仓数量_3']  = hold['持仓数量_3'][index-1];

        # ----重新分配持仓
        total_U = hold['持仓U_1'][index] + hold['持仓U_2'][index] + hold['持仓U_3'][index];
        hold.at[index,'持仓U_1'] = 5* total_U / 10;
        hold.at[index,'持仓U_2'] = 3 * total_U / 10;
        hold.at[index,'持仓U_3'] = 2 * total_U / 10;

        # ----buy
        if(hold['持仓_1'][index] != 'USDT'):
            hold.at[index,'持仓U_1'] = hold['持仓U_1'][index] * (1 - gasfee);
            hold.at[index,'持仓数量_1']  = hold['持仓U_1'][index] / market[hold['持仓_1'][index]].iloc[index]['开盘价格'];

        # 仓位2
        if(hold['持仓_2'][index] != 'USDT'):
            hold.at[index,'持仓U_2'] = hold['持仓U_2'][index] * (1 - gasfee);
            hold.at[index,'持仓数量_2']  = hold['持仓U_2'][index] / market[hold['持仓_2'][index]].iloc[index]['开盘价格'];

        # 仓位3
        if(hold['持仓_3'][index] != 'USDT'):
            hold.at[index,'持仓U_3'] = hold['持仓U_3'][index] * (1 - gasfee);
            hold.at[index,'持仓数量_3']  = hold['持仓U_3'][index] / market[hold['持仓_3'][index]].iloc[index]['开盘价格'];

        
        total_U = hold['持仓U_1'][index] + hold['持仓U_2'][index] + hold['持仓U_3'][index];
        
        # 净值
        hold.at[index,'持仓净值'] = total_U / init_U;   
    return hold;

'''***************************************************
函数名:drawPlot
函数说明:根据回测收益绘制折线图
输入: hold_backtest, backtest, listToken
输出: None
*******************************************************'''
def drawPlot(hold_backtest,back_sum, N, listToken):
    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

    # 创建图形
    plt.figure();
    #设置网格，途中红色虚线
    plt.grid(linestyle=":", color ="red")

    # 持仓收益变化
    x = hold_backtest.loc[:, 'UTC+8时间'];
    y = hold_backtest.loc[:, '持仓净值'];
    plt.plot(x, y);
    l = plt.plot(x, y, 'g--', label=N);

    # btc/eth净值   
    token = {};
    color = ['blue', 'coral', 'gold', 'green'];
    index = 0;
    for symbol in listToken:
        #获取数据
        df = readCsv(symbol)
        # 获取所有1天涨跌幅
        #x_n = df.loc[:, 'UTC+8时间'];
        y_n = df.loc[:, '净值'];
        print(y_n);
        plt.plot(x, y_n);
        ln = plt.plot(x, y_n, color[index], label=symbol);
        index += 1;

    #最大回撤注释
    #转换为日期索引
    hold_backtest['UTC+8时间']=pd.to_datetime(hold_backtest['UTC+8时间'])
    hold_backtest.set_index('UTC+8时间', inplace=True);

    x_back = back_sum['历史最大回撤日期'];
    y_back = hold_backtest.loc[x_back]['持仓净值'];
    back_max = '最大回撤' + str(back_sum['历史最大回撤比例']);
    plt.annotate(text=back_max,xy=(x_back,y_back),xytext=(x_back,y_back+10),fontsize=6, arrowprops={'arrowstyle':'->'});

    plt.title(u'回测最优解');
    plt.xlabel(u'UTC+8时间');
    plt.ylabel('持仓净值');
    plt.legend();
    plt.show();

'''***************************************************
函数名:getSumData
函数说明:根据回测收益计算每年涨幅/年华收益率/最大回撤/净值(截止目前)
输入: hold_backtest
输出: backtest
*******************************************************'''
def getSumData(hold_backtest):
    backtest = {};
    #转换为日期索引
    hold_backtest['UTC+8时间']=pd.to_datetime(hold_backtest['UTC+8时间'])
    hold_backtest.set_index('UTC+8时间', inplace=True);

    # 计算每年涨幅/年华收益率
    years = ['2019', '2020', '2021', '2022'];
    for year in years:
        head = hold_backtest.loc[year].head(1)['持仓净值'][0];
        tail = hold_backtest.loc[year].tail(1)['持仓净值'][0];
        backtest['N'] = N;
        backtest[year+'年涨幅'] = '%.2f%%' % (tail / head * 100);
        backtest[year+'年化收益率'] = '%.2f%%' % ((tail - head) / head * 100);
        backtest[year+'年度净值'] = tail - head;
        backtest[year+'年度最大回撤'] = hold_backtest.loc[year]['持仓净值'].diff(1).min();


    date = hold_backtest['持仓净值'].diff(1).idxmin();
    backtest['总净值'] = hold_backtest.tail(1)['持仓净值'][0] - hold_backtest.head(1)['持仓净值'][0];
    backtest['历史最大回撤日期'] = date;
    
    hold_U_day = float( hold_backtest.loc[date]['持仓净值'] );
    back_U_day = float( hold_backtest['持仓净值'].diff(1).min() );
    backtest['历史最大回撤'] = back_U_day;
    backtest['历史最大回撤比例'] = '%.2f%%' % ( back_U_day / hold_U_day * 100);
    
    return backtest;


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

# 回测收益
N1 = 21; # 持仓周期
N2 = 3; # 代币列表中自动选取几个币持仓
for N in range(1, N1):
    # 计算涨跌幅
    # 根据涨跌幅计算持仓,选择涨幅最大的N2个币种 
    hold = getChange(listToken, N, N2);

    # 写数据到csv
    csv = '../database/持仓明细_'+str(N)+'.csv';
    df = pd.DataFrame(hold);
    df.columns = ['UTC+8时间','持仓_1','持仓当日涨跌幅_1','持仓_2', '持仓当日涨跌幅_2','持仓_3','持仓当日涨跌幅_3'];
    df.to_csv(csv, encoding='utf_8_sig', index=None);

    # 根据持仓回测收益
    init_U = 10000;   # 初始资金
    key = "N="+str(N);
    hold_backtest[key] = backTest(init_U, listToken, csv, gasfee);
    print(hold_backtest[key]);

    csv = '../database/持仓明细_回测收益_'+str(N)+'.csv';
    df = pd.DataFrame(hold_backtest[key]);
    df.columns = ['UTC+8时间','持仓_1', '持仓当日涨跌幅_1','持仓_2','持仓当日涨跌幅_2', '持仓_3','持仓当日涨跌幅_3',
    '持仓数量_1','持仓数量_2','持仓数量_3',
    '持仓U_1','持仓U_2','持仓U_3', '持仓净值'];
    df.to_csv(csv, encoding='utf_8_sig', index=None);
    
    # 计算每年涨幅/年华收益率/最大回撤/净值(截止目前)
    back_sum[key] = getSumData(df);
    #print(back_sum[key]);

    # 存入数据到csv
    csv = '../database/回测收益总计'+str(N)+'.csv';
    df = pd.DataFrame(back_sum[key], index=[0]).T;
    #df.columns = ['分项','数据'];
    df.to_csv(csv, encoding='utf_8_sig');

    if((not max_N) or (max_N['最大总净值'] < back_sum[key]['总净值'])):
        max_N['最大总净值'] = back_sum[key]['总净值'];
        max_N['最优N'] = key;

# 绘制最优收益的回测收益折线图
drawPlot(hold_backtest[max_N['最优N']], back_sum[max_N['最优N']], max_N['最优N'], ['BTCUSDT', 'ETHUSDT']);

# Finish
print('Finish');



