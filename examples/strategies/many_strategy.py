from typing import Sequence

import pandas as pd
from pandas import DataFrame

from howtrader.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from howtrader.trader.constant import Exchange, Interval, Direction, OrderType, Offset
from howtrader.trader.database import database_manager


class ManyStrategy(CtaTemplate):
    author = "zjl"

    # 止盈止损参数
    take_profit_pips = 4
    stop_loss_pips = 2
    trade_amount = 4000  # 交易金额

    window_length = 15  # 窗口长度

    # 保存当前持仓
    positions = {}

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, window=self.window_length, on_window_bar=self.on_window_bar(), interval=Interval.MINUTE)
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("策略初始化")

    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.put_event()
        self.bg.update_bar(bar)

    def on_window_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 获取每分钟涨幅最大的前5个数字货币
        top_5_symbols = self.get_top_5_symbols(bar.datetime)

        # 如果持仓数量已经达到5个，则不进行新的交易
        if len(self.positions) >= 5:
            return

        for i in range(5 - len(top_5_symbols)):
            # 检查是否已经持有该数字货币
            symbolObj = top_5_symbols[i]
            if symbolObj.symbol in self.positions:
                continue

            # 选择一个涨幅最高的数字货币进行购买
            self.cta_engine.send_order(vt_symbol=symbolObj.symbol,
                                       price=symbolObj.close_price,
                                       volume=self.trade_amount / symbolObj.close_price,
                                       direction=Direction.LONG,
                                       offset=Offset.OPEN
                                       )
            self.positions[symbolObj.symbol] = bar.close_price

    def on_order(self, order: OrderData):
        """
        处理订单事件回调函数。

        Args:
            order (OrderData): 订单数据对象，包含订单的所有信息。

        Returns:
            None: 无返回值。

        """
        pass

    def on_trade(self, trade: TradeData):
        """
        处理交易事件。

        Args:
            trade (TradeData): 交易数据对象，包含了交易相关的所有信息。

        Returns:
            None: 该方法没有返回值。

        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        处理停止订单事件的回调函数。

        Args:
            stop_order (StopOrder): 停止订单对象，包含停止订单的相关信息。

        Returns:
            None: 该方法不返回任何值。

        """
        pass

    def get_top_5_symbols(self,datetime):
        """
        获取涨幅最大的前五个数字货币符号及其相关信息。

        Args:
            datetime (datetime.datetime): 指定时间点的datetime对象，用于加载该时间点的数字货币数据。

        Returns:
            List[Dict[str, Union[str, float]]]: 包含涨幅最大的前五个数字货币信息的列表，每个元素为字典类型，
            包含以下字段：
            - symbol (str): 数字货币符号。
            - open_price (float): 开盘价。
            - close_price (float): 收盘价。
            - percentage_change (float): 涨跌幅（百分比）。

        """
        # 从数据库加载所有数字货币的数据
        all_symbols: Sequence["BarData"] = database_manager.load_bar_symbols_data(exchange=Exchange.BINANCE, interval=Interval.MINUTE,
                                                         symbol_datetime=datetime.strftime("%Y-%m-%d %H:%M:%S"))
        # 将数据转换为Pandas DataFrame
        df: DataFrame = pd.DataFrame(all_symbols)
        # 计算每个数字货币的涨幅
        df['percentage_change'] = (df['close_price'] - df['open_price']) / df['open_price'] * 100
        top_5_symbols = df.nlargest(5, 'percentage_change')

        return top_5_symbols.to_dict('records')
