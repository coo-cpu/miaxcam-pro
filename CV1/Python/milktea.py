import numpy as np
from pathlib import Path
import imageio.v2 as imageio

#确定图片地址和需要存放到的地址
base_dir = Path(__file__).parent
input_path = base_dir/ "Assets" / "milktea.jpg"
output_path = base_dir/ "Assets" / "milktea_stretched.jpg"

#读取一个jpg的数据格式，统一为RGB类型
img = imageio.imread(input_path)
#print(img)
if img.ndim == 2: #.ndm是Numpy的一个内置函数，用来确定数据的维度的
    img = np.stack([img, img, img], axis=-1)
elif img.shape[2] == 4:
	img = img[:, :, :3]
print(img.shape)
    

#将这个jpg的数据变成多维[W,H,RGB]数组，并且进行伸缩变换
img_tinted = img * np.array([1, 0.5, 0.9])





#将这个数组保存到指定的位置
