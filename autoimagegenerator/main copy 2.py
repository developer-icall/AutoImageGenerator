import base64
import json
import random
import requests
from PIL import Image, ImageOps
import io
import os
import base64
from PIL import Image, PngImagePlugin
from datetime import datetime
import re

# 保存先フォルダのルートパス
output_folder = "./autoimagegenerator/images/output"
url = "http://localhost:7860"
# url = base_url  + "/sdapi/v1/options"


# JSONファイルからデータを読み込む
with open('./autoimagegenerator/prompts/brav6_positive.json', 'r') as file:
    data_positive = json.load(file)
with open('./autoimagegenerator/prompts/brav6_negative.json', 'r') as file:
    data_negative = json.load(file)

# すべてのキーに対してランダムなプロンプトを生成
def generate_random_prompts(data):
    combined_prompt = []

    for key, value in data.items():
        if isinstance(value, dict):
            use_max_prompts = value.get("use max prompts", 0)
            use_min_prompts = value.get("use min prompts", 0)
            prompts = value.get("prompts", [])

            # ランダムな数のプロンプトを取得
            num_prompts = random.randint(use_min_prompts, use_max_prompts)
            selected_prompts = random.sample(prompts, num_prompts)

            # プロンプトを一つの文字列に結合
            combined_prompt.extend(selected_prompts)

    return ", ".join(combined_prompt)

# すべてのキーに対してランダムなプロンプトを生成
positive_prompts = generate_random_prompts(data_positive)
negative_prompts = generate_random_prompts(data_negative)

# 結果を表示
print(positive_prompts)
print(negative_prompts)

payload = {
    "prompt": positive_prompts,
    "negative_prompt": negative_prompts,
    "steps": 40,
    "seed": -1,
    "width": 512,
    "height": 768,
    "cfg_scale": 7,
    "batch_size": 2,
}

response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

r = response.json()

# 今日の日付を取得してフォルダパスを生成
today = datetime.today()
folder_name = today.strftime("%Y%m%d")
folder_path = os.path.join(output_folder, folder_name)

# フォルダが存在しない場合は作成
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

count = 0
for i in r['images']:
    seed_value = 0
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
 
    png_payload = {
        "image": "data:image/png;base64," + i
    }
    response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

    # 正規表現を使用してSeedの値を抽出
    match = re.search(r"Seed:\s*(\d+)", response2.json().get("info"))

    if match:
        seed_value = int(match.group(1))
        print(f"Seedの値は: {seed_value}")
    else:
        print("Seedが見つかりませんでした。")

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))

    # 5桁ゼロ埋めの数字を生成
    filename = f"{str(count).zfill(5)}-{seed_value}.png"
    count += 1

    # ファイルを保存
    file_path = os.path.join(folder_path, filename)
    image.save(file_path, pnginfo=pnginfo)
