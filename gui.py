"""GUI Interface Module"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import queue
import customtkinter as ctk

from constants import REPAIR_STEPS, THEME_COLORS, STEP_STATUS_CONFIG
from network_utils import (
    get_ethernet_adapters,
    configure_network,
    set_dns_to_dhcp,
    refresh_network_config,
    display_network_info,
    # upload_usage
)


class NetworkRepairGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Repair Tool")
        self.root.geometry("800x850")
        
        # Set CustomTkinter theme
        self.appearance_mode = "System"
        ctk.set_appearance_mode(self.appearance_mode)  # Follow system
        ctk.set_default_color_theme("blue")
        
        # Set window icon
        self.setup_icon()
        
        # Color configuration - select colors based on appearance mode
        current_mode = ctk.get_appearance_mode().lower()
        self.colors = THEME_COLORS.get(current_mode, THEME_COLORS['light'])
        
        # Create message queue for inter-thread communication
        self.message_queue = queue.Queue()
        
        # Status variables
        self.current_step = 0
        self.is_repairing = False
        
        self.setup_ui()
        self.start_repair_automatically()
        
    def setup_icon(self):
        """Set window and taskbar icons"""
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
                print(f"Icon file not found, tried paths: {possible_paths}")
        except Exception as e:
            print(f"Failed to set window icon: {e}")
        
    def setup_ui(self):
        """Set up user interface"""
        # Configure Grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main background container
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color=self.colors['background'])
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1) # Log area auto-resize height
        
        # 1. Title card area
        header_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb" if ctk.get_appearance_mode().lower() == "light" else "#334155",
            height=100
        )
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 15), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔧 Network Repair Tool", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=28, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Automatically repair Windows network connection issues", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=15),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 2. Step progress card
        steps_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb" if ctk.get_appearance_mode().lower() == "light" else "#334155"
        )
        steps_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        
        self.steps = REPAIR_STEPS
        self.step_icons = []
        self.step_labels = []
        
        # Configure column weights
        for i in range(len(self.steps)):
            steps_frame.grid_columnconfigure(i, weight=1)
            
        for i, step in enumerate(self.steps):
            # Single step container
            step_container = ctk.CTkFrame(steps_frame, fg_color="transparent")
            step_container.grid(row=0, column=i, padx=5, pady=20, sticky="ew")
            
            # Add hover effect
            step_container.bind("<Enter>", lambda e, container=step_container: container.configure(fg_color="#f1f5f9" if ctk.get_appearance_mode().lower() == "light" else "#334155"))
            step_container.bind("<Leave>", lambda e, container=step_container: container.configure(fg_color="transparent"))
            
            # Icon
            icon_label = ctk.CTkLabel(
                step_container, 
                text="⏳", 
                font=ctk.CTkFont(family="Segoe UI Emoji", size=24)
            )
            icon_label.pack(side="top", pady=(0, 8))
            self.step_icons.append(icon_label)
            
            # Text
            step_label = ctk.CTkLabel(
                step_container, 
                text=step, 
                font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
                text_color=self.colors['text_secondary']
            )
            step_label.pack(side="top")
            self.step_labels.append(step_label)
            
        # 3. Execution log card
        log_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb" if ctk.get_appearance_mode().lower() == "light" else "#334155"
        )
        log_frame.grid(row=2, column=0, padx=20, pady=(15, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_title = ctk.CTkLabel(
            log_frame, 
            text="📋 Execution Log", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=16, weight="bold"),
            text_color=self.colors['text']
        )
        log_title.grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # Textbox
        self.output_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=self.colors['text'],
            fg_color="#f8f9fa" if ctk.get_appearance_mode().lower() == "light" else "#1e293b",
            border_width=1,
            border_color="#e2e8f0" if ctk.get_appearance_mode().lower() == "light" else "#334155",
            corner_radius=8
        )
        self.output_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Add right-click menu for log textbox
        self.setup_textbox_context_menu()
        
        # Start processing message queue
        self.process_queue()
        
    def update_step_progress(self, step_index, status="waiting"):
        """Update step progress"""
        if 0 <= step_index < len(self.steps):
            icon, color_key = STEP_STATUS_CONFIG.get(status, STEP_STATUS_CONFIG["waiting"])
            color = self.colors[color_key]
            
            # Add animation effect for step status change
            self.animate_step_change(step_index, icon, color, status)
            
            self.root.update_idletasks()
    
    def start_repair_automatically(self):
        """Automatically start network repair"""
        self.is_repairing = True
        self.log_message("https://github.com/PPPerryPan/network_repair")
        self.log_message("Administrator privileges acquired, starting automatic network repair...")
        
        repair_thread = threading.Thread(target=self.perform_repair)
        repair_thread.daemon = True
        repair_thread.start()
    
    def log_message(self, message):
        """Add message to output box"""
        self.message_queue.put(message)
    
    def process_queue(self):
        """Process message queue"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.output_text.insert(tk.END, message + "\n")
                self.output_text.see(tk.END)
                # CustomTkinter Textbox update may need update
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)
    
    def perform_repair(self):
        """Perform network repair operations"""
        try:
            self.log_message("🚀 Starting network repair...")
            
            # Get Ethernet adapters
            self.log_message("📡 Getting network adapter information...")
            self.update_step_progress(0, "running")
            self.current_step_index = 0
            adapters = get_ethernet_adapters(log_callback=self.log_message)
            if not adapters:
                self.log_message("❌ No Ethernet adapters found")
                self.update_step_progress(0, "error")
                return
            
            self.log_message(f"✅ Found {len(adapters)} Ethernet adapters")
            self.update_step_progress(0, "completed")
            
            # Configure network
            self.log_message("⚙️ Configuring network settings...")
            self.update_step_progress(1, "running")
            self.current_step_index = 1
            configure_network(adapters, log_callback=self.log_message)
            self.update_step_progress(1, "completed")
            
            # Set DNS
            self.log_message("🌐 Setting DNS to DHCP...")
            self.update_step_progress(2, "running")
            self.current_step_index = 2
            set_dns_to_dhcp(adapters, log_callback=self.log_message)
            self.update_step_progress(2, "completed")
            
            # Refresh network configuration
            self.log_message("🔄 Refreshing network configuration...")
            self.update_step_progress(3, "running")
            self.current_step_index = 3
            refresh_network_config(log_callback=self.log_message)
            self.update_step_progress(3, "completed")
            
            # Display network information
            self.log_message("📊 Getting network configuration information...")
            # try:
            #     upload_usage(log_callback=self.log_message)
            # except Exception as e:
            #     self.log_message(f"Skipped")
            self.update_step_progress(4, "running")
            self.current_step_index = 4
            display_network_info(log_callback=self.log_message)
            self.update_step_progress(4, "completed")
            
            self.log_message("\n🎉 Processing completed, network should be restored []~(￣▽￣)~*")
            self.log_message("💡 If it still doesn't work, you might be using a TUN Adapter, or it's a non-local network issue. Please check your network proxy tool configuration or contact your network administrator. (＠_＠;)")
            
        except Exception as e:
            self.log_message(f"❌ Error occurred during repair: {str(e)}")
            if hasattr(self, 'current_step_index'):
                self.update_step_progress(self.current_step_index, "error")
        finally:
            self.is_repairing = False
            self.root.after(0, self.repair_completed)
    
    def repair_completed(self):
        """UI updates after repair completion"""
        self.update_step_progress(0, "completed")
        self.update_step_progress(1, "completed")
        self.update_step_progress(2, "completed")
        self.update_step_progress(3, "completed")
        self.update_step_progress(4, "completed")
        
        # Add celebration animation
        self.animate_completion()
        
        self.log_message("\n✅ Repair completed, program will automatically close in 60 seconds...")
        self.root.after(60000, self.root.destroy)
    
    def animate_step_change(self, step_index, icon, color, status):
        """Add animation effect for step change"""
        # Update icon and color
        self.step_icons[step_index].configure(text=icon, text_color=color)
        
        # Update text color
        if status == "running":
            self.step_labels[step_index].configure(text_color=self.colors['primary'], font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"))
        elif status == "completed":
            self.step_labels[step_index].configure(text_color=self.colors['success'])
        elif status == "error":
            self.step_labels[step_index].configure(text_color=self.colors['error'])
        else:
            self.step_labels[step_index].configure(text_color=self.colors['text_secondary'], font=ctk.CTkFont(family="Microsoft YaHei UI", size=12))
        
        # Add scale animation
        self.animate_icon_scale(self.step_icons[step_index])
    
    def animate_icon_scale(self, icon_label):
        """Icon scale animation"""
        # Save original font size
        original_font = icon_label.cget("font")
        
        # Enlarge animation
        def scale_up():
            icon_label.configure(font=ctk.CTkFont(family="Segoe UI Emoji", size=28))
            self.root.after(100, scale_down)
        
        # Shrink back to original size
        def scale_down():
            icon_label.configure(font=original_font)
        
        scale_up()
    
    def animate_completion(self):
        """Completion celebration animation"""
        # Make all completed step icons bounce
        def animate_step_icons():
            for i in range(5):
                for icon in self.step_icons:
                    if icon.cget("text") == "✅":
                        # Save original font
                        original_font = icon.cget("font")
                        # Enlarge
                        icon.configure(font=ctk.CTkFont(family="Segoe UI Emoji", size=28))
                        self.root.after(100, lambda icon=icon, original_font=original_font: icon.configure(font=original_font))
                self.root.after(200, lambda: None)  # Wait for next frame
        
        # Execute animation
        animate_step_icons()
    
    def setup_textbox_context_menu(self):
        """Set up right-click menu for textbox"""
        # Create right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.colors['surface'], fg=self.colors['text'])
        
        # Add menu items
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all_text)
        
        # Bind right-click event
        self.output_text.bind("<Button-3>", self.show_context_menu)
        # Bind keyboard shortcuts
        self.output_text.bind("<Control-c>", self.copy_text)
        self.output_text.bind("<Control-v>", self.paste_text)
        self.output_text.bind("<Control-a>", self.select_all_text)
    
    def show_context_menu(self, event):
        """Show right-click menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self, event=None):
        """Copy selected text"""
        try:
            selected_text = self.output_text.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected
            pass
    
    def paste_text(self, event=None):
        """Paste text"""
        try:
            clipboard_text = self.root.clipboard_get()
            # Insert text at current cursor position
            self.output_text.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            # Clipboard is empty
            pass
    
    def select_all_text(self, event=None):
        """Select all text"""
        self.output_text.tag_add(tk.SEL, "1.0", tk.END)
        self.output_text.mark_set(tk.INSERT, "1.0")
        self.output_text.see(tk.INSERT)
        return 'break'
