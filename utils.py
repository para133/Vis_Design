import plotly.graph_objects as go

labels = ["老妈", "庄玉坤", "银行充值", "中奖", "零钱", "银行卡", "商户消费", "群收款", "红包", "提现"]
sources = [0, 1, 2, 3, 4, 4, 4, 4, 4]  # 收入到零钱
targets = [4, 4, 4, 4, 5, 6, 7, 8, 9]  # 零钱到各支出
values  = [2600, 50, 50, 0.1, 1450, 100, 50, 30, 2700]  # 示例数据

fig = go.Figure(go.Sankey(
    node=dict(label=labels),
    link=dict(source=sources, target=targets, value=values)
))
fig.show()