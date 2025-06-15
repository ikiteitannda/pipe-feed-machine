import cv2
import numpy as np
import math
from typing import List, Tuple


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
                              dp: float = 1.2,
                              mindist: float = 120,
                              param1: float = 35,
                              param2: float = 35,
                              minradius: int = 45,
                              maxradius: int = 60
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
    blur = cv2.GaussianBlur(gray, (5,5), 1)
    # 调用HoughCircles方法
    circles = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT, dp=dp, minDist=mindist,
        param1=param1, param2=param2,
        minRadius=minradius, maxRadius=maxradius)
    results = []
    if circles is not None:
        # 将检测结果四舍五入并转为整数
        for x,y,r in np.round(circles[0]).astype(int):
            if minradius <= r <= maxradius:
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
    out = img.copy()
    # 绘制所有圆边界及中心点
    for cnt,(cx,cy,r) in circles:
        cv2.circle(out, (cx,cy), r, (0,255,0), 2)     # 绿色圆边
        cv2.circle(out, (cx,cy), 3, (0,255,255), -1)    # 黄色圆心点
    # 绘制最左上圆心
    tx,ty = target
    if (tx,ty)!=(-1,-1):
        cv2.circle(out,(tx,ty),6,(0,0,255),-1)        # 红色标记点
        cv2.putText(out,f"Top-Left: ({tx},{ty})",(tx+8,ty-8),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)  # 标注文本
    return out

if __name__ == "__main__":
    # 读取图像并转换为灰度
    img = cv2.imread("test_image7.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 第一步：图像预处理 → 提升对比度 + 亮度校正
    gray_p = preprocess_image(gray)

    # 第二步：Hough圆检测
    h_circles = detect_circles_via_hough(gray_p)
    # 第三步：非极大抑制过滤重叠
    circles = nms_circles(h_circles)

    # 第四步：按行分组并找到最左上圆心
    groups = group_by_rows(circles)
    tl = find_top_left_circle(groups)

    # 第五步：绘制结果并展示/保存
    out = draw_detected_circles(img, circles, tl)
    cv2.imwrite("output_with_circles.png", out)
    cv2.imshow("Result", out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
