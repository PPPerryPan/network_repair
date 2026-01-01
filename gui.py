"""GUI 界面模块"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import queue
import customtkinter as ctk

from constants import REPAIR_STEPS, THEME_COLORS, STEP_STATUS_CONFIG
from admin_utils import is_admin, request_admin_privileges
from network_utils import (
    get_ethernet_adapters,
    configure_network,
    set_dns_to_dhcp,
    refresh_network_config,
    display_network_info,
    upload_usage
)


class NetworkRepairGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网络修复工具")
        self.root.geometry("800x850")
        
        # 设置 CustomTkinter 主题
        ctk.set_appearance_mode("System")  # 跟随系统
        ctk.set_default_color_theme("blue")
        
        # 设置窗口图标
        self.setup_icon()
        
        # 颜色配置
        self.colors = THEME_COLORS
        # 覆盖一些颜色以适应深色/浅色模式 (这里简单处理，主要适配浅色，因为 constant 是固定的)
        # 如果需要更好的深色模式支持，建议 constant 中定义元组 (light, dark)
        
        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 状态变量
        self.current_step = 0
        self.is_repairing = False
        
        self.setup_ui()
        self.start_repair_automatically()
        
    def setup_icon(self):
        """设置窗口图标和任务栏图标"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            
            possible_paths = [
                os.path.join(base_path, 'icon.ico'),
                os.path.join(base_path, '..', 'icon.ico'),
                os.path.join(os.path.dirname(base_path), 'icon.ico'),
            ]
            
            icon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            if icon_path and os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"未找到图标文件，尝试的路径: {possible_paths}")
        except Exception as e:
            print(f"设置窗口图标失败: {e}")
        
    def setup_ui(self):
        """设置用户界面"""
        # 配置 Grid 权重
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # 主背景容器
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color=self.colors['background'])
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1) # 日志区域自适应高度
        
        # 1. 标题卡片区域
        header_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=10,
            border_width=1,
            border_color="#e5e7eb" # 浅边框
        )
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔧 网络修复工具", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=24, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="自动检测并修复本地网络连接问题", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=14),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        # 2. 步骤进度卡片
        steps_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=10,
            border_width=1,
            border_color="#e5e7eb"
        )
        steps_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.steps = REPAIR_STEPS
        self.step_icons = []
        self.step_labels = []
        
        # 配置列权重
        for i in range(len(self.steps)):
            steps_frame.grid_columnconfigure(i, weight=1)
            
        for i, step in enumerate(self.steps):
            # 单个步骤容器
            step_container = ctk.CTkFrame(steps_frame, fg_color="transparent")
            step_container.grid(row=0, column=i, padx=5, pady=15, sticky="ew")
            
            # 图标
            icon_label = ctk.CTkLabel(
                step_container, 
                text="⏳", 
                font=ctk.CTkFont(family="Segoe UI Emoji", size=20)
            )
            icon_label.pack(side="top", pady=(0, 5))
            self.step_icons.append(icon_label)
            
            # 文字
            step_label = ctk.CTkLabel(
                step_container, 
                text=step, 
                font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
                text_color=self.colors['text_secondary']
            )
            step_label.pack(side="top")
            self.step_labels.append(step_label)
            
        # 3. 执行日志卡片
        log_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=10,
            border_width=1,
            border_color="#e5e7eb"
        )
        log_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_title = ctk.CTkLabel(
            log_frame, 
            text="📋 执行日志", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=16, weight="bold"),
            text_color=self.colors['text']
        )
        log_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # 文本框
        self.output_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=self.colors['text'],
            fg_color="#f8f9fa", # 浅灰底色
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=5
        )
        self.output_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # 开始处理消息队列
        self.process_queue()
        
    def update_step_progress(self, step_index, status="waiting"):
        """更新步骤进度"""
        if 0 <= step_index < len(self.steps):
            icon, color = STEP_STATUS_CONFIG.get(status, STEP_STATUS_CONFIG["waiting"])
            # 更新图标
            self.step_icons[step_index].configure(text=icon, text_color=color)
            
            # 更新文字颜色
            if status == "running":
                self.step_labels[step_index].configure(text_color=self.colors['primary'], font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"))
            elif status == "completed":
                self.step_labels[step_index].configure(text_color=self.colors['success'])
            elif status == "error":
                self.step_labels[step_index].configure(text_color=self.colors['error'])
            else:
                self.step_labels[step_index].configure(text_color=self.colors['text_secondary'], font=ctk.CTkFont(family="Microsoft YaHei UI", size=12))
            
            self.root.update_idletasks()
    
    def start_repair_automatically(self):
        """自动开始修复网络"""
        self.is_repairing = True
        self.log_message("正在检查管理员权限...")
        
        if not is_admin():
            self.log_message("需要管理员权限，正在请求提权...")
            if request_admin_privileges():
                self.root.after(2000, self.root.destroy)
            else:
                self.log_message("请求管理员权限失败")
                self.log_message("请手动以管理员身份运行此程序")
                time.sleep(5)
            return
        
        self.log_message("已获取管理员权限，开始自动修复网络...")
        
        repair_thread = threading.Thread(target=self.perform_repair)
        repair_thread.daemon = True
        repair_thread.start()
    
    def log_message(self, message):
        """添加消息到输出框"""
        self.message_queue.put(message)
    
    def process_queue(self):
        """处理消息队列"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.output_text.insert(tk.END, message + "\n")
                self.output_text.see(tk.END)
                # CustomTkinter 的 Textbox 更新可能需要 update
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)
    
    def perform_repair(self):
        """执行网络修复操作"""
        try:
            self.log_message("🚀 开始网络修复...")
            
            # 获取以太网适配器
            self.log_message("📡 正在获取网络适配器信息...")
            self.update_step_progress(0, "running")
            self.current_step_index = 0
            adapters = get_ethernet_adapters(log_callback=self.log_message)
            if not adapters:
                self.log_message("❌ 未找到任何以太网适配器")
                self.update_step_progress(0, "error")
                return
            
            self.log_message(f"✅ 找到 {len(adapters)} 个以太网适配器")
            self.update_step_progress(0, "completed")
            
            # 配置网络
            self.log_message("⚙️ 正在配置网络设置...")
            self.update_step_progress(1, "running")
            self.current_step_index = 1
            configure_network(adapters, log_callback=self.log_message)
            self.update_step_progress(1, "completed")
            
            # 设置DNS
            self.log_message("🌐 正在设置DNS为DHCP...")
            self.update_step_progress(2, "running")
            self.current_step_index = 2
            set_dns_to_dhcp(adapters, log_callback=self.log_message)
            self.update_step_progress(2, "completed")
            
            # 刷新网络配置
            self.log_message("🔄 正在刷新网络配置...")
            self.update_step_progress(3, "running")
            self.current_step_index = 3
            refresh_network_config(log_callback=self.log_message)
            self.update_step_progress(3, "completed")
            
            # 显示网络信息
            self.log_message("📊 正在获取网络配置信息...")
            # try:
            #     upload_usage(log_callback=self.log_message)
            # except Exception as e:
            #     self.log_message(f"跳过")
            self.update_step_progress(4, "running")
            self.current_step_index = 4
            display_network_info(log_callback=self.log_message)
            self.update_step_progress(4, "completed")
            
            self.log_message("\n🎉 已完成处理，网络应该恢复正常了 []~(￣▽￣)~*")
            self.log_message("💡 若还是不行，可能使用了 TUN 网卡，或非本机网络问题，请检查网络代理工具配置或联系您的网络管理员。 (＠_＠;)")
            
        except Exception as e:
            self.log_message(f"❌ 修复过程中出现错误: {str(e)}")
            if hasattr(self, 'current_step_index'):
                self.update_step_progress(self.current_step_index, "error")
        finally:
            self.is_repairing = False
            self.root.after(0, self.repair_completed)
    
    def repair_completed(self):
        """修复完成后的UI更新"""
        self.update_step_progress(0, "completed")
        self.update_step_progress(1, "completed")
        self.update_step_progress(2, "completed")
        self.update_step_progress(3, "completed")
        self.update_step_progress(4, "completed")
        self.log_message("\n✅ 修复完成，程序将在60秒后自动关闭...")
        self.root.after(60000, self.root.destroy)
