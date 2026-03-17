import numpy as np
from pathlib import Path
import imageio.v2 as imageio
from PIL import Image

# Read a JPEG image into a numpy array
base_dir = Path(__file__).resolve().parent
input_path = base_dir / 'Assets' / 'bluecat.jpg'
output_path = base_dir / 'Assets' / 'bluecat_tinted.jpg'

img = imageio.imread(input_path)
if img.ndim == 2:
	img = np.stack([img, img, img], axis=-1)
elif img.shape[2] == 4:
	img = img[:, :, :3]

print(img.dtype, img.shape)

# Tint
img_tinted = img * np.array([1, 0.95, 0.9])
img_tinted = np.clip(img_tinted, 0, 255).astype(np.uint8)

# Resize to 300x300
img_tinted = np.array(Image.fromarray(img_tinted).resize((300, 300)))

# Save
imageio.imwrite(output_path, img_tinted)