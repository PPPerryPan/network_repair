"""常量定义模块"""

# 修复步骤列表
REPAIR_STEPS = [
    "获取适配器",
    "重置网卡",
    "重置 DNS",
    "重新联网",
    "完成"
]

# 现代化主题颜色配置
THEME_COLORS = {
    'primary': '#2563eb',      # 蓝色
    'success': '#16a34a',      # 绿色
    'warning': '#ea580c',      # 橙色
    'error': '#dc2626',        # 红色
    'background': '#f8fafc',   # 浅灰背景
    'surface': '#ffffff',      # 白色表面
    'text': '#1e293b',         # 深灰文字
    'text_secondary': '#64748b' # 次要文字
}

# 步骤状态配置
STEP_STATUS_CONFIG = {
    "waiting": ("⏳", THEME_COLORS['text_secondary']),
    "running": ("⏳", THEME_COLORS['primary']),
    "completed": ("✅", THEME_COLORS['success']),
    "error": ("❌", THEME_COLORS['error'])
}

# 使用统计 API 配置
# USAGE_API_URL = 'http://localhost:10001/api/usage'
# USAGE_SOFTWARE_NAME = 'network_repair'

