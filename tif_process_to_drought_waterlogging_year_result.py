# 读入n个tif文件, 然后将其组成 (x * y * n) 的三维矩阵
# 然后取出 (i, j, , 0:m)进行判断
# env python38-2
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


# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')
tif_data_dir = os.getenv('tif_data_dir')

def max_one_serial(tensor):
    #  这里传入的tensor是一个向量
    tensor_padded = torch.cat(
        [torch.tensor([0], dtype=torch.uint8), (tensor > 0).float(), torch.tensor([0], dtype=torch.uint8)])
    # Find start and end indices of sequences
    diff = tensor_padded[1:] - tensor_padded[:-1]
    starts = (diff > 0).nonzero()[:, 0].tolist()  # 注意：这里我们使用了 [:, 0] 来选择列，但这与 .squeeze() 类似（当且仅当为二维时）
    ends = (diff < 0).nonzero()[:, 0].tolist()    # 同样的，这里也使用了 [:, 0]  
    # Identify sequences meeting criteria
    count = sum(1 for start, end in zip(starts, ends) if end - start >= 30)
    return 1 if count >= 1 else 0
    

def rule(tensor):
    # 确保输入tensor的维度和类型是正确的  
    height, width = tensor.size(1), tensor.size(2)  # 4391   5467
    threshold = 5.  # 阈值
    result = torch.zeros((height, width), dtype=tensor.dtype)
    tmp = torch.zeros(tensor.shape[0], dtype=torch.float16)
    for row in trange(height):
        for col in range(width):
            # 处理 [365]的数据
            tmp = tensor[ : ,row, col]
            tmp = (tmp < threshold).to(torch.int8)
            result[row, col] = max_one_serial(tmp)
    return result.numpy()

# 定义一个函数来从文件名中提取日期  
def extract_date_from_filename(filename):
    basename = os.path.basename(filename)
    year_month_day = basename[len('raster_wa'):-4]
    parts = year_month_day.split('_')
    year = int(parts[0][:4])
    month = int(parts[0][4:])
    day = int(parts[1])
    return datetime(year, month, day)

file_num = -1  # 测试期间限制读入的数据数量,若不限制则改为-1
# 模拟的TIFF文件路径
tiff_dir = os.path.join(tif_data_dir, 'jiangyu')  # 您的TIFF文件所在的目录   路径中不能包含te wi wa字符
if 'te' in tiff_dir or 'wi' in tiff_dir or 'wa' in tiff_dir:
    print('路径中不能包含关键字te, wi, wa')
    exit()

# 获取所有以'raster_wa'开头的TIFF文件
tiff_files = glob.glob(os.path.join(tiff_dir, 'raster_wa*.tif'))
tiff_files_const = tiff_files
data_year = ['2004', '2007', '2010', '2013', '2016', '2019', '2022'] # 2004,2007,2010,2013,2016,2019,2022

height, width = 4391, 5467  #

for year in data_year:
    print('开始处理,年份:', year, ', 类型数据:wa')
    prefix = 'wa' + str(year)
    tiff_files = [item for item in tiff_files_const if prefix in item]
    print('处理列表:',year,  len(tiff_files))
    # 空数据直接跳过
    if len(tiff_files) == 0:
        continue
    sorted_files = sorted(tiff_files, key=extract_date_from_filename)
    sorted_files = sorted_files[:file_num]  # 计算一年365个数据
    # 要存储的尺寸
    images_3d = np.empty((len(sorted_files), height, width), dtype=np.float16)  # 初始化三维数组
    # 保留一些有用的信息,坐标信息等
    t = rasterio.open(sorted_files[0])
    transform, crs = t.transform, t.crs

    print('开始加载数据...')
    if os.path.exists(f'./npy/{prefix}_water_images_3d.npy'):
        print('npy文件已生成...开始加载...')
        images_3d = np.load(f'./npy/{prefix}_water_images_3d.npy')
    else:
        print('npy文件不存在...开始读取并生成...')
        # 将所有的tif全部读取进来
        for index, file in enumerate(sorted_files):
            with rasterio.open(file) as src:
                print(index, ', ', file)
                image_data = src.read(1)  # 读取第一个波段
                images_3d[index, :, :] = image_data
        np.save(f'./npy/{prefix}_water_images_3d.npy', images_3d)
    print('数据加载完成...')
    print('开始将numpy.ndarray转换为tensor...')
    images_3d = torch.from_numpy(images_3d)
    print('tensor转换完成...\n开始计算...')

    outband = rule(images_3d)   # result应该是一个(x*y的图像)
    outband = np.asarray(outband, dtype=np.float32)
    # outband.reshape(d, w, h)
    # 最后生成新的栅格并导出
    prefix_hot_tif = rasterio.open(
        os.path.join(root_dir, f'workspace/tiff_result/{prefix}_water.tif'),
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