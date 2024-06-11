# 读入n个tif文件, 然后将其组成 (x * y * n) 的三维矩阵
# 然后取出 (i, j, , 0:m)进行判断

import os
import glob
from datetime import datetime
import numpy as np
import rasterio
from tqdm import trange
from tools.logger import Logger
import sys
import dotenv

sys.stdout = Logger(sys.stdout)  #  将输出记录到log
sys.stderr = Logger(sys.stderr)  # 将错误信息记录到log 

corn_dict = {'90-150': 10, '151-180': 18, '161-180': 10, '181-211': 16}
soya_dict = {'59-120': 10, '120-139': 17, '140-180': 15, '181-211': 10, '212-231': 17, '232-272': 15, '273-282': 10}
rice_dict = {'129-195': 10, '196-221': 17, '222-252': 19, '253-262': 15, '263-282': 10}
corn_cold_damage = False
soya_cold_damage = False
rice_cold_damage = False

# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')
tif_data_dir = os.getenv('tif_data_dir')

def rule(nparray):  
    # 定义冷害规则表  注意，比如90代表4月1日，因为 1月31 2月28 3月31 4月1日久刚好90天
    result = np.zeros((nparray.shape[1], nparray.shape[2]), dtype=np.int8)
    for ii in trange(nparray.shape[1]):
        for jj in range(nparray.shape[2]):
            subarray = nparray[:, ii, jj]
            for k,v in corn_dict.items():
                for i in range(int(k.split('-')[0]), int(k.split('-')[1])):
                    if all(subarray[i:i+3] <= v):
                        corn_cold_damage = True
            for k,v in soya_dict.items():
                for i in range(int(k.split('-')[0]), int(k.split('-')[1])):
                    if all(subarray[i:i+3] <= v):
                        soya_cold_damage = True
            for k,v in rice_dict.items():
                for i in range(int(k.split('-')[0]), int(k.split('-')[1])):
                    if all(subarray[i:i+3] <= v):
                        rice_cold_damage = True
            if(corn_cold_damage or soya_cold_damage or rice_cold_damage):
                result[ii, jj] = 1
            else:
                result[ii, jj] = 0
            # 用完以后要将冷害flag归位
            corn_cold_damage = False
            soya_cold_damage = False
            rice_cold_damage = False
            
    return result

# 定义一个函数来从文件名中提取日期  
def extract_date_from_filename(filename):
    basename = os.path.basename(filename)
    year_month_day = basename[len('raster_te'):-4]
    parts = year_month_day.split('_')
    year = int(parts[0][:4])
    month = int(parts[0][4:])
    day = int(parts[1])
    return datetime(year, month, day)

file_num = -1  # 测试期间限制读入的数据数量,若不限制则改为-1
# 模拟的TIFF文件路径
tiff_dir = os.path.join(tif_data_dir, 'wendu')  # 您的TIFF文件所在的目录   路径中不能包含te wi wa字符
if 'te' in tiff_dir or 'wi' in tiff_dir or 'wa' in tiff_dir:
    print('路径中不能包含关键字te, wi, wa')
    exit()

# 获取所有以'raster_te'开头的TIFF文件  
tiff_files = glob.glob(os.path.join(tiff_dir, 'raster_te*.tif'))
tiff_files_const = tiff_files

##################################################
#            在此处对数据进行过滤                   #
#        看是要计算什么,temperature, wind, water   #
#           然后看看是要计算哪一年                  #
##################################################
data_type = ['te', 'wi', 'wa']   # temperature, wind, water
data_year = ['2004', '2007', '2010', '2013', '2016', '2019', '2022'] # 2004,2007,2010,2013,2016,2019,2022

height, width = 4391, 5467  # 

for year in data_year:
    for type in data_type:
        print('开始处理,年份:', year, ', 类型数据:', type)
        prefix = type + str(year)
        tiff_files = [item for item in tiff_files_const if type in item and year in item]
        # 空数据直接跳过
        if len(tiff_files) == 0:
            continue
        sorted_files = sorted(tiff_files, key=extract_date_from_filename)
        sorted_files = sorted_files[:file_num]  # 计算一年365个数据
        # 要存储的尺寸
        images_3d = np.empty((len(sorted_files), height, width), dtype=np.int8)  # 初始化三维数组

        # 保留一些有用的信息,坐标信息等
        t = rasterio.open(sorted_files[0])
        transform, crs = t.transform, t.crs

        print('开始加载数据...')
        if os.path.exists(f'./npy/{prefix}_cold_images_3d.npy'):
            print('npy文件已生成...开始加载...')
            images_3d = np.load(f'./npy/{prefix}_cold_images_3d.npy')
        else:
            print('npy文件不存在...开始读取并生成...')
            # 将所有的tif全部读取进来
            for index, file in enumerate(sorted_files):
                with rasterio.open(file) as src:
                    image_data = src.read(1)  # 读取第一个波段
                    image_data = image_data.astype(np.int8)  # 转换数据类型为int8
                    images_3d[index, :, :] = image_data
            np.save(f'./npy/{prefix}_cold_images_3d.npy', images_3d)
        # print(images_3d.shape)  # (366, 4391, 5467)
        print('数据加载完成...')
        print('开始将numpy.ndarray转换为tensor...')
        # d = images_3d.shape[0]
        # w = images_3d.shape[1]
        # h = images_3d.shape[2]
        # images_3d = images_3d.reshape(d, 1, w * h)
        outband = rule(images_3d)   # result应该是一个(x*y的图像)
        # outband.reshape(d, w, h)
        # 最后生成新的栅格并导出
        prefix_hot_tif = rasterio.open(
            os.path.join(root_dir, f'workspace/tiff_result/{prefix}_cold_tif.tif'),
            'w',
            driver='GTiff',
            height=outband.shape[0],
            width=outband.shape[1],
            count=1,
            dtype=outband.dtype,
            crs=crs,  # ds.crs
            transform=transform,
        )
        prefix_hot_tif.write(outband, 1)  # 将band1的值写入new_dataset的第一个波段
print('congraduation!! everything down!!')
exit()