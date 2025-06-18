# -*- coding: utf-8 -*-
"""

PlcWorker 线程：
- 负责将图像检测得到的机械手坐标 x,z 和管子数量 count
  通过 Modbus TCP 协议写入 PLC 寄存器
- 支持可配置的字节顺序和寄存器值顺序
- 自动重连与重试逻辑，提供日志信号通知 UI

修改人： hnchen
修改时间： 2025/06/16
"""

import struct
import time
from pymodbus.client import ModbusTcpClient
from PySide6.QtCore import QThread, Slot, Signal
from util.file import load_ini

class PlcWorker(QThread):
    # 日志信号，用于将操作信息发送到 UI
    logMessage = Signal(str)

    """
    构造函数：
    :param section: 对应 settings.ini 中的节名，用于读取 Plc 配置
    :param host: PLC 的 IP 地址
    :param port: PLC 的 Modbus TCP 端口（通常 502）
    :param slave_id: PLC 的 Unit ID
    :param start_addr: 写寄存器的起始地址
    """
    def __init__(self,
                 section: str,
                 host: str,
                 port: int,
                 slave_id: int,
                 start_addr: int,
                 parent=None):
        super().__init__(parent)

        self.section = section  # INI 中的节，用于区分不同模式
        self.host = host  # PLC IP
        self.port = port  # PLC 端口
        self.slave_id = slave_id  # PLC Unit ID
        self.start_addr = start_addr  # 寄存器起始地址
        self._queue = []  # 待发送的坐标队列 [(x,z,count), ...]
        self._running = False  # 线程运行标志
        self.client = None  # Modbus 客户端实例

        # 读取 INI 配置
        cfg = load_ini()
        # 寄存器字节重排顺序，例如 'BADC' 或 'DCAB'
        self.byte_order = cfg["Plc"].get("byte_order", "DCAB").upper()
        # 寄存器值发送顺序序列，例如 ['x','z','count','mode','const']
        self.seq = [s.strip() for s in cfg["Plc"].get('sequence', 'x,z,count,mode,const').split(',')]
        # 可选固定值
        self.mode = cfg["Plc"].getfloat("mode")
        self.const = cfg["Plc"].getfloat("const")

    def run(self):
        """
        线程入口：
        - 循环检查队列，有数据则连接 PLC 并写入寄存器
        - 支持失败重试和自动断线重连
        """
        self._running = True
        while self._running:
            if not self._queue:
                time.sleep(0.01)
                continue
            # 弹出一组坐标准备发送
            x, z, count = self._queue.pop(0)
            try:
                # 创建并连接 Modbus 客户端
                self.client = ModbusTcpClient(self.host, port=self.port)
                if not self.client.connect():
                    self.logMessage.emit(f"[{self.section}] plc无法连接到 {self.host}:{self.port}")
                    continue
                self.logMessage.emit(f"[{self.section}] 发送plc数据开始...")
                # 构造寄存器值列表并写入
                self.write_registers(x, z, count)
            except Exception as e:
                # 捕获任何异常，并记录日志
                self.logMessage.emit(f"[{self.section}] plc处理失败：{e}")
            finally:
                # 关闭客户端连接
                if self.client:
                    self.client.close()

    @Slot(str)
    def set_section(self, section):
        """外部槽：动态切换 INI 节名"""
        self.section = section

    @Slot(float, float, int)
    def send_coord(self, x: float, z: float, count: int = 0):
        """
        外部槽：接收来自 CameraWorker 的坐标数据，追加到发送队列
        """
        self._queue.append((x, z, count))

    def float_to_registers(self, value: float) -> list[int]:
        """
        将一个 32 位浮点数拆成 2 个寄存器值，顺序由 self.byte_order 决定
        支持 A/B/C/D 四个字节的任意排列
        """
        # 按大端格式打包成 4 字节
        packed = struct.pack('>f', value)
        idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        try:
            # 按 byte_order 字符串依次取出对应字节
            reordered = bytes(packed[idx[ch]] for ch in self.byte_order)
            # 前两个字节合成第一个寄存器，后两个字节合成第二个
            reg1 = (reordered[0] << 8) | reordered[1]
            reg2 = (reordered[2] << 8) | reordered[3]
            return [reg1, reg2]
        except KeyError:
            # 配置异常时发日志并返回空列表
            self.logMessage.emit(f"[{self.section}] 无效的字节顺序：'{self.byte_order}'，必须由 A/B/C/D 组成")
            return []

    def write_registers(self, x: float, z: float, count: int):
        """
        根据 self.seq 定义的顺序拼接寄存器值并写入 PLC
        支持 'x','z','count','mode','const' 等关键字
        重试机制：最多尝试两次
        """
        # 构建关键字到数值的映射
        mapping = {
            'x': round(x, 2),
            'z': round(z, 2),
            'count': float(count),
            'mode': round(self.mode, 2),
            'const': round(self.const, 2),
        }
        # 根据 seq 顺序生成完整寄存器列表
        regs = []
        for key in self.seq:
            if key not in mapping:
                raise ValueError(f"配置文件中未找到该属性：'{key}'")
            regs.extend(self.float_to_registers(mapping[key]))
        # 写寄存器并重试逻辑
        times = 2
        while self._running and times > 0:
            try:
                result = self.client.write_registers(
                    address=self.start_addr,
                    values=regs,
                    slave=self.slave_id
                )
                # 写入失败，记录并重试
                if result.isError():
                    self.logMessage.emit(f"[{self.section}] plc写寄存器失败: {result}，重试中...")
                    times = times - 1
                else:
                    # 成功，记录并退出
                    self.logMessage.emit(f"[{self.section}] 发送plc数据结束：机械手坐标=({x:.2f},{z:.2f})")
                    return
            except Exception as e:
                self.logMessage.emit(f"[{self.section}] plc写数据失败：{e}，重试中...")
                times = times - 1
        if times == 0:
            self.logMessage.emit(f"[{self.section}] 发送plc数据失败：机械手坐标=({x:.2f},{z:.2f}) 放弃本次发送")

    def stop(self):
        """
        停止线程：清空运行标志并等待线程结束
        """
        self._running = False
        self.wait()
