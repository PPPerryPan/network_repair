"""网络操作工具模块"""
import subprocess
import time
import wmi
import pythoncom
import requests
# from constants import USAGE_API_URL, USAGE_SOFTWARE_NAME


def get_startupinfo():
    """获取 subprocess 启动信息，用于隐藏控制台窗口"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return startupinfo


def get_ethernet_adapters(log_callback=None):
    """
    获取以太网适配器信息
    
    Args:
        log_callback: 日志回调函数，用于输出日志信息
    
    Returns:
        list: 适配器信息列表，每个元素包含 'name' 和 'description'
    """
    if log_callback:
        log_callback("正在获取以太网适配器信息...")
    
    startupinfo = get_startupinfo()
    
    try:
        result = subprocess.run(
            ["ipconfig", "/all"], 
            capture_output=True, 
            text=True, 
            encoding='gb2312', 
            startupinfo=startupinfo
        )
        output = result.stdout
        
        adapters = []
        current_adapter = None
        adapter_info = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('以太网适配器'):
                adapter_name = line.replace('以太网适配器', '').replace(':', '').strip()
                current_adapter = adapter_name
                adapter_info[current_adapter] = {'name': adapter_name}
            elif current_adapter and line.startswith('描述'):
                description = line.split(':', 1)[1].strip()
                adapter_info[current_adapter]['description'] = description
                if any(x in current_adapter for x in ['以太网', 'Eth', 'eth']):
                    adapters.append(adapter_info[current_adapter])
        
        for adapter in adapters:
            if log_callback:
                log_callback(f"  📡 找到适配器: {adapter['name']} ({adapter['description']})")
        
        return adapters
        
    except Exception as e:
        if log_callback:
            log_callback(f"❌ 获取适配器信息失败: {str(e)}")
        return []


def configure_network(adapters, log_callback=None):
    """
    配置网络设置（设置IP和DNS为DHCP）
    
    Args:
        adapters: 适配器信息列表
        log_callback: 日志回调函数
    """
    if log_callback:
        log_callback("开始配置网络设置...")
    
    startupinfo = get_startupinfo()
    
    for adapter_info in adapters:
        if log_callback:
            log_callback(f"  🔧 正在配置适配器: {adapter_info['name']}")
        adapter_name = adapter_info['name']
        
        # 设置DHCP
        try:
            # 设置IP地址为DHCP
            result = subprocess.run([
                "netsh", "interface", "ip", "set", "address",
                adapter_name, "source=dhcp"
            ], capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode == 0:
                if log_callback:
                    log_callback(f"    ✅ 设置IP地址为DHCP成功")
            else:
                if result.stderr:
                    if log_callback:
                        log_callback(f"    ❌ 设置IP地址失败: {result.stderr}")
                else:
                    if log_callback:
                        log_callback(f"    ✅ 设置IP地址为DHCP成功")
            
            # 设置DNS为DHCP
            result = subprocess.run([
                "netsh", "interface", "ip", "set", "dnsservers",
                adapter_name, "source=dhcp"
            ], capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode == 0:
                if log_callback:
                    log_callback(f"    ✅ 设置DNS为DHCP成功")
            else:
                if result.stderr:
                    if log_callback:
                        log_callback(f"    ❌ 设置DNS失败: {result.stderr}")
                else:
                    if log_callback:
                        log_callback(f"    ✅ 设置DNS为DHCP成功")
                        
        except Exception as e:
            if log_callback:
                log_callback(f"    ❌ 配置适配器时出错: {str(e)}")


def set_dns_to_dhcp(adapters, log_callback=None):
    """
    使用WMI设置DNS为DHCP
    
    Args:
        adapters: 适配器信息列表
        log_callback: 日志回调函数
    """
    if log_callback:
        log_callback("正在设置DNS为DHCP...")
    
    try:
        # 在子线程中初始化COM
        pythoncom.CoInitialize()
        
        c = wmi.WMI()
        
        for adapter_info in adapters:
            if log_callback:
                log_callback(f"  🌐 正在为适配器设置DNS: {adapter_info['name']}")
            for adapter in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                if adapter.Description == adapter_info['description']:
                    result = adapter.SetDNSServerSearchOrder()
                    if result[0] == 0:
                        if log_callback:
                            log_callback(f"    ✅ DNS设置为自动获取成功")
                    else:
                        if log_callback:
                            log_callback(f"    ❌ DNS设置为自动获取失败，错误代码: {result[0]}")
                    break
    except Exception as e:
        if log_callback:
            log_callback(f"❌ 设置DNS时出错: {str(e)}")
    finally:
        # 清理COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def refresh_network_config(log_callback=None):
    """
    刷新网络配置
    
    Args:
        log_callback: 日志回调函数
    """
    startupinfo = get_startupinfo()
    
    if log_callback:
        log_callback("正在刷新DNS缓存...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, startupinfo=startupinfo)
    
    if log_callback:
        log_callback("正在释放IP地址...")
    subprocess.run(["ipconfig", "/release"], capture_output=True, startupinfo=startupinfo)
    subprocess.run(["ipconfig", "/release"], capture_output=True, startupinfo=startupinfo)
    subprocess.run(["ipconfig", "/release"], capture_output=True, startupinfo=startupinfo)
    
    time.sleep(5)
    
    if log_callback:
        log_callback("正在重新获取IP地址...")
        log_callback("运行中，请耐心等待...")
        log_callback("部分网络环境复杂的电脑可能需要几分钟时间加载，请耐心等待...")
        log_callback("这是 Windows 的一个 Feature ，不是 Bug，请耐心等待")
    subprocess.run(["ipconfig", "/renew"], capture_output=True, startupinfo=startupinfo)
    
    if log_callback:
        log_callback("再次刷新DNS缓存...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, startupinfo=startupinfo)
    
    if log_callback:
        log_callback("重置Winsock...")
    subprocess.run(["netsh", "winsock", "reset"], capture_output=True, startupinfo=startupinfo)
    
    # 更新注册表设置，禁用代理
    if log_callback:
        log_callback("正在禁用代理设置...")
    try:
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "AutoConfigURL", "/t", "REG_SZ", "/d", "", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "UseAutoDetect", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "ProxyEnable", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "ProxyServer", "/d", "", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        if log_callback:
            log_callback("✅ 代理设置已禁用")
    except Exception as e:
        if log_callback:
            log_callback(f"❌ 禁用代理设置失败: {str(e)}")
    
    # 额外的DNS刷新
    if log_callback:
        log_callback("重复DNS刷新...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, startupinfo=startupinfo)
    subprocess.run(["netsh", "winsock", "reset"], capture_output=True, startupinfo=startupinfo)


def display_network_info(log_callback=None):
    """
    显示网络配置信息
    
    Args:
        log_callback: 日志回调函数
    """
    if log_callback:
        log_callback("——————当前网络配置——————")
    
    startupinfo = get_startupinfo()
    
    try:
        result = subprocess.run(
            ["ipconfig", "/all"], 
            capture_output=True, 
            text=True, 
            encoding='gb2312', 
            startupinfo=startupinfo
        )
        if result.returncode == 0:
            if log_callback:
                log_callback(result.stdout)
        else:
            if log_callback:
                log_callback("❌ 获取网络配置信息失败")
    except Exception as e:
        if log_callback:
            log_callback(f"❌ 显示网络信息时出错: {str(e)}")
    
    if log_callback:
        log_callback("————————————")


# def upload_usage(log_callback=None):
#     """
#     上传使用统计
    
#     Args:
#         log_callback: 日志回调函数
#     """
#     try:
#         data = {'software': USAGE_SOFTWARE_NAME}
#         response = requests.post(USAGE_API_URL, json=data)
#         if log_callback:
#             log_callback(f"内网测试结果: {response.status_code}")
#     except Exception as e:
#         if log_callback:
#             log_callback(f"上传使用统计失败: {str(e)}")

