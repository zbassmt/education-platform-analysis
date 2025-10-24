import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pyecharts.charts import Line, Bar, Map
import datetime
import chinese_calendar
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Map

# 中文乱码与坐标轴负号处理
plt.rcParams['font.sans-serif'] = ['Microsoft Yahei']
plt.rcParams['axes.unicode_minus'] = False

Login = pd.read_csv(r'C:\Users\DELL\Desktop\数字图书馆关键技术期末作业-20250108\线上教育课程数据分析\Login.csv', encoding='gbk')
Login.head()

study_information = pd.read_csv(r'C:\Users\DELL\Desktop\数字图书馆关键技术期末作业-20250108\线上教育课程数据分析\study_information.csv', encoding='gbk')
study_information.head()

users = pd.read_csv(r'C:\Users\DELL\Desktop\数字图书馆关键技术期末作业-20250108\线上教育课程数据分析\users.csv', encoding='gbk')
users1 = users[['user_id', 'register_time', 'recently_logged', 'learn_time']].copy()  # 使用 .copy() 显式创建副本
users1.head()

# 缺失值处理
Login.isnull().mean()
study_information.isnull().mean()
# 删除 price 的缺失，认 0 为免费课程
study_information = study_information.dropna(subset=['price'])
study_information.head()

users1.isnull().mean()
users1 = users1.dropna(subset=['user_id'])  # 修改为 users1 而不是 users
users1.head()

# excel 表格处理
users1.to_csv('new_users1.csv', index=False)
new_users1 = pd.read_csv('new_users1.csv')
new_users1.columns
new_users = new_users1[['user_id', 'register_time', 'recently_logged', 'learn_time']]  # 只选择存在的列
new_users.head()

print("Login表存在重复值：", any(Login.duplicated()))
print("study_information表存在重复值：", any(study_information.duplicated()))
print("users表存在重复值：", any(new_users.duplicated()))

new_users.drop_duplicates(inplace=True)
new_users.head()

# 国内热力图
Login['guobie'] = Login['login_place'].apply(lambda x: x[0:2]).tolist()
Login.head(5)
#处理掉省份名为三个字的省，即内蒙古、黑龙江
# 使用 .copy() 显式创建副本，内蒙古
Login_nei = Login.loc[Login['login_place'].str.contains("内蒙古")].copy()
Login_nei['shengfen'] = Login_nei['login_place'].apply(lambda x: x[2:5])
Login_nei['chengshi'] = Login_nei['login_place'].apply(lambda x: x[5:])
Login_nei.head()
#处理黑龙江
Login_hei = Login.loc[Login['login_place'].str.contains("黑龙江")].copy()
Login_hei['shengfen'] = Login_hei['login_place'].apply(lambda x: x[2:5])
Login_hei['chengshi'] = Login_hei['login_place'].apply(lambda x: x[5:])
Login_hei.head()

#处理其他名字为两个字的省份
Login2 = Login.loc[~Login['login_place'].str.contains("内蒙古|黑龙江")].copy()
Login2['shengfen'] = Login2['login_place'].apply(lambda x: x[2:4])
Login2['chengshi'] = Login2['login_place'].apply(lambda x: x[4:])
Login2.head(5)

#将所有数据进行合并，得到完整数据
Login_he1 = pd.concat([Login_nei, Login2], ignore_index=True)
Login_he2 = pd.concat([Login_he1, Login_hei], ignore_index=True)
Login_he = Login_he2[['user_id', 'login_time', 'guobie', 'shengfen', 'chengshi']]
Login_he.head()

# 国外
# 按照国别进行分组，并统计每个国家的登录次数
Login_he2 = Login_he.groupby(by='guobie', as_index=False).count()
# 不包括中国的数据
Login_he3 = Login_he2[~Login_he2['guobie'].isin(["中国"])].copy()  # 使用 .copy() 显式创建副本
Login_he3


x_data = list(Login_he3['guobie'])
y_data = Login_he3['user_id']

# 特殊值标记
line = (Line()
        .add_xaxis(x_data)
        .add_yaxis("国外平台登录情况", y_data)
        .set_series_opts(
            # 为了不影响标记点，这里把标签关掉
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值")
                ]))
        .set_global_opts(
            toolbox_opts=opts.ToolboxOpts(),  # 工具箱
            datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100)  # 横轴缩放
        )
        )
