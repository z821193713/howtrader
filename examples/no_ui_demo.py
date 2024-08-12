import logging
from datetime import datetime

from howtrader.app.cta_strategy.backtesting_new import BacktestingEngine
from examples.strategies.duo_strategy import DuoBinanceStrategy
from howtrader.trader.constant import Interval

# 配置日志
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol=[
        "BTCUSDT.BINANCE",
        "ETHUSDT.BINANCE",
        "BCHUSDT.BINANCE",
        "XRPUSDT.BINANCE",
        "EOSUSDT.BINANCE",
        "LTCUSDT.BINANCE",
        "TRXUSDT.BINANCE",
        "ETCUSDT.BINANCE"
    ],
    interval=Interval.MINUTE,
    start=datetime(2023, 10, 1),
    end=datetime(2023, 10, 2),
    rate=6/ 10000,
    slippage=0,
    size=1,
    pricetick=0.01,
    capital=10000,
)

# 设置策略参数
strategy_setting = {
    "max_pos": 5,
    "buy_amount": 4000,
    "take_profit": 5,
    "stop_loss": 2.5,
}

# 添加策略
engine.add_strategy(DuoBinanceStrategy, strategy_setting)

# 加载数据并运行回测
engine.load_data()
engine.run_backtesting()

# # 显示回测结果
# engine.calculate_result()





















# engine.calculate_statistics()
# engine.show_chart()
