import requests
import json
import time 
import pandas as pd 
import os 
import jwt
import uuid 
import hashlib
from urllib.parse import urlencode 

#거래가능 코인 조회 
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
    #책에없던 코드. 무슨말인지? 
    if current == "ALL" :
      ticker = ticker 
    else : 
      ticker = ticker[current]
    return tickers[current]

#시세조회

def coin_prices(coin) :
    url = "https://api.upbit.com/v1/orderbook"
    querystring = {"markets" :coin}
    response = requests.request("GET", url, params = querystring) 
    response_json = json.loads(response.text)
    coin_now_price = response_json[0]['orderbook_units'][0]["ask_price"]
    return coin_now_price
  
#과거 호가조회 

def coin_history(coin, time1 = 'minutes', time2 = "") : 
    url = f"https://api.upbit.com/v1/candles/{time1}/{time2}" #minues, 시간단위 넣으려고 f형식
    querystring = {"market": coin, "count":"200"}
    response = requests.request("GET", url, params = querystring)
    response_json = json.loads(response.text)
    df = pd.DataFrame(response_json)
    return df 
  
#로그인
def login() : 
    f = open("업비트.txt")
    lines = f.readlines()
    global access_key
    global secret_key
    
    #access_key = str(lines[0].strip())
    #secret_key = str(lines[1].strip())
    access_key = input("access_key:")
    secret_key = input("secret_key:") #파일읽어오지말고 직접입력하도록 
    #f.close
    
#계좌잔고조회
def balance() : 
    global server_url 
    server_url = 'https://api.upbit.com'
    payload = {'access_key' : access_key, 'nonce':str(uuid.uuid4())} #뭐지이부분
    
    jwt_token = jwt.encode(payload, secret_key) 
    authorization = "Bearer {}".format(jwt_token)
    headers = {"Authorization" : authorization}
    
    res = requests.get(server_url + "/v1/accounts", headers = headers)
    return res.json()
  
#매수(지정가)
def buy_limit(coin, volume, price) : 
    query = {'market': coin,
  'side': 'bid', 
  'ord_type': 'limit',
  'price': price,
  'volume': volume}
    query_string = urlencode(query).encode()
    
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    
    payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512'}
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization' : authorize_token}
    
    res = requests.post(server_url +'/v1/orders', params = query, headers= headers)
    print(res.json)
    return res.json()
  
#매도(지정가)
def sell_limit(coin, volume, price) : 
    query = {'market': coin,
  'side': 'ask', 
  'ord_type': 'limit',
  'price': price,
  'volume': volume}
    query_string = urlencode(query).encode()
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    
    payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512'}
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization' : authorize_token}
    
    res = requests.post(server_url +'/v1/orders', params = query, headers= headers)
    print(res.json)
    return res.json()
  
#매수(시장가)
def buy_market(coin, price) : 
    query = {'market': coin,
  'side': 'bid', 
  'ord_type': 'price',
  'price': price,
  'volume': ''}
    query_string = urlencode(query).encode()
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    
    payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512'}
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization' : authorize_token}
    
    res = requests.post(server_url +'/v1/orders', params = query, headers= headers)
    print(res.json)
    return res.json()
  
#매도(시장가)
def sell_market(coin, price) : 
    query = {'market': coin,
  'side': 'ask', 
  'ord_type': 'price',
  'price': price,
  'volume': ''}
    query_string = urlencode(query).encode()
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    
    payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512'}
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization' : authorize_token}
    
    res = requests.post(server_url +'/v1/orders', params = query, headers= headers)
    print(res.json)
    return res.json()
 
login()

#코인 가격에 따른 호가표시단위와 거래 trim 조건문 
def trim(price_trim) : 
    if price_trim < 10 :  # 0~10원미만이면 소수점 둘째자리 
        price_trim = round(price_trim, 2) 
    elif price_trim < 100 : # 100원미만이면 소수점1째자리 
        price_trim = round(price_trim, 1)
    elif price_trim < 1000 : #천원미만이면 1원단위 
        price_trim = round(price_trim)
    elif price_trim < 10000 : #만원미만이면 5원단위 
        price_trim = round(price_trim*2, -1)/2 
    elif price_trim < 100000 : #10만원미만이면 10원단위 
        price_trim = round(price_trim -1) 
    elif price_trim < 500000 : #50만원미만이면 50원단위 
        price_trim = round(price_trim*2, -2)/2 
    elif price_trim < 1000000 : #100만원미만이면 100원단위 
        price_trim = round(price_trim, -2) 
    elif price_trim < 2000000 : #200만원미만이면 500원단위 
        price_trim = round(price_trim*2, -3)/2
    else : #200만원이상, 1000원단위 
        price_trim = round(price_trim, -3)
    return price_trim
    
print('진행9')

#실제 매수매도행위
while True : 
    # 가장 많이 떨어진 코인을 조회 (과거 200봉 기준)
    try : 
        tickers = coins('KRW')
        mdd_top_score = 0.001
        print('진행10')
        for ticher in tickers : 
            time.sleep(1)
            coin_1m = coin_history(ticker, 'minutes', 1)
            coin_10m = coin_history(ticker, 'minutes', 10)
            coin_30m = coin_history(ticker, 'minutes', 30)
            print("coin_1m :", coin_1m)
            print("coin_10m :", coin_10m)
            print("coin_30m :", coin_30m)
            
            max_high_price = coin_1m["high_price"].max() #여기 1m부분만 바꾸면됨
            now_price = coin_price(ticker)
            mdd= round(((1-(now_price/max_high_price))*100),3) #하락률소수셋째까지
            if mdd > mdd_top_score : 
                mdd_top_score = mdd 
                mdd_top_score_ticker = [ticker, max_high_price, now_price, 
                                        (-1)*mdd]
        print(mdd_top_score_ticker)
        print("진행11")

        # 매수: 매수금액계산  
        for a in balance() : 
            time.sleep(1)
            if a['currency']= 'KRW'
                print(a['balance']) #보유 현금 조회
                #현금의 10%를 곱한 후 반올림해서 매수할 양 산정  
                buy_amount = round(float(a['balance'])*0.10,-2) #현금의 10%만 
                print(buy_amount)
        
        #매수 : 시장가 매수 
        buy_market(mdd_top_score_ticker[0], buy_amount)
        #3초 쉬고 
        time.sleep(3)
        
        #매도하기 
        ask = trim(coin_prices(mdd_top_score_ticker[0])*1.02) #2%오르면 팔아버리기
        for c in balance() : 
            if c['currency'] = mdd_top_score_ticker[0].replace('KRW-','')
                sell_amount = a['balance'] #전량매도 가정 
        
        #지정가매도(익절)
        sell_limit(mdd_top_score_tickerd[0], sell_amount, ask) 
        print("진행12")
        time.sleep(3000) #30분간 휴식 
        
    except : 
        print("진행13, except구문에걸림")
        time.sleep(3000)


