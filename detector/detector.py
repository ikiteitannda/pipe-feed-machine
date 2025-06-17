# -*- coding: utf-8 -*-
"""

detector：
    图像检测算法 目前适用于：22mm-双端开口-无色

修改人： hnchen
修改时间： 2025/06/17
"""
import cv2
import numpy as np
import math
from typing import List, Tuple
from util.file import load_ini
from PySide6.QtGui import QImage, QPixmap

def preprocess_image(gray: np.ndarray,
                     clahe_clip: float = 2.0,
                     clahe_grid: Tuple[int,int] = (8,8),
                     gamma: float = 0.7) -> np.ndarray:
    """
    对输入的灰度图像进行预处理，提升对比度并校正亮度。

    参数:
        gray (np.ndarray): 输入的单通道灰度图像。
        clahe_clip (float): CLAHE（对比度受限自适应直方图均衡化）中的对比度限制因子。
        clahe_grid (Tuple[int,int]): CLAHE的网格大小，用于划分子区域进行均衡化。
        gamma (float): 伽马校正的伽马值，<1时整体变亮，>1时整体变暗。

    返回:
        np.ndarray: 预处理后的灰度图像。
    """
    # 创建CLAHE对象，并对图像进行局部直方图均衡化
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid)
    img = clahe.apply(gray)
    # 伽马校正
    inv_gamma = 1.0 / gamma
    # 构建查找表，将灰度值映射到校正值
    table = np.array([((i/255.0) ** inv_gamma) * 255 for i in range(256)], dtype="uint8")
    img = cv2.LUT(img, table)
    return img


def nms_circles(circles: List[Tuple],
                overlap_thresh: float = 0.6) -> List[Tuple]:
    """
    对检测得到的圆应用非极大抑制（NMS），去除重叠过多的次优圆，保留最有代表性的圆。

    参数:
        circles (List[Tuple]): 输入的圆列表，每个元素格式为 (cnt, (cx, cy, r))，cnt为源ID占位。
        overlap_thresh (float): 圆与圆重叠的阈值，范围0~1。若两圆心距离 < overlap_thresh*(r1+r2)，视为重叠。

    返回:
        List[Tuple]: 经过NMS筛选后的圆列表。
    """
    if not circles:
        return []
    # 按半径从大到小排序，优先保留较大圆
    sorted_c = sorted(circles, key=lambda x: x[1][2], reverse=True)
    selected: List[Tuple] = []
    for cnt,(cx,cy,r) in sorted_c:
        keep = True
        for _,(sx,sy,sr) in selected:
            dist = math.hypot(cx-sx, cy-sy)
            # 若与已选圆过度重叠，则丢弃当前圆
            if dist < overlap_thresh * (r + sr):
                keep = False
                break
        if keep:
            selected.append((cnt,(cx,cy,r)))
    return selected


def detect_circles_via_hough(gray: np.ndarray,
                              ksize_grid: Tuple[int,int] = (9,9),
                              sigma_x: float = 1.0,
                              dp: float = 1.2,
                              min_dist: float = 200,
                              param1: float = 110,
                              param2: float = 45,
                              min_radius: int = 110,
                              max_radius: int = 150
                              ) -> List[Tuple[None, Tuple[int,int,int]]]:
    """
    使用Hough变换检测图像中的圆圈。

    参数:
        gray (np.ndarray): 预处理后的灰度图像。
        dp (float): 累加器分辨率与原图像分辨率的反比，越大检测速度越快但精度下降。
        minDist (float): 检测到的圆心之间的最小距离，防止检测到多个过近的圆。
        param1 (float): Canny边缘检测的高阈值（低阈值为该值一半）。
        param2 (float): Hough累计阈值，值越大越严格，只保留得分高的圆。
        minRadius (int): 可检测圆的最小半径。
        maxRadius (int): 可检测圆的最大半径。

    返回:
        List[Tuple[None, Tuple[int,int,int]]]: 检测出的圆的列表，每个元素为 (None, (cx, cy, r))。
    """
    # 先进行高斯模糊，抑制噪声
    blur = cv2.GaussianBlur(gray, ksize_grid, sigma_x)
    # 使用霍夫变换，寻找所有圆
    circles = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT, dp=dp, minDist=min_dist,
        param1=param1, param2=param2,
        minRadius=min_radius, maxRadius=max_radius)
    results = []
    if circles is not None:
        # 将检测结果四舍五入并转为整数
        for x,y,r in np.round(circles[0]).astype(int):
            if min_radius <= r <= max_radius:
                results.append((None,(x,y,r)))
    return results


