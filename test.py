import rasterio
import os
import numpy as np

prefix = 'test'


outband = np.asarray([[1.,1.,1.,1.,1.],[1.,1.,1.,1.,1.],[1.,1.,1.,1.,1.],[1.,1.,1.,1.,1.],[1.,1.,1.,1.,1.]], dtype=np.float16)
outband = np.asarray(outband, np.float32)
root_dir = '.'
prefix_hot_tif = rasterio.open(
    os.path.join(root_dir, f'workspace/tiff_result/{prefix}_water.tif'),
    'w',
    driver='GTiff',
    height=outband.shape[0],
    width=outband.shape[1],
    count=1,
    dtype=outband.dtype
)
prefix_hot_tif.write(outband, 1)  # 将band1的值写入new_dataset的第一个波段