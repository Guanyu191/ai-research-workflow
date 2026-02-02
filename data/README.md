# data/ 说明

推荐分层:  
- `raw/`: 原始数据 (不可变).  
- `processed/`: 处理后数据 (可再生).  
- `external/`: 第三方数据下载.  
- `cache/`: 临时缓存 (可随时清理).  

任何数据必须登记到 `REGISTRY.json`: 来源，版本，hash，生成命令，许可信息.  
