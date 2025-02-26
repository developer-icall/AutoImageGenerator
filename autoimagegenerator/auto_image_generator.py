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
import time
import logging

class AutoImageGenerator:

    def __init__(
        self,
        image_generate_batch_execute_count=1,
        another_version_generate_count=11,
        input_folder="./autoimagegenerator/images/input",
        output_folder="./autoimagegenerator/images/output",
        prompts_folder="./autoimagegenerator/prompts",
        url="http://localhost:7860",
        sd_model_checkpoint="Brav6.safetensors",
        sd_model_prefix="brav6",
        enable_hr=False,
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

        # プロンプトの保存先フォルダを画像タイプに応じて設定
        style, category = output_folder_prefix.strip('/').split('/')[:2]
        self.PROMPT_PATH = os.path.join(prompts_folder, style, category).replace('\\', '/')

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
            "height": 768,
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
            "height": 768,
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

        # 透過画像として出力する際に追加する payload
        self.TRANPARENT_PAYLOAD = {
            "script_name": "ABG Remover",
            "script_args": [False, True, False, 0, False]   # 背景除去スクリプトの引数(背景透過画像のみ保存, 自動保存, カスタム背景色使用, 背景色, ランダム背景色使用)
        }
        self.DATA_POSITIVE_BASE = None
        self.DATA_POSITIVE_OPTIONAL = None
        self.DATA_POSITIVE_SELFIE = None
        self.DATA_NEGATIVE = None
        self.DATA_CANCEL_SEEDS = None

        # JSONファイルからデータを読み込む
        try:
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_BASE_FILENAME), 'r') as file:
                self.DATA_POSITIVE_BASE = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_POSE_FILENAME), 'r') as file:
                self.DATA_POSITIVE_POSE = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_OPTIONAL_FILENAME), 'r') as file:
                self.DATA_POSITIVE_OPTIONAL = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_SELFIE_FILENAME), 'r') as file:
                self.DATA_POSITIVE_SELFIE = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.NEGATIVE_PROMPT_FILENAME), 'r') as file:
                self.DATA_NEGATIVE = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME), 'r') as file:
                self.DATA_POSITIVE_CANCEL_PAIR = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.CANCEL_SEEDS_FILENAME), 'r') as file:
                self.DATA_CANCEL_SEEDS = json.load(file)
        except FileNotFoundError as e:
            print(f"エラー: プロンプトファイルが見つかりません: {e.filename}")
            raise

        # Seed の桁数が少ない場合生成される画像の質が低い可能性が高いため、生成をキャンセルする閾値として設定
        self.CANCEL_MIN_SEED_VALUE = 999999999

        # APIのエンドポイントを追加
        self.OPTIONS_URL = f'{self.URL}/sdapi/v1/options'

        # ロガーの設定
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # 画像タイプに応じたフォルダ構造を作成
        self._create_output_directories()

    def _create_output_directories(self):
        """
        画像タイプに応じた出力ディレクトリ構造を作成する
        """
        # スタイル（大項目）
        styles = ["realistic", "illustration"]

        # カテゴリー（中項目）
        categories = {
            "realistic": ["female", "male", "animal"],
            "illustration": ["female", "male", "animal", "background", "rpg_icon", "vehicle", "other"]
        }

        # サブカテゴリー（小項目）
        subcategories = {
            "female": ["normal", "transparent", "selfie"],
            "male": ["normal", "transparent", "selfie"],
            "animal": ["dog", "cat", "bird", "fish", "other"],
            "background": ["nature", "city", "sea", "sky", "other"],
            "rpg_icon": ["weapon", "monster", "other"],
            "vehicle": ["car", "ship", "airplane", "other"]
        }

        # ディレクトリ構造を作成
        for style in styles:
            style_path = os.path.join(self.OUTPUT_FOLDER, style)
            os.makedirs(style_path, exist_ok=True)

            for category in categories[style]:
                category_path = os.path.join(style_path, category)
                os.makedirs(category_path, exist_ok=True)

                # カテゴリーに対応するサブカテゴリーがある場合
                if category in subcategories:
                    for subcategory in subcategories[category]:
                        subcategory_path = os.path.join(category_path, subcategory)
                        os.makedirs(subcategory_path, exist_ok=True)

        self.logger.info("出力ディレクトリ構造を作成しました")

    def _get_output_path(self, style, category, subcategory=None):
        """
        画像タイプに応じた出力パスを取得する

        Args:
            style (str): 画像スタイル（realistic/illustration）
            category (str): 画像カテゴリー（female/male/animal等）
            subcategory (str, optional): 画像サブカテゴリー

        Returns:
            str: 出力パス
        """
        # 基本パス
        output_path = os.path.join(self.OUTPUT_FOLDER, style, category)

        # サブカテゴリーがある場合は追加
        if subcategory:
            output_path = os.path.join(output_path, subcategory)

        # 日時とシード値を含むフォルダ名を作成
        now = datetime.now().strftime("%Y%m%d-%H")
        seed = self.current_seed if hasattr(self, 'current_seed') else random.randint(1, 4294967295)
        folder_name = f"{now}-{seed}"

        # 最終的な出力パス
        final_output_path = os.path.join(output_path, folder_name)
        os.makedirs(final_output_path, exist_ok=True)

        # サブフォルダも作成
        os.makedirs(os.path.join(final_output_path, "thumbnail"), exist_ok=True)
        os.makedirs(os.path.join(final_output_path, "sample"), exist_ok=True)
        os.makedirs(os.path.join(final_output_path, "sample-thumbnail"), exist_ok=True)
        os.makedirs(os.path.join(final_output_path, "half-resolution"), exist_ok=True)

        return final_output_path

    def set_model(self, model_name):
        """モデルを切り替えるためのリクエストを送信"""
        option_payload = {
            "sd_model_checkpoint": model_name
        }

        try:
            # 現在のモデルを確認
            current_model_response = requests.get(self.OPTIONS_URL)
            current_model = current_model_response.json().get("sd_model_checkpoint")

            # 既に指定されたモデルが設定されている場合はスキップ
            if current_model == model_name:
                print(f"モデル {model_name} は既に設定されています")
                return True
            else:
                print(f"モデル {model_name} への切り替えを行います")

            # モデル切り替えリクエスト
            response = requests.post(url=self.OPTIONS_URL, json=option_payload)
            response.raise_for_status()

            # モデルの切り替えが完了するまで待機
            max_retries = 20
            retry_count = 0
            while retry_count < max_retries:
                time.sleep(5)
                verify_response = requests.get(self.OPTIONS_URL)
                current_model = verify_response.json().get("sd_model_checkpoint")
                if current_model == model_name:
                    print(f"モデルを {model_name} に切り替えました")
                    return True
                retry_count += 1

            print(f"モデルの切り替えが確認できませんでした")
            return False

        except requests.exceptions.RequestException as e:
            print(f"モデルの切り替え中にエラーが発生しました: {e}")
            return False

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

        try:
            if self.IS_TRANPARENT_BACKGROUND:
                try:
                    payload = {**payload, **self.TRANPARENT_PAYLOAD}
                    positive_base_prompts = "(no background: 1.3, white background: 1.3), " + positive_base_prompts
                    print(f"透過画像生成モードを有効化しました。使用スクリプト: {self.TRANPARENT_PAYLOAD['script_name']}")
                except Exception as e:
                    print(f"透過画像設定中にエラーが発生しました: {e}")
                    # エラーが発生しても処理を続行

            if self.IS_SELFIE:
                positive_pose_prompts, positive_pose_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_SELFIE)
            else:
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

            # text2imgリクエストの送信
            try:
                response = requests.post(url=self.TEXT2IMG_URL, json=txt2img_payload)

                # 500エラーの場合は即座に終了
                if response.status_code == 500:
                    print(f"サーバーエラー (500): APIサーバーで内部エラーが発生しました")
                    print(f"透過画像生成に失敗した可能性があります。別のモードで試してください。")

                    # Stable Diffusion Web UIのログを取得
                    try:
                        log_response = requests.get(f"{self.URL}/sdapi/v1/log")
                        if log_response.status_code == 200:
                            logs = log_response.json()
                            print(f"Stable Diffusion Web UIのログ (最新10行):")
                            log_lines = logs.get("lines", [])
                            for line in log_lines[-10:]:
                                print(f"  {line}")
                    except Exception as log_error:
                        print(f"ログ取得中にエラーが発生しました: {log_error}")

                    # プログラムを終了
                    import sys
                    sys.exit(1)

                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                # HTTPエラーの詳細情報を取得
                print(f"HTTPエラー: {e}")
                try:
                    error_json = response.json()
                    print(f"サーバーからのエラー詳細: {json.dumps(error_json, indent=2)}")
                except:
                    print(f"サーバーからのレスポンス: {response.text}")

                # Stable Diffusion Web UIのログを取得
                try:
                    log_response = requests.get(f"{self.URL}/sdapi/v1/log")
                    if log_response.status_code == 200:
                        logs = log_response.json()
                        print(f"Stable Diffusion Web UIのログ (最新10行):")
                        log_lines = logs.get("lines", [])
                        for line in log_lines[-10:]:
                            print(f"  {line}")
                    else:
                        print(f"ログの取得に失敗しました: {log_response.status_code}")
                except Exception as log_error:
                    print(f"ログ取得中にエラーが発生しました: {log_error}")

                # エラー発生時にも作成したフォルダを削除
                if 'created_folder_path' in locals() and created_folder_path and os.path.exists(created_folder_path):
                    import shutil
                    try:
                        shutil.rmtree(created_folder_path)
                        print(f"エラー発生のため、フォルダを削除しました: {created_folder_path}")
                    except Exception as e2:
                        print(f"フォルダの削除中にエラーが発生しました: {e2}")

                # 500エラーの場合はプログラムを終了
                if response.status_code == 500:
                    print(f"致命的なサーバーエラーのため、プログラムを終了します")
                    import sys
                    sys.exit(1)

                return {}

            r = response.json()
            images_processed_count = 0
            seed_value = 0
            paramteters = ""
            created_folder_path = None

            for i in r['images']:
                images_processed_count = images_processed_count + 1
                image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

                # 透過画像生成時は最初の１つ目の r['images'] にのみ PNG 画像情報があるので、そこから各種値を取得
                if seed_value == 0:
                    png_payload = {
                        "image": "data:image/png;base64," + i
                    }
                    response2 = requests.post(url=self.PNGINFO_URL, json=png_payload)

                    # 正規表現を使用してSeedの値を抽出
                    match = re.search(r"Seed:\s*(\d+)", response2.json().get("info"))

                    if match:
                        seed_value = int(match.group(1))
                        # 現在のシードを保存
                        self.current_seed = seed_value
                    else:
                        print("Seedが見つかりませんでした。")

                    if paramteters == "":
                        paramteters = response2.json().get("info")

                # 透過画像生成時は３つ目の画像のみを保存するため、１つ目と２つ目はスキップ
                if self.IS_TRANPARENT_BACKGROUND and images_processed_count != 3:
                    continue

                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", paramteters)

                # 画像タイプに応じた出力パスを取得
                if folder_path is None:
                    # OUTPUT_FOLDER_PREFIXからスタイル、カテゴリー、サブカテゴリーを取得
                    path_parts = self.OUTPUT_FOLDER_PREFIX.strip('/').split('/')
                    style = path_parts[0]
                    category = path_parts[1]
                    subcategory = path_parts[2] if len(path_parts) > 2 else None

                    # サブカテゴリーが指定されていない場合、デフォルト値を設定
                    if subcategory is None:
                        if self.IS_TRANPARENT_BACKGROUND:
                            subcategory = "transparent"
                        elif self.IS_SELFIE:
                            subcategory = "selfie"
                        else:
                            subcategory = "normal"

                    folder_path = self._get_output_path(style, category, subcategory)
                    created_folder_path = folder_path

                # キャンセル対象のSeed値かチェック
                is_cancel_seed = False
                for seed in self.DATA_CANCEL_SEEDS["Seeds"]:
                    if seed_value == seed:
                        print(f"folder_path: {folder_path} のSeed値はキャンセル対象です。")
                        is_cancel_seed = True
                        break

                # Seed値が閾値よりも小さい場合もキャンセル
                if seed_value <= self.CANCEL_MIN_SEED_VALUE:
                    print(f"folder_path: {folder_path} のSeed値は閾値よりも小さいのでキャンセル対象です。")
                    is_cancel_seed = True

                # キャンセル対象の場合、作成したフォルダを削除して空の結果を返す
                if is_cancel_seed:
                    if created_folder_path and os.path.exists(created_folder_path):
                        import shutil
                        try:
                            shutil.rmtree(created_folder_path)
                            print(f"キャンセル対象のため、フォルダを削除しました: {created_folder_path}")
                        except Exception as e:
                            print(f"フォルダの削除中にエラーが発生しました: {e}")
                    return {}

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

        except requests.exceptions.RequestException as e:
            print(f"画像生成中にエラーが発生しました: {e}")

            # Stable Diffusion Web UIのログを取得
            try:
                log_response = requests.get(f"{self.URL}/sdapi/v1/log")
                if log_response.status_code == 200:
                    logs = log_response.json()
                    print(f"Stable Diffusion Web UIのログ (最新10行):")
                    log_lines = logs.get("lines", [])
                    for line in log_lines[-10:]:
                        print(f"  {line}")
                else:
                    print(f"ログの取得に失敗しました: {log_response.status_code}")
            except Exception as log_error:
                print(f"ログ取得中にエラーが発生しました: {log_error}")

            # エラー発生時にも作成したフォルダを削除
            if 'created_folder_path' in locals() and created_folder_path and os.path.exists(created_folder_path):
                import shutil
                try:
                    shutil.rmtree(created_folder_path)
                    print(f"エラー発生のため、フォルダを削除しました: {created_folder_path}")
                except Exception as e2:
                    print(f"フォルダの削除中にエラーが発生しました: {e2}")
            return {}

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


    def run(self):
        """画像生成の実行"""
        # 最初にモデルを切り替え
        if not self.set_model(self.SD_MODEL_CHECKPOINT):
            print("モデルの切り替えに失敗したため、処理を中止します")
            return

        for _ in tqdm(range(self.IMAGE_GENERATE_BATCH_EXECUTE_COUNT)):
            # すべてのキーに対してランダムなプロンプトを生成
            positive_base_prompts, positive_base_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_BASE)
            negative_prompts, negative_prompt_dict = self.generate_random_prompts(self.DATA_NEGATIVE)

            # 画像が生成されるまで繰り返す
            while True:
                # 関数から生成された画像の辞書を取得
                generated_images = self.generate_images(positive_base_prompts, negative_prompts, self.TXT2IMG_BASE_PAYLOAD, 0)

                if len(generated_images) == 0:
                    print("キャンセル対象の Seed 値だったため、画像の生成を再試行しました。")
                else:
                    break  # 画像が生成された場合、ループを終了

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
