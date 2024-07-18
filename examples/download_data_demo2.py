"""
    我们使用币安原生的api进行数据爬取.

"""
import logging
import pandas as pd
import time
from datetime import datetime
import requests
import pytz

from howtrader.trader.database import database_manager

pd.set_option('expand_frame_repr', False)  #
from howtrader.trader.object import BarData, Interval, Exchange

BINANCE_SPOT_LIMIT = 1000
BINANCE_FUTURE_LIMIT = 1500

CHINA_TZ = pytz.timezone("Asia/Shanghai")
from threading import Thread


def exchangeInfo():
    """
    {'timezone': 'UTC', 'serverTime': 1570802268092, 'rateLimits':
    [{'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200},
    {'rateLimitType': 'ORDERS', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200}],
     'exchangeFilters': [], 'symbols':
     [{'symbol': 'BTCUSDT', 'status': 'TRADING', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000',
     'baseAsset': 'BTC', 'quoteAsset': 'USDT', 'pricePrecision': 2, 'quantityPrecision': 3, 'baseAssetPrecision': 8,
     'quotePrecision': 8,
     'filters': [{'minPrice': '0.01', 'maxPrice': '100000', 'filterType': 'PRICE_FILTER', 'tickSize': '0.01'},
     {'stepSize': '0.001', 'filterType': 'LOT_SIZE', 'maxQty': '1000', 'minQty': '0.001'},
     {'stepSize': '0.001', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '1000', 'minQty': '0.001'},
     {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'},
     {'multiplierDown': '0.8500', 'multiplierUp': '1.1500', 'multiplierDecimal': '4', 'filterType': 'PERCENT_PRICE'}],
     'orderTypes': ['LIMIT', 'MARKET', 'STOP'], 'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX']}]}

    :return:
    """

    path = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    return requests.get(url=path, timeout=20, proxies=proxies).json()


def generate_datetime(timestamp: float) -> datetime:
    """
    :param timestamp:
    :return:
    """
    dt = datetime.fromtimestamp(timestamp / 1000)
    dt = CHINA_TZ.localize(dt)
    return dt


def get_binance_data(symbol: str, exchanges: str, start_time: str, end_time: str):
    """
    爬取币安交易所的数据
    :param symbol: BTCUSDT.
    :param exchanges: 现货、USDT合约, 或者币币合约.
    :param start_time: 格式如下:2020-1-1 或者2020-01-01
    :param end_time: 格式如下:2020-1-1 或者2020-01-01
    :return:
    """

    api_url = ''
    save_symbol = symbol
    gate_way = 'BINANCES'

    if exchanges == 'spot':
        print("spot")
        limit = BINANCE_SPOT_LIMIT
        save_symbol = symbol.lower()
        gate_way = 'BINANCE'
        api_url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit={limit}'

    elif exchanges == 'future':
        print('future')
        limit = BINANCE_FUTURE_LIMIT
        api_url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1m&limit={limit}'

    elif exchanges == 'coin_future':
        print("coin_future")
        limit = BINANCE_FUTURE_LIMIT
        f'https://dapi.binance.com/dapi/v1/klines?symbol={symbol}&interval=1m&limit={limit}'

    else:
        raise Exception('交易所名称请输入以下其中一个：spot, future, coin_future')

    start_time = int(datetime.strptime(start_time, '%Y-%m-%d').timestamp() * 1000)
    end_time = int(datetime.strptime(end_time, '%Y-%m-%d').timestamp() * 1000)

    while True:
        try:
            url = f'{api_url}&startTime={start_time}'
            print(f'{api_url}&startTime={datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")}')
            data = requests.get(url=url, timeout=100, proxies=proxies).json()
            buf = []

            for l in data:
                bar = BarData(
                    symbol=save_symbol,
                    exchange=Exchange.BINANCE,
                    datetime=generate_datetime(l[0]),
                    interval=Interval.MINUTE,
                    volume=float(l[5]),
                    open_price=float(l[1]),
                    high_price=float(l[2]),
                    low_price=float(l[3]),
                    close_price=float(l[4]),
                    gateway_name=gate_way
                )
                buf.append(bar)

            database_manager.save_bar_data(buf)

            # 到结束时间就退出, 后者收盘价大于当前的时间.
            if (data[-1][0] > end_time) or data[-1][6] >= (int(time.time() * 1000) - 60 * 1000):
                break

            start_time = data[-1][0]

        except Exception as error:
            print(error)
            time.sleep(10)