def group_by_rows(circles: List[Tuple], tolerance: int=25) -> List[List[Tuple]]:
    """
    将圆按行进行分组，便于后续找到最上面一排的圆。

    参数:
        circles (List[Tuple]): 已筛选的圆列表，每项为 (cnt, (cx, cy, r))。
        tolerance (int): 行高容差，同一行的圆心y坐标差距小于该值时划入同一行。

    返回:
        List[List[Tuple]]: 按行分组后的圆列表。
    """
    if not circles:
        return []
    # 按y坐标排序
    sorted_c = sorted(circles, key=lambda x: x[1][1])
    rows: List[List[Tuple]] = []
    for cnt,(cx,cy,r) in sorted_c:
        placed=False
        for row in rows:
            # 与当前行首圆心y距离在容差范围内，视为同一行
            if abs(row[0][1][1] - cy) < tolerance:
                row.append((cnt,(cx,cy,r)))
                placed=True
                break
        if not placed:
            # 新建一行
            rows.append([(cnt,(cx,cy,r))])
    return rows


def find_top_left_circle(groups: List[List[Tuple]]) -> Tuple[int,int]:
    """
    在分组后的行列表中，选择最上面一行（groups[0]），并在该行中选取最左侧的圆心。

    参数:
        groups (List[List[Tuple]]): 按行分组后的圆列表。

    返回:
        Tuple[int,int]: 最左上圆的圆心坐标 (x, y)，若列表为空返回 (-1, -1)。
    """
    if not groups:
        return -1,-1
    top = groups[0]
    # 在首行中找到最小x值的圆
    _, (x,y,_) = min(top, key=lambda x: x[1][0])
    return x,y


def draw_detected_circles(img: np.ndarray,
                           circles: List[Tuple],
                           target: Tuple[int,int]) -> np.ndarray:
    """
    在原图上绘制检测到的圆及最左上圆心，并标注坐标文本。

    参数:
        img (np.ndarray): 原始彩色图像。
        circles (List[Tuple]): 最终筛选的圆列表，每项为 (cnt, (cx, cy, r))。
        target (Tuple[int,int]): 最左上圆的圆心坐标 (x, y)。

    返回:
        np.ndarray: 绘制完成的结果图像。
    """
    annotated = img.copy()
    # 绘制颜色
    fill_color = (139, 0, 0)   # 深蓝色填充
    radius_color = (0, 255, 0) # 绿色边框
    target_color = (0, 0, 255) # 红色标注

    # 1) 用淡蓝色填充圆管区域
    for (_, (cx, cy, r)) in circles:
        # 绘制虚拟圆轮廓
        cv2.circle(annotated, (cx, cy), r, radius_color, thickness=2)
        # thickness=-1 表示实心填充
        cv2.circle(annotated, (cx, cy), r, fill_color, thickness=-1)

    # 2) 标注最左上圆心（如果有效）
    if target != (-1, -1):
        tx, ty = target
        cv2.circle(annotated, (tx, ty), 6, target_color, -1)
        cv2.putText(annotated, f"Top-Left: ({tx},{ty})", (tx + 8, ty - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, target_color, 2)
    cv2.imwrite("output_with_circles.png", annotated)
    return annotated


def detect_image (section: str, height: float, width: float, gray: np.ndarray, bgr: np.ndarray) -> (np.ndarray, float, float, int):
    """
    图像检测算法

    参数:
        section: 配置节名称。
        height: 原始图像高度。
        width: 原始图像宽度。
        gray (np.ndarray): 原始灰度图像。
        bgr (np.ndarray): 原始彩色图像。

    返回:
        pix (np.ndarray): 绘制后的图像。
        tx, ty (Tuple[int,int]): 最左上圆的圆心坐标 (x, y)。
        len(circles): 圆管总数
    """
    # 使用程序目录下的 INI
    cfg = load_ini()
    sec = cfg[section]

    # 读取配置
    clahe_clip = sec.getfloat('clahe_clip')
    kx, ky = map(int, sec.get('clahe_grid').split(','))
    gamma = sec.getfloat('gamma')
    ksize_x, ksize_y = map(int, sec.get('ksize_grid').split(','))
    sigma_x = sec.getfloat('sigma_x')
    dp = sec.getfloat('dp')
    min_dist = sec.getfloat('min_dist')
    param1 = sec.getfloat('param1')
    param2 = sec.getfloat('param2')
    min_radius = sec.getint('min_radius')
    max_radius = sec.getint('max_radius')
    overlap_thresh = sec.getfloat('overlap_thresh')
    tolerance = sec.getint('tolerance')

    # 第一步：图像预处理 → 提升对比度 + 亮度校正
    gray_p = preprocess_image(gray, clahe_clip, (kx, ky), gamma)

    # 第二步：Hough圆检测
    h_circles = detect_circles_via_hough(gray_p, (ksize_x, ksize_y), sigma_x, dp, min_dist, param1, param2, min_radius, max_radius)

    # 第三步：非极大抑制过滤重叠
    circles = nms_circles(h_circles, overlap_thresh)

    # 第四步：按行分组并找到最左上圆心
    groups = group_by_rows(circles, tolerance)
    tx, ty = find_top_left_circle(groups)

    # 绘制检测结果
    annotated = draw_detected_circles(bgr.copy(), circles, (tx, ty))
    rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
    qimg = QImage(rgb.data, width, height, 3 * width, QImage.Format_RGB888)
    pix = QPixmap.fromImage(qimg)
    return pix, tx, ty, len(circles)