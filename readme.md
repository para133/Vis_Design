# A bill analyzer

（python = 3.11.0）

### You might need

后端：Flask（Python Web 框架）  
前端：Bootstrap（页面样式）、ECharts/Chart.js（可视化图表）  
数据库：SQLite/MySQL（存储账单）  
数据处理：Pandas（数据清洗与分析）  
文件解析：针对微信/支付宝账单的 CSV/XLS 文件解析

<<<<<<< HEAD
### Structure may be like

```
VisDesign/
=======
### stucture may be like:
```
Vis_Design/
    ├── app.py
    ├── requirements.txt
>>>>>>> 2d52074e04c3753292e409e7fa6b9fcd6d5be070
    ├── static/
    │   └── js/
    ├── templates/
    │   └── index.html
    ├── uploads/
    │   └── (账单文件上传目录)
<<<<<<< HEAD
    ├── app.py
    ├── requirements.txt
    ├── data/
    │   ├── visData.db (数据库文件)
    ├── models.py  
    ├── utils.py
```


```
wechat data：
交易时间,交易类型,交易对方,商品,收/支,金额(元),支付方式,当前状态,交易单号,商户单号,备注
alipay data:
交易时间,交易分类,交易对方,对方账号,商品说明,收/支,金额,收/付款方式,交易状态,交易订单号,商家订单号,备注,
=======
    ├── models.py
    ├── utils.py
>>>>>>> 2d52074e04c3753292e409e7fa6b9fcd6d5be070
```