import time
import numpy
import pandas as pd
import json 
import datetime
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
def getChange(listToken, N):
    #集合存储结果
    change_dict = {}
    for symbol in listToken:
        #获取数据
        df = readCsv(symbol)
        #df 我们需要 时间，开盘价，收盘价 这三个参数
        df['最近N天涨跌幅'] = df['收盘价格'].pct_change(N)
        # 获取所有1天涨跌幅
        change_dict[symbol] = df[['UTC+8时间', '最近N天涨跌幅']]
    #print(change_dict);
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

        if numpy.isnan(BTCChange) or numpy.isnan(ETHChange):
            hold_result[index] = [date, 'BTCUSDT'];

        # =====判断操作：待细化
        elif BTCChange >= ETHChange:
            #print('买入比特币')
            hold_result[index] = [date, 'BTCUSDT']
        # 并非两者都<0时，且以太坊涨得多
        elif BTCChange < ETHChange:
            #print('买入以太坊')
            hold_result[index] = [date, 'ETHUSDT']

    return hold_result

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
    hold['持仓数量'] = 0;
    hold['持仓U'] = 0;
    

    # 首日
    hold.at[0,'持仓U'] = init_U;
    hold.at[0,'持仓净值'] = 1;
    if(hold['持仓'][0] == 'BTCUSDT'):
        # 购入BTC
        hold.at[0,'持仓U'] *= (1 - gasfee);
        hold.at[0,'持仓数量'] = hold.at[0,'持仓U'] / market['BTCUSDT'].iloc[0]['开盘价格'];
    elif(hold['持仓'][0] == 'ETHUSDT'):
        #购入ETH
        hold.at[0,'持仓U'] *= (1 - gasfee);
        hold.at[0,'持仓数量'] = hold.at[0,'持仓U'] / market['ETHUSDT'].iloc[0]['开盘价格'];
    print(hold);  

    for index in range(1,len(hold)):
        # 与前一轮持仓相同，不交易,只更新净值
        if(hold['持仓'][index] == hold['持仓'][index-1]): 
            hold.at[index,'持仓数量'] = hold['持仓数量'][index-1];
            if(hold['持仓'][index]  == 'BTCUSDT'):
                hold.at[index,'持仓U'] = hold['持仓数量'][index] * market['BTCUSDT'].iloc[index]['开盘价格'];
                hold.at[index,'持仓净值'] = hold['持仓U'][index]  / init_U;
            elif(hold['持仓'][index]  == 'ETHUSDT'):
                hold.at[index,'持仓U'] = hold['持仓数量'][index] * market['ETHUSDT'].iloc[index]['开盘价格'];
                hold.at[index,'持仓净值'] = hold['持仓U'][index]  / init_U;

        # 需要换仓，则交易
        elif(hold['持仓'][index] == 'BTCUSDT' and hold['持仓'][index-1] == 'ETHUSDT'):
            # 以当日开盘价格卖出ETH
            hold.at[index,'持仓U'] = hold['持仓数量'][index-1] * market['ETHUSDT'].iloc[index]['开盘价格'];
            hold.at[index,'持仓U'] *= (1 - gasfee);
            hold.at[index,'持仓净值'] = hold['持仓U'][index]  / init_U;
            # 以当日开盘价格购入BTC
            hold.at[index,'持仓U'] *= (1 - gasfee);
            hold.at[index,'持仓数量'] = hold['持仓U'][index] / market['BTCUSDT'].iloc[index]['开盘价格'];
        elif(hold['持仓'][index] == 'ETHUSDT' and hold['持仓'][index-1] == 'BTCUSDT'):
            #卖出BTC
            hold.at[index,'持仓U'] = hold['持仓数量'][index-1] * market['BTCUSDT'].iloc[index]['开盘价格'];
            hold.at[index,'持仓U'] *= (1 - gasfee);
            hold.at[index,'持仓净值'] = hold['持仓U'][index]  / init_U;
            #购入ETH
            hold.at[index,'持仓U'] *= (1 - gasfee);
            hold.at[index,'持仓数量'] = hold['持仓U'][index] / market['ETHUSDT'].iloc[index]['开盘价格'];
    #print(hold)
    return hold;



'''***************************************************
函数名:drawPlot
函数说明:根据回测收益绘制折线图
输入: hold_backtest, backtest
输出: None
*******************************************************'''
def drawPlot(hold_backtest,back_sum, N):
    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

    # 创建图形
    plt.figure();
    #设置网格，途中红色虚线
    plt.grid(linestyle=":", color ="red")

    # 持仓收益变化
    x = hold_backtest.loc[:, 'UTC+8时间'];
    y = hold_backtest.loc[:, '持仓净值'];
    #plt.subplot(2, 1, 1)
    plt.plot(x, y)

    # 调整线条颜色：可以使用标准颜色名称、缩写颜色代码、0-1 灰度值、十六进制、RGB 元组、HTML 颜色名称
    l = plt.plot(x,y, 'g--',label=N);

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
        head = hold_backtest.loc[year].head(1)['持仓U'][0];
        tail = hold_backtest.loc[year].tail(1)['持仓U'][0];
        backtest['N'] = N;
        backtest[year+'年涨幅'] = '%.2f%%' % (tail / head * 100);
        backtest[year+'年化收益率'] = '%.2f%%' % ((tail - head) / head * 100);
        backtest[year+'年度净值'] = tail - head;
        backtest[year+'年度最大回撤'] = hold_backtest.loc[year]['持仓U'].diff(1).min();


    date = hold_backtest['持仓U'].diff(1).idxmin();
    backtest['总净值'] = hold_backtest.tail(1)['持仓U'][0] - hold_backtest.head(1)['持仓U'][0];
    backtest['历史最大回撤日期'] = date;
    
    hold_U_day = float( hold_backtest.loc[date]['持仓U'] );
    back_U_day = float( hold_backtest['持仓U'].diff(1).min() );
    backtest['历史最大回撤'] = back_U_day;
    backtest['历史最大回撤比例'] = '%.2f%%' % ( back_U_day / hold_U_day * 100);
    
    return backtest;

'''*****************************************************************************
逻辑部分
******************************************************************************'''
# Start
print('Start');

listToken = ['BTCUSDT', 'ETHUSDT']
hold_backtest = {};
back_sum = {};
max_N = {};
gasfee = 0.0002;

# 回测收益
for N in range(1,21):
    # 计算涨跌幅
    change = getChange(listToken, N);

    # 根据涨跌幅计算持仓
    hold = calHold(change)

    # 写数据到csv
    csv = '../database/持仓明细_'+str(N)+'.csv';
    df = pd.DataFrame(hold).T
    df.columns = ['UTC+8时间','持仓']
    df.to_csv(csv, encoding='utf_8_sig', index=None)

    # 回测
    init_U = 10000;   # 初始资金
    key = "N="+str(N);
    hold_backtest[key] = backTest(init_U, listToken, csv, gasfee);

    # 存入数据到csv
    csv = '../database/持仓明细_回测收益_'+str(N)+'.csv';
    df = pd.DataFrame(hold_backtest[key]);
    df.columns = ['UTC+8时间','持仓','持仓数量','持仓U', '持仓净值'];
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
drawPlot(hold_backtest[max_N['最优N']], back_sum[max_N['最优N']], max_N['最优N']);

# Finish
print('Finish');



