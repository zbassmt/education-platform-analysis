import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取用户数据
users = pd.read_csv(r'C:\Users\DELL\Desktop\数字图书馆关键技术期末作业-20250108\线上教育课程数据分析\users.csv',
                    encoding='gbk')

# 将注册时间和最近登录时间转换为日期时间格式
users['register_time'] = pd.to_datetime(users['register_time'], errors='coerce')
users['recently_logged'] = pd.to_datetime(users['recently_logged'], errors='coerce')

# 定义观察日期
observation_dates = {
    '1_month': timedelta(days=30),
    '3_months': timedelta(days=90),
    '6_months': timedelta(days=180)
}

# 初始化留存率字典
retention_rates = {}

# 计算每个观察日期的留存率
for period, delta in observation_dates.items():
    # 计算观察日期
    observation_date = users['register_time'] + delta

    # 统计在观察日期仍然活跃的用户数
    active_users = users[users['recently_logged'] >= observation_date]
    retention_count = active_users.shape[0]

    # 计算留存率
    retention_rate = retention_count / users.shape[0]
    retention_rates[period] = retention_rate

# 打印留存率
for period, rate in retention_rates.items():
    print(f'{period} 留存率: {rate:.2%}')

# 绘制留存率图表
periods = list(retention_rates.keys())
rates = list(retention_rates.values())

plt.figure(figsize=(10, 6))
plt.bar(periods, rates, color='skyblue')
plt.title('用户留存率分析')
plt.xlabel('观察周期')
plt.ylabel('留存率')
plt.ylim(0, 1)
plt.show()
