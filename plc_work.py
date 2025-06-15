import struct
import time
from pymodbus.client import ModbusTcpClient
from PySide6.QtCore import QThread, Slot, Signal

def float_to_registers_badc(value: float) -> list[int]:
    """
    按 BADC 顺序，将一个 32 位浮点数拆成 2 个 uint16 寄存器。
    与 libmodbus 的 modbus_set_float_badc 完全等价。
    """
    # 按大端打包 4 字节
    b0, b1, b2, b3 = struct.pack('>f', value)
    # 重排为 B A D C
    badc = bytes((b1, b0, b3, b2))
    # 每两个字节组成一个 uint16
    reg1 = (badc[0] << 8) | badc[1]
    reg2 = (badc[2] << 8) | badc[3]
    return [reg1, reg2]


class PlcWorker(QThread):
    logMessage = Signal(str)
    """
    后台线程，接收 (x, z, count) 三元组。
    将它们与 mode=3.0、0.0 一起打包写入 PLC 的 760~769 寄存器（5 个 float）。
    若写入失败，会持续重试直到成功或线程停止。
    """
    def __init__(self,
                 section: str,
                 host: str,
                 port: int,
                 slave_id: int,
                 start_addr: int,
                 parent=None):
        super().__init__(parent)
        self.section = section
        self.host       = host
        self.port       = port
        self.slave_id    = slave_id
        self.start_addr = start_addr
        self._queue     = []
        self._running   = False
        self.client     = None

    def run(self):
        # 建立 Modbus TCP 连接
        self.client = ModbusTcpClient(self.host, port=self.port)
        if not self.client.connect():
            print(f"[PLC] 无法连接到 {self.host}:{self.port}")
            return

        self._running = True
        while self._running:
            if self._queue:
                self.logMessage.emit(f"[{self.section}] 发送plc数据开始...")
                x, z, count = self._queue.pop(0)
                self._write_registers(x, z, count)
            time.sleep(0.02)

        # 退出前关闭连接
        self.client.close()

    @Slot(str)
    def set_section(self, section):
        """UI 模式切换时调用，更新要读取的 INI 节名"""
        self.section = section

    @Slot(float, float, int)
    def send_coord(self, x: float, z: float, count: int = 0):
        """
        槽：接收来自 CameraWorker 的 (x, z, count)，入队后
        run() 循环会消费并发往 PLC。
        """
        self._queue.append((x, z, count))

    def _write_registers(self, x: float, z: float, count: int):
        """
        依次打包：X, Z, mode=3.0, total_count, 0.0，
        按 BADC 顺序转换成 10 个寄存器并写入。
        如果失败，会持续重试。
        """
        # 打包 5 个浮点到 10 个寄存器
        regs = []
        regs += float_to_registers_badc(x)
        regs += float_to_registers_badc(z)
        regs += float_to_registers_badc(3.0)
        regs += float_to_registers_badc(float(count))
        regs += float_to_registers_badc(0.0)

        # 重试直到成功或线程结束
        while self._running:
            result = self.client.write_registers(
                address=self.start_addr,
                values=regs,
                slave=self.slave_id
            )
            if result.isError():
                self.logMessage.emit(f"[{self.section}] plc写寄存器失败: {result}，重试中...")
                time.sleep(0.1)
                continue
            else:
                self.logMessage.emit(f"[{self.section}] 发送plc数据结束：机械手坐标=({x:.3f},{z:.3f})")
                break

    def stop(self):
        self._running = False
        self.wait()
