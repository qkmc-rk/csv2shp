# 克里金插值，把所有的shp文件都转换成raster存到数据库中，速度比较慢啊，卧槽，只有且行且试了

import arcpy  
import os
from tools.logger import Logger
import sys
import dotenv

sys.stdout = Logger(sys.stdout)  #  将输出记录到log
sys.stderr = Logger(sys.stderr)  # 将错误信息记录到log 

# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')

# 设置工作空间为你的地理数据库  
arcpy.env.workspace = os.path.join(root_dir, 'workspace/geodatabase.gdb')

out_raster_root = os.path.join(root_dir, 'workspace/geodatabase.gdb')
in_shp_root = os.path.join(root_dir, 'workspace/geodatabase.gdb')

# 计数器,计算代码运行时间
all = 0
now = 0

# 获取工作空间中的所有要素类列表  
datasets = arcpy.ListDatasets()
# 此处可以通过年份、数据类型（温度、湿度）进行筛选

# 筛选保留一下
# datasets = [item for item in datasets if 'temperature' in item]
datasets = [item for item in datasets if 'water' in item]
# datasets = [item for item in datasets if 'wind' in item]

print(datasets)
all = len(datasets)  # 所有需要处理的数量

# 开始遍历数据
for index, dataset in enumerate(datasets):
    # if index == 0:
    #     continue
    featureclasses = arcpy.ListFeatureClasses(None,None,datasets[index])
    for featureclass in featureclasses:
        # 执行栅格生成任务
        print('开始执行栅格生成任务,数据集: ', dataset, ', shp数据: ', featureclass, '......')
        out_raster_name = 'raster_' + featureclass
        in_shp = os.path.join(root_dir, 'workspace/geodatabase.gdb/' + dataset + '/' + featureclass)
        # D:\\VSCodeProjects\\csv2shp\\workspace\\geodatabase.gdb\\temperature2004\\raster_xxxx
        out_raster = os.path.join(os.path.join(out_raster_root,dataset), out_raster_name)
        print('shp:', in_shp)
        print('raster:', out_raster)
        field = 'RZGQW' # 如果是temperature的话就是这个
        if 'water' in dataset:
            field = 'LJJS'
        if 'wind' in dataset:
            field = 'JDFS'
        with arcpy.EnvManager(outputCoordinateSystem='PROJCS["Albers_105_25_47",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",105.0],PARAMETER["Standard_Parallel_1",25.0],PARAMETER["Standard_Parallel_2",47.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]', snapRaster=os.path.join(root_dir, 'workspace/snapraster/scdem_abs_250'), extent='96.0066486511672 25.3923347589358 109.616134432842 34.8546420069083 GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'):
            try:
                out_surface_raster = arcpy.sa.Kriging(in_shp, field, "Spherical # # # #", 250, "VARIABLE 12")
                out_surface_raster.save(out_raster)
                print('成功！执行栅格生成任务完成,数据集: ', dataset, ', shp数据: ', featureclass, '!!!')
            except Exception as e:
                # 记录下无法
                if not os.path.exists('./log/unable_do.txt'):
                    with open('./log/unable_do.txt', 'w') as file:
                        file.write('e\n')  # 写入字符串e并换行
                else:
                    with open('./log/unable_do.txt', 'a') as file:
                        file.write('e\n')  # 写入字符串e并换行
                print('无法估算半变异函数', e)
            now = now + 1
            print('---------------进度完成:',f"{round(now/all,2)}%--------------")

