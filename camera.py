# camera.py

import time
import cv2
import numpy as np
from gxipy.gxiapi import DeviceManager
from gxipy.gxidef import (
    GxAccessMode,
    GxDSStreamBufferHandlingModeEntry,
    GxTriggerSelectorEntry,
    GxTriggerSourceEntry,
    GxTriggerActivationEntry,
    GxSwitchEntry
)
from PySide6.QtGui import QImage, QPixmap

class IndustrialCamera:
    """
    Industrial camera wrapper for external-trigger mode.
    Provides async callback and sync polling interfaces.
    """
    def __init__(self, index=1, timeout=1000, trigger_line=GxTriggerSourceEntry.LINE0):
        # 1) 枚举并打开设备
        mgr = DeviceManager()
        count, _ = mgr.update_device_list(timeout)
        if count < index:
            raise RuntimeError(f"No camera found at index {index}")
        self.dev = mgr.open_device_by_index(index, access_mode=GxAccessMode.EXCLUSIVE)
        self.stream = self.dev.data_stream[0]

        # 2) 外部触发配置
        self.dev.TriggerMode.set(GxSwitchEntry.ON)
        self.dev.TriggerSelector.set(GxTriggerSelectorEntry.FRAME_START)
        self.dev.TriggerSource.set(trigger_line)
        self.dev.TriggerActivation.set(GxTriggerActivationEntry.RISINGEDGE)

        # 3) 包长、心跳、缓冲区策略
        pkt = self.dev.GevSCPSPacketSize.get()
        self.dev.GevSCPSPacketSize.set(pkt)
        self.dev.GevHeartbeatTimeout.set(timeout)
        self.stream.StreamBufferHandlingMode.set(
            GxDSStreamBufferHandlingModeEntry.OLDEST_FIRST
        )

        # 4) 回调与存储
        self._last_pix = None
        # self.frame_callback = None
        self.stream.register_capture_callback(lambda data: self._on_frame(data))

        # 5) 启动流和采集
        self.dev.stream_on()
        self.dev.AcquisitionStart.send_command()

    def _on_frame(self, data):
        """内部回调：从原始数据到 QPixmap，再推给 frame_callback"""
        arr = data.get_numpy_array()
        if arr.ndim == 2:
            rgb = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        qimg = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self._last_pix = pix
        if callable(self.frame_callback):
            self.frame_callback(pix)

    def software_trigger(self):
        """发送一次软件触发信号（若支持）"""
        try:
            self.dev.TriggerSoftware.send_command()
        except Exception:
            pass

    def get_qpixmap(self, timeout=1000) -> QPixmap:
        """
        同步拉取首帧：等待 _last_pix 非空或超时后返回 QPixmap，否则返回 None。
        """
        start = time.time()
        while self._last_pix is None:
            if (time.time() - start)*1000 > timeout:
                return None
            time.sleep(0.005)
        return self._last_pix

    def close(self):
        """优雅停止采集并关闭设备"""
        try: self.dev.AcquisitionStop.send_command()
        except: pass
        try: self.dev.stream_off()
        except: pass
        try: self.stream.unregister_capture_callback()
        except: pass
        try: self.dev.close()
        except: pass


# Self-test
if __name__ == "__main__":
    cam = IndustrialCamera(index=1)
    cam.frame_callback = lambda pix: print("Frame:", pix.size())
    time.sleep(2)
    pix = cam.get_qpixmap()
    print("Last frame:", pix.size() if pix else None)
    cam.close()
