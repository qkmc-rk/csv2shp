# 克里金插值，把所有的shp文件都转换成raster存到数据库中，速度比较慢啊，卧槽，只有且行且试了

import arcpy  
import os
from tools.logger import Logger
import sys
import dotenv
# env arcgispro-python-clone
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
# 是否需要计算某些年份
datasets = [item for item in datasets if '2019' in item]

# 开始遍历数据
for index, dataset in enumerate(datasets):
    featureclasses = arcpy.ListFeatureClasses(None,None,datasets[index])
    all = len(featureclasses)
    now = 0
    for featureclass in featureclasses:
        # if '20198' in featureclass or '20199' in featureclass:
        # 执行栅格生成任务
        print('开始执行栅格生成任务,数据集: ', dataset, ', shp数据: ', featureclass, '......')
        out_raster_name = 'raster_' + featureclass
        in_shp = os.path.join(root_dir, 'workspace/geodatabase.gdb/' + dataset + '/' + featureclass)
        # D:\\VSCodeProjects\\csv2shp\\workspace\\geodatabase.gdb\\temperature2004\\raster_xxxx
        out_raster = os.path.join(out_raster_root, out_raster_name)
        print('shp:', in_shp)
        print('raster:', out_raster)
        field = 'RZGQW' # 如果是temperature的话就是这个
        if 'water' in dataset:
            field = 'LJJS'
        if 'wind' in dataset:
            field = 'JDFS'
        with arcpy.EnvManager(outputCoordinateSystem='PROJCS["Albers_105_25_47",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",105.0],PARAMETER["standard_parallel_1",25.0],PARAMETER["standard_parallel_2",47.0],PARAMETER["latitude_of_origin",0.0],UNIT["Meter",1.0]]', snapRaster=os.path.join(root_dir, 'workspace/snapraster/scdem_abs_250'), extent='-902802.594650205 2657392.81069733 463947.405349795 3755142.81069733 PROJCS["Albers_105_25_47",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",105.0],PARAMETER["standard_parallel_1",25.0],PARAMETER["standard_parallel_2",47.0],PARAMETER["latitude_of_origin",0.0],UNIT["Meter",1.0]]'):
            out_raster_file = arcpy.sa.Idw(in_shp, field, 250, 2, "VARIABLE 12", None)
            out_raster_file.save(out_raster)
            print('成功！执行栅格生成任务完成,数据集: ', dataset, ', shp数据: ', featureclass, '!!!')
            now = now + 1
            print('---------------进度完成:',f"{round(now/all,2)}%--------------")

# out_raster = arcpy.sa.Idw(r"D:\VSCodeProjects\csv2shp\workspace\geodatabase.gdb\water2007\wa20071_4", "LJJS", 0.0283333333319999, 2, "VARIABLE 12", None); 
# out_raster.save(r"D:\ArcGISProProjects\MyProject\MyProject.gdb\fdgdgdf")