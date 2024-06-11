def day_of_year(month, day):  
    """  
    计算给定月日的年内天数（0-364）  
    """  
    # 每个月的天数（非闰年）  
    days_in_month_leap = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]   # leap

    
    # 累加前几个月的天数  
    total_days_leap = sum(days_in_month_leap[:month-1])  
      
    # 如果月份大于2且是闰年，并且日期在2月29日之前，则天数加1  
    if month > 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) and day <= 29:  
        total_days_leap += 1  
      
    # 加上本月的天数  
    total_days += day - 1  # 减1是因为我们是从0开始计数的  
      
    return total_days  
  
# 假设所有日期都是非闰年的，如果有闰年情况，需要传入对应的年份作为参数  
year = 2023  # 非闰年示例  
  
def convert_to_day_numbers(date_dict):  
    """  
    将给定的日期字典转换为数字编号的字典  
    """  
    converted_dict = {}  
    for key, value in date_dict.items():  
        start, end = key.split('-')  
        start_month, start_day = map(int, start.split('.'))  
        end_month, end_day = map(int, end.split('.'))  
          
        start_day_num = day_of_year(start_month, start_day)  
        end_day_num = day_of_year(end_month, end_day)  
          
        converted_dict[f"{start_day_num}-{end_day_num}"] = value  
      
    return converted_dict  
  
corn_dict = {"4.1-5.31": 10, "6.1-6.30": 18, "6.11-6.30": 10, "7.1-7.31": 16}  
soya_dict = {"3.1-4.31": 10, "5.1-5.20": 17, "5.21-6.30": 15, "7.1-7.31": 10, "8.1-8.20": 17, "8.21-9.30": 15, "10.1-10.10": 10}  
rice_dict = {"5.10-7.15": 10, "7.16-8.10": 17, "8.11-9.10": 19, "9.11-9.20": 15, "9.21-10.10": 10}  
  
corn_dict_converted = convert_to_day_numbers(corn_dict)  
soya_dict_converted = convert_to_day_numbers(soya_dict)  # 注意：4月没有31天，这里可能需要修正  
rice_dict_converted = convert_to_day_numbers(rice_dict)  
  
print(corn_dict_converted)  
print(soya_dict_converted)  # 这里的'4.31'需要修正为有效的日期  
print(rice_dict_converted)