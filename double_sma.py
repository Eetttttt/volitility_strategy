from tqsdk import TqApi, TqAuth, TargetPosTask, TqKq
from tqsdk.tafunc import ma

SHORT = 30  # 短周期
LONG = 60  # 长周期
SYMBOL = "SHFE.bu2012"  # 合约代码

api = TqApi(TqKq(), auth=TqAuth("ggmmh", "gmh339714"))
print("策略开始运行")

data_length = LONG + 2  # k线数据长度
# "duration_seconds=60"为一分钟线, 日线的duration_seconds参数为: 24*60*60
klines = api.get_kline_serial(SYMBOL, duration_seconds=60, data_length=data_length)
target_pos = TargetPosTask(api, SYMBOL)

while True:
    api.wait_update()

    if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算SMA
        short_avg = ma(klines["close"], SHORT)  # 短周期
        long_avg = ma(klines["close"], LONG)  # 长周期

        # 如果长周期均线在前一个K线时期（-2）低于短周期均线，而在当前K线时期（-1）高于短周期均线，那么执行做空操作
        if long_avg.iloc[-2] < short_avg.iloc[-2] and long_avg.iloc[-1] > short_avg.iloc[-1]:
            target_pos.set_target_volume(-3)
            print("均线下穿，做空")

        # 如果短周期均线在前一个K线时期低于长周期均线，而在当前K线时期高于长周期均线，那么执行做多操作
        if short_avg.iloc[-2] < long_avg.iloc[-2] and short_avg.iloc[-1] > long_avg.iloc[-1]:
            target_pos.set_target_volume(3)
            print("均线上穿，做多")