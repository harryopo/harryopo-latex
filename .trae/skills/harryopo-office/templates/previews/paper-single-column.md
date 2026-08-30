<!-- 使用 harryopo-preview.css 预览本文档：
     - typora：菜单 → 主题 → 打开主题文件夹 → 放入 css 并重启
     - VS Code：Ctrl+Shift+P → "Markdown: Open Preview" → 安装 "Markdown Preview Enhanced" 扩展后在 front-matter 指定 css
     - GitHub：本地浏览器打开 + 引入此 css，或使用 md-to-html 工具
-->

# 基于注意力机制的轻量化图像分类方法研究

> 作者：张三 计算机学院 2025000101
> 单位：示例大学
> 日期：2026年8月29日

**摘要：** 图像分类是计算机视觉领域的基础任务之一。本文提出了一种基于注意力机制的轻量化图像分类方法，在保持较高准确率的同时显著降低了模型复杂度。实验结果表明，所提方法在 ImageNet 数据集上的 Top-1 准确率达到 78.3%，参数量仅为 3.2M，FLOPs 为 0.8G，优于现有的 MobileNetV3 和 ShuffleNetV2 等轻量化模型。

**关键词：** 图像分类；注意力机制；轻量化网络；深度学习

---

## 一、引言

图像分类是计算机视觉中最基本的任务之一，其目标是将输入图像分配到预定义的类别中。传统方法依赖手工设计的特征提取器，泛化能力有限。深度学习技术的兴起——特别是卷积神经网络（CNN）——彻底改变了这一局面。

自 AlexNet 在 2012 年 ImageNet 挑战赛中取得突破以来，研究者们提出了大量 CNN 架构。ResNet 通过残差连接解决了深层网络训练困难的问题，EfficientNet 则通过复合缩放策略实现了效率与精度的平衡。

### 1.1 研究背景

随着移动设备和边缘计算的普及，模型轻量化成为研究热点。轻量化模型需要在保持较高准确率的同时，显著减少参数量和计算量。

### 1.2 主要贡献

本文的主要贡献包括：

1. 提出了一种新的通道注意力机制，**计算开销降低 40%**
2. 设计了自适应空间池化模块，增强多尺度特征提取能力
3. 在 ImageNet、CIFAR-100 上均取得 SOTA 性能

## 二、相关工作

### 2.1 轻量化网络

MobileNetV3 通过深度可分离卷积和 SE 注意力机制实现高效推理；ShuffleNetV2 则通过通道混洗优化并行计算。

| 模型 | Top-1 (%) | Params (M) | FLOPs (G) |
|------|-----------|-----------|-----------|
| MobileNetV3-Small | 67.5 | 2.5 | 0.06 |
| ShuffleNetV2-1.0× | 69.4 | 2.3 | 0.15 |
| EfficientNet-B0 | 77.3 | 5.3 | 0.39 |
| **本文方法** | **78.3** | **3.2** | **0.8** |

### 2.2 注意力机制

SE 注意力通过全局平均池化建模通道关系，CBAM 进一步引入空间注意力。两者均能以较小开销提升模型性能。

## 三、方法

### 3.1 整体架构

本文方法的整体架构如下图所示：

```
输入图像 → 初始卷积 → 阶段1（注意力模块 × 3）→ 阶段2（注意力模块 × 4）
       → 阶段3（注意力模块 × 6）→ 阶段4（注意力模块 × 3）→ 全局池化 → 分类器
```

### 3.2 轻量化注意力模块

轻量化注意力模块（LAM）由两个分支组成：通道注意力分支和空间注意力分支。

> **公式 1** 通道注意力计算公式：
> $$M_c(F) = \sigma(\text{MLP}(\text{AvgPool}(F)) + \text{MLP}(\text{MaxPool}(F)))$$

其中 $\sigma$ 表示 Sigmoid 激活函数，$\text{MLP}$ 为多层感知机。

```python
class LightweightAttention(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.mlp = nn.Sequential(
            nn.Linear(channels, channels // reduction),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        avg_out = self.mlp(self.avg_pool(x).view(b, c))
        max_out = self.mlp(self.max_pool(x).view(b, c))
        scale = (avg_out + max_out).view(b, c, 1, 1)
        return x * scale.expand_as(x)
```

### 3.3 损失函数

本文使用标签平滑交叉熵损失：

> **公式 2** 标签平滑交叉熵损失：
> $$L = -\sum_{i=1}^{C} y_i^{\text{smooth}} \log(p_i), \quad y_i^{\text{smooth}} = (1-\epsilon) y_i + \frac{\epsilon}{C}$$

其中 $\epsilon = 0.1$ 为平滑系数，$C$ 为类别数。

## 四、实验与分析

### 4.1 实验设置

- 数据集：ImageNet-1K（1000 类，128 万张训练图像）
- 优化器：SGD（momentum=0.9, weight_decay=4e-5）
- 初始学习率：0.1，cosine 衰减，训练 300 epoch
- 批量大小：256（4×RTX 3090）

### 4.2 消融实验

| 模块 | Top-1 (%) | Params (M) | FLOPs (G) |
|------|-----------|-----------|-----------|
| 基线 | 72.4 | 2.8 | 0.5 |
| + 通道注意力 | 76.1 | 3.0 | 0.7 |
| + 空间注意力 | 77.5 | 3.1 | 0.75 |
| + 标签平滑 | 78.3 | 3.2 | 0.8 |

> **结论**：三个模块均带来稳定提升，组合使用时效果最佳。

### 4.3 可视化分析

通过 Grad-CAM 可视化发现，注意力模块能有效聚焦于图像的判别性区域，抑制背景噪声的干扰。

## 五、结论

本文提出了一种基于注意力机制的轻量化图像分类方法，通过通道-空间双分支注意力设计，在仅增加 14% 参数量的前提下将 Top-1 准确率从 72.4% 提升至 78.3%。实验结果表明所提方法在精度和效率间取得了良好平衡，适合在边缘设备上部署。

未来的研究方向包括：

1. 探索神经架构搜索（NAS）自动设计注意力模块
2. 研究量化感知训练，进一步压缩模型体积
3. 拓展到目标检测、语义分割等下游任务

## 参考文献

[1] Krizhevsky A, Sutskever I, Hinton G E. ImageNet classification with deep convolutional neural networks[C]. NeurIPS, 2012: 1097-1105.

[2] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]. CVPR, 2016: 770-778.

[3] Tan M, Le Q. EfficientNet: Rethinking model scaling for convolutional neural networks[C]. ICML, 2019: 6105-6114.

[4] Howard A, Sandler M, Chu G, et al. Searching for MobileNetV3[C]. ICCV, 2019: 1314-1324.

[5] Ma N, Zhang X, Zheng H T, et al. ShuffleNetV2: Practical guidelines for efficient CNN architecture design[C]. ECCV, 2018: 116-131.
