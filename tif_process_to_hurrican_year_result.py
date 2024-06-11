# 读入n个tif文件, 然后将其组成 (x * y * n) 的三维矩阵
# 然后取出 (i, j, , 0:m)进行判断

import os
import glob
from datetime import datetime
import numpy as np
import rasterio
import torch.types
from tqdm import trange
from tools.logger import Logger
import sys
import dotenv
import torch

sys.stdout = Logger(sys.stdout)  #  将输出记录到log
sys.stderr = Logger(sys.stderr)  # 将错误信息记录到log 

big_wind = 17
huge_wind = 24.5

# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')
tif_data_dir = os.getenv('tif_data_dir')

def rule(tensor):
    # tensor 大小为(365, 4000+, 5000+)
    # 需要遍历dim0，求出1，2的个数
    result = np.zeros((tensor.shape[1], tensor.shape[2]), dtype=np.int8)
    for i in trange(tensor.shape[1]):
        for j in range(tensor.shape[2]):
            big_wind = (tensor[:,i,j] == 1).sum(dim=0)
            huge_wind = (tensor[:,i,j] == 2).sum(dim=0)
            if(big_wind >= 30 or huge_wind >= 1):
                result[i, j] = 1
    return result


# 定义一个函数来从文件名中提取日期  
def extract_date_from_filename(filename):
    basename = os.path.basename(filename)
    year_month_day = basename[len('raster_wi'):-4]
    parts = year_month_day.split('_')
    year = int(parts[0][:4])
    month = int(parts[0][4:])
    day = int(parts[1])
    return datetime(year, month, day)

file_num = -1  # 测试期间限制读入的数据数量,若不限制则改为-1
# 模拟的TIFF文件路径
tiff_dir = os.path.join(tif_data_dir, 'fengsu')  # 您的TIFF文件所在的目录   路径中不能包含te wi wa字符
if 'te' in tiff_dir or 'wi' in tiff_dir or 'wa' in tiff_dir:
    print('路径中不能包含关键字te, wi, wa')
    exit()

# 获取所有以'raster_wi'开头的TIFF文件  
tiff_files = glob.glob(os.path.join(tiff_dir, 'raster_wi*.tif'))
tiff_files_const = tiff_files

data_year = ['2004', '2007', '2010', '2013', '2016', '2019', '2022'] # 2004,2007,2010,2013,2016,2019,2022

height, width = 4391, 5467  # 

for year in data_year:
    print('开始处理,年份:', year, ', 类型数据:wi')
    prefix = 'wi' + str(year)
    tiff_files = [item for item in tiff_files_const if 'wi' in item and year in item]
    print('处理列表:', tiff_files)
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
    if os.path.exists(f'./npy/{prefix}_wind_images_3d.npy'):
        print('npy文件已生成...开始加载...')
        images_3d = np.load(f'./npy/{prefix}_wind_images_3d.npy')
    else:
        print('npy文件不存在...开始读取并生成...')
        # 将所有的tif全部读取进来
        for index, file in enumerate(sorted_files):
            with rasterio.open(file) as src:
                print(index, ', ', file)
                image_data = src.read(1)  # 读取第一个波段
                # 创建一个新的数组来存储结果（或者你可以直接修改 image_data）
                new_image_data = np.zeros_like(image_data, dtype=np.int8)  # 使用 int8 类型来存储 0, 1, 2
                # 使用条件索引来更新 new_image_data
                new_image_data[(image_data >= 17) & (image_data < 24.5)] = 1
                new_image_data[image_data >= 24.5] = 2
                images_3d[index, :, :] = new_image_data
        np.save(f'./npy/{prefix}_wind_images_3d.npy', images_3d)
    print('数据加载完成...')
    print('开始将numpy.ndarray转换为tensor...')
    images_3d = torch.from_numpy(images_3d)
    print('tensor转换完成...\n开始计算...')

    # 计算大于 17 的元素的个数
    # count_greater_than_17 = (images_3d == 1).sum(dim=0)
    # # 计算大于 24.5 的元素的个数  
    # count_greater_than_24_5 = (images_3d == 2).sum(dim=0)
    # # 如果每个值大于等于30则置1，否则置0  
    # count_greater_than_17_thresholded = (count_greater_than_17 >= 30)
    # count_greater_than_24_5_thresholded = (count_greater_than_24_5 >= 1)
    # # 合并两个张量，只要这两个tensor对应的位置有一个是1则为1，否则为0  
    # outband = torch.logical_or(count_greater_than_17_thresholded, count_greater_than_24_5_thresholded)

    outband = rule(images_3d)   # result应该是一个(x*y的图像)
    # outband.reshape(d, w, h)
    # 最后生成新的栅格并导出
    prefix_hot_tif = rasterio.open(
        os.path.join(root_dir, f'workspace/tiff_result/{prefix}_wind.tif'),
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