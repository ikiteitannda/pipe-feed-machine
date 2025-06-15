import cv2
import numpy as np
from typing import List, Tuple


def detect_circles_via_fitellipse(gray: np.ndarray,
                                  thresh_val: int = 160,
                                  blur_ksize: Tuple[int, int] = (13, 13),
                                  area_min: float = 13000,
                                  ellipse_area_min: float = 20000,
                                  axis_ratio_range: Tuple[float, float] = (0.5, 1.5)
                                  ) -> List[Tuple[np.ndarray, Tuple[int, int, int]]]:
    """
    使用二值化 + 大尺寸模糊 + 轮廓 + fitEllipse 筛选来检测近似圆形目标，
    返回列表中每个元素包含原轮廓(cnt)和对应圆心半径(center_x, center_y, radius)。

    参数:
      - thresh_val:        二值化阈值
      - blur_ksize:        均值模糊核大小 (如 (13,13)), 用于平滑圆内部噪点
      - area_min:          轮廓最小面积下限 (过滤碎片)
      - ellipse_area_min:  拟合椭圆面积下限 (过滤过小/过扁区域)
      - axis_ratio_range:  长宽比阈值 (仅保留 ratio ∈ [min, max] 的椭圆)

    返回值列表中每个元素为 (cnt, (x, y, radius))：
      - cnt:     原轮廓，用于后续精确绘制轮廓
      - x, y, r: 拟合圆心及半径 (近似 (w+h)/4)

    参数微调思路
        thresh_val（固定阈值）：

        图中圆管内部灰度略高，可从 140～200 范围尝试。

        如果某一行最左几个漏检，可能是该处亮度偏低或阈值偏高，可适当下调到 150～160。

        blur_ksize（均值滤波核）：

        13×13 与原 C++ 大核滤波类似，可先保持，若中间某些圆因噪点过多漏检，可改成 (9,9) 试试；

        如果圆边缘变模糊，可适当减小到 (7,7)。

        area_min、ellipse_area_min：

        目前设置了轮廓面积 >13000、拟合椭圆面积 >20000。

        若最小几行漏检，可考虑将 area_min 降到 8000；或将 ellipse_area_min 降到 15000，以捕捉更小/部分截断的圆。

        axis_ratio_range：

        默认 (0.5,1.5) 允许轻微不对称；若漏检偏扁的圆，可适当放宽到 (0.4, 2.0)。

        若误检非圆形干扰，可收紧到 (0.7,1.3)。

        内部白色占比检查：

        目前要求 ≥50%，若管底部或顶端被遮挡导致内部暗，可临时下调到 40%。
    """
    # ——— 1. 灰度处理 —————
    if len(gray.shape) == 3:
        gray_img = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = gray.copy()

    h, w_img = gray_img.shape[:2]
    # ——— 2. 限制检测区域：忽略底部黑色噪声区域
    cutoff_row = int(h * 0.85)

    # ——— 3. 全局二值化 —————
    _, binary = cv2.threshold(gray_img, thresh_val, 255, cv2.THRESH_BINARY)
    binary[cutoff_row:, :] = 0

    # ——— 4. 大尺度均值模糊 —————
    blurred = cv2.blur(binary, blur_ksize)
    blurred[cutoff_row:, :] = 0

    # ——— 5. 提取轮廓 —————
    contours_info = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours_info) == 3:
        _, contours, _ = contours_info
    else:
        contours, _ = contours_info

    results: List[Tuple[np.ndarray, Tuple[int, int, int]]] = []
    for cnt in contours:
        # 5.1 过滤轮廓面积：剔除过小的碎片
        area = cv2.contourArea(cnt)
        if area < area_min:
            continue

        # 5.2 拟合椭圆需至少 5 个点
        if len(cnt) < 5:
            continue

        # 5.3 椭圆拟合
        ellipse = cv2.fitEllipse(cnt)
        (cx_f, cy_f), (maj_axis, min_axis), angle = ellipse
        ellipse_area = maj_axis * min_axis

        # 5.4 过滤拟合面积过小
        if ellipse_area < ellipse_area_min:
            continue

        # 5.5 长宽比过滤：排除极度扁的形状
        ratio = maj_axis / min_axis if min_axis != 0 else 0
        if not (axis_ratio_range[0] < ratio < axis_ratio_range[1]):
            continue

        # 5.6 计算近似半径: (maj + min)/4
        radius = int(round((maj_axis + min_axis) / 4))
        cx = int(round(cx_f))
        cy = int(round(cy_f))

        # 5.7 圆内部白色像素占比检查，剔除被截断的管口
        mask = np.zeros_like(gray_img, dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 255, -1)
        mask_vals = cv2.bitwise_and(binary, binary, mask=mask)
        nonzero = cv2.countNonZero(mask_vals)
        circle_area = np.pi * (radius ** 2)
        if nonzero < circle_area * 0.5:
            continue

        # 5.8 通过所有过滤，保留原轮廓和圆形参数
        results.append((cnt, (cx, cy, radius)))

    return results


