import arcpy
import os
import arcgisscripting
import dotenv

# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')
# 设置工作空间为你的地理数据库  
arcpy.env.workspace = os.path.join(root_dir, 'workspace/geodatabase.gdb')

raster_db = os.path.join(root_dir, 'workspace/geodatabase.gdb')
tiff_save_path = os.path.join(root_dir, 'workspace/tiff')

raster_list = arcpy.ListRasters()

existed_tiff = os.listdir(tiff_save_path) # 列表读入内存，直接在内存中检查文件是否存在，效率更高
tiff_types = ['wendu', 'jiangyu', 'fengsu']

raster_list = [item for item in raster_list if '2019' in item and ('20198' not in item or '20199' not in item)]

total = len(raster_list)
if len(raster_list) > 0:
    for index, raster_name in enumerate(raster_list):
        print('正在处理:', "{:.2%}".format(index/total), raster_name)
        # 跳过存在的文件
        if raster_list[index] in existed_tiff:
            print(raster_list[index], existed_tiff, '已经存在,不必再次生成...')
        raster = os.path.join(raster_db, raster_list[index])
        tiff_type = 'wendu'
        if 'te' in raster_list[index]:
            tiff_type = 'wendu'
        if 'wa' in raster_list[index]:
            tiff_type = 'jiangyu'
        if 'wi' in raster_list[index]:
            tiff_type = 'fengsu'
        
        output = os.path.join(tiff_save_path,tiff_type + '/' + raster_list[index] + '.tif')
        try:
            arcpy.management.CopyRaster(raster, output, '', None, "3.4e+38", "NONE", "NONE", '', "NONE", "NONE", "TIFF", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
        except arcgisscripting.ExecuteError as e:
            print(e)
            print('任务执行失败,文件信息-from:' + raster + '，to: ' + output)
            exit()
    print('全部处理完成...!')
