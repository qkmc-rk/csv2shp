# 读入n个tif文件, 然后将其组成 (x * y * n) 的三维矩阵
# 然后取出 (i, j, , 0:m)进行判断

import os
import glob
from datetime import datetime
import numpy as np
import rasterio
import torch
from tqdm import trange
import dotenv
from tools.logger import Logger
import sys

sys.stdout = Logger(sys.stdout)  #  将输出记录到log
sys.stderr = Logger(sys.stderr)  # 将错误信息记录到log 


# 获取项目根路径
dotenv.load_dotenv('.env')
root_dir = os.getenv('root_dir')

def rule_1(tensor):
    #  这里传入的tensor是一个向量
    # 规则1 如果366个数据中有超过30都大于0，则返回1，否则返回0
    count_greater_0 = (tensor > 0).sum().item()
    return 1 if count_greater_0 >= 30 else 0

def rule_2(tensor):
    #  这里传入的tensor是一个向量
    # 规则2 首先找到大于0的序列，然后判断序列的长度，如果长度大于2，则该序列贡献一个高温过程，如果序列长度等于2且有一个值为2则贡献一个高温过程
    #  如果高温过程大于等于3个，则返回1否则返回0
    tensor_padded = torch.cat(
        [torch.tensor([0], dtype=torch.uint8), (tensor > 0).float(), torch.tensor([0], dtype=torch.uint8)])
    # Find start and end indices of sequences
    diff = tensor_padded[1:] - tensor_padded[:-1]
    starts = (diff > 0).nonzero()[:, 0].tolist()  # 注意：这里我们使用了 [:, 0] 来选择列，但这与 .squeeze() 类似（当且仅当为二维时）
    ends = (diff < 0).nonzero()[:, 0].tolist()    # 同样的，这里也使用了 [:, 0]  
    # Identify sequences meeting criteria
    count = sum(1 for start, end in zip(starts, ends) if end - start > 2 or (end - start == 2 and (tensor[start:end] == 2).any()))
    return 1 if count >= 3 else 0
def rule(tensor):
    # 怎么样才能在GPU上面运算呢
    # device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    rs = np.zeros((tensor.shape[1], tensor.shape[2]), dtype=np.int8)
    for i in trange(tensor.shape[1]):
        for j in range(tensor.shape[2]):
            rs1 = rule_1(tensor[:, i, j])
            rs2 = rule_2(tensor[:, i, j])
            # rs[i, j] = 1 if rs1 + rs2 > 0 else 0
            if (rs1 + rs2) > 0:
                rs[i, j] = 1
            else:
                rs[i, j] = 0
    return rs


# 定义一个函数来从文件名中提取日期
def extract_date_from_filename(filename):
    # 20071_1
    # 201012_4
    # 20041_20
    # 200412_20
    basename = os.path.basename(filename)
    year_month_day = basename[len('raster_te'):-4]
    # Split using the underscore
    parts = year_month_day.split('_')
    # If the second part is of length 2, then it's in the month_day format
    year = int(parts[0][:4])
    month = int(parts[0][4:])
    day = int(parts[1])
    # print(year, month, day)
    return datetime(year, month, day)

file_num = -1  # 测试期间限制读入的数据数量,若不限制则改为-1
# 模拟的TIFF文件路径
tiff_dir = os.path.join(root_dir, '/tiffdata/wendu')  # 您的TIFF文件所在的目录   路径中不能包含te wi wa字符
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
        del t # 清理不需要的大文件
        print('开始加载数据...')
        if os.path.exists(f'./npy/{prefix}_images_3d.npy'):
            print('npy文件已生成...开始加载...')
            images_3d = np.load(f'./npy/{prefix}_images_3d.npy')
        else:
            print('npy文件不存在...开始读取并生成...')
            # 将所有的tif全部读取进来
            for index, file in enumerate(sorted_files):
                with rasterio.open(file) as src:
                    image_data = src.read(1)  # 读取第一个波段
                    image_data = image_data.astype(np.int8)  # 转换数据类型为int8
                    images_3d[index, :, :] = image_data
            np.save(f'./npy/{prefix}_images_3d.npy', images_3d)
        # print(images_3d.shape)  # (366, 4391, 5467)
        print('数据加载完成...')
        print('开始转换tensor...')
        tensor = torch.tensor(images_3d)  # 转换为tensor方便计算
        del images_3d # 清理不需要的大文件
        print('tensor转换完毕...')

        # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # tensor = tensor.to(device)

        # 首先将tensor中的数据变成0,1,2
        print('开始转换为012值...')
        tensor = torch.where(tensor < 35, 0, tensor)
        tensor = torch.where(tensor >= 38, 2, tensor)
        tensor = torch.where((tensor >= 35) & (tensor < 38), 1, tensor)
        print('开始计算tensor...')
        outband = rule(tensor)   # result应该是一个(x*y的图像)
        print('最终结果出来了...', outband)
        # 最后生成新的栅格并导出
        prefix_hot_tif = rasterio.open(
            os.path.join(root_dir, 'workspace/tiff_result/{prefix}_hot_tif.tif'),
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