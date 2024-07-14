from howtrader.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from howtrader.trader.database import database_manager

class ManyStrategy(CtaTemplate):
    author = "your_name"

    # 止盈止损参数
    take_profit_pips = 4
    stop_loss_pips = 2
    trade_amount = 400  # 交易金额

    # 保存当前持仓
    positions = {}

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("策略初始化")

    def on_start(self):
        self.write_log("策略启动")

    def on_stop(self):
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # 获取每分钟涨幅最大的前5个数字货币
        top_5_symbols = self.get_top_5_symbols()

        for symbol in top_5_symbols:
            # 检查是否已经持有该数字货币
            if symbol in self.positions:
                continue

            # 按照收盘价购买400美元的数字货币
            self.buy(symbol, self.trade_amount / bar.close_price, bar.close_price)

            # 设置止盈止损
            self.set_stop_order(symbol, bar.close_price)

    def on_order(self, order: OrderData):
        pass

    def on_trade(self, trade: TradeData):
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        pass

    def get_top_5_symbols(self):
        # 这里需要实现获取每分钟涨幅最大的前5个数字货币的逻辑
        # 以下代码为示例，实际需要根据您的数据源进行实现
        all_symbols = self.cta_engine.get_all_symbols()
        top_5_symbols = sorted(all_symbols, key=lambda x: self.cta_engine.get_symbol_info(x).change_rate, reverse=True)[
                        :5]
        return top_5_symbols

    def buy(self, symbol, volume, price):
        # 发送买入订单
        self.send_order(symbol, CtaTemplate.ORDER_TYPE_MARKET, CtaTemplate.DIRECTION_LONG, volume, price, "buy")

    def set_stop_order(self, symbol, price):
        # 设置止盈止损
        self.send_stop_order(symbol, CtaTemplate.ORDER_TYPE_LIMIT, CtaTemplate.DIRECTION_SHORT,
                             self.trade_amount / price, price * (1 + self.take_profit_pips / 100), "take_profit")
        self.send_stop_order(symbol, CtaTemplate.ORDER_TYPE_LIMIT, CtaTemplate.DIRECTION_SHORT,
                             self.trade_amount / price, price * (1 - self.stop_loss_pips / 100), "stop_loss")

    def send_order(self, symbol, order_type, direction, volume, price, comment):
        # 发送订单
        self.cta_engine.send_order(symbol, order_type, direction, volume, price, comment)

    def send_stop_order(self, symbol, order_type, direction, volume, price, comment):
        # 发送止损/止盈订单
        self.cta_engine.send_stop_order(symbol, order_type, direction, volume, price, comment)
