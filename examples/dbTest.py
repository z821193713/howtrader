import logging
from datetime import datetime
from typing import Sequence

from howtrader.trader.constant import Exchange, Interval
from howtrader.trader.database import database_manager
from howtrader.trader.database.database import Driver
from howtrader.trader.object import BarData

from howtrader.trader.database import database_sql

# 配置日志
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == '__main__':
    # import os
    # os.environ["http_proxy"] = "http://rootadmin:HZBr3TwDy0um1yrH@101.42.15.169:8888"
    # os.environ["https_proxy"] = "http://rootadmin:HZBr3TwDy0um1yrH@101.42.15.169:8888"
    db = database_sql.init(driver=Driver.SQLITE, settings={'database': 'C:/Users/Administrator/howtrader/database.db'})
    dataList: Sequence[BarData] = db.load_bar_data(symbol='BTCUSDT',
                     exchange=Exchange.BINANCE,
                     interval=Interval.MINUTE,
                     start=datetime.strptime('2020-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"),
                     end=datetime.strptime("2024-01-01 23:59:59", "%Y-%m-%d %H:%M:%S")
                     )

    print(database_manager.save_bar_data(datas=dataList))
