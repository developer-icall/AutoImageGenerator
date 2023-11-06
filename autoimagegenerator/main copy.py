import base64
import json
from urllib import request
from PIL import Image, ImageOps
from io import BytesIO
import os

base_url = "http://localhost:7860"

url = base_url  + "/sdapi/v1/options"

path = os.getcwd()
print(path)

image = Image.open("./autoimagegenerator/images/input/test-image.jpg")
mask = Image.open("./autoimagegenerator/images/input/test-mask.png")

SHORTEST_TARGET = 512

def resize(image):
    width, height = image.size
    if width < height:
        new_width = SHORTEST_TARGET
        new_height = int(new_width / width * height)
    else:
        new_height = SHORTEST_TARGET
        new_width = int(new_height / height * width)

    return image.resize((new_width, new_height))

image = resize(image)
mask = resize(mask)

buffered = BytesIO()
image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

buffered = BytesIO()
mask.save(buffered, format="PNG")
mask_str = base64.b64encode(buffered.getvalue()).decode()

data = {
  "init_images": [img_str], # 入力画像
  "resize_mode": 0,
  "denoising_strength": 0.75,
  "image_cfg_scale": 0,
  "mask": mask_str, # マスク画像
  "mask_blur": 4,
  "inpainting_fill": 1, # ※1
  "inpaint_full_res": False,
  "inpaint_full_res_padding": 0,
  "inpainting_mask_invert": 0,
  "initial_noise_multiplier": 0,
  "prompt": "beautiful pink flower",
  "negative_prompt": "",
  "styles": [
  ],
  "seed": -1,
  "subseed": -1,
  "subseed_strength": 0,
  "seed_resize_from_h": -1,
  "seed_resize_from_w": -1,
  "sampler_name": "Euler", # ※2
  "batch_size": 1,
  "n_iter": 1,
  "steps": 50, # ※3
  "cfg_scale": 7,
  "width": image.width,
  "height": image.height,
  "restore_faces": False,
  "tiling": False,
  "do_not_save_samples": False,
  "do_not_save_grid": False,
  "eta": 0,
  "s_min_uncond": 0,
  "s_churn": 0,
  "s_tmax": 0,
  "s_tmin": 0,
  "s_noise": 1,
  "override_settings": {},
  "override_settings_restore_afterwards": True,
  "script_args": [],
  "sampler_index": "Euler", # ※2
  "include_init_images": False,
  "script_name": "",
  "send_images": True,
  "save_images": False,
  "alwayson_scripts": {} # 後で使います
}

cn_unit = {
    "input_image": img_str, # ※1
    "module": "canny",
    "model": "control_canny-fp16 [e3fe7712]",
    "weight": 1.0,
    "mask": "", # ※2
    "resize_mode": "Scale to Fit (Inner Fit)",
    "lowvram": False,
    "processor_res": SHORTEST_TARGET,
    "threshold_a": 0.0,
    "threshold_b": 255.0,
    "guidance": 1.0,
    "guidance_start": 0.0,
    "guidance_end": 1.0,
    "guessmode": False,
    "control_mode": 0, # ※3
}

cn_args = {
    "alwayson_scripts": {
        "ControlNet": {
            "args": [
                cn_unit,
                {"enabled":False},
                {"enabled":False},
                {"enabled":False},
            ]
        }
    }
}
data.update(cn_args)

url = base_url  + "/sdapi/v1/img2img"
headers = {
    "Content-Type": "application/json"
}

with request.urlopen(request.Request(url, json.dumps(data).encode(), headers)) as res:
    body = json.loads(res.read())

out_image = Image.open(BytesIO(base64.b64decode(body["images"][0])))
out_image.save("./autoimagegenerator/images/output/out-image2.png")