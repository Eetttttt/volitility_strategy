import datetime


# 将 Unix 时间戳转换为 datetime 对象
timestamp = 1.694966e+18
dt = datetime.datetime.fromtimestamp(timestamp / 1e9)  # 除以 1e9 以将纳秒转换为秒

# 将 datetime 格式化为字符串
formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')

print(formatted_date)
