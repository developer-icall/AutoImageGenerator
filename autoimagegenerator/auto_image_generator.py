import base64
import json
import random
import requests
from PIL import Image, PngImagePlugin
import io
import os
from datetime import datetime
import re
from tqdm import tqdm

class AutoImageGenerator:

    def __init__(
        self,
        image_generate_batch_execute_count=1,
        another_version_generate_count=11,
        input_folder="./autoimagegenerator/images/input",
        output_folder="./autoimagegenerator/images/output",
        prompts_folder="./prompts",
        url="http://localhost:7860",
        sd_model_checkpoint="Brav6.safetensors",
        sd_model_prefix="brav6",
        enable_hr=False,
    ):
        # パラメータから受け取った値をプロパティへセット
        # 画像生成バッチの実行回数を指定
        self.IMAGE_GENERATE_BATCH_EXECUTE_COUNT = image_generate_batch_execute_count

        # 生成された画像の別バージョン(同じSeed値でオプションのプロンプトを変更)を作成する回数を指定
        self.ANOTHER_VERSION_GENERATE_COUNT = another_version_generate_count

        # 生成時に利用する画像の保存先フォルダのルートパス
        self.INPUT_FOLDER = input_folder
        # 生成された画像の保存先フォルダのルートパス
        self.OUTPUT_FOLDER = output_folder

        # プロンプトの保存先フォルダ
        self.PROMPT_PATH = prompts_folder + "/" + sd_model_prefix

        # StableDiffusionのAPI URL
        self.URL = url
        
        # 使用するモデルチェックポイント
        self.SD_MODEL_CHECKPOINT = sd_model_checkpoint
        
        # 使用するモデルのプリフィックス
        self.SD_MODEL_PREFIX = sd_model_prefix

        # ハイレゾ画像で生成するかどうか
        self.ENABLE_HR = enable_hr

        # 定数定義
        self.POSITIVE_PROMPT_BASE_FILENAME = "positive_base.json"
        self.POSITIVE_PROMPT_POSE_FILENAME = "positive_pose.json"
        self.POSITIVE_PROMPT_OPTIONAL_FILENAME = "positive_optional.json"
        self.NEGATIVE_PROMPT_FILENAME = "negative.json"
        self.CANCEL_SEEDS_FILENAME = "cancel_seeds.json"

        # 同時に使用できないプロンプトの組み合わせを保存したファイル
        self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME = "positive_cancel_pair.json"

        # サムネイル用画像の保存先フォルダのパス
        self.THUMBNAIL_FOLDER = "/thumbnail"

        # 解像度を半分にした画像の保存先フォルダのパス
        self.HALF_RESOLUTION_FOLDER = "/half-resolution"

        # Sample文字が入っている等倍画像の保存先フォルダのパス
        self.WITH_SAMPLE_TEXT_FOLDER = "/sample"

        # Sample文字が入っている解像度を半分にした画像(サムネイル用)の保存先フォルダのパス
        self.WITH_SAMPLE_THUMBNAIL_FOLDER = "/sample-thumbnail"

        self.IMAGE_FILE_EXTENSION = ".png"
        self.TEXT2IMG_URL = f'{self.URL}/sdapi/v1/txt2img'
        self.PNGINFO_URL = f'{self.URL}/sdapi/v1/png-info'

        # text2imgのベースとなるpayload
        self.TXT2IMG_BASE_PAYLOAD = {
            "steps": 60,
            "seed": -1,
            "width": 512,
            "height": 768,
            "cfg_scale": 7,
            "batch_size": 1,
            "batch_count": 1,
            "sampler_name": "DPM++ 2M Karras",
            "sd_model_checkpoint": self.SD_MODEL_CHECKPOINT,
            "enable_hr": enable_hr,
            "hr_scale": 2,
            "hr_upscaler": "4x-UltraSharp",
            "denoising_strength": 0.3
        }

        # 生成された画像の別バージョン作成時のtext2imgのベースとなるpayload
        self.ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD = {
            "steps": 60,
            "width": 512,
            "height": 768,
            "cfg_scale": 7,
            "batch_size": 1,
            "batch_count": 1,
            "sampler_name": "DPM++ 2M Karras",
            "sd_model_checkpoint": self.SD_MODEL_CHECKPOINT,
            "enable_hr": enable_hr,
            "hr_scale": 2,
            "hr_upscaler": "4x-UltraSharp",
            "denoising_strength": 0.3
        }
        self.DATA_POSITIVE_BASE = None
        self.DATA_POSITIVE_OPTIONAL = None
        self.DATA_NEGATIVE = None
        self.DATA_CANCEL_SEEDS = None

        # JSONファイルからデータを読み込む
        with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_BASE_FILENAME, 'r') as file:
            self.DATA_POSITIVE_BASE = json.load(file)
        with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_POSE_FILENAME, 'r') as file:
            self.DATA_POSITIVE_POSE = json.load(file)
        with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_OPTIONAL_FILENAME, 'r') as file:
            self.DATA_POSITIVE_OPTIONAL = json.load(file)
        with open(self.PROMPT_PATH + '/' + self.NEGATIVE_PROMPT_FILENAME, 'r') as file:
            self.DATA_NEGATIVE = json.load(file)
        with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME, 'r') as file:
            self.DATA_POSITIVE_CANCEL_PAIR = json.load(file)
        with open(self.PROMPT_PATH + '/' + self.CANCEL_SEEDS_FILENAME, 'r') as file:
            self.DATA_CANCEL_SEEDS = json.load(file)

    # ランダムなプロンプトを生成
    def generate_random_prompts(self, data):
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

    # 画像を生成
    def generate_images(self, positive_base_prompts, negative_prompts, payload, image_number, folder_path=None):
        result_images = {}

        # ポーズ用のランダムなプロンプトを生成
        positive_pose_prompts, positive_pose_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_POSE)

        # オプション用のランダムなプロンプトを生成
        positive_optional_prompts, positive_optional_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_OPTIONAL)

        # プロンプトを結合
        prompt = positive_pose_prompts + ", " + positive_base_prompts + ", " + positive_optional_prompts

        # 結合したプロンプト文字列内にキー文字列が含まれている場合は、キーに対応する cancel prompts 内にキャンセル対象の文字列がないかを検索
        cancel_prompts = []
        for key, value in self.DATA_POSITIVE_CANCEL_PAIR.items():
            # キー文字列がプロンプト文字列内に含まれているかを検索
            if key in prompt:
                for cancel_prompt in value:
                    # キャンセル対象の文字列がプロンプト文字列内に含まれているかを検索
                    if cancel_prompt in prompt:
                        # キャンセル対象の文字列が見つかった場合は、その文字列を削除
                        prompt = prompt.replace(cancel_prompt + ", ", "").replace(", " + cancel_prompt, "").replace(cancel_prompt, "")
                        cancel_prompts.append({key: cancel_prompt})

        txt2img_payload = payload
        txt2img_payload["prompt"] = prompt
        txt2img_payload["negative_prompt"] = negative_prompts

        response = requests.post(url=self.TEXT2IMG_URL, json=txt2img_payload)

        r = response.json()

        for i in r['images']:
            seed_value = 0
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=self.PNGINFO_URL, json=png_payload)

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
            folder_name = today.strftime("%Y%m%d-%H")
            folder_name = f"{folder_name}-{seed_value}"
            if folder_path is None:
                folder_path = os.path.join(self.OUTPUT_FOLDER, folder_name).replace("\\", "/")

            if len(cancel_prompts) > 0:
                print(f"folder_name: {folder_name} のプロンプト文字列内のキャンセル対象文字列のペア")
                for item in cancel_prompts:
                    for key, value in item.items():
                        print(f"{key}: {value}")

            for seed in self.DATA_CANCEL_SEEDS["Seeds"]:
                if seed_value == seed:
                    print(f"folder_name: {folder_name} のSeed値はキャンセル対象です。")
                    continue    

            # フォルダが存在しない場合は作成
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # 5桁ゼロ埋めの数字を生成
            filename = f"{str(image_number).zfill(5)}-{seed_value}"

            # ファイルを保存
            file_path = os.path.join(folder_path, filename + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
            image.save(file_path, pnginfo=pnginfo)

            # 画像をJPG形式で保存（別ファイルとして）
            jpg_file_path = os.path.join(folder_path, filename + ".jpg").replace("\\", "/")
            image.convert("RGB").save(jpg_file_path, format="JPEG")            

            result_images[folder_path] = {
                'filename': filename,
                'seed_value': seed_value,
                'image': image,
                'positive_pose_prompt_dict': positive_pose_prompt_dict,
                'positive_optional_prompt_dict': positive_optional_prompt_dict,
                'pnginfo': pnginfo,
                'cancel_prompts': cancel_prompts
            }

        return result_images

    # 必要な関連画像を作成
    def generate_related_images(self, base_image, folder_path, filename, pnginfo=None):

        # 画像に「Sample」のテキストを追加して保存
        sample_text_image = Image.open(self.INPUT_FOLDER + "/sample.png")

        image_with_sample_text = self.merge_images(base_image, sample_text_image)
        image_with_sample_text_file_path = os.path.join(folder_path + self.WITH_SAMPLE_TEXT_FOLDER,
                                                         filename + "-with-sample-text" + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
        # フォルダが存在しない場合は作成
        if not os.path.exists(folder_path + self.WITH_SAMPLE_TEXT_FOLDER):
            os.makedirs(folder_path + self.WITH_SAMPLE_TEXT_FOLDER)

        image_with_sample_text.save(image_with_sample_text_file_path)

        # サムネイル用画像を生成して保存
        thumbnail_ratio = 2
        if self.ENABLE_HR == True:
            thumbnail_ratio = 4
        thumbnail_image = base_image.resize((base_image.width // thumbnail_ratio, base_image.height // thumbnail_ratio))
        thumbnail_filename = f"{filename}-thumbnail"
        thumbnail_file_path = os.path.join(folder_path + self.THUMBNAIL_FOLDER,
                                                 thumbnail_filename + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
        if not os.path.exists(folder_path + self.THUMBNAIL_FOLDER):
            os.makedirs(folder_path + self.THUMBNAIL_FOLDER)
        thumbnail_image.save(thumbnail_file_path)

        # 画像に「Sample」のテキストを追加して保存
        image_with_sample_text = self.merge_images(thumbnail_image, sample_text_image)
        image_with_sample_text_file_path = os.path.join(folder_path + self.WITH_SAMPLE_THUMBNAIL_FOLDER,
                                                         thumbnail_filename + "-with-sample-text" + self.IMAGE_FILE_EXTENSION).replace(
            "\\", "/")
        if not os.path.exists(folder_path + self.WITH_SAMPLE_THUMBNAIL_FOLDER):
            os.makedirs(folder_path + self.WITH_SAMPLE_THUMBNAIL_FOLDER)
        image_with_sample_text.save(image_with_sample_text_file_path)

        if self.ENABLE_HR == True:
            # 画像の解像度を半分にして保存
            half_resolution_image = base_image.resize((base_image.width // 2, base_image.height // 2), Image.LANCZOS)
            half_resolution_filename = f"{filename}-half-resolution"
            half_resolution_file_path = os.path.join(folder_path + self.HALF_RESOLUTION_FOLDER,
                                                    half_resolution_filename + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
            if not os.path.exists(folder_path + self.HALF_RESOLUTION_FOLDER):
                os.makedirs(folder_path + self.HALF_RESOLUTION_FOLDER)
            half_resolution_image.save(half_resolution_file_path, pnginfo=pnginfo)


        return {}

    # 使用されたプロンプトをテキストファイルに保存
    def save_prompts_to_json(self, positive_base_prompt_dict, positive_optional_pose_dict, positive_optional_prompt_dict, negative_prompt_dict, folder_path, filename, cancel_prompts):
        merged_dict = {"sd_model": self.SD_MODEL_PREFIX, **positive_optional_pose_dict, **positive_base_prompt_dict, **positive_optional_prompt_dict, **negative_prompt_dict}
        if len(cancel_prompts) > 0:
            merged_dict["cancel_prompts"] = cancel_prompts
        # プロンプトをJSONファイルに保存
        json_filename = os.path.join(folder_path, filename + ".json").replace("\\", "/")
        with open(json_filename, 'w') as json_file:
            json.dump(merged_dict, json_file, indent=4)

        return {}

    # 画像の合成
    def merge_images(self, background_image, transparent_image):
        # 透過画像を背景画像のサイズに合わせる
        transparent_image = transparent_image.resize(background_image.size)

        # 透過画像を背景画像に合成
        result_image = Image.alpha_composite(background_image.convert("RGBA"), transparent_image)

        return result_image


    def run(self):
        for _ in tqdm(range(self.IMAGE_GENERATE_BATCH_EXECUTE_COUNT)):
            # すべてのキーに対してランダムなプロンプトを生成
            positive_base_prompts, positive_base_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_BASE)
            negative_prompts, negative_prompt_dict = self.generate_random_prompts(self.DATA_NEGATIVE)

            # 関数から生成された画像の辞書を取得
            generated_images = self.generate_images(positive_base_prompts, negative_prompts, self.TXT2IMG_BASE_PAYLOAD, 0)

            if len(generated_images) == 0:
                print("キャンセル対象の Seed値だったため、画像の生成をスキップしました。")
                continue

            # 関連画像および同じSeed値(同一人物)の別バリエーション画像を作成(画像生成時のbatch_size, batch_countを現状1固定のため、ループは1回のみだが将来的に変更される可能性があるためループで処理)
            for folder_path, image_data in generated_images.items():
                filename = image_data['filename']
                seed_value = image_data['seed_value']
                image = image_data['image']
                positive_optional_prompt_dict = image_data['positive_optional_prompt_dict']
                positive_pose_pose_dict = image_data['positive_pose_prompt_dict']
                pnginfo = image_data['pnginfo']
                cancel_prompts = image_data['cancel_prompts']

                # 必要な関連画像を作成
                self.generate_related_images(image, folder_path, filename, pnginfo)
                self.save_prompts_to_json(positive_base_prompt_dict, positive_pose_pose_dict, positive_optional_prompt_dict, negative_prompt_dict, folder_path, filename, cancel_prompts)

                # 生成された画像の別バージョン(同じSeed値でポーズとオプションのプロンプトを変更)を作成
                image_number = 1
                for _ in range(self.ANOTHER_VERSION_GENERATE_COUNT):
                    payload_another_version = self.ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD
                    payload_another_version["seed"] = seed_value
                    # 関数から生成された画像の辞書を取得
                    generated_images = self.generate_images(positive_base_prompts, negative_prompts, payload_another_version, image_number, folder_path)

                    # 生成された画像の辞書をループで処理
                    for folder_path, image_data in generated_images.items():
                        filename = image_data['filename']
                        seed_value = image_data['seed_value']
                        image = image_data['image']
                        positive_optional_prompt_dict = image_data['positive_optional_prompt_dict']
                        positive_pose_pose_dict = image_data['positive_pose_prompt_dict']
                        cancel_prompts = image_data['cancel_prompts']

                        # 必要な関連画像を作成
                        self.generate_related_images(image, folder_path, str(image_number).zfill(5) + "-" + str(seed_value))
                        self.save_prompts_to_json(positive_base_prompt_dict, positive_pose_pose_dict, positive_optional_prompt_dict, negative_prompt_dict, folder_path, filename, cancel_prompts)

                    image_number += 1
