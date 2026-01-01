### 如需统计运行次数
1. 在 `network_utils.py` 中取消注释 `upload_usage(log_callback=self.log_message)`  `from constants import USAGE_API_URL, USAGE_SOFTWARE_NAME`
1. 再 `gui.py` 中取消注释 `upload_usage(log_callback=self.log_message)`  `upload_usage`
2. 在 `constants.py` 中取消注释 `USAGE_API_URL` 和 `USAGE_SOFTWARE_NAME`，并设置为自己的 API 地址和软件名称