line.render_notebook()
line.render("world.html")

# 各省份登陆热力图
# 不包括国外
Login_china = Login_he[Login_he['guobie'].isin(["中国"])].copy()  # 使用 .copy() 显式创建副本

Login_china2 = Login_china.groupby(by='shengfen', as_index=False).count()
Login_china3 = Login_china2.iloc[1:,].copy()  # 使用 .copy() 显式创建副本
Login_china3['count'] = Login_china3['user_id']  # 使用 .loc 进行显式赋值
Login_china3.head()
print(Login_china3)

# 全国省份登陆用户人数分布
x_data = list(Login_china3['shengfen'])
y_data = list(Login_china3['count'])
# 特殊值标记
bar = (Bar()
       .add_xaxis(x_data)
       .add_yaxis('国内平台登录次数', y_data)
       .set_series_opts(
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
            ]))
       .set_global_opts(
            # title_opts=opts.TitleOpts(title="国内平台登录次数", subtitle="副标题"),                         # 标题
            toolbox_opts=opts.ToolboxOpts(),                 # 工具箱
            datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100)     # 横轴缩放
        )
       .set_series_opts(
        # 为了不影响标记点，这里把标签关掉
        label_opts=opts.LabelOpts(is_show=False),
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(type_="average", name="平均值")
            ]))
      )

bar.render_notebook()
bar.render('map2.html')  # 保存到本地


province = ['北京市', '天津市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
            '山东省', '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区', '海南省', '重庆市', '四川省', '贵州省', '云南省', '陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区']

values = list(Login_china3['count'])
data = [[province[i], values[i]] for i in range(len(province))]
map = (
    Map()
    .add("中国地图平台登录次数", data, 'china')
)

map.set_global_opts(
    visualmap_opts=opts.VisualMapOpts(max_=125000),  # 最大数据范围
    toolbox_opts=opts.ToolboxOpts()  # 工具箱
)

map.render_notebook()
map.render("cmap.html")  # 全国热力图

# 所有省份
def plot_city_login_map(df, province, max_value, filename):
    # 确保 chengshi 列为字符串类型
    df["new_chengshi"] = df['chengshi'].astype(str) + '市'

    city_name_mapping = {
        '恩施土家族苗族自治州市': '恩施土家族苗族自治州',
        '神农架林区市': '神农架林区',
        '黔东南苗族侗族自治州市': '黔东南苗族侗族自治州',
        '黔南布依族苗族自治州市': '黔南布依族苗族自治州',
        '黔西南布依族苗族自治州市': '黔西南布依族苗族自治州'
    }

    df['new_chengshi'] = df['new_chengshi'].replace(city_name_mapping)

    x_data = list(df['new_chengshi'])
    y_data = list(df['user_id'])
    data = [[x_data[i], y_data[i]] for i in range(len(y_data))]

    if not data:
        print(f"警告: {province} 的数据为空，跳过绘制热力图。")
        return

    map = (
        Map()
        .add(f"{province}各城市平台登录次数热力地图", data, province)
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                max_=max_value,
                is_piecewise=True,  # 启用分段模式
                pieces=[
                    {"min": 100000, "color": "#c82423"} , # 蓝色
                    {"min": 50000, "max": 99999, "color": "#fa8878"},  # 青色
                    {"min": 10000, "max": 49999, "color":"#ffbe7a"},  # 绿色
                    {"min": 1000, "max": 9999, "color": "#3480b8"},  # 黄色
                    {"min": 100, "max": 999, "color":"#add3e2"},  # 橙色
                    {"min": 0, "max": 99, "color": "#8dcec88"},  # 红色

                ]
            ),
            toolbox_opts=opts.ToolboxOpts()
        )
    )
    map.render_notebook()
    map.render(f"{filename}.html")
    print(f"{filename}.html 文件已保存。")
# 定义省份列表
provinces = [
    '内蒙古','广东','北京','香港','广西','山东','湖南','湖北','浙江','福建','江苏','贵州','陕西','重庆',
    '四川','河北','甘肃','安徽','海南','河南','辽宁','江西','天津','新疆','上海','山西','云南','台湾',
    '吉林','宁夏','青海','澳门','西藏','黑龙江'
    # 可以继续添加其他省份
]


