import base64
import json
import random
import requests
from PIL import Image, PngImagePlugin, ImageDraw, ImageFont
import io
import os
from datetime import datetime
import re


# 画像生成バッチの実行回数を指定
IMAGE_GENERATE_BATCH_EXECUTE_COUNT = 10

# 生成された画像の別バージョン(同じSeed値でオプションのプロンプトを変更)を作成する回数を指定
ANOTHER_VERSION_GENERATE_COUNT = 11

# 保存先フォルダのルートパス
INPUT_FOLDER = "./autoimagegenerator/images/input"
OUTPUT_FOLDER = "./autoimagegenerator/images/output"

# 解像度を半分にした画像(サムネイル用)の保存先フォルダのパス
HALF_RESOLUTION_FOLDER = "/half-resolution"

# 解像度を倍にした画像の保存先フォルダのパス
DOUBLE_RESOLUTION_FOLDER = "/double-resolution"

# Sample文字が入っている等倍画像の保存先フォルダのパス
WITH_SAMPLE_TEXT_FOLDER = "/sample"

# Sample文字が入っている解像度を半分にした画像(サムネイル用)の保存先フォルダのパス
WITH_SAMPLE_HALF_RESOLUTION_FOLDER = "/sample-half-resolution"

# StableDiffusionのAPI URL
URL = "http://localhost:7860"

IMAGE_FILE_EXTENSION = ".png"

# text2imgのAPIのURL
TEXT2IMG_URL = f'{URL}/sdapi/v1/txt2img'

# png-infoのAPIのURL
PNGINFO_URL = f'{URL}/sdapi/v1/png-info'

# ベース画像作成時のtext2imgのベースとなるpayload
TXT2IMG_BASE_PAYLOAD = {
    "steps": 40,
    "seed": -1,
    "width": 512,
    "height": 768,
    "cfg_scale": 7,
    "batch_size": 1,
    "batch_count": 1,
    "sampler_name": "DPM++ 2M Karras",
    "sd_model_checkpoint": "Brav6.safetensors"
}

# 生成された画像の別バージョン作成時のtext2imgのベースとなるpayload
ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD = {
    "steps": 40,
    "width": 512,
    "height": 768,
    "cfg_scale": 7,
    "batch_size": 1,
    "batch_count": 1,
    "sampler_name": "DPM++ 2M Karras",
    "sd_model_checkpoint": "Brav6.safetensors"
}


# JSONファイルからデータを読み込む
with open('./autoimagegenerator/prompts/brav6_positive_base.json', 'r') as file:
    DATA_POSITIVE_BASE = json.load(file)
with open('./autoimagegenerator/prompts/brav6_positive_optional.json', 'r') as file:
    DATA_POSITIVE_OPTIONAL = json.load(file)
with open('./autoimagegenerator/prompts/brav6_negative.json', 'r') as file:
    DATA_NEGATIVE = json.load(file)


# すべてのキーに対してランダムなプロンプトを生成
def generate_random_prompts(data):
    combined_prompt = []
    prompt_json = {}

    for key, value in data.items():
        if isinstance(value, dict):
            use_max_prompts = value.get("use max prompts", 0)
            use_min_prompts = value.get("use min prompts", 0)
            prompts = value.get("prompts", [])

            # ランダムな数のプロンプトを取得
            num_prompts = random.randint(use_min_prompts, use_max_prompts)
            selected_prompts = random.sample(prompts, num_prompts)
            prompt_json[key] = selected_prompts

            # プロンプトを一つの文字列に結合
            combined_prompt.extend(selected_prompts)

    return ", ".join(combined_prompt), prompt_json

def merge_images(background_image, transparent_image):

    # 透過画像を背景画像のサイズを合わせる
    transparent_image = transparent_image.resize(background_image.size)

    # 透過画像を背景画像に合成
    result_image = Image.alpha_composite(background_image.convert("RGBA"), transparent_image)

    return result_image

# 画像を生成
# 引数: ベースとなるポジティブプロンプト, ネガティブプロンプト
# 戻り値: 画像の辞書
#           画像の辞書のキー: フォルダパス
#           画像の辞書の値: 画像の辞書
#               画像の辞書の値のキー: seed_value, image, positive_optional_prompts
def generate_images(positive_base_prompts, negative_prompts, payload, image_number):
    result_images = {}

    # すべてのキーに対してオプション用のランダムなプロンプトを生成
    positive_optional_prompts, positive_optional_prompt_dict = generate_random_prompts(DATA_POSITIVE_OPTIONAL)

    txt2img_payload = payload
    txt2img_payload["prompt"] = positive_base_prompts + ", " + positive_optional_prompts
    txt2img_payload["negative_prompt"] = negative_prompts

    response = requests.post(url=TEXT2IMG_URL, json=txt2img_payload)

    r = response.json()

    for i in r['images']:
        seed_value = 0
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=PNGINFO_URL, json=png_payload)

        # 正規表現を使用してSeedの値を抽出
        match = re.search(r"Seed:\s*(\d+)", response2.json().get("info"))

        if match:
            seed_value = int(match.group(1))
            # print(f"Seedの値は: {seed_value}")
        else:
            print("Seedが見つかりませんでした。")

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        # 日付とSeedを取得してフォルダパスを生成
        today = datetime.today()
        folder_name = today.strftime("%Y%m%d")
        folder_name = f"{folder_name}-{seed_value}"
        folder_path = os.path.join(OUTPUT_FOLDER, folder_name).replace("\\", "/")

        # フォルダが存在しない場合は作成
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 5桁ゼロ埋めの数字を生成
        filename = f"{str(image_number).zfill(5)}-{seed_value}"

        # ファイルを保存
        file_path = os.path.join(folder_path, filename + IMAGE_FILE_EXTENSION).replace("\\", "/")
        image.save(file_path, pnginfo=pnginfo)

        result_images[folder_path] = {
            'filename': filename,
            'seed_value': seed_value,
            'image': image,
            'positive_optional_prompt_dict': positive_optional_prompt_dict
        }

    return result_images

