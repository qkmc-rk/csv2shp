import torch

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


tensor = torch.tensor((0,0,0,0,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0))

print(max_one_serial(tensor))