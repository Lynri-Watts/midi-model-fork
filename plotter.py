import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

#读取CSV文件 lightning_logs/version_5/metrics.csv 并以loss为纵坐标画图
df = pd.read_csv('lightning_logs/version_5/metrics.csv')
# 设置绘图样式
plt.style.use('seaborn-v0_8-darkgrid')

# 提取loss列的数据
loss_data = df['val/acc'].dropna() 
print(loss_data)

# 创建一个新的图形
plt.figure(figsize=(10, 6))

# 绘制loss数据
plt.plot(loss_data, label='Loss')

# 设置图表标题和坐标轴标签
plt.title('Loss over time')
plt.xlabel('Step')
plt.ylabel('Loss')

# 添加图例
plt.legend()

# 显示图表
plt.show()
