import arcpy
import os

def create_directories_if_not_exist(base_dir, subdirs):  
    for subdir in subdirs:  
        subdir_path = os.path.join(base_dir, subdir)  
        if not os.path.exists(subdir_path):  
            os.makedirs(subdir_path)  
            print(f"Created directory: {subdir_path}")  
  
def check_and_create_directories():  
    current_dir = os.getcwd()  # 获取当前工作目录  
  
    # 拼接完整的路径  
    workspace_path = os.path.join(current_dir, 'workspace')  
    npy_path = os.path.join(current_dir, 'npy')
  
    # 定义workspace目录下的子目录列表  
    workspace_subdirs = ['data_weather_by_day', 'range', 'snapraster', 'tiff', 'tiff_result']  
    tiff_subdirs = ['wendu', 'jiangyu', 'fengsu']
    # 检查目录是否存在  
    workspace_exists = os.path.isdir(workspace_path)  
    npy_exists = os.path.isdir(npy_path)  
  
    # 输出结果  
    if workspace_exists:  
        print("'workspace' 目录存在。")  
        # 检查并创建workspace目录下的子目录  
        create_directories_if_not_exist(workspace_path, workspace_subdirs)
        # 检查并创建tiff下的子目录
        create_directories_if_not_exist(os.path.join(workspace_path,workspace_subdirs[3]), tiff_subdirs)
    else:  
        # 如果workspace目录不存在，则创建它  
        os.makedirs(workspace_path)
        print("'workspace' 目录已创建。")  
        # 接着创建workspace目录下的子目录  
        create_directories_if_not_exist(workspace_path, workspace_subdirs)
  
    if npy_exists:  
        print("'npy' 目录存在。")  
    else:  
        # 如果npy目录不存在，可以选择创建它，这里根据你的需求决定是否添加以下代码  
        os.makedirs(npy_path)  
        print("'npy' 目录不存在。")  
        print("'npy' 目录已创建。")  
  
# 第一步调用函数检查并创建目录  
check_and_create_directories()

# 设置工作空间和GDB数据库路径  
workspace_dir = './workspace'  
gdb_path = os.path.join(workspace_dir, 'geodatabase.gdb')  
  
# 创建一个新的文件地理数据库  
if not arcpy.Exists(gdb_path):  
    arcpy.CreateFileGDB_management(workspace_dir, 'geodatabase')  
  
# 定义要创建的子目录列表  
subdirectories = ['temperature', 'water', 'wind']  
years = ['2004', '2007', '2010', '2013', '2016', '2019', '2022']  
  
spatial_reference = arcpy.SpatialReference(4326)
# 遍历子目录列表  
for subdir in subdirectories:  
    for year in years:
        arcpy.management.CreateFeatureDataset(gdb_path, subdir + year, spatial_reference)
  
print('File geodatabase and subdirectories created successfully.')