# 数据预处理：填充 chengshi 为空的值
Login_he['chengshi'] = Login_he['chengshi'].fillna('未知')

# 按省份分类处理
max_values = {}
provinces = Login_he['shengfen'].unique()

for province in provinces:
    # 筛选出当前省份的数据
    Login_prov1 = Login_he[Login_he['shengfen'] == province].copy()

    if Login_prov1.empty:
        print(f"警告: {province} 的数据为空，跳过绘制热力图。")
        max_values[province] = 0
        continue

    # 按城市分组并计算登录次数
    Login_prov2 = Login_prov1.groupby('chengshi', as_index=False).count()

    if Login_prov2.empty:
        print(f"警告: {province} 的 groupby 数据为空，跳过绘制热力图。")
        max_values[province] = 0
        continue

    # 找到最大登录次数
    max_value = Login_prov2['user_id'].max()
    max_values[province] = max_value

# 循环遍历省份列表并绘制热力图
for province, max_value in max_values.items():
    Login_prov1 = Login_he[Login_he['shengfen'] == province].copy()

    if Login_prov1.empty:
        print(f"警告: {province} 的数据为空，跳过绘制热力图。")
        continue

    Login_prov2 = Login_prov1.groupby('chengshi', as_index=False).count()

    if Login_prov2.empty:
        print(f"警告: {province} 的 groupby 数据为空，跳过绘制热力图。")
        continue

    # 调用 plot_city_login_map 函数
    plot_city_login_map(Login_prov2, province, max_value, f'{province}_map')

# 统计不同国家用户的分布情况
users['register_time'] = pd.to_datetime(users['register_time'], errors='coerce')
users['year_month'] = users['register_time'].dt.to_period('M').astype(str)
# 从 Login 数据框中提取国家信息
Login['guobie'] = Login['login_place'].apply(lambda x: x[0:2]).tolist()
# users 数据框中有一个 user_id 列，用于与 Login 数据框合并
# 合并 users 和 Login 数据框，根据 user_id 进行合并
users = pd.merge(users, Login[['user_id', 'guobie']].drop_duplicates(), on='user_id', how='left')

# 使用数据透视表统计不同国家用户的分布情况
country_user_count = users.pivot_table(index='year_month', columns='guobie', values='user_id', aggfunc='count', fill_value=0)
print(country_user_count)

# 设置表格样式
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('tight')
ax.axis('off')

# 绘制表格
table = ax.table(
    cellText=country_user_count.values,
    colLabels=country_user_count.columns,
    rowLabels=country_user_count.index,
    cellLoc='center',
    loc='center',
    bbox=[0, 0, 1, 1],  # 调整表格的边界框
    edges='open'  # 去掉表格边框
)
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.2)  # 调整表格大小

# 设置标题
plt.title("不同国家用户的分布情况", fontsize=16, fontweight='bold')
plt.show()


# 2.2统计每月新增用户数
monthly_new_users = users.groupby('year_month').size().reset_index(name='new_user_count')

# 绘制每月新增用户数折线图
x_data = list(monthly_new_users['year_month'])
y_data = list(monthly_new_users['new_user_count'])

line = (
    Line()
    .add_xaxis(x_data)
    .add_yaxis('每月新增用户数', y_data)
    .set_series_opts(
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
            ]))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="每月新增用户数"),  # 标题
        toolbox_opts=opts.ToolboxOpts(),  # 工具箱
        datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100)  # 横轴缩放
    )
    .set_series_opts(
        # 为了不影响标记点，这里把标签关掉
        label_opts=opts.LabelOpts(is_show=False),
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(type_="average", name="平均值")
            ]))
)

line.render_notebook()
line.render('monthly_new_users.html')  # 每月新增用户数折线图



# 2.2 分别绘制工作日与非工作日各时段的用户登录次数柱状图
# 并分析用户活跃的主要时间段。
# 将日期与时间分割
Login1 = Login["login_time"].str.split(" ", expand=True).fillna("")
Login1['login_data'] = Login1[0].copy()
Login1['login_hour'] = Login1[1].copy()
Login1['user_id'] = Login['user_id']
Login2 = Login1[['user_id', 'login_data', 'login_hour']].copy()  # 使用 .copy() 显式创建副本
Login2.head()

