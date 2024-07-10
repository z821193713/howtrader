# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Sequence

from howtrader.trader.constant import Exchange, Interval
from howtrader.trader.database import database_manager
from howtrader.trader.object import BarData

if __name__ == '__main__':
    btcdata: Sequence[BarData] = database_manager.load_bar_data(symbol='BTCUSDT',
                                                                exchange=Exchange.BINANCE,
                                                                interval=Interval.MINUTE,
                                                                start=datetime.strptime('2020-08-01', '%Y-%m-%d'),
                                                                end=datetime.strptime('2020-09-01', '%Y-%m-%d')
                                                                )
    for bar_data in btcdata:
        print(bar_data.datetime, bar_data.close_price)