def group_by_rows(circles: List[Tuple[np.ndarray, Tuple[int, int, int]]], tolerance: int = 25) -> List[List[Tuple[np.ndarray, Tuple[int, int, int]]]]:
    """
    按照圆心 y 坐标将圆分组到不同的行中。
    circles 中元素为 (cnt, (x,y,radius))，这里只基于 y 分组。
    """
    if not circles:
        return []
    circles_sorted = sorted(circles, key=lambda item: item[1][1])
    groups: List[List[Tuple[np.ndarray, Tuple[int, int, int]]]] = []
    for (cnt, (cx, cy, r)) in circles_sorted:
        placed = False
        for grp in groups:
            if abs(grp[0][1][1] - cy) < tolerance:
                grp.append((cnt, (cx, cy, r)))
                placed = True
                break
        if not placed:
            groups.append([(cnt, (cx, cy, r))])
    return groups


def find_top_left_circle(groups: List[List[Tuple[np.ndarray, Tuple[int, int, int]]]]) -> Tuple[int, int]:
    """
    在分组后的行列表中，找最上面一行（groups[0]）中最左侧的圆心。
    返回 (x, y)。若 groups 为空则 (-1, -1)
    """
    if not groups:
        return -1, -1
    top_row = groups[0]
    top_row_sorted = sorted(top_row, key=lambda item: item[1][0])
    x, y, _ = top_row_sorted[0][1]
    return x, y


