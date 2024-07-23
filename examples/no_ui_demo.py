from datetime import datetime

from howtrader.app.cta_strategy.backtesting import BacktestingEngine
from examples.strategies.demo01_strategy import BinanceStrategy
from howtrader.trader.constant import Interval

engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="BTCUSDT.BINANCE",
    interval=Interval.MINUTE,
    start=datetime(2023, 10, 1),
    end=datetime(2023, 10, 3),
    rate=6/ 10000,
    slippage=0,
    size=1,
    pricetick=0.01,
    capital=10000,
)

# 设置策略参数
strategy_setting = {
    "symbols": [
        "BTCUSDT.BINANCE",
        "ETHUSDT.BINANCE",
        "BCHUSDT.BINANCE",
        "XRPUSDT.BINANCE",
        "EOSUSDT.BINANCE",
        "LTCUSDT.BINANCE",
        "TRXUSDT.BINANCE",
        "ETCUSDT.BINANCE"
    ],
    "max_pos": 5,
    "buy_amount": 4000,
    "take_profit": 5,
    "stop_loss": 2.5,
}

# 添加策略
engine.add_strategy(BinanceStrategy, strategy_setting)

# 加载数据并运行回测
engine.load_data()
engine.run_backtesting()

# 显示回测结果
engine.calculate_result()
engine.calculate_statistics()
engine.show_chart()
