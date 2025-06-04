# A bill analyzer

（python = 3.11.0）
### you might need:
后端：Flask（Python Web 框架）
前端：Bootstrap（页面样式）、ECharts/Chart.js（可视化图表）
数据库：SQLite/MySQL（存储账单）
数据处理：Pandas（数据清洗与分析）
文件解析：针对微信/支付宝账单的 CSV/XLS 文件解析

### stucture may be like:
```
Vis_Design/
    ├── app.py
    ├── requirements.txt
    ├── static/
    │   └── js/
    ├── templates/
    │   └── index.html
    ├── uploads/
    │   └── (账单文件上传目录)
    ├── models.py
    ├── utils.py
```