def draw_detected_circles(img: np.ndarray,
                           circles: List[Tuple[np.ndarray, Tuple[int, int, int]]],
                           target: Tuple[int, int]) -> np.ndarray:
    """
    使用虚拟圆 (cv2.circle) 绘制每个检测到的圆管轮廓。
    circles: 列表元素为 (cnt, (x, y, r))
    target: 最左上圆心 (x, y)
    返回：带注释图像
    """
    annotated = img.copy()

    # 绘制每个拟合圆 (绿色圆环) 及圆心 (黄色)
    for (cnt, (cx, cy, r)) in circles:
        # 绘制虚拟圆轮廓
        cv2.circle(annotated, (cx, cy), r, (0, 255, 0), 2)
        # 绘制圆心
        cv2.circle(annotated, (cx, cy), 3, (0, 255, 255), -1)

    # 标注最左上圆心 (红色)
    if target != (-1, -1):
        tx, ty = target
        cv2.circle(annotated, (tx, ty), 6, (0, 0, 255), -1)
        cv2.putText(annotated, f"Top-Left: ({tx},{ty})",
                    (tx + 8, ty - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imwrite("output_with_circles.png", annotated)
    return annotated

def detect_image (section: str, gray: np.ndarray, bgr: np.ndarray):



if __name__ == "__main__":
    # 读取输入图像，路径确保正确
    img = cv2.imread("test_image5.bmp")  # 替换为实际文件名
    if img is None:
        raise FileNotFoundError("无法打开输入图像，请检查路径是否正确。")

    # 转灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. 调用检测函数 （开口）
    detected = detect_circles_via_fitellipse(
        gray,
        thresh_val=130,
        blur_ksize=(5, 5),
        area_min=13000,
        ellipse_area_min=15000,
        axis_ratio_range=(0.8, 1.5)
    )

    # 2. 按行分组
    groups = group_by_rows(detected, tolerance=25)

    # 3. 找最上左圆心
    top_left = find_top_left_circle(groups)

    # 4. 绘制虚拟圆形轮廓并标注
    annotated = draw_detected_circles(img.copy(), detected, top_left)
    cv2.imshow("Detected Circles", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    # 读取检测参数
    cfg = configparser.ConfigParser()
    cfg.read('settings.ini', encoding='utf-8')
    sec = cfg[self.section]
    thresh = sec.getint('thresh_val')
    kx, ky = map(int, sec.get('blur_ksize').split(','))
    amin = sec.getfloat('area_min')
    eamin = sec.getfloat('ellipse_area_min')
    ar_min, ar_max = map(float, sec.get('axis_ratio_range').split(','))
    tol = sec.getint('tolerance')

    # 执行检测算法
    self.logMessage.emit(f"[{self.section}] 开始检测算法...")
    circles = detect_circles_via_fitellipse(
        gray, thresh, (kx, ky), amin, eamin, (ar_min, ar_max)
    )
    groups = group_by_rows(circles, tolerance=tol)
    tx, ty = find_top_left_circle(groups)

    # 绘制检测结果
    annotated = draw_detected_circles(bgr.copy(), circles, (tx, ty))
    rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
    qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
    pix = QPixmap.fromImage(qimg)



#
# import cv2
# import numpy as np
# import math
# from typing import List, Tuple
#
#
# def preprocess_image(gray: np.ndarray,
#                      clahe_clip: float = 2.0,
#                      clahe_grid: Tuple[int,int] = (8,8),
#                      gamma: float = 0.7) -> np.ndarray:
#     """
#     对输入的灰度图像进行预处理，提升对比度并校正亮度。
#
#     参数:
#         gray (np.ndarray): 输入的单通道灰度图像。
#         clahe_clip (float): CLAHE（对比度受限自适应直方图均衡化）中的对比度限制因子。
#         clahe_grid (Tuple[int,int]): CLAHE的网格大小，用于划分子区域进行均衡化。
#         gamma (float): 伽马校正的伽马值，<1时整体变亮，>1时整体变暗。
#
#     返回:
#         np.ndarray: 预处理后的灰度图像。
#     """
#     # 创建CLAHE对象，并对图像进行局部直方图均衡化
#     clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid)
#     img = clahe.apply(gray)
#     # 伽马校正
#     inv_gamma = 1.0 / gamma
#     # 构建查找表，将灰度值映射到校正值
#     table = np.array([((i/255.0) ** inv_gamma) * 255 for i in range(256)], dtype="uint8")
#     img = cv2.LUT(img, table)
#     return img
#
#
# def nms_circles(circles: List[Tuple],
#                 overlap_thresh: float = 0.6) -> List[Tuple]:
#     """
#     对检测得到的圆应用非极大抑制（NMS），去除重叠过多的次优圆，保留最有代表性的圆。
#
#     参数:
#         circles (List[Tuple]): 输入的圆列表，每个元素格式为 (cnt, (cx, cy, r))，cnt为源ID占位。
#         overlap_thresh (float): 圆与圆重叠的阈值，范围0~1。若两圆心距离 < overlap_thresh*(r1+r2)，视为重叠。
#
#     返回:
#         List[Tuple]: 经过NMS筛选后的圆列表。
#     """
#     if not circles:
#         return []
#     # 按半径从大到小排序，优先保留较大圆
#     sorted_c = sorted(circles, key=lambda x: x[1][2], reverse=True)
#     selected: List[Tuple] = []
#     for cnt,(cx,cy,r) in sorted_c:
#         keep = True
#         for _,(sx,sy,sr) in selected:
#             dist = math.hypot(cx-sx, cy-sy)
#             # 若与已选圆过度重叠，则丢弃当前圆
#             if dist < overlap_thresh * (r + sr):
#                 keep = False
#                 break
#         if keep:
#             selected.append((cnt,(cx,cy,r)))
#     return selected
#
#
# def detect_circles_via_hough(gray: np.ndarray,
#                               dp: float = 1.3,
#                               minDist: float = 80,
#                               param1: float = 110,
#                               param2: float = 45,
#                               minRadius: int = 95,
#                               maxRadius: int = 130
#                               ) -> List[Tuple[None, Tuple[int,int,int]]]:
#     """
#     使用Hough变换检测图像中的圆圈。
#
#     参数:
#         gray (np.ndarray): 预处理后的灰度图像。
#         dp (float): 累加器分辨率与原图像分辨率的反比，越大检测速度越快但精度下降。
#         minDist (float): 检测到的圆心之间的最小距离，防止检测到多个过近的圆。
#         param1 (float): Canny边缘检测的高阈值（低阈值为该值一半）。
#         param2 (float): Hough累计阈值，值越大越严格，只保留得分高的圆。
#         minRadius (int): 可检测圆的最小半径。
#         maxRadius (int): 可检测圆的最大半径。
#
#     返回:
#         List[Tuple[None, Tuple[int,int,int]]]: 检测出的圆的列表，每个元素为 (None, (cx, cy, r))。
#     """
#     # 先进行高斯模糊，抑制噪声
#     blur = cv2.GaussianBlur(gray, (9,9), 1)
#     # 调用HoughCircles方法
#     circles = cv2.HoughCircles(
#         blur, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
#         param1=param1, param2=param2,
#         minRadius=minRadius, maxRadius=maxRadius)
#     results = []
#     if circles is not None:
#         # 将检测结果四舍五入并转为整数
#         for x,y,r in np.round(circles[0]).astype(int):
#             if minRadius <= r <= maxRadius:
#                 results.append((None,(x,y,r)))
#     return results
#
#
# def group_by_rows(circles: List[Tuple], tolerance: int=25) -> List[List[Tuple]]:
#     """
#     将圆按行进行分组，便于后续找到最上面一排的圆。
#
#     参数:
#         circles (List[Tuple]): 已筛选的圆列表，每项为 (cnt, (cx, cy, r))。
#         tolerance (int): 行高容差，同一行的圆心y坐标差距小于该值时划入同一行。
#
#     返回:
#         List[List[Tuple]]: 按行分组后的圆列表。
#     """
#     if not circles:
#         return []
#     # 按y坐标排序
#     sorted_c = sorted(circles, key=lambda x: x[1][1])
#     rows: List[List[Tuple]] = []
#     for cnt,(cx,cy,r) in sorted_c:
#         placed=False
#         for row in rows:
#             # 与当前行首圆心y距离在容差范围内，视为同一行
#             if abs(row[0][1][1] - cy) < tolerance:
#                 row.append((cnt,(cx,cy,r)))
#                 placed=True
#                 break
#         if not placed:
#             # 新建一行
#             rows.append([(cnt,(cx,cy,r))])
#     return rows
#
#
# def find_top_left_circle(groups: List[List[Tuple]]) -> Tuple[int,int]:
#     """
#     在分组后的行列表中，选择最上面一行（groups[0]），并在该行中选取最左侧的圆心。
#
#     参数:
#         groups (List[List[Tuple]]): 按行分组后的圆列表。
#
#     返回:
#         Tuple[int,int]: 最左上圆的圆心坐标 (x, y)，若列表为空返回 (-1, -1)。
#     """
#     if not groups:
#         return -1,-1
#     top = groups[0]
#     # 在首行中找到最小x值的圆
#     _, (x,y,_) = min(top, key=lambda x: x[1][0])
#     return x,y
#
#
# def draw_detected_circles(img: np.ndarray,
#                            circles: List[Tuple],
#                            target: Tuple[int,int]) -> np.ndarray:
#     """
#     在原图上绘制检测到的圆及最左上圆心，并标注坐标文本。
#
#     参数:
#         img (np.ndarray): 原始彩色图像。
#         circles (List[Tuple]): 最终筛选的圆列表，每项为 (cnt, (cx, cy, r))。
#         target (Tuple[int,int]): 最左上圆的圆心坐标 (x, y)。
#
#     返回:
#         np.ndarray: 绘制完成的结果图像。
#     """
#     out = img.copy()
#     # 绘制所有圆边界及中心点
#     for cnt,(cx,cy,r) in circles:
#         cv2.circle(out, (cx,cy), r, (0,255,0), 2)     # 绿色圆边
#         cv2.circle(out, (cx,cy), 3, (0,255,255), -1)    # 黄色圆心点
#     # 绘制最左上圆心
#     tx,ty = target
#     if (tx,ty)!=(-1,-1):
#         cv2.circle(out,(tx,ty),6,(0,0,255),-1)        # 红色标记点
#         cv2.putText(out,f"Top-Left: ({tx},{ty})",(tx+8,ty-8),
#                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)  # 标注文本
#     return out
#
# if __name__ == "__main__":
#     # 读取图像并转换为灰度
#     img = cv2.imread("test_image5.bmp")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     # 第一步：图像预处理 → 提升对比度 + 亮度校正
#     gray_p = preprocess_image(gray)
#     # 第二步：Hough圆检测
#     h_circles = detect_circles_via_hough(gray_p)
#     # 第三步：非极大抑制过滤重叠
#     circles = nms_circles(h_circles)
#
#     # 第四步：按行分组并找到最左上圆心
#     groups = group_by_rows(circles)
#     tl = find_top_left_circle(groups)
#
#     # 第五步：绘制结果并展示/保存
#     out = draw_detected_circles(img, circles, tl)
#     cv2.imwrite("output_with_circles.png", out)
#     cv2.imshow("Result", out)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