# 必要な関連画像を作成
def generate_related_images(base_image, folder_path, filename):
    # 画像に「Sample」のテキストを追加して保存
    sample_text_image = Image.open(INPUT_FOLDER + "/sample.png")

    image_with_sample_text = merge_images(base_image, sample_text_image)
    image_with_sample_text_file_path = os.path.join(folder_path + WITH_SAMPLE_TEXT_FOLDER, filename + "-with-sample-text" + IMAGE_FILE_EXTENSION).replace("\\", "/")
    # フォルダが存在しない場合は作成
    if not os.path.exists(folder_path + WITH_SAMPLE_TEXT_FOLDER):
        os.makedirs(folder_path + WITH_SAMPLE_TEXT_FOLDER)
   
    image_with_sample_text.save(image_with_sample_text_file_path)

    # 解像度を半分にした画像を生成して保存
    half_resolution_image = image.resize((base_image.width // 2, base_image.height // 2))
    half_resolution_filename = f"{filename}-half-resolution"
    half_resolution_file_path = os.path.join(folder_path + HALF_RESOLUTION_FOLDER, half_resolution_filename + IMAGE_FILE_EXTENSION).replace("\\", "/")
    if not os.path.exists(folder_path + HALF_RESOLUTION_FOLDER):
        os.makedirs(folder_path + HALF_RESOLUTION_FOLDER)
    half_resolution_image.save(half_resolution_file_path)

    # 画像を2倍に拡大し、高画質化
    double_resolution_image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
    double_resolution_filename = f"{filename}-double-resolution"
    double_resolution_file_path = os.path.join(folder_path + DOUBLE_RESOLUTION_FOLDER, double_resolution_filename + IMAGE_FILE_EXTENSION).replace("\\", "/")
    if not os.path.exists(folder_path + DOUBLE_RESOLUTION_FOLDER):
        os.makedirs(folder_path + DOUBLE_RESOLUTION_FOLDER)
    double_resolution_image.save(double_resolution_file_path)

    # 画像に「Sample」のテキストを追加して保存
    image_with_sample_text = merge_images(half_resolution_image, sample_text_image)
    image_with_sample_text_file_path = os.path.join(folder_path + WITH_SAMPLE_HALF_RESOLUTION_FOLDER, half_resolution_filename + "-with-sample-text" + IMAGE_FILE_EXTENSION).replace("\\", "/")
    if not os.path.exists(folder_path + WITH_SAMPLE_HALF_RESOLUTION_FOLDER):
        os.makedirs(folder_path + WITH_SAMPLE_HALF_RESOLUTION_FOLDER)
    image_with_sample_text.save(image_with_sample_text_file_path)

    return {}

# 使用されたプロンプトをテキストファイルに保存
def save_prompts_to_json(positive_base_prompt_dict, positive_optional_prompt_dict, folder_path, filename):
    merged_dict = {**positive_base_prompt_dict, **positive_optional_prompt_dict}
    # プロンプトをJSONファイルに保存
    json_filename = os.path.join(folder_path, filename + ".json").replace("\\", "/")
    with open(json_filename, 'w') as json_file:
        json.dump(merged_dict, json_file, indent=4)

    return {}



for _ in range(IMAGE_GENERATE_BATCH_EXECUTE_COUNT):
    # すべてのキーに対してランダムなプロンプトを生成
    positive_base_prompts, positive_base_prompt_dict = generate_random_prompts(DATA_POSITIVE_BASE)
    negative_prompts, negative_prompt_dict = generate_random_prompts(DATA_NEGATIVE)

    # 関数から生成された画像の辞書を取得
    generated_images = generate_images(positive_base_prompts, negative_prompts, TXT2IMG_BASE_PAYLOAD, 0)

    # 生成された画像の辞書をループで処理
    for folder_path, image_data in generated_images.items():
        filename = image_data['filename']
        seed_value = image_data['seed_value']
        image = image_data['image']
        positive_optional_prompt_dict = image_data['positive_optional_prompt_dict']

        # 必要な関連画像を作成positive_optional_prompt_dict
        generate_related_images(image, folder_path, filename)
        save_prompts_to_json(positive_base_prompt_dict, positive_optional_prompt_dict, folder_path, filename)

        # 生成された画像の別バージョン(同じSeed値でオプションのプロンプトを変更)を作成
        image_number = 1
        for _ in range(ANOTHER_VERSION_GENERATE_COUNT):
            payload_another_version = ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD
            payload_another_version["seed"] = seed_value
            # 関数から生成された画像の辞書を取得
            generated_images = generate_images(positive_base_prompts, negative_prompts, payload_another_version, image_number)

            # 生成された画像の辞書をループで処理
            for folder_path, image_data in generated_images.items():
                filename = image_data['filename']
                seed_value = image_data['seed_value']
                image = image_data['image']
                positive_optional_prompt_dict = image_data['positive_optional_prompt_dict']

                # 必要な関連画像を作成
                generate_related_images(image, folder_path, str(image_number).zfill(5) + "-" + str(seed_value))
                save_prompts_to_json(positive_base_prompt_dict, positive_optional_prompt_dict, folder_path, filename)

            image_number += 1

