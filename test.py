import torch

def rule_optimized(tensor):  
    # 确保输入tensor的维度和类型是正确的  
    assert tensor.dim() == 3 and tensor.size(0) == 365 and tensor.dtype == torch.float16  
    height, width = tensor.size(1), tensor.size(2)  
      
    # 创建一个365x1的阈值tensor，用于比较  
    threshold = torch.full((365,), 5, dtype=tensor.dtype, device=tensor.device)  
      
    # 检查每天降雨是否低于阈值，得到一个布尔tensor  
    is_below_threshold = tensor < threshold  
      
    # 计算每个位置连续低于阈值的降雨天数（通过计算累积和然后比较）  
    # 使用cumsum计算累积和，然后diff计算差值，diff(cumsum) > 0表示降雨值从低于阈值变为高于阈值  
    # 对结果取反得到连续低于阈值的区间，并计算其长度  
    # 使用roll将tensor向右移动，以模拟相邻位置的对比  
    consecutive_below_threshold = (  
        is_below_threshold.cumsum(dim=0, dtype=torch.int32) -   
        is_below_threshold.roll(1, dims=0).cumsum(dim=0, dtype=torch.int32).roll(1, dims=0)  
    )  
    # 注意：需要处理第一天的特殊情况，因为它没有前一天可以比较  
    consecutive_below_threshold[:, 0] = is_below_threshold[:, 0].int()  
      
    # 检查是否有任何连续区间长度达到或超过30天  
    has_30_consecutive_dry_days = (consecutive_below_threshold >= 30).any(dim=0)  
      
    # 将结果reshape回原始的空间维度  
    return has_30_consecutive_dry_days.view(height, width)  