def download_spot(symbol):
    """
    下载现货数据的方法.
    :return:
    """
    t1 = Thread(target=get_binance_data, args=(symbol, 'spot', "2018-1-1", "2019-1-1"))

    t2 = Thread(target=get_binance_data, args=(symbol, 'spot', "2019-1-1", "2020-1-1"))

    t3 = Thread(target=get_binance_data, args=(symbol, 'spot', "2020-1-1", "2020-11-16"))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


def download_future(symbol, start_time, end_time='2024-12-31'):
    """
    下载合约数据的方法。
    :return:
    """
    year = datetime.strptime(start_time, '%Y-%m-%d').year
    threads = []

    for year in range(year, 2025):
        for month in range(1, 12, 3):
            month_str = str(month + 3) if month < 10 else str(1)
            year_str = str(year) if month < 10 else str(year + 1)
            if year == 2024:
                if month >= 10:
                    continue
            print(symbol, "%s-%s-01" % (str(year), str(month).zfill(2)), "%s-%s-01" % (year_str, month_str.zfill(2)))
            t = Thread(
                target=get_binance_data,
                args=(symbol, 'future', "%s-%s-01" % (str(year), str(month).zfill(2)),
                      "%s-%s-01" % (year_str, month_str.zfill(2)))
            )
            t.start()
            threads.append(t)

    # 等待所有线程完成
    for t in threads:
        t.join()


if __name__ == '__main__':
    # 配置日志
    # logger = logging.getLogger('peewee')
    # logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    # 如果你有代理你就设置，如果没有你就设置为 None 或者空的字符串 "",
    # 但是你要确保你的电脑网络能访问币安交易所，你可以通过 ping api.binance.com 看看过能否ping得通
    proxy_host = "127.0.0.1"  # 如果没有就设置为"", 如果有就设置为你的代理主机如：127.0.0.1
    proxy_port = 7890  # 设置你的代理端口号如: 1087, 没有你修改为0,但是要保证你能访问api.binance.com这个主机。
    proxies = None
    if proxy_host and proxy_port:
        proxy = f'http://{proxy_host}:{proxy_port}'
        proxies = {'http': proxy, 'https': proxy}

    data = exchangeInfo()
    usdt_symbols = [symbol for symbol in data['symbols'] if symbol['symbol'].endswith('USDT')]
    usdt_symbols
    for symbol in usdt_symbols:
        sym = symbol['symbol']
        deliveryDate = symbol['deliveryDate']
        onboardDate = symbol['onboardDate']
        print("symbol=%s, deliveryDate=%s, onboardDate=%s" % (sym,
                                                              datetime.fromtimestamp(deliveryDate / 1000).strftime(
                                                                  '%Y-%m-%d %H:%M:%S'),
                                                              datetime.fromtimestamp(onboardDate / 1000).strftime(
                                                                  '%Y-%m-%d %H:%M:%S')
                                                              )
              )

        download_future(sym, start_time=datetime.fromtimestamp(onboardDate / 1000).strftime('%Y-%m-%d'))  # 下载合约的数据

    # download_future('XLMUSDT', start_time='2024-01-01')  # 下载合约的数据
    # print(symbols)

    # download_spot(symbol) # 下载现货的数据.

    # download_future(symbol)  # 下载合约的数据
