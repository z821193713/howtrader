from howtrader.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData
)
from howtrader.trader.object import Direction, Status, Interval
from howtrader.trader.constant import Exchange
import pandas as pd
from datetime import timedelta

from howtrader.trader.utility import BarGenerator


class DuoBinanceStrategy(CtaTemplate):
    author = "ChatGPT"

    parameters = ["max_pos", "buy_amount", "take_profit", "stop_loss"]
    variables = ["holding_symbols", "kline_dict"]

    def __init__(self, cta_engine, strategy_name, vt_symbols, setting):
        super().__init__(cta_engine, strategy_name, vt_symbols, setting)
        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.max_pos = 5
        self.buy_amount = 4000
        self.take_profit = 5
        self.stop_loss = 2.5
        self.vt_symbol = vt_symbols
        self.holding_symbols = []
        self.kline_dict = {}


    def on_init(self):
        self.write_log("策略初始化")
        # 加载所有合约的历史数据
        self.load_bar(15)

    def on_bar(self, bar: tuple):
        # print(f"on_bar-symbol=:{bar[0]},datetime=:{bar[1].datetime.strftime('%Y-%m-%d %H:%M:%S')},open={bar[1].open_price},high={bar[1].high_price},low={bar[1].low_price},close={bar[1].close_price},volume={bar[1].volume}")
        self.bg.update_bar_sybmol(bar)

    def on_15min_bar(self, bar: tuple):
        print(f"on_15min_bar-symbol=:{bar[0]},datetime=:{bar[1].datetime.strftime('%Y-%m-%d %H:%M:%S')},open={bar[1].open_price},high={bar[1].high_price},low={bar[1].low_price},close={bar[1].close_price},volume={bar[1].volume}")
        print(f"success")
    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_order(self, order: OrderData):
        pass

    def on_trade(self, trade: TradeData):
        pass

    def on_stop_order(self, stop_order: StopOrder):
        pass