# 获取工作日时期
start_time = datetime.datetime(2018, 9, 6)
end_time = datetime.datetime(2020, 6, 18)

# 获取工作日日期
workdays = chinese_calendar.get_workdays(start_time, end_time)

# 转换为日期列表
date_string = [d.strftime('%Y-%m-%d') for d in workdays]

# 筛选工作日所含数据
Login3 = Login2[Login2['login_data'].isin(date_string)].copy()  # 使用 .copy() 显式创建副本

# 将小时取整
Login3['login_newhour'] = Login3['login_hour'].apply(lambda x: int(x[0:2]))
Login3.head()

gongzuori = Login3.groupby(by=Login3['login_newhour'],as_index=False)['user_id'].count()
gongzuori['gongzuori'] = gongzuori['user_id']
gongzuori = gongzuori[['login_newhour','gongzuori']]
gongzuori.head()

# 准备数据
attr = list(gongzuori['login_newhour'])
v1 = list(gongzuori['gongzuori'])

# 创建柱状图对象
bar = (
    Bar()
    .add_xaxis(attr)
    .add_yaxis('工作日登录次数', v1)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="工作日各时段用户登录次数"),  # 标题
        toolbox_opts=opts.ToolboxOpts(),  # 工具箱
        datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100)  # 横轴缩放
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=True),  # 显示数据标签
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
            ]
        ),
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(type_="average", name="平均值")
            ]
        )
    )
)

# 渲染图表
bar.render_notebook()
bar.render("workday_login_analysis.html")  # 保存到本地


######非工作日分析
start_time = datetime.datetime(2018, 9, 6)
end_time = datetime.datetime(2020, 6, 18)

# 获取非工作日日期
a = chinese_calendar.get_holidays(start_time, end_time)

# 转换为日期列表
date_string = [d.strftime('%Y-%m-%d') for d in a]

# 筛选非工作日所含数据
Login4 = Login2[Login2['login_data'].isin(date_string)].copy()  # 使用 .copy() 显式创建副本

# 将小时取整
Login4.loc[:, 'login_newhour'] = Login4['login_hour'].apply(lambda x: int(x[0:2]))  # 使用 .loc 进行显式赋值
Login4.head()

holidays = Login4.groupby(by=Login4['login_newhour'], as_index=False)['user_id'].count()
holidays['holidays'] = holidays['user_id']
holidays = holidays[['login_newhour', 'holidays']]
holidays.head()

# 准备数据
attr = list(holidays['login_newhour'])
v1 = list(holidays['holidays'])

# 创建柱状图对象
bar = (
    Bar()
    .add_xaxis(attr)
    .add_yaxis('非工作日登录次数', v1)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="非工作日各时段用户登录次数"),  # 标题
        toolbox_opts=opts.ToolboxOpts(),  # 工具箱
        datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100)  # 横轴缩放
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=True),  # 显示数据标签
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
            ]
        ),
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(type_="average", name="平均值")
            ]
        )
    )
)

# 渲染图表
bar.render_notebook()
bar.render("non_workday_login_analysis.html")  # 保存到本地


#2.4计算用户流失率
Tend = pd.date_range('2020-06-18 23:59:59', periods=1)
new_users.drop_duplicates(inplace=True)
new_users['Tend'] = list(Tend) * len(new_users)  # 确保 Tend 列的长度与 new_users 一致

# 处理 recently_logged 列中的无效数据
new_users['recently_logged'] = pd.to_datetime(new_users['recently_logged'], errors='coerce')

# 计算 longtime 列
new_users['longtime'] = (pd.to_datetime(new_users['Tend']) - pd.to_datetime(new_users['recently_logged'])).dt.days

# 删除包含 NaN 值的行
new_users3 = new_users.dropna(subset=['longtime'])

# 查看数据描述
new_users3['longtime'].describe()

# 按 longtime 分组并计数
new_users4 = new_users3.groupby(by='longtime', as_index=False).count()

x_data = list(new_users4['longtime'])
y_data = list(new_users4['user_id'])

