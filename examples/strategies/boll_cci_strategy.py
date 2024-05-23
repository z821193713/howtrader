from pandas import Series

from howtrader.app.cta_strategy import CtaTemplate, StopOrder
from howtrader.trader.object import TickData, BarData, OrderData, TradeData
from howtrader.trader.utility import BarGenerator, ArrayManager
import pandas_ta as ta
import pandas as pd

class BollCciStrategy(CtaTemplate):
    """
    移动平均线(ma)、CCI（Commodity Channel Index）
    """
    author = "zjl"
    sma_window: int = 19  # 10日移动平均线
    cci_window: int = 18  # 10天的平均价
    buy_sell_value: int = 100

    sma_result: float = 0.0  # 结果
    cci_value: float = 0.0  # cci值

    parameters = [
        "sma_window",
        "cci_window",
        "buy_sell_value"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """
        Constructor for BollRsiCciStrategy class.
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        # self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()


    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.put_event()
        self.bg.update_bar(bar)

    def on_15min_bar(self, bar: BarData):
        """
        Callback of new 15min bar data update.
        """
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        close: Series = pd.Series(am.close_array)
        high: Series = pd.Series(am.high_array)
        low: Series = pd.Series(am.low_array)

        current_close: float = close.iloc[-1]  # 当前k线的收盘价
        front1_close: float = close.iloc[-2]  # 前1跟k线的收盘价
        front2_close: float = close.iloc[-3]  # 前2跟k线的收盘价
        front3_close: float = close.iloc[-4]  # 前3跟k线的收盘价
        self.sma_result = ta.sma(close, self.sma_window).iloc[-1]

        self.cci_value = ta.cci(high, low, close, self.cci_window).iloc[-1]

        cross_over: bool = (front3_close < self.sma_result and
                            front2_close < self.sma_result and
                            front1_close < self.sma_result and
                            current_close > self.sma_result)  # 上穿

        cross_below: bool = (front3_close > self.sma_result and
                             front2_close > self.sma_result and
                             front1_close > self.sma_result and
                             current_close < self.sma_result)  # 下穿

        if self.pos == 0:
            if cross_over:
                self.buy(bar.close_price, 100)  # 开多
            elif cross_below:
                self.short(bar.close_price, 100)  # 开空
        elif self.pos > 0:
            if self.buy_sell_value < self.cci_value:
                self.sell(bar.close_price, 100)  # 卖多
            if cross_below and self.pos > 0:
                self.sell(bar.close_price, 100)  # 卖多
                self.short(bar.close_price, 100)  # 开空

        elif self.pos < 0:
            if (-self.buy_sell_value) > self.cci_value:
                self.cover(bar.close_price, 100)  # 卖空
            if cross_over and self.pos < 0:
                self.cover(bar.close_price, 100)  # 卖空
                self.buy(bar.close_price, 100)  # 开多
        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass
        # print(f"order datetime: {order.datetime} price: {order.price}, volume: {order.volume}, direction: {order.direction.value}, offset: {order.offset.value}, traded: {order.traded}, status: {order.status.value}")

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        print(f" trade datetime: {trade.datetime} symbol: {trade.symbol} price: {trade.price}, volume: {trade.volume}")
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass