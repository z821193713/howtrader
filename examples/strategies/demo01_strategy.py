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


class BinanceStrategy(CtaTemplate):
    author = "ChatGPT"

    parameters = ["max_pos", "buy_amount", "take_profit", "stop_loss"]
    variables = ["holding_symbols", "kline_dict"]

    def __init__(self, cta_engine, strategy_name, vt_symbols, setting):
        super().__init__(cta_engine, strategy_name, vt_symbols, setting)
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
        self.load_bar(5)

    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        pass

    def on_bar(self, bar: BarData):
        self.cancel_all()

        symbol = bar.symbol
        if symbol not in self.kline_dict:
            self.kline_dict[symbol] = pd.DataFrame()

        self.kline_dict[symbol] = self.kline_dict[symbol].append(bar.__dict__, ignore_index=True)

        # 保持仅保留最新的5分钟数据
        self.kline_dict[symbol] = self.kline_dict[symbol].loc[
            self.kline_dict[symbol]["datetime"] >= (bar.datetime - timedelta(minutes=5))
            ]

        if len(self.kline_dict[symbol]) < 5:
            return

        # 计算所有合约的5分钟涨幅
        kline_changes = {}
        for sym, kline_df in self.kline_dict.items():
            if len(kline_df) >= 5:
                first_close = kline_df.iloc[0]["close"]
                last_close = kline_df.iloc[-1]["close"]
                change = (last_close - first_close) / first_close * 100
                kline_changes[sym] = change

        # 找到涨幅最大的5个合约
        sorted_symbols = sorted(kline_changes, key=kline_changes.get, reverse=True)
        top_symbols = sorted_symbols[:5]

        # 卖出止盈或止损的持仓
        for holding_symbol in list(self.holding_symbols):
            holding_pos = self.get_pos(holding_symbol)
            if holding_pos:
                symbol_close = self.kline_dict[holding_symbol].iloc[-1]["close"]
                avg_price = holding_pos.price
                pnl = (symbol_close - avg_price) / avg_price * 100

                if pnl >= self.take_profit or pnl <= -self.stop_loss:
                    self.sell(holding_symbol, symbol_close, holding_pos.volume)
                    self.holding_symbols.remove(holding_symbol)

        # 买入新的合约
        for symbol in top_symbols:
            if len(self.holding_symbols) >= self.max_pos:
                break

            if symbol not in self.holding_symbols:
                symbol_close = self.kline_dict[symbol].iloc[-1]["close"]
                volume = self.buy_amount / symbol_close
                self.buy(symbol, symbol_close, volume)
                self.holding_symbols.add(symbol)

    def on_order(self, order: OrderData):
        pass

    def on_trade(self, trade: TradeData):
        pass

    def on_stop_order(self, stop_order: StopOrder):
        pass
