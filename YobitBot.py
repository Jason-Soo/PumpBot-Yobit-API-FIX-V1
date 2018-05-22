# uncompyle6 version 2.11.2
# Python bytecode 3.5 (3351)
# Decompiled from: Python 2.7.13 (default, Apr  4 2017, 08:47:57)
# [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.38)]
# Embedded file name: ./YobitBot.py
# Compiled at: 2017-07-13 21:04:56
# Size of source mod 2**32: 13441 bytes
import json
import requests
from time import strftime, gmtime
import time
import hmac
import hashlib
import pprint
import pdb
import platform
import colorama
import utils
import datetime
import random
try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

import configparser
import sys
sys.setrecursionlimit(10000)
config = configparser.ConfigParser()
config.readfp(open('config.txt'))
key = config.get('Yobit', 'Key')
secret = config.get('Yobit', 'Secret')
secret = bytes(secret, 'utf8')
BuyPercent = config.get('PriceLip', 'BuyPercent')
SellPercent = config.get('PriceLip', 'SellPercent')
BuyPercent, SellPercent = utils.percentageFix(BuyPercent,SellPercent)

def nonceHandler():
    f = open('nonce.txt')
    nonce = f.readlines()
    f.close()
    newnonce = int(nonce[0]) + 1
    file = open('nonce.txt', 'w+')
    file.write(str(newnonce))
    file.close()
    return newnonce


