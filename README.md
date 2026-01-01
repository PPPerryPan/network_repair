# Network Repair Tool

[中文版本 (Chinese Version)](README_zh.md)

A network repair tool developed based on Python and CustomTkinter that can automatically detect and fix common network connection issues.

## Features

- 📡 **Automatic Adapter Detection**: Supports both Ethernet and WLAN adapters
- 🔧 **One-Click Repair**: Automatically executes the complete network repair process
- 📊 **Real-time Progress Display**: Clearly shows repair steps and progress
- 📋 **Detailed Logs**: Records the complete repair process and results

## Repair Process

1. **Get Adapters**: Detect and obtain all available network adapters
2. **Reset Network Card**: Set IP address and DNS to DHCP
3. **Reset DNS**: Clear DNS cache and reset Winsock
4. **Reconnect Network**: Release and renew IP address
5. **Complete**: Display repair results and current network configuration

## Installation and Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Program**:
   ```bash
   python main.py
   ```
   Or directly double-click the compiled executable file

3. **The Program Will Automatically**:
   - Request administrator privileges
   - Start the repair process
   - Display repair progress and results

## Development Instructions

### Project Structure

```
network_repair/
├── main.py              # Main entry file
├── gui.py               # GUI interface module
├── network_utils.py     # Network operation utility module
├── admin_utils.py       # Administrator privileges utility module
├── constants.py         # Constants definition module
├── requirements.txt     # Dependencies list
├── icon.ico             # Application icon
├── network_repair.spec  # PyInstaller configuration file
├── README.md            # Project documentation (English)
└── README_zh.md         # Project documentation (Chinese)
```

### Main Module Functions

- **main.py**: Program main entry, handles administrator privileges requests and starts GUI
- **gui.py**: Implements modern GUI interface and repair process control
- **network_utils.py**: Provides core network repair functionality
- **admin_utils.py**: Checks and requests administrator privileges
- **constants.py**: Defines repair steps, theme colors and status configurations

## Statistics Feature (Optional)

If you need to count the number of program runs, follow these steps to enable:

1. Uncomment in `network_utils.py`:
   ```python
   from constants import USAGE_API_URL, USAGE_SOFTWARE_NAME
   # upload_usage(log_callback=self.log_message)
   ```

2. Uncomment in `gui.py`:
   ```python
   # upload_usage(log_callback=self.log_message)
   ```

3. Uncomment and configure API address in `constants.py`:
   ```python
   USAGE_API_URL = 'http://your-api-url.com/api/usage'
   USAGE_SOFTWARE_NAME = 'network_repair'
   ```

## Notes

- The program must run with administrator privileges, otherwise network repair operations cannot be performed
- The repair process may require restarting the network connection, please be patient
- Some complex network environments may require longer repair time
- If the repair fails, it may be due to TUN network card, network proxy or other non-local network issues
