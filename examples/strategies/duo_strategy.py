from howtrader.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData
)
from howtrader.trader.object import Direction, Status, Interval
from howtrader.trader.constant import Exchange, Offset
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
        self.max_pos = 3  # 最大仓位
        self.buy_amount = 4000  # 买入数量
        self.take_profit = 0.05  # 止盈
        self.stop_loss = 0.025  # 止损
        self.vt_symbol = vt_symbols  # type: list
        self.holding_symbols = {}  # 持仓 symbol
        self.kline_dict = {}  # 存储 kline 数据
        self.expected_symbols = set(vt_symbols)  # 期望的 symbol
        self.trading = True  # 交易状态

    def on_init(self):
        self.write_log("策略初始化")
        # 加载所有合约的历史数据
        self.load_bar(15)

    def on_bar(self, bar: tuple):
        symbol = bar[0]
        bar_data = bar[1]

        if symbol in self.holding_symbols:
            # 持仓 symbol
            order_data: OrderData = self.holding_symbols[symbol]
            if order_data.price * (1 + self.take_profit) < bar_data.close_price:
                # 持仓价格高于最新价，则止盈
                self.send_order_symbol(Direction.LONG, Offset.CLOSETODAY, bar_data.close_price, order_data.volume, False,False, symbol)
            elif order_data.price * (1 - self.stop_loss) > bar_data.close_price:
                # 持仓价格低于最新价，则止损
                self.send_order_symbol(Direction.LONG, Offset.CLOSETODAY, bar_data.close_price, order_data.volume, False,False, symbol)
        self.bg.update_bar_sybmol(bar)

    def on_15min_bar(self, bar: tuple):
        # print(f"on_15min_bar-symbol=:{bar[0]},datetime=:{bar[1].datetime.strftime('%Y-%m-%d %H:%M:%S')},open={bar[1].open_price},high={bar[1].high_price},low={bar[1].low_price},close={bar[1].close_price},volume={bar[1].volume}")
        symbol = bar[0]
        bar_data = bar[1]
        # 存储 bar 数据
        if bar_data.datetime not in self.kline_dict:
            self.kline_dict[bar_data.datetime] = {}
            self.kline_dict[bar_data.datetime][symbol] = bar_data
        else:
            self.kline_dict[bar_data.datetime][symbol] = bar_data

        # 检查是否所有预期的 symbol 都已经到达
        if symbol in self.expected_symbols:
            self.expected_symbols.remove(symbol)

        # 如果所有预期的 symbol 都已经到达，则找出涨幅最大的 3 个 symbol
        if not self.expected_symbols:
            if bar_data.datetime not in self.kline_dict:
                return

            bars = self.kline_dict[bar_data.datetime]
            gainers = []

            for symbol, bar_data in bars.items():
                open_price = bar_data.open_price
                close_price = bar_data.close_price
                gain = (close_price - open_price) / open_price * 100
                gainers.append((symbol, gain))

            # 按涨幅从大到小排序
            gainers.sort(key=lambda x: x[1], reverse=True)

            # 打印涨幅最大的 3 个 symbol
            top_gainers = gainers[:self.max_pos]
            # print(f"Top gainers at {bar_data.datetime.strftime('%Y-%m-%d %H:%M:%S')}:")
            if len(self.holding_symbols) >= self.max_pos:
                # print("Already holding 3 symbols, no more buys.")
                return

            # 买入
            for symbol, gain in top_gainers:
                if symbol not in self.holding_symbols:
                    self.send_order_symbol(Direction.LONG, Offset.OPEN, bars[symbol].close_price, self.buy_amount / bars[symbol].close_price, False, False, symbol)
                    if len(self.holding_symbols) >= self.max_pos:
                        break

            # 重置预期的 symbol 集合
            self.expected_symbols = set(self.vt_symbol)
        # print(f"success")

    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_order(self, order: OrderData):
        if order.status == Status.ALLTRADED and order.direction == Direction.LONG and order.offset == Offset.OPEN:
            self.holding_symbols[order.symbol] = order
            print(f"开多仓-symbol=:{order.symbol},datetime=:{order.datetime.strftime('%Y-%m-%d %H:%M:%S')},price={order.price},volume={order.volume}, ")
        elif order.status == Status.ALLTRADED and order.direction == Direction.LONG and order.offset == Offset.CLOSETODAY:
            if order.symbol in self.holding_symbols:
                self.holding_symbols.pop(order.symbol)
                print(f"平多仓-symbol=:{order.symbol},datetime=:{order.datetime.strftime('%Y-%m-%d %H:%M:%S')},price={order.price},volume={order.volume}")


    def on_trade(self, trade: TradeData):
        """
        交易事件回调函数，当交易发生时触发该函数
        Args: trade (TradeData): 交易数据对象，包含交易相关信息
        """
        # print(f"on_trade:{trade}")

    def on_stop_order(self, stop_order: StopOrder):
        print(f"stop order:{stop_order}")