def generate_nonce(length=9):
    """Generate pseudo-random number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def getTicker(market):
    url = 'https://www.yobit.net/api/3/ticker/' + market + '_btc'
    r = requests.get(url, headers={'apisign': hmac.new(secret, url.encode(), hashlib.sha512).hexdigest()})
    try:
        resp = json.loads(r.text)
    except:
        print(r.text)
    return resp[market + '_btc']['last']


def getBalance(symbol):
    values = {}
    url = 'https://www.yobit.net/tapi'
    foundit = None
    while foundit == None:
        nonce = nonceHandler()
        values['method'] = 'getInfo'
        values['nonce'] = nonce
        body = urlencode(values)
        signature = hmac.new(secret, body.encode('utf8'), hashlib.sha512).hexdigest()
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
         'Key': key,
         'Sign': signature}
        r = requests.post(url, data=values, headers=headers)
        
        try:
            resp = json.loads(r.text)
        except:
            print(r.text)
        try:
            if resp['success'] == 0:
                print(r.text)
            if symbol in resp['return']['funds']:
                return resp['return']['funds'][symbol]
                foundit = 1
        except:
            print(resp)

        # if resp['error'] == 'invalid nonce (has already been used)':
        #     print("www.yobit.net: invalid nonce (has already been used)")
        #     print("Create new API keys")
        #     return
        # elif resp['error']:
        #     print(resp)
        # elif symbol in resp['return']['funds']:
        #     return resp['return']['funds'][symbol]
        #     foundit = 1
        




def getOrder(order_id):
    nonce = nonceHandler()
    values = {}
    url = 'https://www.yobit.net/tapi'
    values['method'] = 'OrderInfo'
    values['nonce'] = nonce
    values['order_id'] = order_id
    body = urlencode(values)
    signature = hmac.new(secret, body.encode('utf8'), hashlib.sha512).hexdigest()
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
     'Key': key,
     'Sign': signature}
    r = requests.post(url, data=values, headers=headers)
    try:
        resp = json.loads(r.text)
    except:
        print(r.text)
    if resp['success'] == 0:
        print(r.text)
    return resp['return'][order_id]


def buyOrder(market, quantity):
    nonce = nonceHandler()
    price = getTicker(market)
    rate = str(price * (1 + float(BuyPercent)))
    values = {}
    url = 'https://www.yobit.net/tapi'
    values['method'] = 'Trade'
    values['nonce'] = nonce
    values['pair'] = market + '_btc'
    values['type'] = 'buy'
    values['rate'] = "%.8f" % float(rate)
    values['amount'] = quantity
    body = urlencode(values)
    signature = hmac.new(secret, body.encode('utf8'), hashlib.sha512).hexdigest()
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
     'Key': key,
     'Sign': signature}
    r = requests.post(url, data=values, headers=headers)
    try:
        resp = json.loads(r.text)
    except:
        print(r.text)
    if resp['success'] == 0:
        print(r.text)
    else:
        order_id = resp['return']['order_id']
        mylist = [order_id, rate]
        return mylist


def sellOrder(symbol, rate):
    quantity = getBalance(symbol)
    nonce = nonceHandler()
    values = {}
    url = 'https://www.yobit.net/tapi'
    values['method'] = 'Trade'
    values['nonce'] = nonce
    values['pair'] = symbol + '_btc'
    values['type'] = 'sell'
    values['rate'] = "%.8f" % float(rate)
    values['amount'] = quantity
    body = urlencode(values)
    signature = hmac.new(secret, body.encode('utf8'), hashlib.sha512).hexdigest()
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
     'Key': key,
     'Sign': signature}
    r = requests.post(url, data=values, headers=headers)
    
    try:
        resp = json.loads(r.text)
    except:
        print(r.text)
    if resp['success'] == 0:
        print(r.text)
    order_id = resp['return']['order_id']
    return order_id


def marketHistory(symbol):
    url = 'https://www.yobit.net/api/3/trades/' + symbol + '_btc'
    r = requests.get(url, headers={'apisign': hmac.new(secret, url.encode(), hashlib.sha512).hexdigest()})
    try:
        resp = json.loads(r.text)
    except:
        print(r.text)

    datetime.datetime.fromtimestamp(1499275110).strftime('%H:%M')
    with open('mh.json', 'w') as outfile:
        json.dump(resp, outfile)
    price = []
    time = []
    for i in resp[symbol + '_btc']:
        price.append(i['price'])
        time.append(i['timestamp'])

    firstItem = time[0]
    currentTime = datetime.datetime.fromtimestamp(firstItem).strftime('%M')
    index1 = 0
    price1 = 0
    for i in time:
        t = datetime.datetime.fromtimestamp(i).strftime('%M')
        if float(t) == float(currentTime) - 1:
            index1 = time.index(i)
            price1 = price[index1]
            break

    index2 = 0
    price2 = 0
    for i in time:
        t = datetime.datetime.fromtimestamp(i).strftime('%M')
        if float(t) == float(currentTime) - 2:
            index2 = time.index(i)
            price2 = price[index2]
            break

    return (price1, price2)


def Trade(market, profitpercent, amount, risk):
    #Styles
    c = colorama.Fore.YELLOW + colorama.Back.BLUE + '['
    r = ']' + colorama.Style.RESET_ALL + ' '
    y = colorama.Fore.YELLOW
    reset = colorama.Style.RESET_ALL

    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Symbol: ' + reset + market)
    lastprice = getTicker(market)
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Current Price: ' + reset + '%.8f' % lastprice)
    usdprice = USD_BTC_Price()
    balance = getBalance('btc')
    usdBalance = balance * usdprice
    amountToUse = amount * usdprice
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Bitcoin Balance:  ' + reset + '%.8f' % balance + ' | $' + '%.2f' % usdBalance)
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Amount to use:  ' + reset + '%.8f' % amount + ' | $' + '%.2f' % amountToUse)
    quantity = amount / lastprice
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Amount To Purchase: ' + reset + '%.8f' % quantity)
    print('------------------------------------' + reset)
    print(' ')
    price1, price2 = marketHistory(market)


    if float(risk) != 0:
        price1, price2 = marketHistory(market)
        riskAmount = config.get('RiskMultiplier', risk)
        p1 = price1 * float(riskAmount)
        p2 = price2 * float(riskAmount)

        if price1 != 0 and lastprice + lastprice * float(profitpercent) >= p1:
            print('Buy conditions not met, canceling order.')
            print('price 1')
            lastUSD = lastprice * usdprice
            print('Last Price: BTC ' + '%.8f' % lastprice + ' | $' + '%.2f' % lastUSD)
            potentialSell = lastprice + lastprice * float(profitpercent)
            potentialSellUSD = potentialSell * usdprice
            print('Potential Sell Price: BTC ' + '%.2f' %  potentialSell + ' | $' + '%.2f' %  potentialSellUSD)
            priceLimitUSD = p1 * usdprice
            print('Price Limit: BTC ' + '%.8f' %p1 + ' | $' + '%.2f' % priceLimitUSD)
            c = getTicker(market)
            currentUSD = c * usdprice
            print('Current Price: BTC ' + '%.8f' % c + ' | $' + '%.2f' % currentUSD)
            return

        if price2 != 0 and lastprice + lastprice * float(profitpercent) >= p2:
            print('Buy conditions not met, canceling order.')
            print('price 2')
            lastUSD = lastprice * usdprice
            print('Last Price: BTC ' + '%.8f' % lastprice + ' | $' + '%.2f' % lastUSD)
            potentialSell = lastprice + lastprice * float(profitpercent)
            potentialSellUSD = potentialSell * usdprice
            print('Potential Sell Price: BTC ' + '%.2f' %  potentialSell + ' | $' + '%.2f' %  potentialSellUSD)
            priceLimitUSD = p1 * usdprice
            print('Price Limit: BTC ' + '%.8f' %p1 + ' | $' + '%.2f' % priceLimitUSD)
            c = getTicker(market)
            currentUSD = c * usdprice
            print('Current Price: BTC ' + '%.8f' % c + ' | $' + '%.2f' % currentUSD)
            return

    buyorder = buyOrder(market, quantity)
    contbuy = True
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Placing Order...')
    while contbuy:
        time.sleep(1)
        order = getOrder(str(buyorder[0]))
        if order['status'] == 1:
            print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Order Successful!')
            print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Price: ' + reset + '%.8f' % order['rate'])
            print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Bitcoin Balance: ' + reset + '%.8f' % getBalance('btc'))
            print('------------------------------------')
            print(' ')
            contbuy = False

    order = getOrder(str(buyorder[0]))
    profit = order['rate'] * float(profitpercent)
    price = order['rate'] + profit
    rate = price / (1 + float(SellPercent))
    sellorder = sellOrder(market, rate)
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Sell Order Placed!')
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Price: ' + reset + '%.8f' % rate)
    print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Patiently Waiting...' + reset)
    contsell = True
    while contsell:
        time.sleep(2)
        order = getOrder(str(sellorder))
        print(c + strftime('%H:%M:%S', gmtime()) + r + y +  "Current Price: " + reset + '%.8f' % getTicker(market) , end="\r")
        if order['status'] == 1:
            print('------------------------------------')
            print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Sold!')
            print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Bitcoin Balance: ' + reset + '%.8f' % getBalance('btc'))
            usdprice = USD_BTC_Price()
            print(c + strftime('%H:%M:%S', gmtime()) + r + y + 'Bitcoin Balance in USD: ' + reset + str(getBalance('btc') * usdprice))
            contsell = False


def USD_BTC_Price():
    url = 'https://www.yobit.net/api/3/ticker/btc_usd'
    r = requests.get(url, headers={'apisign': hmac.new(secret, url.encode(), hashlib.sha512).hexdigest()})
    resp = json.loads(r.text)
    return resp['btc_usd']['last']


def main():
    balance = getBalance('btc')
    usd = USD_BTC_Price()
    usdprice = balance * usd
    print(colorama.Fore.RED + '_____________________________________________________________________')
    print(colorama.Fore.RED + 'Balance (BTC): ' + str(balance))
    print(colorama.Fore.RED + 'Balance in USD: ' + str(usdprice))
    print(colorama.Fore.RED + '_____________________________________________________________________')
    if platform.system() == "Windows":
        risk = input('[1] Risk Multiplier: ')
        amount = input('[2] % of bitcoin to spend: ')
        profit = input('[3] Profit %: ')
        symbol = input('[4] Coin: ')
    else:
        risk = input(colorama.Fore.CYAN + '[1] Risk Multiplier: ')
        amount = input(colorama.Fore.CYAN + '[2] % of bitcoin to spend: ')
        profit = input(colorama.Fore.CYAN + '[3] Profit %: ')
        symbol = input(colorama.Fore.CYAN + '[4] Coin: ')

    if len(profit) <= 1:
        profit = '0.0' + profit
    elif len(profit) <= 2:
        profit = '0.' + profit
    else:
        if len(profit) <= 3:
            profit = profit[0] + '.' + profit[1:]
        else:
            profit = profit[0:2]
    if len(amount) <= 1:
        amount = '0.0' + amount
    elif len(amount) <= 2:
        amount = '0.' + amount
    else:
        if len(amount) <= 3:
            amount = amount[0] + '.' + amount[1:]
        else:
            amount = amount[0:2]


    purchaseamount = balance * float(amount)
    Trade(symbol.lower(), profit, purchaseamount, risk)
