import os
import hqx
import PIL.Image
import numpy as np

dr = './n/assets/graphics/items'
td = './assets/graphics/items'

os.makedirs(dr, exist_ok=True)

for l in os.listdir(td):
    if l.endswith('.png'):
        img = PIL.Image.open(os.path.join(td, l))
        width = img.width
        fi = 0

        sis = [32, 27, 18, 16]


        if width not in sis:
            print(f'Error: {l} has an invalid size')
            continue

        img = hqx.hq4x(img)

        img = img.convert("RGBA")
        # Get the image data as a NumPy array
        data = np.array(img)

        # Find all pixels that are black (RGB value (0,0,0))
        # We compare only the first three channels (R, G, B)
        black_pixels_mask = np.all(data[:, :, :3] == [0, 0, 0], axis=-1)

        # Set the alpha channel of black pixels to 0 (transparent)
        data[black_pixels_mask, 3] = 0

        # Create a new PIL Image from the modified NumPy array
        new_img = PIL.Image.fromarray(data)
        new_img.save(os.path.join(dr, l))