bar = (Bar()
       .add_xaxis(x_data)
       .add_yaxis('人数', y_data)
       .set_series_opts(
        # 为了不影响标记点，这里把标签关掉
        label_opts=opts.LabelOpts(is_show=False))
       .set_global_opts(
            title_opts=opts.TitleOpts(title="各类时间差值人数分析"),      # 标题
            toolbox_opts=opts.ToolboxOpts(),                             # 工具箱
            datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100) # 横轴缩放
        )
      )
bar.render_notebook()
bar.render("lostgap.html")

#流失天数及流失率
new_users5  = new_users3[new_users3['longtime'] >90]

new_users6 =  new_users5.groupby(by='longtime',as_index=False).count()

x_data = list(new_users6['longtime'])
y_data = list(new_users6['user_id'])

bar = (Bar()
       .add_xaxis(x_data)
       .add_yaxis('天数', y_data)
       .set_series_opts(
        # 为了不影响标记点，这里把标签关掉
        label_opts=opts.LabelOpts(is_show=False))
       .set_global_opts(
            title_opts=opts.TitleOpts(title="流失用户的流失天数分析"),                         # 标题
            toolbox_opts=opts.ToolboxOpts(),                                                     # 工具箱
            datazoom_opts=opts.DataZoomOpts(range_start=0,range_end=100)                         # 横轴缩放
        )
      )
bar.render_notebook()
bar.render("lostdays.html")

print('流失率：',new_users5['longtime'].count()/43717)
print('流失人数：',new_users5['longtime'].count())

#3.线上课程推荐
study_information1= study_information.groupby(by='course_id',as_index=False)['user_id'].count()
study_information1['num'] = study_information1['user_id']
study_information2 = study_information1[['course_id','num']]
study_information2.head()
#选课人数分析
# 选课人数分析
total_students = study_information2['num'].sum()
print(f'总选课人数：{total_students}')

# 定义选课人数区间
intervals = [
    (10000, float('inf'), '10000以上'),
    (5000, 10000, '5000-10000'),
    (1000, 5000, '1000-5000'),
    (500, 1000, '500-1000'),
    (100, 500, '100-500'),
    (0, 100, '100以下')
]

for lower, upper, label in intervals:
    num = study_information2[(study_information2['num'] > lower) & (study_information2['num'] <= upper)]['num'].sum()
    print(f'选课人数{label}：{num}')
    print(f'选课人数占比：{num / total_students:.4f}')

from pyecharts.charts import Pie
x_data = ["选课人数10000以上", "选课人数5000-10000", "选课人数1000-5000", "选课人数500-1000", "选课人数100-500","选课人数100以下"]
y_data = [13265, 53968, 89075, 13057, 18819,2552]

c = (
    Pie()
    .add("", [list(z) for z in zip(x_data, y_data)],radius=["30%", "70%"])   # zip函数两个部分组合在一起list(zip(x,y))-----> [(x,y)]
    .set_global_opts(
        title_opts=opts.TitleOpts(title="课程参与人数分析"), # 标题
        toolbox_opts=opts.ToolboxOpts(),                                                     # 工具箱
        legend_opts=opts.LegendOpts(orient="vertical", pos_top="10%", pos_left="80%")) #图例设置
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))  # 数据标签设置
    )
c.render_notebook()
c.render("lesson.html")

study_information2.describe()
study_information2['y'] = (study_information2['num']-1)/13624
study_information2 = study_information2.sort_values(by='y',ascending=False)
study_information3 = study_information2.iloc[0:10,:]
study_information3
x_data = list(study_information3['course_id'])
y_data_line = list(study_information3['y'])

from pyecharts.charts import Bar
from pyecharts import options as opts

b = (
    Bar()
    .add_xaxis(x_data)
    .add_yaxis("课程受欢迎程度", y_data_line)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="课程受欢迎程度分析"),  # 标题
        toolbox_opts=opts.ToolboxOpts(),                      # 工具箱
        legend_opts=opts.LegendOpts(orient="vertical", pos_top="10%", pos_left="80%")  # 图例设置
    )
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))  # 数据标签设置
)
b.render_notebook()
b.render("lesson_popular_b.html")

