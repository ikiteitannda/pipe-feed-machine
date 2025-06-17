# -*- coding: utf-8 -*-
"""

操作配置文件

修改人： hnchen
修改时间： 2025/06/14
"""
import sys
import os
import configparser

def get_exe_dir() -> str:
    """
    获取程序运行根目录
    """
    # 先看 EXE/脚本 所在目录
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return exe_dir

def load_ini() -> configparser.ConfigParser:
    """
    1) 如果 exe 同级目录下有 settings.ini，就读它（用户可修改）
    2) 否则，如果是 PyInstaller one-file 打包后解出的临时 _MEIPASS 下有，就读那个
    3) 都没有，报错或使用默认
    """
    # 先看 EXE/脚本 所在目录
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    ini_path = os.path.join(exe_dir, "settings.ini")
    if os.path.isfile(ini_path):
        # 用户修改的外部 ini
        config_path = ini_path
    else:
        # 回退到 PyInstaller 解包目录里的内置 ini
        # noinspection PyProtectedMember
        config_path = os.path.join(sys._MEIPASS, "settings.ini")

    cfg = configparser.ConfigParser()
    cfg.read(config_path, encoding="utf-8")
    return cfg

def write_ini(section: str, key: str, value: str):
    """
    UI 中参数编辑框变更时回调，立即写回 settings.ini
    - section: INI 节名
    - key: 参数名
    - value: 新值
    """
    config = load_ini()
    config_path = os.path.join(get_exe_dir(), 'settings.ini')
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, value)
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)