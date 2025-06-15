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


if __name__ == "__main__":
    # # 读取输入图像，路径确保正确
    # img = cv2.imread("test_image6.bmp")  # 替换为实际文件名
    # if img is None:
    #     raise FileNotFoundError("无法打开输入图像，请检查路径是否正确。")
    #
    # # 转灰度
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #
    # # 1. 分别使用阈值 130 和 140 进行检测
    # det_130 = detect_circles_via_fitellipse(
    #     gray,
    #     thresh_val=130,
    #     blur_ksize=(5, 5),
    #     area_min=13000,
    #     ellipse_area_min=17000,
    #     axis_ratio_range=(0.8, 1.5)
    # )
    # det_140 = detect_circles_via_fitellipse(
    #     gray,
    #     thresh_val=140,
    #     blur_ksize=(5, 5),
    #     area_min=13000,
    #     ellipse_area_min=17000,
    #     axis_ratio_range=(0.8, 1.5)
    # )
    #
    # # 合并两次检测结果，去重（中心距离 < 200px 视为同一圆）
    # detected = det_130.copy()
    # for cnt, (cx, cy, r) in det_140:
    #     if not any(abs(cx - x0) < 200 and abs(cy - y0) < 200 for (_, (x0, y0, _)) in detected):
    #         detected.append((cnt, (cx, cy, r)))

    # 读取输入图像，路径确保正确
    img = cv2.imread("test_image8.bmp")  # 替换为实际文件名
    if img is None:
        raise FileNotFoundError("无法打开输入图像，请检查路径是否正确。")

    # 转灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. 分别使用阈值 130 和 140 进行检测
    det_20 = detect_circles_via_fitellipse(
        gray,
        thresh_val=20,
        blur_ksize=(5, 5),
        area_min=13000,
        ellipse_area_min=17000,
        axis_ratio_range=(0.8, 1.5)
    )
    det_15 = detect_circles_via_fitellipse(
        gray,
        thresh_val=15,
        blur_ksize=(5, 5),
        area_min=13000,
        ellipse_area_min=17000,
        axis_ratio_range=(0.8, 1.5)
    )

    # 合并两次检测结果，去重（中心距离 < 200px 视为同一圆）
    detected = det_20.copy()
    for cnt, (cx, cy, r) in det_15:
        if not any(abs(cx - x0) < 200 and abs(cy - y0) < 200 for (_, (x0, y0, _)) in detected):
            detected.append((cnt, (cx, cy, r)))

    # 2. 按行分组
    groups = group_by_rows(detected, tolerance=25)

    # 3. 找最上左圆心
    top_left = find_top_left_circle(groups)

    # 4. 绘制虚拟圆形轮廓并标注
    annotated = draw_detected_circles(img.copy(), detected, top_left)
    cv2.imshow("Detected Circles", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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
#     预处理：CLAHE 增强 + Gamma 矫正
#     """
#     # CLAHE
#     clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid)
#     img = clahe.apply(gray)
#     # Gamma 矫正
#     inv_gamma = 1.0 / gamma
#     table = np.array([((i/255.0) ** inv_gamma) * 255 for i in range(256)], dtype="uint8")
#     img = cv2.LUT(img, table)
#     return img
#
#
# def nms_circles(circles: List[Tuple],
#                 overlap_thresh: float = 0.6) -> List[Tuple]:
#     """
#     对检测出的圆进行非极大抑制（NMS），保留最符合实际尺寸的圆：
#     根据圆心距离与半径之和的比例判断重叠。
#     """
#     if not circles:
#         return []
#     # 按半径从大到小排序
#     sorted_c = sorted(circles, key=lambda x: x[1][2], reverse=True)
#     selected: List[Tuple] = []
#     for cnt,(cx,cy,r) in sorted_c:
#         keep = True
#         for _,(sx,sy,sr) in selected:
#             dist = math.hypot(cx-sx, cy-sy)
#             if dist < overlap_thresh * (r + sr):
#                 keep = False
#                 break
#         if keep:
#             selected.append((cnt,(cx,cy,r)))
#     return selected
#
#
# def detect_circles_via_hough(gray: np.ndarray,
#                               dp: float = 1.0,
#                               minDist: float = 90,
#                               param1: float = 70,
#                               param2: float = 30,
#                               minRadius: int = 50,
#                               maxRadius: int = 100
#                               ) -> List[Tuple[None, Tuple[int,int,int]]]:
#     """
#     HoughCircles 检测，返回 (None,(cx,cy,r)) 列表
#     """
#     blur = cv2.GaussianBlur(gray, (5,5), 1)
#     circles = cv2.HoughCircles(
#         blur, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist,
#         param1=param1, param2=param2,
#         minRadius=minRadius, maxRadius=maxRadius)
#     results = []
#     if circles is not None:
#         for x,y,r in np.round(circles[0]).astype(int):
#             if minRadius <= r <= maxRadius:
#                 results.append((None,(x,y,r)))
#     return results
#
#
# def group_by_rows(circles: List[Tuple], tolerance: int=25) -> List[List[Tuple]]:
#     if not circles:
#         return []
#     sorted_c = sorted(circles, key=lambda x: x[1][1])
#     rows: List[List[Tuple]] = []
#     for cnt,(cx,cy,r) in sorted_c:
#         placed=False
#         for row in rows:
#             if abs(row[0][1][1] - cy) < tolerance:
#                 row.append((cnt,(cx,cy,r)))
#                 placed=True
#                 break
#         if not placed:
#             rows.append([(cnt,(cx,cy,r))])
#     return rows
#
#
# def find_top_left_circle(groups: List[List[Tuple]]) -> Tuple[int,int]:
#     if not groups:
#         return -1,-1
#     top = groups[0]
#     _, (x,y,_) = min(top, key=lambda x: x[1][0])
#     return x,y
#
#
# def draw_detected_circles(img: np.ndarray,
#                            circles: List[Tuple],
#                            target: Tuple[int,int]) -> np.ndarray:
#     out = img.copy()
#     for cnt,(cx,cy,r) in circles:
#         cv2.circle(out, (cx,cy), r, (0,255,0), 2)
#         cv2.circle(out, (cx,cy), 3, (0,255,255), -1)
#     tx,ty = target
#     if (tx,ty)!=(-1,-1):
#         cv2.circle(out,(tx,ty),6,(0,0,255),-1)
#         cv2.putText(out,f"Top-Left: ({tx},{ty})",(tx+8,ty-8),
#                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
#     return out
#
#
# if __name__ == "__main__":
#     img = cv2.imread("test_image6.bmp")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     # 预处理
#     gray_p = preprocess_image(gray)
#     # 轮廓检测
#     h_circles = detect_circles_via_hough(gray_p)
#     circles = nms_circles(h_circles)
#
#     # 按行分组、找最左上
#     groups = group_by_rows(circles)
#     tl = find_top_left_circle(groups)
#
#     # 绘制并保存
#     out = draw_detected_circles(img, circles, tl)
#     cv2.imwrite("output_with_circles.png", out)
#     cv2.imshow("Result", out)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
