import logging
from datetime import datetime

from howtrader.trader.constant import Exchange, Interval
from howtrader.trader.database import database_manager
from howtrader.trader.object import BarData
# 配置日志
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == '__main__':

    bar = BarData(
        symbol='rb2010',
        exchange=Exchange.BINANCE,
        datetime=datetime.now(),
        interval=Interval.MINUTE,
        volume=float(12.3),
        open_price=float(12.3),
        high_price=float(12.3),
        low_price=float(12.3),
        close_price=float(12.3),
        gateway_name=Exchange.BINANCE.value
    )
    print(database_manager.save_bar_data(datas=[bar]))