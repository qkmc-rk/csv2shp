# 项目流程, 请参照该教程顺序进行执行，注意数据集存放的位置
---
# 流程
csv2shp --> kriging --> raster2tiff --> single_year_temperature
- 将代码中的路径等改好，创建好对应的文件夹，将csv数据放到合适的位置上。
- 修改代码中涉及的路径，默认是在D:/VSCodeProjects/csv2shp目录下。
- 执行create_gdb.py, 执行后在workspace下会生成gdb数据库文件
- 执行batch_csv2shp.py, 该文件将csv文件转换为shp并将shp数据存到gdb数据库中。
- 执行batch_kriging.py, 将所有shp进行插值, 插值后raster会存放在gdb数据库中。
- 执行batch_raster2tiff.py, 将raster数据全部转换为tiff文件存到某个本地目录中。
- 
---
## 将gdb中的raster保存为tiff图像
<!-- with arcpy.EnvManager(parallelProcessingFactor="100%"):
    arcpy.management.CopyRaster(r"D:\arcgisproProjects\export_to_raster\export_to_raster.gdb\Kriging_c1_11", r"D:\arcgisproProjects\export_to_raster\output\raster\c1", '', None, "3.4e+38", "NONE", "NONE", '', "NONE", "NONE", "TIFF", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE") -->

> 使用parallel处理会得到意料之外的结果
```
arcpy.management.CopyRaster(r"D:\VSCodeProjects\csv2shp\workspace\geodatabase.gdb\raster_te20041_4", r"C:\Users\Administrator\Documents\ArcGIS\Projects\MyProject4\raster_tif\aaa.tif", '', None, "3.4e+38", "NONE", "NONE", '', "NONE", "NONE", "TIFF", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
```

> conda装pytorch: conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia