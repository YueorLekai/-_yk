import numpy as np


# 直接灰度线性变换
def linear_trans(image, a, b, c, d, flag):
    """
    :param image: 灰度图矩阵
    :param a: 选择原灰度图变换最小值
    :param b: 选择原灰度图变换最大值
    :param c: 变换后目标最小值
    :param d: 变换后目标最大值
    :param flag: 非目标区间值处理依据
    :return:图像线性灰度变换结果
    """
    A = np.array(image, dtype=float)
    A_1 = ((d - c) / (b - a)) * (A - a) + c
    Max = A.max()
    Min = A.min()
    mask1 = (A <= a)
    mask2 = (A >= b)
    if b < Max or a > Min:
        if flag:  # flag默认1非目标区间为定值
            A_1[mask1] = c
            A_1[mask2] = d
        else:  # 否则为原值
            A_1[mask1] = A[mask1]
            A_1[mask2] = A[mask2]
    return A_1


# 分段线性变换
def P_linear_trans(image, a, b, c, d):
    """
    :param image: 灰度图矩阵
    :param a: 选择原灰度图变换最小值
    :param b: 选择原灰度图变换最大值
    :param c: 变换后目标最小值
    :param d: 变换后目标最大值
    :return:图像线性灰度变换结果
    """
    A = np.array(image, dtype=float)
    A_1 = np.zeros_like(A, dtype=float)
    mask1 = (A >= 0) & (A < a)
    A_1[mask1] = (c / a) * A[mask1]
    mask2 = (A >= a) & (A < b)
    A_1[mask2] = ((d - c) / (b - a)) * (A[mask2] - a) + c
    mask3 = (A >= b) & (A < 256)
    A_1[mask3] = ((256 - d) / (256 - b)) * (A[mask3] - b) + d
    return A_1


# 非线性变换，阈值变换
def threshold_trans(image, T, min_val, max_val):
    """
    :param image:目标图像
    :param T: 阈值
    :param min_val:大于阈值等于的常数
    :param max_val: 小于阈值等于的常数
    :return: 变换后的图像矩阵
    """
    A = np.array(image, dtype=float)
    A_1 = np.zeros_like(A, dtype=float)
    # 创建布尔掩码
    mask = (A >= T)
    # 应用阈值变换
    A_1[mask] = max_val
    A_1[~mask] = min_val
    # 返回结果
    return A_1


# 灰度反转
def invert_gray(image):
    """
    :param image: 目标图像
    :return: 反转后图像
    """
    A = np.array(image, dtype=float)
    A_1 = 255 - A
    return A_1


# 对数变换，拓展图像暗部细节
def log_trans(image, c=None):
    """
    :param image: 目标图像
    :param c:调节对比度，范围0-105.9
    :return:变换后图像矩阵
    """
    A = np.array(image, dtype=float)
    # 如果没有提供 c 值，则自动计算
    if c is None:
        max_value = A.max()
        c = 255 / np.log(1 + max_value)
    # 应用对数变换
    A_1 = c * np.log(1 + A)
    # 将结果转换为 8 位无符号整数
    A_1 = np.clip(A_1, 0, 255).astype(np.uint8)
    return A_1


# 幂次变换，γ<1增强暗部，γ>1增强亮部
def power_trans(image, gamma, c=None):
    """
    :param image: 目标灰度图
    :param gamma: 幂次值（注意滑动条要非线性）
    :param c: 常数
    :return: 变换后图像矩阵
    """
    A = np.array(image, dtype=float)
    # 计算默认的 c 值
    default_c = 255 / (255 ** gamma)
    # 如果提供了 c 值，检查其合理性
    if c is not None:
        if c <= 0:
            raise ValueError("c必须比0大")
    else:
        c = default_c
    # 应用幂次变换
    A_1 = c * (A ** gamma)
    # 将结果裁剪到 0 到 255 的范围内，并转换为 8 位无符号整数
    A_1 = np.clip(A_1, 0, 255).astype(np.uint8)
    return A_1


# 直方图均衡化
def Histogram_Equalization(image):
    """
    :param image:目标图像矩阵
    :return: 均衡化之后的图像
    """
    # 将图像转换为 NumPy 数组
    A = np.array(image, dtype=np.uint8)
    # 计算直方图
    hist, bins = np.histogram(A.flatten(), bins=256, range=[0, 256], density=True)
    # 计算累积分布函数
    cdf = hist.cumsum()
    # 归一化累积分布函数
    cdf = (cdf * (A.max() - A.min()) + 0.5).astype(np.uint8)
    # 使用累积分布函数对图像进行均衡化
    equalized_image = cdf[A]
    return equalized_image
