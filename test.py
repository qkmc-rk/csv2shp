flag = 0
current_year = '2005'

# 开始遍历数据
for index, dataset in enumerate(['2001','2002','2003','2004','2005','2006','2007']):
    if not flag and current_year not in dataset:
        continue
    flag = 1
    print('处理年份:', dataset)