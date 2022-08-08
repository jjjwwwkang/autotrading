import pyupbit
import numpy as np
import pandas as pd
import requests
import json
import time
import datetime
from datetime import date


def coins(current) :
    url = "http://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"true"}
    response = requests.request("GET", url, params = querystring)
    response_json = json.loads(response.text)
    KRWticker = []
    BTCticker = []
    USDticker = []
    for a in response_json :
        if "KRW-" in a["market"] :
            KRWticker.append(a["market"])
        elif "BTC-" in a["market"] :
            BTCticker.append(a['market'])
        elif "USDT-" in a["market"] :
            USDticker.append(a["market"])
    tickers = {"KRW" : KRWticker, 'BTC': BTCticker, 'USD' : USDticker}
    return tickers[current]

L = coins("KRW")
D = dict()

#import time
#import pyupbit
#import datetime

access = "mgaHbHYVrMOxlVwlpj9AMNzznFoXeMGLd9BUN3vZ"
secret = "Mm7lgHQWzXpMKVeITntwt5kCqaPj06dJBoyqancd"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance']) * float(b['avg_buy_price']) #20220808수정
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

thedate = date(1900,1,1)

# 자동매매 시작
while True:
    nowdate = date.today()
    if nowdate == thedate :
        pass
    else :
        for l in L:
            df = pyupbit.get_ohlcv(l)
        # count = 7 을 넣는 등으로 일정기간의 MDD계산가능. 안넣으면 200일.
        # 변동폭 * K 계산, (고가-저가)*K값
            df['range'] = (df['high'] - df['low']) * 0.5
            df['target'] = df['open'] + df['range'].shift(1)

            fee = 0.0032
        # 수익률계산 (np. where구문 : 조건문, 참일때값, 거짓일때값 )
            df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'] - fee,
                             1)
        # hpr: 누적수익률
            df['hpr'] = df['ror'].cumprod()
        # 누적 최대값과 현재 hpr의 차이 / 누적 최대값 *100
            df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
        # print("MDD(%): ", df['dd'].max())
            df['johnBurr'] = df['close'] / df['close'].iloc[0]
            df['diff'] = df['hpr'] - df['johnBurr']
            result = df[['hpr', 'johnBurr', 'diff', 'dd']]
            A = list(result.iloc[-1])
            if A[2] > 0:
                D[l] = A
            time.sleep(0.4)

        a = 0
        Bestkv = dict()
        for k, v in D.items():
            if v[0] > a and 0 < v[3] <= D['KRW-BTC'][3]:
                a = v[0]
                Bestkv[k] = v[0]

    # Bestkv = 매수대상
        purchase = list(Bestkv.keys())

        print("Best", Bestkv)
        print("매수대상",purchase)
        thedate = nowdate
# 매수대상에 대하여,

    for i in purchase :
        print(i)
        try:
            now = datetime.datetime.now()
            start_time = get_start_time(i)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time < now < end_time - datetime.timedelta(seconds=10):
                target_price = get_target_price(i, 0.5)
                ma15 = get_ma15(i)
                current_price = get_current_price(i)
                print(target_price, current_price, ma15)
                #보유하지 않은 코인에 대해서 매수조건 따지기 
                if target_price < current_price and ma15 < current_price and get_balance(i) < 5000.0 : #20220808
                    #매수금액 : 잔고돈 / 매수대상코인갯수
                    krw = round(get_balance("KRW") / len(purchase),1)
                    if krw > 5000:
                        upbit.buy_market_order(i, krw*0.9995)
            else:
                sellcoin = get_balance(i[4:])
                if sellcoin > 0.00008:
                    upbit.sell_market_order(i, sellcoin*0.9995)
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
