import arcpy  
import os
import dotenv

# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')

# 设置工作空间和GDB数据库路径
workspace_sub_child_dir = ['2007','2010','2013','2016','2019','2022']
# workspace_sub_child_dir = ['2004'] 
# workspace_parent_parerent_dir = ['temperature']
workspace_parent_parerent_dir = ['temperature', 'water', 'wind']
FIELD_DIC = {  
    'temperature': 'RZGQW',  
    'water': 'LJJS',  
    'wind': 'JDFS'  
}

# 该变量永久不变，用于保存workspace_dir的初始状态, per = permernate永久的
workspace_dir_per = os.path.join(root_dir, 'workspace/data_weather_by_day')
# 该变量代码中会改变
workspace_dir = os.path.join(root_dir, 'workspace/data_weather_by_day')
gdb_path_per = os.path.join(root_dir, 'workspace/geodatabase.gdb')
gdb_path = os.path.join(root_dir, 'workspace/geodatabase.gdb')

# 设置t代表temperature w代表water wi代表wind
csv_temperature_type = 'te'
csv_water_type = 'wa'
csv_wind_type = 'wi'

  
# 确保GDB存在
if not arcpy.Exists(gdb_path):
    arcpy.CreateFileGDB_management(os.path.dirname(gdb_path), os.path.basename(gdb_path))


# 遍历每个指标
for parent_dir in workspace_parent_parerent_dir:
    # 遍历每个年份
    for child_dir in workspace_sub_child_dir:
        #重置一下目标目录
        workspace_dir = workspace_dir_per
        gdb_path = gdb_path_per
        workspace_dir = os.path.join(workspace_dir, parent_dir)
        workspace_dir = os.path.join(workspace_dir, child_dir)
        # 遍历指定目录下的所有CSV文件
        for root, dirs, files in os.walk(workspace_dir):  
            for file in files:  
                if file.lower().endswith('.csv'):  
                    # ----------------------------测试阶段: 如果索引超过5就停止了-------------------------------------
                    # if int((file.lower().split("_")[1]).split(".")[0]) > 5:
                    #     continue
                    # 构造CSV文件的完整路径  
                    input_csv = os.path.join(root, file)
                    
                    # 提取CSV文件名（不含扩展名），并作为SHP文件的名称
                    if(parent_dir == 'temperature'):
                        shp_name = csv_temperature_type + child_dir + os.path.splitext(file)[0]
                    elif(parent_dir == 'water'):
                        shp_name = csv_water_type + child_dir + os.path.splitext(file)[0]
                    elif(parent_dir == 'wind'):
                        shp_name = csv_wind_type + child_dir + os.path.splitext(file)[0]
                    else:
                        shp_name = 'unknown' + child_dir + os.path.splitext(file)[0]
                    # 构造SHP文件的完整路径（在GDB中） 
                    gdb_path = os.path.join(gdb_path, parent_dir + child_dir) 
                    output_shp = os.path.join(gdb_path, shp_name)
                    gdb_path = gdb_path_per
                    
                    # 调用XYTableToPoint工具  temperature-RZGQW  water-LJJS   wind-JDFS
                    # 在导入点后，生成shp时要转换成自定义的abs_250坐标系,方便后面的插值等操作
                    with arcpy.EnvManager(outputCoordinateSystem='PROJCS["Albers_105_25_47",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",105.0],PARAMETER["Standard_Parallel_1",25.0],PARAMETER["Standard_Parallel_2",47.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'):
                        arcpy.management.XYTableToPoint(input_csv, output_shp, "X", "Y", FIELD_DIC.get(parent_dir, 'unknown'), 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],VERTCS["WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')
                    print(f'Converted {input_csv} to {output_shp} successfully!')  
        
print('All CSV files converted to SHP successfully!')