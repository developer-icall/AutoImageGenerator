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
import sys

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
        enable_hr=True,
        output_folder_prefix="",
        is_transparent_background=False,
        is_selfie=False
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

        self.OUTPUT_FOLDER_PREFIX = output_folder_prefix

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

        # 背景透過画像で生成するかどうか
        self.IS_TRANPARENT_BACKGROUND = is_transparent_background

        # 地鶏画像で生成するかどうか
        self.IS_SELFIE = is_selfie

        # 定数定義
        self.POSITIVE_PROMPT_BASE_FILENAME = "positive_base.json"
        self.POSITIVE_PROMPT_POSE_FILENAME = "positive_pose.json"
        self.POSITIVE_PROMPT_OPTIONAL_FILENAME = "positive_optional.json"
        self.POSITIVE_PROMPT_SELFIE_FILENAME = "positive_selfie.json"
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
            "height": 768,  # この値は後で条件分岐で上書きされます
            "cfg_scale": 7,
            "batch_size": 1,
            "batch_count": 1,
            "sampler_name": "DPM++ 2M",
            "Schedule type": "Karras",
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
            "height": 768,  # この値は後で条件分岐で上書きされます
            "cfg_scale": 7,
            "batch_size": 1,
            "batch_count": 1,
            "sampler_name": "DPM++ 2M",
            "Schedule type": "Karras",
            "sd_model_checkpoint": self.SD_MODEL_CHECKPOINT,
            "enable_hr": enable_hr,
            "hr_scale": 2,
            "hr_upscaler": "4x-UltraSharp",
            "denoising_strength": 0.3
        }

        # RPGIcon用に画像サイズを設定
        if sd_model_prefix == "rpgicon":
            self.TXT2IMG_BASE_PAYLOAD["height"] = 512
            self.ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD["height"] = 512

        # 透過画像として出力する際に追加する payload
        self.TRANPARENT_PAYLOAD = {
            "script_name": "ABG Remover",
            "script_args": []
        }
        self.DATA_POSITIVE_BASE = None
        self.DATA_POSITIVE_OPTIONAL = None
        self.DATA_POSITIVE_SELFIE = None
        self.DATA_NEGATIVE = None
        self.DATA_CANCEL_SEEDS = None

        # RPGIcon用の出力フォルダを設定
        if sd_model_prefix == "rpgicon":
            self.OUTPUT_FOLDER = os.path.join(output_folder, "RPGIcon").replace("\\", "/")
        elif sd_model_prefix.startswith("brav"):  # bravシリーズの場合
            self.OUTPUT_FOLDER = os.path.join(output_folder, "brav").replace("\\", "/")
        else:
            self.OUTPUT_FOLDER = output_folder

        # JSONファイルからデータを読み込む
        self.DATA_POSITIVE_BASE = {}
        self.DATA_POSITIVE_POSE = {}
        self.DATA_POSITIVE_OPTIONAL = {}
        self.DATA_POSITIVE_SELFIE = {}
        self.DATA_NEGATIVE = {}
        self.DATA_POSITIVE_CANCEL_PAIR = {}
        self.DATA_CANCEL_SEEDS = {}

        # 必須のJSONファイルを読み込み
        try:
            with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_BASE_FILENAME, 'r') as file:
                self.DATA_POSITIVE_BASE = json.load(file)
        except FileNotFoundError:
            print(f"Error: Required file {self.POSITIVE_PROMPT_BASE_FILENAME} not found in {self.PROMPT_PATH}")
            print("This file is required for image generation. Process will exit.")
            sys.exit(1)

        try:
            with open(self.PROMPT_PATH + '/' + self.NEGATIVE_PROMPT_FILENAME, 'r') as file:
                self.DATA_NEGATIVE = json.load(file)
        except FileNotFoundError:
            print(f"Error: Required file {self.NEGATIVE_PROMPT_FILENAME} not found in {self.PROMPT_PATH}")
            print("This file is required for image generation. Process will exit.")
            sys.exit(1)

        # オプションのJSONファイルを読み込み
        try:
            with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_POSE_FILENAME, 'r') as file:
                self.DATA_POSITIVE_POSE = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {self.POSITIVE_PROMPT_POSE_FILENAME} not found. Using empty dict.")

        try:
            with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_OPTIONAL_FILENAME, 'r') as file:
                self.DATA_POSITIVE_OPTIONAL = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {self.POSITIVE_PROMPT_OPTIONAL_FILENAME} not found. Using empty dict.")

        try:
            with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_SELFIE_FILENAME, 'r') as file:
                self.DATA_POSITIVE_SELFIE = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {self.POSITIVE_PROMPT_SELFIE_FILENAME} not found. Using empty dict.")

        try:
            with open(self.PROMPT_PATH + '/' + self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME, 'r') as file:
                self.DATA_POSITIVE_CANCEL_PAIR = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME} not found. Using empty dict.")

        try:
            with open(self.PROMPT_PATH + '/' + self.CANCEL_SEEDS_FILENAME, 'r') as file:
                self.DATA_CANCEL_SEEDS = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {self.CANCEL_SEEDS_FILENAME} not found. Using empty dict.")
            self.DATA_CANCEL_SEEDS = {"Seeds": []}  # Seedsキーは必要なので空の配列を設定

        # Seed の桁数が少ない場合生成される画像の質が低い可能性が高いため、生成をキャンセルする閾値として設定
        self.CANCEL_MIN_SEED_VALUE = 999999999

        self.style = "realistic"  # デフォルト値
        self.category = "female"  # デフォルト値
        self.subcategory = "normal"  # デフォルト値

    def get_prompts_path(self):
        """スタイル、カテゴリーに応じたプロンプトファイルのパスを取得"""
        return os.path.join(self.PROMPT_PATH, self.style, self.category)

    def get_output_path(self):
        """スタイル、カテゴリー、サブカテゴリーに応じた出力パスを取得"""
        return os.path.join(
            self.OUTPUT_FOLDER,
            self.style,
            self.category,
            self.subcategory
        )

    def set_generation_params(self, style, category, subcategory):
        """生成パラメータを設定"""
        self.style = style
        self.category = category
        self.subcategory = subcategory

    def load_prompts(self):
        """プロンプトファイルを読み込む"""
        prompts_path = self.get_prompts_path()

        # 基本プロンプトの読み込み
        with open(os.path.join(prompts_path, "positive_base.json"), "r", encoding="utf-8") as f:
            self.DATA_POSITIVE_BASE = json.load(f)

        # オプショナルプロンプトの読み込み
        with open(os.path.join(prompts_path, "positive_optional.json"), "r", encoding="utf-8") as f:
            self.DATA_POSITIVE_OPTIONAL = json.load(f)

        # ネガティブプロンプトの読み込み
        with open(os.path.join(prompts_path, "negative.json"), "r", encoding="utf-8") as f:
            self.DATA_NEGATIVE = json.load(f)

        # キャンセルシードの読み込み
        try:
            with open(os.path.join(prompts_path, "cancel_seeds.json"), "r", encoding="utf-8") as f:
                self.DATA_CANCEL_SEEDS = json.load(f)
        except FileNotFoundError:
            self.DATA_CANCEL_SEEDS = {"seeds": []}

    def generate_prompt(self):
        """プロンプトを生成"""
        prompt_parts = []

        # 基本プロンプトの追加
        for category, config in self.DATA_POSITIVE_BASE.items():
            max_prompts = config.get("use max prompts", 1)
            min_prompts = config.get("use min prompts", 0)
            num_prompts = random.randint(min_prompts, max_prompts)
            if num_prompts > 0:
                selected = random.sample(config["prompts"], num_prompts)
                prompt_parts.extend(selected)

        # オプショナルプロンプトの追加
        for category, config in self.DATA_POSITIVE_OPTIONAL.items():
            max_prompts = config.get("use max prompts", 1)
            min_prompts = config.get("use min prompts", 0)
            num_prompts = random.randint(min_prompts, max_prompts)
            if num_prompts > 0:
                selected = random.sample(config["prompts"], num_prompts)
                prompt_parts.extend(selected)

        return ", ".join(prompt_parts)

    def generate_negative_prompt(self):
        """ネガティブプロンプトを生成"""
        negative_parts = []

        for category, config in self.DATA_NEGATIVE.items():
            max_prompts = config.get("use max prompts", 1)
            min_prompts = config.get("use min prompts", 0)
            num_prompts = random.randint(min_prompts, max_prompts)
            if num_prompts > 0:
                selected = random.sample(config["prompts"], num_prompts)
                negative_parts.extend(selected)

        return ", ".join(negative_parts)

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
        """画像を生成"""
        generated_images = {}

        # APIリクエストを実行
        response = requests.post(url=self.TXT2IMG_URL, json=payload)

        for i in response.json()['images']:
            # 画像データをデコード
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

            # シード値を取得
            seed_value = self.get_seed_value(i)
            if not seed_value:
                continue

            # キャンセル条件をチェック
            if self.should_cancel_generation(seed_value):
                continue

            # 保存パスを取得
            save_path = folder_path or self.get_save_path(seed_value)

            # 画像を保存
            filename = f"{str(image_number).zfill(5)}-{seed_value}"
            self.save_image(image, save_path, filename)

            generated_images[save_path] = {
                'filename': filename,
                'seed_value': seed_value,
                'image': image,
                'pnginfo': self.get_pnginfo(i),
                'cancel_prompts': []  # 必要に応じて設定
            }

        return generated_images

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

    def create_image_collage(self, input_folder, output_path, rows, cols, recreate_collage=True):

        # フォルダ内のファイル一覧を取得
        files = os.listdir(output_path)

        # "collage" を含むファイルを削除
        for file_name in files:
            if "collage" in file_name:
                if recreate_collage:
                    file_path = os.path.join(input_folder, file_name)
                    try:
                        os.remove(file_path)
                        print(f"ファイル {file_name} を削除しました。")
                    except Exception as e:
                        print(f"ファイル {file_name} の削除中にエラーが発生しました: {e}")
                else:
                    print(f"既にファイル {file_name} が存在したのでスキップしました。")
                    return


        # 入力フォルダから画像ファイルのパスを取得
        image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png'))]

        if len(image_files) == 0:
            print("指定されたフォルダに画像が存在しません。")
            return

        # 画像サイズを取得
        image = Image.open(os.path.join(input_folder, image_files[0]))
        image_width, image_height = image.size

        # 出力画像のサイズを計算
        collage_width = image_width * cols
        collage_height = image_height * rows

        # 出力用の画像を作成
        collage = Image.new('RGB', (collage_width, collage_height))

        # 画像を配置
        for i, image_file in enumerate(image_files):
            col = i % cols
            row = i // cols
            img = Image.open(os.path.join(input_folder, image_file))
            collage.paste(img, (col * image_width, row * image_height))

        folder_numbers = re.findall(r'\d+', input_folder)
        collage_filename = f"{folder_numbers[0]}-{folder_numbers[1]}-{folder_numbers[2]}-thumbnail-collage"
        collage_file_path = os.path.join(output_path, collage_filename + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
        # 画像を保存
        collage.save(collage_file_path)
        print(f"画像コラージュを作成しました: {collage_file_path}")

    def create_image_sample(self, input_folder, delete_exists_sample=True):

        if delete_exists_sample:
            # フォルダ内のファイル一覧を取得
            files = os.listdir(input_folder + self.WITH_SAMPLE_TEXT_FOLDER)

            # ファイルを削除
            for file_name in files:
                file_path = os.path.join(input_folder + self.WITH_SAMPLE_TEXT_FOLDER, file_name)
                try:
                    os.remove(file_path)
                    print(f"ファイル {file_name} を削除しました。")
                except Exception as e:
                    print(f"ファイル {file_name} の削除中にエラーが発生しました: {e}")

        # 入力フォルダから画像ファイルのパスを取得
        image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png'))]

        if len(image_files) == 0:
            print("指定されたフォルダに画像が存在しません。")
            return

        for i, image_file in enumerate(image_files):
            file_name = os.path.basename(image_file).replace(self.IMAGE_FILE_EXTENSION, "")
            base_image = Image.open(os.path.join(input_folder, image_file))

            # 画像に「Sample」のテキストを追加して保存
            sample_text_image = Image.open(self.INPUT_FOLDER + "/sample.png")
            image_with_sample_text = self.merge_images(base_image, sample_text_image)
            image_with_sample_text_file_path = os.path.join(input_folder + self.WITH_SAMPLE_TEXT_FOLDER,
                                                            file_name + "-with-sample-text" + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
            print(f"image_with_sample_text_file_path: {image_with_sample_text_file_path}")
            image_with_sample_text.save(image_with_sample_text_file_path)

        # サムネイルフォルダから画像ファイルのパスを取得
        thumbnail_image_files = [f for f in os.listdir(input_folder + self.THUMBNAIL_FOLDER) if f.endswith(('.png'))]

        if len(thumbnail_image_files) == 0:
            print("指定されたフォルダに画像が存在しません。")
            return

        for i, image_file in enumerate(thumbnail_image_files):
            file_name = os.path.basename(image_file).replace(self.IMAGE_FILE_EXTENSION, "")
            base_image = Image.open(os.path.join(input_folder + self.THUMBNAIL_FOLDER, image_file))

            # 画像に「Sample」のテキストを追加して保存
            sample_text_image = Image.open(self.INPUT_FOLDER + "/sample.png")
            image_with_sample_text = self.merge_images(base_image, sample_text_image)
            image_with_sample_text_file_path = os.path.join(input_folder + self.WITH_SAMPLE_THUMBNAIL_FOLDER,
                                                            file_name + "-with-sample-text" + self.IMAGE_FILE_EXTENSION).replace("\\", "/")
            print(f"image_with_sample_text_file_path: {image_with_sample_text_file_path}")
            image_with_sample_text.save(image_with_sample_text_file_path)

    def get_generation_payload(self):
        """画像生成のペイロードを取得"""
        payload = self.TXT2IMG_BASE_PAYLOAD.copy()

        # スタイルとカテゴリーに応じたペイロード設定
        if self.style == "illustration":
            payload.update({
                "steps": 30,
                "cfg_scale": 8,
                "width": 512,
                "height": 512
            })

        # サブカテゴリーに応じた設定
        if self.subcategory == "transparent":
            payload["enable_hr"] = False

        return payload

    def get_save_path(self, seed_value):
        """画像保存パスを生成"""
        # 日付とシード値でフォルダ名を生成
        today = datetime.today()
        folder_name = today.strftime("%Y%m%d-%H")
        folder_name = f"{folder_name}-{seed_value}{self.OUTPUT_FOLDER_PREFIX}"

        # スタイル/カテゴリー/サブカテゴリーのパスを追加
        base_path = os.path.join(
            self.get_output_path(),
            folder_name
        ).replace("\\", "/")

        return base_path

    def run(self):
        """画像生成の実行"""
        self.load_prompts()

        for _ in range(self.IMAGE_GENERATE_BATCH_EXECUTE_COUNT):
            # プロンプトの生成
            prompt = self.generate_prompt()
            negative_prompt = self.generate_negative_prompt()

            # 画像生成のベースペイロードを設定
            payload = self.get_generation_payload()

            # 画像が生成されるまで繰り返す
            while True:
                generated_images = self.generate_images(
                    prompt,
                    negative_prompt,
                    payload,
                    0  # initial image number
                )

                if generated_images:  # 画像が生成された場合
                    break
                print("キャンセル対象のSeed値だったため、画像の生成を再試行します。")

            # 関連画像および同じSeed値(同一人物)の別バリエーション画像を作成(画像生成時のbatch_size, batch_countを現状1固定のため、ループは1回のみだが将来的に変更される可能性があるためループで処理)
            for folder_path, image_data in generated_images.items():
                filename = image_data['filename']
                seed_value = image_data['seed_value']
                image = image_data['image']
                pnginfo = image_data['pnginfo']

                # 必要な関連画像を作成
                self.generate_related_images(image, folder_path, filename, pnginfo)
                self.save_prompts_to_json(self.DATA_POSITIVE_BASE, self.DATA_POSITIVE_POSE, self.DATA_POSITIVE_OPTIONAL, self.DATA_NEGATIVE, folder_path, filename, [])

                # 生成された画像の別バージョン(同じSeed値でポーズとオプションのプロンプトを変更)を作成
                image_number = 1
                for _ in range(self.ANOTHER_VERSION_GENERATE_COUNT):
                    payload_another_version = self.ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD
                    payload_another_version["seed"] = seed_value
                    # 関数から生成された画像の辞書を取得
                    generated_images = self.generate_images(prompt, negative_prompt, payload_another_version, image_number, folder_path)

                    # 生成された画像の辞書をループで処理
                    for folder_path, image_data in generated_images.items():
                        filename = image_data['filename']
                        seed_value = image_data['seed_value']
                        image = image_data['image']
                        pnginfo = image_data['pnginfo']

                        # 必要な関連画像を作成
                        self.generate_related_images(image, folder_path, str(image_number).zfill(5) + "-" + str(seed_value))
                        self.save_prompts_to_json(self.DATA_POSITIVE_BASE, self.DATA_POSITIVE_POSE, self.DATA_POSITIVE_OPTIONAL, self.DATA_NEGATIVE, folder_path, filename, [])

                    image_number += 1
