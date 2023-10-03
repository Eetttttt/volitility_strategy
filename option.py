from tqsdk import TqApi, TqAuth, TqKq
from tqsdk.ta import OPTION_IMPV, VOLATILITY_CURVE
import pandas as pd
import datetime

# 创建API实例,传入自己的快期账户
api = TqApi(TqKq(), auth=TqAuth("ggmmh", "gmh339714"))

# ------------------------------------------------------------------------------------------------------------------

# # 获取大商所豆粕期权行情
# quote_m = api.get_quote("DCE.m2401-C-3950")

# # 获取中金所股指期权行情
# quote_IO = api.get_quote("CFFEX.IO2002-C-3550")

# # 输出 m1807-C-2450 的最新行情时间和最新价
# print(quote_m.datetime, quote_m.last_price)

# ------------------------------------------------------------------------------------------------------------------

# quote_AU = api.get_quote("SHFE.au2312")

# # 预计输出的为以au2312现在最新价来比对的认购的平值期权，当没有符合的平值期权时返回为空,如果有返回则格式为 ["SHFE.au2312C30000"]
# ls1 = api.query_atm_options("SHFE.au2312", quote_AU.last_price, 0, "CALL")

# # 预计输出的为au2312，以开盘价来比对的认购的实值3档，实值2档，实值1档期权，如果没有符合要求的期权则对应栏返回为None，如果有则返回格式例如 [None,None,"SHFE.au2312C30000"]
# ls2 = api.query_atm_options("SHFE.au2312", quote_AU.open, [3, 2, 1], "CALL")

# print(ls1)
# print(ls2)

# ------------------------------------------------------------------------------------------------------------------

# # 获取指定期权行情
# quote = api.get_quote("SHFE.au2312C480")

# # 获取期权和对应标的的多合约 kline
# klines = api.get_kline_serial(["SHFE.au2312C480", "SHFE.au2312"], 24 * 60 * 60, 20)

# # 通过 OPTION_IMPV 函数计算隐含波动率，设置无风险利率为 0.025
# impv = OPTION_IMPV(klines, quote, 0.025)

# print(impv)

# ------------------------------------------------------------------------------------------------------------------

# 获取 m2112 的看跌期权
underlying = "SHFE.au2402"
options = api.query_options(underlying_symbol=underlying, option_class="PUT", expired=False)

# 批量获取合约的行情信息, 存储结构必须为 dict, key 为合约, value 为行情数据
quote = {}
for symbol in options:
    quote[symbol] = api.get_quote(symbol)
options.append(underlying)

klines = api.get_kline_serial(options, 24 * 60 * 60, 3)

# 使用 VOLATILITY_CURVE 函数计算波动率曲面
vc = VOLATILITY_CURVE(klines, quote, underlying, r=0.025)

vc['datetime'] = pd.to_datetime(vc['datetime'] / 1e9, unit='s')  # 除以 1e9 以将纳秒转换为秒

# 创建中国时区的时差
china_offset = datetime.timedelta(hours=8)  # 中国时区通常是 UTC+8

# 将时间转换为中国时区
vc['datetime'] = vc['datetime'] + china_offset  # 添加时差以转换为中国时区

# 格式化 datetime 列为字符串
vc['datetime'] = vc['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

vc.set_index('datetime',inplace=True)

print(vc)

# 关闭api,释放资源
api.close()