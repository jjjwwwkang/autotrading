import pyupbit
import numpy as np
import pandas as pd
import requests
import json
import time

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

for l in L :
    df = pyupbit.get_ohlcv(l)
#count = 7 을 넣는 등으로 일정기간의 MDD계산가능. 안넣으면 200일.
#변동폭 * K 계산, (고가-저가)*K값
    df['range'] = (df['high'] - df['low']) * 0.5
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
#수익률계산 (np. where구문 : 조건문, 참일때값, 거짓일때값 )
    df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'] - fee,
                     1)
#hpr: 누적수익률
    df['hpr'] = df['ror'].cumprod()
#누적 최대값과 현재 hpr의 차이 / 누적 최대값 *100
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
    #print("MDD(%): ", df['dd'].max())
    df['johnBurr'] = df['close']/df['close'].iloc[0]
    df['diff'] = df['hpr']-df['johnBurr']
    result = df[['hpr','johnBurr', 'diff','dd']]
    A = list(result.iloc[-1])
    if A[2] >0 :
        D[l] = A
    time.sleep(0.4)

a = 0
Bestkv = dict()
for k,v in D.items() :
    if v[0] > a :
        a = v[0]
        Bestkv[k] = v[0]

print(Bestkv)
