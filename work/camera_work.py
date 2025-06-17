# -*- coding: utf-8 -*-
"""

CameraWorker 线程：
- 负责工业相机的打开、配置和外触发采集
- 图像通道处理（灰度/BGR 数据兼容）
- 检测算法调用（拟合椭圆检测圆形）
- 像素坐标转换为机械手物理坐标
- 通过信号提供：带注释图像帧、检测坐标、日志信息和相机状态

修改人： hnchen
修改时间： 2025/06/13
"""
import datetime
import os
import cv2

from gxipy.gxiapi import DeviceManager
from gxipy.gxidef import (
    GxAccessMode,
    GxSwitchEntry,
    GxTriggerSourceEntry,
    GxTriggerActivationEntry,
    GxTriggerSelectorEntry,
    GxDSStreamBufferHandlingModeEntry
)
from PySide6.QtCore import QThread, Signal, Slot

from util.file import (load_ini, get_exe_dir)

class CameraWorker(QThread):
    # 信号定义：
    frameReady = Signal(object)          # 输出处理后 QPixmap 图像
    statusCheck = Signal(int)            # 输出相机连接状态（设备数或 0）
    logMessage = Signal(str)             # 输出运行日志信息
    coordReady = Signal(float, float, int)# 输出物理坐标 x,z 及圆管数量

    def __init__(self, section: str, save_image: bool, index=1, timeout=5000, parent=None):
        """
        初始化 CameraWorker
        :param section: 要读取的 INI 节名
        :param save_image: 是否保存原始帧到本地
        :param index: 相机索引（以 1 开始）
        :param timeout: 获取图像超时毫秒数
        """
        super().__init__(parent)

        # 创建原图保存目录
        # 确保 pictures 目录存在
        pics_dir = os.path.join(get_exe_dir(), 'pictures')
        os.makedirs(pics_dir, exist_ok=True)

        self.index = index                # 相机序号
        self.timeout = timeout            # 抓图超时
        self.section = section            # INI 配置节名
        self._running = False             # 线程运行标志
        self.save_image = save_image      # 是否保存原始图片

    @Slot(str)
    def set_section(self, section):
        """动态切换读取的节"""
        self.section = section

    def check_save_image(self, checked: bool):
        """复选框控制是否保存原始图像"""
        self.save_image = checked

    def transform_to_robot_position(self, px: float, py: float) -> tuple[float, float]:
        """
        将像素坐标 (px, py) 转换成机械手物理坐标 (x, z)
        读取 'Calib' 节的 A-F 校准系数及 Home 偏移，
        再加上当前节下的 ui_offest_x, ui_offest_z 微调偏移
        计算公式：
          x = A*px + B*py + C + HomeX + ui_offest_x
          z = D*px + E*py + F + HomeZ + ui_offest_z
        出错时返回 (-1, -1)
        """
        try:
            cfg = load_ini()
            # 校准系数
            a = float(cfg['Calib']['A'])
            b = float(cfg['Calib']['B'])
            c = float(cfg['Calib']['C'])
            d = float(cfg['Calib']['D'])
            e = float(cfg['Calib']['E'])
            f = float(cfg['Calib']['F'])
            # Home 偏移
            home_x = float(cfg['Calib']['HomeX'])
            home_z = float(cfg['Calib']['HomeZ'])
            # UI 微调偏移（节内键名需正确）
            ui_offset_x = float(cfg[self.section]['ui_offest_x'])
            ui_offset_z = float(cfg[self.section]['ui_offest_z'])
            # 仿射变换 + 平移
            rx = a * px + b * py + c + home_x + ui_offset_x
            rz = d * px + e * py + f + home_z + ui_offset_z
            return rx, rz
        except Exception as ex:
            # 转换失败，写日志并返回非法值
            self.logMessage.emit(f"[{self.section}] 坐标转换失败：{ex}")
            return -1, -1

    def run(self):
        """
        线程入口：
        1. 枚举设备，检查相机连接
        2. 打开相机，配置外触发、网络包大小和心跳
        3. 配置数据流缓存策略
        4. 进入循环：
           - 抓取图像，适配通道（灰度/彩色）
           - 保存原图（可选）
           - 读取检测参数并执行检测
           - 转换坐标并发出信号
        5. 停止循环后释放资源
        """
        try:
            mgr = DeviceManager()
            # 更新设备列表
            cnt, _ = mgr.update_device_list(self.timeout)
            # 发出设备状态
            self.statusCheck.emit(cnt >= self.index)
            if cnt < self.index:
                # 未找到相机，退出线程
                self.logMessage.emit(f"[{self.section}] 未检测到相机，停止运行")
                return

            # 打开相机（独占模式）
            cam = mgr.open_device_by_index(self.index, access_mode=GxAccessMode.EXCLUSIVE)
            # 外触发配置
            cam.TriggerMode.set(GxSwitchEntry.ON)
            cam.TriggerSource.set(GxTriggerSourceEntry.LINE0)
            cam.TriggerActivation.set(GxTriggerActivationEntry.RISINGEDGE)
            cam.TriggerSelector.set(GxTriggerSelectorEntry.FRAME_START)
            # 网络包与心跳
            cfg = load_ini()
            pkt = cam.GevSCPSPacketSize.get()
            cam.GevSCPSPacketSize.set(pkt)
            cam.GevHeartbeatTimeout.set(cfg["Camera"].getint("heartbeat"))
            # 数据流配置
            stream = cam.data_stream[0]
            stream.set_acquisition_buffer_number(cfg["Camera"].getint("buffer_number"))
            stream.StreamBufferHandlingMode.set(GxDSStreamBufferHandlingModeEntry.OLDEST_FIRST)

            self._running = True
            # 循环抓图、处理
            while self._running:
                try:
                    # 开始采集
                    cam.stream_on()
                    raw = stream.get_image(self.timeout)
                    if raw is None:
                        continue

                    self.logMessage.emit(f"[{self.section}] 图像采集开始...")
                    buf = raw.get_numpy_array()  # 获取原始数据缓冲区
                    # 获取分辨率
                    try:
                        h = raw.frame_data.height
                        w = raw.frame_data.width
                    except AttributeError:
                        h, w = buf.shape[:2]
                    try:
                        # 通道兼容：灰度、RGB、RGBA
                        if buf.size == h * w:
                            gray = buf.reshape((h, w))
                            bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                        elif buf.size == h * w * 3:
                            bgr = buf.reshape((h, w, 3))
                            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                        elif buf.size == h * w * 4:
                            bgr = buf.reshape((h, w, 4))[..., :3]
                            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                        else:
                            # 其他异常通道，强制当灰度
                            gray = buf.reshape((h, w))
                            bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                    except Exception as e:
                        self.logMessage.emit(f"[{self.section}] 采集图片失败：{e}")
                        continue
                    self.logMessage.emit(f"[{self.section}] 已获取图像")
                    self.logMessage.emit(f"[{self.section}] 检测开始...")
                    # 根据配置获取当前模式对应的图像检测算法
                    cfg = load_ini()
                    detector = cfg["Detector"].getint(self.section)
                    if detector == 1:
                        # 引入检测算法接口
                        from detector.detector import detect_image
                        pix, tx, ty, circles_len = detect_image(self.section, h, w, gray, bgr)
                    elif detector == 2:
                        # 引入检测算法接口
                        from detector.detector import one_detect_image
                        pix, tx, ty, circles_len = one_detect_image()
                    else:
                        # 引入检测算法接口
                        from detector.detector import one_detect_image
                        pix, tx, ty, circles_len = one_detect_image()

                    self.frameReady.emit(pix)  # 发射图像信号
                    self.logMessage.emit(f"[{self.section}] 检测完成: 圆心=({tx},{ty}), 圆管数量={circles_len}")

                    # 可选：保存原图文件 构造文件名：YYYYMMDD_节名.bmp
                    if self.save_image:
                        # 确保 pictures 目录存在
                        pics_dir = os.path.join(get_exe_dir(), 'pictures')
                        os.makedirs(pics_dir, exist_ok=True)
                        now = datetime.datetime.now()
                        date_str = now.strftime("%Y%m%d")
                        time_str = now.strftime("%H%M%S%f")[:-3]  # 毫秒精度
                        filename = f"{date_str}_{time_str}_{self.section}_{circles_len}.bmp"
                        filepath = os.path.join(pics_dir, filename)
                        # 3) 写磁盘 用 cv2 编码，再用 Python 原生文件 IO 写入
                        ext = os.path.splitext(filename)[1]
                        success, enc = cv2.imencode(ext, buf.copy())
                        if success:
                            try:
                                with open(filepath, 'wb') as f:
                                    f.write(enc.tobytes())
                                self.logMessage.emit(f"[{self.section}] 原图像已保存到：{filepath}")
                            except Exception as io_e:
                                self.logMessage.emit(f"[{self.section}] 原图像保存失败：{io_e}")
                        else:
                            self.logMessage.emit(f"[{self.section}] 原图像保存失败：图像编码失败")

                    if tx == -1 or ty == -1:
                        self.logMessage.emit(f"[{self.section}] 坐标无效，忽略发送: x={tx}, y={ty}")
                    else:
                        # 坐标转换并发 PLC 信号
                        rx, rz = self.transform_to_robot_position(tx, ty)
                        if abs(rx) <= 200 and abs(rz) <= 500 and circles_len > 0:
                            self.coordReady.emit(rx, rz, circles_len)
                        else:
                            self.logMessage.emit(f"[{self.section}] 坐标越界，忽略发送: x={rx}, z={rz}")
                except Exception as e:
                    # 采集或处理异常：记录日志并停止循环
                    self.logMessage.emit(f"[{self.section}] 图像处理失败: {e}")
                    self._running = False
                    self.statusCheck.emit(0)
                finally:
                    try:
                        cam.stream_off()
                    finally:
                        pass
            # 退出循环后清理资源
            try:
                cam.close_device()
            finally:
                pass
        except Exception as e:
            self.logMessage.emit(f"[{self.section}] 图像处理失败: {e}")

    def stop(self):
        """
        停止线程：设置标志并等待退出
        """
        self._running = False
        self.wait()
