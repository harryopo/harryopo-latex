# 图像识别研究报告

# **一、引言**

本文研究**深度学习**在图像识别中的应用。

## **1.1 方法**

实验配置如下表：

<table><tr><td><p>模型</p></td><td><p>准确率</p></td><td><p>速度</p></td></tr><tr><td><p>ResNet-50</p></td><td><p>94.2%</p></td><td><p>1.2s</p></td></tr><tr><td><p>EfficientNet</p></td><td><p>95.1%</p></td><td><p>0.8s</p></td></tr></table>

消融实验：

<table><tr><td colspan="2"><p>配置</p></td><td><p>结果</p></td></tr><tr><td><p>baseline</p></td><td><p>90.5%</p></td><td><p>无增强</p></td></tr><tr><td><p>full</p></td><td><p>96.8%</p></td><td><p>完整方案</p></td></tr></table>

多数据集：

<table><tr><td><p>模型</p></td><td><p>准确率</p></td></tr><tr><td rowspan="2"><p>Ours</p></td><td><p>98.5%</p></td></tr><tr><td><p>85.3%</p></td></tr><tr><td rowspan="2"><p>Base</p></td><td><p>95.2%</p></td></tr><tr><td><p>78.9%</p></td></tr></table>

# **二、结论**

实验证明所提方法有效。