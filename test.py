# 原始数据量（字节）  
data_bytes = 70096343240  
  
# 定义单位转换因子  
KB = 1024  # 1KB = 1024 bytes  
MB = KB * 1024  # 1MB = 1024 KB  
GB = MB * 1024  # 1GB = 1024 MB  
TB = GB * 1024  # 1TB = 1024 GB  
  
# 转换到KB  
data_KB = data_bytes / KB  
  
# 转换到MB  
data_MB = data_bytes / MB  
  
# 转换到GB  
data_GB = data_bytes / GB  
  
# 转换到TB  
data_TB = data_bytes / TB  
  
# 打印结果  
print(f"数据量相当于 {data_KB:.2f} KB")  
print(f"数据量相当于 {data_MB:.2f} MB")  
print(f"数据量相当于 {data_GB:.2f} GB")  
print(f"数据量相当于 {data_TB:.2f} TB")