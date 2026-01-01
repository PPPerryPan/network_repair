### 如何打包
`pyinstaller --onefile --windowed --icon=icon.ico --name=network_repair --add-data "icon.ico;." --clean main.py`

### 如何统计运行次数
1. 再 gui 中取消注释 `upload_usage(log_callback=self.log_message)` 
2. 在 `constants.py` 中取消注释 `USAGE_API_URL` 和 `USAGE_SOFTWARE_NAME`，并设置为自己的 API 地址和软件名称
