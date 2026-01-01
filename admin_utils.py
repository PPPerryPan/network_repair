"""管理员权限工具模块"""
import ctypes
import sys


def is_admin():
    """检查当前是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin_privileges():
    """请求管理员权限（以管理员身份重新运行程序）"""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join([sys.argv[0]] + sys.argv[1:]), None, 1
        )
        return True
    except Exception as e:
        return False

