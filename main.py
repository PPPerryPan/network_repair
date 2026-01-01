"""网络修复工具主入口"""
import customtkinter as ctk
from gui import NetworkRepairGUI


def main():
    """主函数"""
    # 替换 tk.Tk() 为 ctk.CTk() 以获得原生 WinUI3 风格支持
    root = ctk.CTk()
    app = NetworkRepairGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
