import pyupbit
import numpy as np
import pandas as pd

df = pyupbit.get_ohlcv("KRW-BTC") #count = 7 을 넣는 등으로 일정기간의 MDD계산가능
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
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")
