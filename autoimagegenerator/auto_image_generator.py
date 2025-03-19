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
import glob
import math
import shutil

class AutoImageGenerator:

    def __init__(
        self,
        image_generate_batch_execute_count=1,
        another_version_generate_count=11,
        input_folder="./images/input",
        output_folder="./images/output",
        prompts_folder="./prompts",
        url="http://localhost:7860",
        sd_model_checkpoint="Brav6.safetensors",
        sd_model_prefix="brav6",
        enable_hr=False,
        output_folder_prefix="",
        is_transparent_background=False,
        is_selfie=False,
        style="realistic",
        category="female",
        subcategory="normal",
        width=None,
        height=None,
        use_custom_checkpoint=False,
        use_lora=False,
        lora_name=None,
        dry_run=False
    ):
        # 設定ファイルの読み込み
        self.settings = self._load_settings()

        # ドライランモードの設定
        self.dry_run = dry_run

        # モデル切り替えが実行済みかどうかを管理するフラグを追加
        self._model_switch_executed = False
        # 現在使用中のモデルを記録
        self._current_model = None

        # LoRAの設定
        self.USE_LORA = use_lora
        self.LORA_NAME = lora_name

        # 画像タイプの設定を追加
        self.style = style
        self.category = category
        self.subcategory = subcategory

        # パラメータから受け取った値をプロパティへセット
        # 画像生成バッチの実行回数を指定
        self.IMAGE_GENERATE_BATCH_EXECUTE_COUNT = image_generate_batch_execute_count

        # 生成された画像の別バージョン(同じSeed値でオプションのプロンプトを変更)を作成する回数を指定
        self.ANOTHER_VERSION_GENERATE_COUNT = another_version_generate_count

        # 絶対パスを取得するためのベースディレクトリ
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 生成時に利用する画像の保存先フォルダのルートパス（絶対パスに変換）
        self.INPUT_FOLDER = os.path.abspath(input_folder)
        # 生成された画像の保存先フォルダのルートパス（絶対パスに変換）
        self.OUTPUT_FOLDER = os.path.abspath(output_folder)
        # プロンプトファイルの保存先フォルダのルートパス（絶対パスに変換）
        self.PROMPTS_FOLDER = os.path.abspath(prompts_folder)

        # Stable Diffusion Web UI APIのURL
        self.URL = url
        self.OPTIONS_URL = f'{self.URL}/sdapi/v1/options'
        # txt2imgエンドポイントを明示的に指定
        self.TXT2IMG_URL = f'{self.URL}/sdapi/v1/txt2img'
        self.PNGINFO_URL = f'{self.URL}/sdapi/v1/png-info'

        # 使用するモデルのチェックポイント
        self.SD_MODEL_CHECKPOINT = sd_model_checkpoint
        self.SD_MODEL_PREFIX = sd_model_prefix

        # カスタムチェックポイントを使用するかどうか
        self.USE_CUSTOM_CHECKPOINT = use_custom_checkpoint

        # ハイレゾ画像生成の有効/無効
        self.ENABLE_HR = enable_hr

        # 出力フォルダのプレフィックス
        self.OUTPUT_FOLDER_PREFIX = output_folder_prefix

        # 透過背景の有効/無効
        self.IS_TRANSPARENT_BACKGROUND = is_transparent_background

        # セルフィーの有効/無効
        self.IS_SELFIE = is_selfie

        # 定数定義 - _get_prompt_folder_pathより前に定義
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

        # ロガーの設定
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # INFOからDEBUGに変更
        if not self.logger.handlers:
            # コンソール出力用ハンドラ
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # ログディレクトリの作成
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)

            # auto_image_generatorログ用のサブディレクトリを作成
            auto_image_generator_log_dir = os.path.join(log_dir, 'auto_image_generator')
            os.makedirs(auto_image_generator_log_dir, exist_ok=True)

            # ファイル出力用ハンドラ
            log_file = os.path.join(auto_image_generator_log_dir, f"auto_image_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            self.logger.info(f"ログファイルを作成しました: {log_file}")

        # 画像タイプに応じたフォルダ構造を作成
        self._create_output_directories()

        # 画像タイプに基づいて適切なモデルを選択
        # カスタムチェックポイントが指定されている場合は、モデル選択をスキップ
        if self.USE_CUSTOM_CHECKPOINT:
            self.model = self.SD_MODEL_PREFIX
            self.logger.info(f"カスタムチェックポイント {self.SD_MODEL_CHECKPOINT} を使用します")
        else:
            self.model = self._select_model_by_image_type()
            # 選択されたモデルに基づいてSD_MODEL_CHECKPOINTを更新
            if self.model != self.SD_MODEL_PREFIX:
                try:
                    from main import SD_MODEL_CHECKPOINTS
                    if self.model in SD_MODEL_CHECKPOINTS:
                        self.SD_MODEL_CHECKPOINT = SD_MODEL_CHECKPOINTS[self.model]
                        self.logger.info(f"画像タイプに基づいて {self.model} モデル ({self.SD_MODEL_CHECKPOINT}) を使用します")
                    else:
                        self.logger.warning(f"警告: モデル {self.model} のチェックポイントが見つかりません")
                        self.logger.info(f"デフォルトモデル {self.SD_MODEL_CHECKPOINT} を使用します")
                except (ImportError, KeyError) as e:
                    self.logger.warning(f"警告: モデルチェックポイントの取得中にエラーが発生しました: {e}")
                    self.logger.info(f"デフォルトモデル {self.SD_MODEL_CHECKPOINT} を使用します")

        # 画像サイズを設定
        self.width = width if width is not None else 768  # デフォルト値を設定
        self.height = height if height is not None else 768  # デフォルト値を設定
        self._set_image_size_by_type()

        # 共通のpayload設定を定義
        self.COMMON_PAYLOAD_SETTINGS = {
            "steps": 50,
            "width": self.width,
            "height": self.height,
            "cfg_scale": 7,
            "batch_size": 1,
            "batch_count": 1,
            "sampler_name": "DPM++ 2M",
            "Schedule type": "Karras",
            "sd_model_checkpoint": self.SD_MODEL_CHECKPOINT,
            "enable_hr": enable_hr,
            "hr_scale": 2,
            "hr_upscaler": "4x-UltraSharp",
            "hr_second_pass_steps": 20,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "hr_checkpoint_name": self.SD_MODEL_CHECKPOINT,
            "hr_additional_modules": [],
            "hr_sampler_name": "DPM++ 2M",
            "hr_scheduler": "Karras",
            "hr_cfg": 7,
            "hr_distilled_cfg": 3.5,
            "denoising_strength": 0.3
        }

        # text2imgのベースとなるpayload
        self.TXT2IMG_BASE_PAYLOAD = {
            "seed": -1,
            **self.COMMON_PAYLOAD_SETTINGS
        }

        # 生成された画像の別バージョン作成時のtext2imgのベースとなるpayload
        self.ANOTHER_VERSION_TXT2IMG_BASE_PAYLOAD = {
            **self.COMMON_PAYLOAD_SETTINGS
        }

        # 透過画像として出力する際に追加する payload
        self.TRANPARENT_PAYLOAD = {
            "script_name": "ABG Remover",
            "script_args": [False, True, False, 0, False]   # 背景除去スクリプトの引数(背景透過画像のみ保存, 自動保存, カスタム背景色使用, 背景色, ランダム背景色使用)
            # 注意: ABG Removerを使用すると、3つの画像が生成されます:
            # 1つ目：元の画像（PNGInfo付き）
            # 2つ目：マスク画像
            # 3つ目：透過背景画像（実際に使用する画像）
        }
        self.DATA_POSITIVE_BASE = None
        self.DATA_POSITIVE_OPTIONAL = None
        self.DATA_POSITIVE_SELFIE = None
        self.DATA_NEGATIVE = None
        self.DATA_CANCEL_SEEDS = None

        # JSONファイルからデータを読み込む
        try:
            # プロンプトの保存先フォルダを画像タイプに応じて設定
            self.PROMPT_PATH = self._get_prompt_folder_path()

            # 各ファイルのフルパスを取得
            positive_base_path = os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_BASE_FILENAME)

            # ファイルが存在しない場合は、既存のプロンプトファイルを探す
            if not os.path.exists(positive_base_path):
                # 既存のプロンプトファイルを探す
                legacy_paths = [
                    os.path.join("autoimagegenerator", "prompts", self.POSITIVE_PROMPT_BASE_FILENAME),
                    os.path.join("autoimagegenerator", "prompts", "default", self.POSITIVE_PROMPT_BASE_FILENAME)
                ]

                for path in legacy_paths:
                    if os.path.exists(path):
                        positive_base_path = path
                        self.PROMPT_PATH = os.path.dirname(path)
                        break

            # ファイルを読み込む
            with open(positive_base_path, 'r', encoding='utf-8') as file:
                self.DATA_POSITIVE_BASE = json.load(file)

            # 以下同様に他のファイルも読み込む
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_POSE_FILENAME), 'r', encoding='utf-8') as file:
                self.DATA_POSITIVE_POSE = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_OPTIONAL_FILENAME), 'r', encoding='utf-8') as file:
                self.DATA_POSITIVE_OPTIONAL = json.load(file)

            # 動物カテゴリーの場合はセルフィープロンプトをスキップ
            if self.category != "animal":
                with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_SELFIE_FILENAME), 'r', encoding='utf-8') as file:
                    self.DATA_POSITIVE_SELFIE = json.load(file)
            else:
                # 動物カテゴリーの場合は空の辞書を設定
                self.DATA_POSITIVE_SELFIE = {}
                self.logger.info("動物カテゴリーのため、セルフィープロンプトをスキップします")

            with open(os.path.join(self.PROMPT_PATH, self.NEGATIVE_PROMPT_FILENAME), 'r', encoding='utf-8') as file:
                self.DATA_NEGATIVE = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME), 'r', encoding='utf-8') as file:
                self.DATA_POSITIVE_CANCEL_PAIR = json.load(file)
            with open(os.path.join(self.PROMPT_PATH, self.CANCEL_SEEDS_FILENAME), 'r', encoding='utf-8') as file:
                self.DATA_CANCEL_SEEDS = json.load(file)
        except FileNotFoundError as e:
            self.logger.error(f"エラー: プロンプトファイルが見つかりません: {e.filename}")
            raise

        # Seed の桁数が少ない場合生成される画像の質が低い可能性が高いため、生成をキャンセルする閾値として設定
        self.CANCEL_MIN_SEED_VALUE = 999999999

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
        # パスを正規化（スラッシュの統一）
        final_output_path = os.path.normpath(final_output_path)
        os.makedirs(final_output_path, exist_ok=True)

        # サブフォルダも作成
        os.makedirs(os.path.normpath(os.path.join(final_output_path, "thumbnail")), exist_ok=True)
        os.makedirs(os.path.normpath(os.path.join(final_output_path, "sample")), exist_ok=True)
        os.makedirs(os.path.normpath(os.path.join(final_output_path, "sample-thumbnail")), exist_ok=True)
        os.makedirs(os.path.normpath(os.path.join(final_output_path, "half-resolution")), exist_ok=True)

        return final_output_path

    def set_model(self, model_name):
        """モデルを切り替えるためのリクエストを送信（最初の1回のみ実行）"""
        # 既にモデル切り替えが実行済みの場合はスキップ
        if self._model_switch_executed:
            self.logger.info("モデル切り替えは既に実行済みのため、スキップします")
            return True

        self.logger.info(f"モデル切り替え開始: {model_name}")

        try:
            # 現在のモデルを確認
            current_model_response = requests.get(self.OPTIONS_URL)
            current_model = current_model_response.json().get("sd_model_checkpoint")
            self.logger.info(f"現在のモデル: {current_model}")

            # 既に指定されたモデルが設定されている場合はスキップ
            if current_model == model_name:
                self.logger.info(f"モデル {model_name} は既に設定されています")
                self._model_switch_executed = True
                return True

            # _switch_modelを呼び出してモデルを切り替え
            self._switch_model(model_name)

            # モデルの切り替えが完了するまで待機
            max_retries = 20
            retry_count = 0
            while retry_count < max_retries:
                time.sleep(5)
                verify_response = requests.get(self.OPTIONS_URL)
                current_model = verify_response.json().get("sd_model_checkpoint")
                self.logger.info(f"モデル切り替え確認 (試行 {retry_count+1}/{max_retries}): 現在のモデル = {current_model}")

                if current_model == model_name:
                    self.logger.info(f"モデルを {model_name} に切り替えました")
                    self._model_switch_executed = True
                    return True
                retry_count += 1

            self.logger.error(f"モデルの切り替えが確認できませんでした。最終モデル: {current_model}")
            return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"モデルの切り替え中にエラーが発生しました: {e}")
            return False

    # ランダムなプロンプトを生成
    def generate_random_prompts(self, data):
        combined_prompt = []
        prompt_json = {}

        # 位置指定のあるカテゴリを保存するための辞書
        positioned_prompts = {
            "start": [],  # 先頭に配置するプロンプト
            "end": []     # 末尾に配置するプロンプト
        }

        # デバッグログを追加
        logging.info(f"generate_random_prompts開始。データキー: {list(data.keys())}")

        # 最初にすべてのカテゴリーのプロンプトを収集
        all_selected_prompts = {}

        # 最初のパスでプロンプトを選択
        for key, value in data.items():
            if isinstance(value, dict):
                # 条件チェックがある場合はスキップ（2回目のパスで処理）
                if "condition" in value:
                    continue

                use_max_prompts = value.get("use_max_prompts", 0)
                use_min_prompts = value.get("use_min_prompts", 0)
                prompts = value.get("prompts", [])
                position = value.get("position", None)  # 位置パラメータを取得

                # デバッグログを追加
                logging.info(f"カテゴリー: {key}, use_max_prompts: {use_max_prompts}, use_min_prompts: {use_min_prompts}, プロンプト数: {len(prompts)}, position: {position}")

                # ランダムな数のプロンプトを取得
                num_prompts = random.randint(use_min_prompts, use_max_prompts)
                selected_prompts = random.sample(prompts, min(num_prompts, len(prompts)))

                # 選択結果をログに出力
                logging.info(f"カテゴリー: {key}, 選択数: {num_prompts}, 選択結果: {selected_prompts}")

                # 結果を保存
                prompt_json[key] = selected_prompts
                all_selected_prompts[key] = selected_prompts

                # 位置指定がある場合は、対応するリストに追加
                if position in positioned_prompts:
                    positioned_prompts[position].extend(selected_prompts)
                    logging.info(f"カテゴリー: {key} のプロンプトを位置 {position} に配置します")
                else:
                    # 位置指定がない場合は通常通り追加
                    combined_prompt.extend(selected_prompts)

        # 2回目のパスで条件付きプロンプトを処理
        for key, value in data.items():
            if isinstance(value, dict) and "condition" in value:
                condition = value["condition"]
                condition_category = condition.get("category", "")
                condition_contains = condition.get("contains", [])
                position = value.get("position", None)  # 位置パラメータを取得

                # デバッグログを追加
                logging.info(f"条件付きカテゴリー: {key}, 条件カテゴリー: {condition_category}, 条件文字列: {condition_contains}, position: {position}")

                # 条件をチェック
                should_include = False
                if condition_category in all_selected_prompts:
                    category_prompts = all_selected_prompts[condition_category]
                    # いずれかの条件が含まれているかチェック
                    for prompt in category_prompts:
                        for contains_str in condition_contains:
                            if contains_str in prompt:
                                should_include = True
                                logging.info(f"条件一致: プロンプト '{prompt}' に '{contains_str}' が含まれています")
                                break
                        if should_include:
                            break

                # 条件が満たされた場合のみプロンプトを追加
                if should_include:
                    use_max_prompts = value.get("use_max_prompts", 0)
                    use_min_prompts = value.get("use_min_prompts", 0)
                    prompts = value.get("prompts", [])

                    # ランダムな数のプロンプトを取得
                    num_prompts = random.randint(use_min_prompts, use_max_prompts)
                    selected_prompts = random.sample(prompts, min(num_prompts, len(prompts)))

                    # 選択結果をログに出力
                    logging.info(f"条件付きカテゴリー: {key}, 条件満たす: True, 選択数: {num_prompts}, 選択結果: {selected_prompts}")

                    # 結果を保存
                    prompt_json[key] = selected_prompts
                    all_selected_prompts[key] = selected_prompts

                    # 位置指定がある場合は、対応するリストに追加
                    if position in positioned_prompts:
                        positioned_prompts[position].extend(selected_prompts)
                        logging.info(f"条件付きカテゴリー: {key} のプロンプトを位置 {position} に配置します")
                    else:
                        # 位置指定がない場合は通常通り追加
                        combined_prompt.extend(selected_prompts)
                else:
                    logging.info(f"条件付きカテゴリー: {key}, 条件満たす: False")

        # 位置指定されたプロンプトを適切な位置に配置
        final_prompt = positioned_prompts["start"] + combined_prompt + positioned_prompts["end"]

        # 最終結果をログに出力
        logging.info(f"generate_random_prompts完了。結果: {json.dumps(prompt_json, indent=2, ensure_ascii=False)[:500]}...")
        logging.info(f"位置指定プロンプト: start={positioned_prompts['start']}, end={positioned_prompts['end']}")
        logging.info(f"最終プロンプト順序: {final_prompt}")

        return ", ".join(final_prompt), prompt_json

    # 必要な関連画像を作成
    def generate_related_images(self, base_image, folder_path, filename, pnginfo=None):

        # 画像に「Sample」のテキストを追加して保存
        sample_text_image_path = os.path.join(self.INPUT_FOLDER, "sample.png")

        # サンプル画像が存在するか確認
        if os.path.exists(sample_text_image_path):
            sample_text_image = Image.open(sample_text_image_path)
            image_with_sample_text = self.merge_images(base_image, sample_text_image)
        else:
            # サンプル画像が存在しない場合は、テキストを直接描画
            logging.warning(f"サンプル画像が見つかりません: {sample_text_image_path}")
            image_with_sample_text = base_image.copy()
            # テキストを描画するためのDrawオブジェクトを作成
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image_with_sample_text)
            # フォントサイズは画像サイズに応じて調整
            font_size = max(10, min(base_image.width, base_image.height) // 10)
            try:
                # フォントを読み込む（システムフォントを使用）
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                # フォントが見つからない場合はデフォルトフォントを使用
                font = ImageFont.load_default()
            # テキストを描画
            draw.text((10, 10), "SAMPLE", fill=(255, 0, 0, 255), font=font)

        sample_folder = os.path.normpath(os.path.join(folder_path, "sample"))
        image_with_sample_text_file_path = os.path.normpath(os.path.join(sample_folder,
                                                         filename + "-with-sample-text" + self.IMAGE_FILE_EXTENSION))
        # フォルダが存在しない場合は作成
        if not os.path.exists(sample_folder):
            os.makedirs(sample_folder)

        image_with_sample_text.save(image_with_sample_text_file_path)

        # サムネイル用画像を生成して保存
        thumbnail_ratio = 2
        if self.ENABLE_HR == True:
            thumbnail_ratio = 4

        # 画像サイズが小さい場合は、サムネイルのサイズを調整
        new_width = max(1, base_image.width // thumbnail_ratio)
        new_height = max(1, base_image.height // thumbnail_ratio)
        thumbnail_image = base_image.resize((new_width, new_height))
        thumbnail_filename = f"{filename}-thumbnail"
        thumbnail_folder = os.path.normpath(os.path.join(folder_path, "thumbnail"))
        thumbnail_file_path = os.path.normpath(os.path.join(thumbnail_folder,
                                                 thumbnail_filename + self.IMAGE_FILE_EXTENSION))
        if not os.path.exists(thumbnail_folder):
            os.makedirs(thumbnail_folder)
        thumbnail_image.save(thumbnail_file_path)

        # サンプルサムネイル画像を生成して保存
        if os.path.exists(sample_text_image_path):
            # サンプル画像が存在する場合
            sample_text_image = Image.open(sample_text_image_path)
            image_with_sample_text = self.merge_images(thumbnail_image, sample_text_image)
        else:
            # サンプル画像が存在しない場合は、テキストを直接描画
            image_with_sample_text = thumbnail_image.copy()
            # テキストを描画するためのDrawオブジェクトを作成
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image_with_sample_text)
            # フォントサイズは画像サイズに応じて調整
            font_size = max(5, min(thumbnail_image.width, thumbnail_image.height) // 10)
            try:
                # フォントを読み込む（システムフォントを使用）
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                # フォントが見つからない場合はデフォルトフォントを使用
                font = ImageFont.load_default()
            # テキストを描画
            draw.text((5, 5), "SAMPLE", fill=(255, 0, 0, 255), font=font)

        sample_thumbnail_folder = os.path.normpath(os.path.join(folder_path, "sample-thumbnail"))
        image_with_sample_text_file_path = os.path.normpath(os.path.join(sample_thumbnail_folder,
                                                         thumbnail_filename + "-with-sample-text" + self.IMAGE_FILE_EXTENSION))
        if not os.path.exists(sample_thumbnail_folder):
            os.makedirs(sample_thumbnail_folder)
        image_with_sample_text.save(image_with_sample_text_file_path)

        if self.ENABLE_HR == True:
            # 半分の解像度の画像を生成して保存
            new_width = max(1, base_image.width // 2)
            new_height = max(1, base_image.height // 2)
            half_resolution_image = base_image.resize((new_width, new_height), Image.LANCZOS)
            half_resolution_filename = f"{filename}-half-resolution"
            half_resolution_folder = os.path.normpath(os.path.join(folder_path, "half-resolution"))
            half_resolution_file_path = os.path.normpath(os.path.join(half_resolution_folder,
                                                      half_resolution_filename + self.IMAGE_FILE_EXTENSION))
            if not os.path.exists(half_resolution_folder):
                os.makedirs(half_resolution_folder)
            half_resolution_image.save(half_resolution_file_path)

        return {}

    def save_prompts_to_json(self, positive_base_prompt_dict, positive_pose_prompt_dict, positive_optional_prompt_dict, negative_prompt_dict, folder_path, filename, cancel_prompts):
        """
        プロンプト情報をJSONファイルに保存する

        Args:
            positive_base_prompt_dict (dict): ベースプロンプト辞書
            positive_pose_prompt_dict (dict): ポーズプロンプト辞書
            positive_optional_prompt_dict (dict): オプショナルプロンプト辞書
            negative_prompt_dict (dict): ネガティブプロンプト辞書
            folder_path (str): 保存先フォルダパス
            filename (str): ファイル名（拡張子なし）
            cancel_prompts (list): キャンセルされたプロンプトのリスト

        Returns:
            dict: 空の辞書
        """
        # モデル情報を取得（ファイル名から拡張子を除去）
        model_name = os.path.splitext(self.SD_MODEL_CHECKPOINT)[0]

        # 元のフォーマットを維持（元のプロンプト辞書をそのまま使用）
        merged_dict = {
            "sd_model": model_name,
            "sd_model_checkpoint": self.SD_MODEL_CHECKPOINT
        }

        # 各辞書を順番にマージ
        for dict_name, dict_obj in [
            ("positive_pose", positive_pose_prompt_dict),
            ("positive_base", positive_base_prompt_dict),
            ("positive_optional", positive_optional_prompt_dict),
            ("negative", negative_prompt_dict)
        ]:
            # 辞書の内容をマージ
            for key, value in dict_obj.items():
                if key not in merged_dict:
                    merged_dict[key] = value

        # キャンセルされたプロンプトがある場合は追加
        if len(cancel_prompts) > 0:
            merged_dict["cancel_prompts"] = cancel_prompts

        # PNGInfoから取得した実際のプロンプト情報を追加（オプション）
        if hasattr(self, 'current_png_info') and self.current_png_info:
            # 実際のプロンプト情報を別のキーとして追加
            if "prompt" in self.current_png_info:
                merged_dict["actual_prompt"] = self.current_png_info["prompt"]
                logging.info(f"実際のプロンプトをJSONに保存します: {self.current_png_info['prompt'][:100]}...")

            if "negative_prompt" in self.current_png_info:
                merged_dict["actual_negative_prompt"] = self.current_png_info["negative_prompt"]
                logging.info(f"実際のネガティブプロンプトをJSONに保存します: {self.current_png_info['negative_prompt'][:100]}...")

            # シード値を追加
            if "seed" in self.current_png_info:
                merged_dict["seed"] = self.current_png_info["seed"]
        else:
            logging.warning("current_png_infoが設定されていません")
            # 代替手段として、生のパラメータから情報を抽出
            if hasattr(self, 'current_parameters') and self.current_parameters:
                lines = self.current_parameters.split('\n')
                if lines:
                    merged_dict["actual_prompt"] = lines[0].strip()
                    logging.info(f"代替手段で実際のプロンプトをJSONに保存します: {lines[0].strip()[:100]}...")

                    # Negative promptを探す
                    for i, line in enumerate(lines):
                        if line.startswith("Negative prompt:"):
                            merged_dict["actual_negative_prompt"] = line[len("Negative prompt:"):].strip()
                            logging.info(f"代替手段で実際のネガティブプロンプトをJSONに保存します: {line[len('Negative prompt:'):].strip()[:100]}...")
                            break

                    # Seedを探す
                    seed_match = re.search(r"Seed:\s*(\d+)", self.current_parameters)
                    if seed_match:
                        merged_dict["seed"] = int(seed_match.group(1))

        # プロンプトをJSONファイルに保存
        json_filename = os.path.normpath(os.path.join(folder_path, filename + ".json"))
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(merged_dict, json_file, indent=4, ensure_ascii=False)

        return {}

    # 画像の合成
    def merge_images(self, background_image, transparent_image):
        # 背景画像がRGBAでない場合は変換
        if background_image.mode != "RGBA":
            background_image = background_image.convert("RGBA")

        # 透過画像がRGBAでない場合は変換
        if transparent_image.mode != "RGBA":
            transparent_image = transparent_image.convert("RGBA")

        # 透過画像を背景画像のサイズに合わせる
        transparent_image = transparent_image.resize(background_image.size)

        try:
            # 透過画像を背景画像に合成
            result_image = Image.alpha_composite(background_image, transparent_image)
        except ValueError as e:
            # エラーが発生した場合はログに記録し、背景画像をそのまま返す
            logging.warning(f"画像の合成中にエラーが発生しました: {e}")
            logging.warning(f"背景画像: サイズ={background_image.size}, モード={background_image.mode}")
            logging.warning(f"透過画像: サイズ={transparent_image.size}, モード={transparent_image.mode}")
            result_image = background_image

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

    def _select_model_by_image_type(self):
        """画像タイプに基づいて適切なモデルを選択する"""
        # リアルテイスト画像の場合
        if self.style == "realistic":
            if self.category == "female":
                # 女性の場合
                if self.SD_MODEL_PREFIX == "yayoiMix":
                    return "yayoiMix"  # yayoiMixが指定されている場合はそれを使用
                else:
                    # それ以外はbrav6またはbrav7を使用
                    return self.SD_MODEL_PREFIX
            elif self.category == "male":
                # 男性の場合
                if self.SD_MODEL_PREFIX == "yayoiMix":
                    return "yayoiMix"  # yayoiMixが指定されている場合はそれを使用
                elif self.SD_MODEL_PREFIX == "brav7":
                    return "brav7_men"
                else:
                    return self.SD_MODEL_PREFIX
            elif self.category == "animal":
                # 動物の場合はpetPhotographyを使用
                return "petPhotography"
            elif self.category == "vehicle":
                # 乗り物の場合はsd_xl_base_1.0を使用
                return "sd_xl_base_1.0"
            elif self.category == "background":
                # 背景の場合はlandscapeRealisticを使用
                return "landscapeRealistic"

        # イラスト風画像の場合
        elif self.style == "illustration":
            if self.category == "rpg_icon":
                # RPGアイコン用モデル
                # SD_MODEL_PREFIXがRPGIconの場合はそれを使用、それ以外はphotoRealRPG（photoRealV15_photorealv21）を使用
                if self.SD_MODEL_PREFIX == "RPGIcon":
                    return "RPGIcon"
                else:
                    return "photoRealRPG"
            elif self.category in ["female", "male"]:
                # イラスト系の人物モデル
                if self.SD_MODEL_PREFIX == "animagineXL":
                    return "animagineXL"  # animagineXLが指定されている場合はそれを使用
                else:
                    # それ以外は暫定的にbrav7を使用
                    if self.category == "male":
                        return "brav7_men"
                    else:
                        return "brav7"
            elif self.category == "animal":
                # イラスト系の動物モデル
                return "animagineXL"
            elif self.category == "background":
                # 背景用モデル
                return "landscapeRealistic"
            elif self.category == "vehicle":
                # 乗り物用モデル
                return "sd_xl_base_1.0"
            elif self.category == "other":
                # その他のカテゴリ（将来的に追加予定）
                return "brav7"  # 仮のモデル名

        # デフォルトモデル
        return self.SD_MODEL_PREFIX

    def _get_prompt_folder_path(self):
        """プロンプトフォルダのパスを取得する"""
        # スタイル、カテゴリーに基づいてパスを生成
        base_path_components = [self.PROMPTS_FOLDER, self.style, self.category]
        base_path = os.path.join(*base_path_components)

        # デバッグ用にパスを出力
        self.logger.debug(f"プロンプトの基本パス: {base_path}")

        # サブカテゴリーが指定されている場合は、サブカテゴリーのパスを試す
        if self.subcategory:
            subcategory_path = os.path.join(base_path, self.subcategory)

            # サブカテゴリーのパスが存在する場合はそれを使用
            if os.path.exists(subcategory_path):
                self.logger.info(f"サブカテゴリーのプロンプトフォルダを使用します: {subcategory_path}")
                return subcategory_path
            else:
                self.logger.info(f"サブカテゴリーのプロンプトフォルダが見つかりません: {subcategory_path}")
                self.logger.info(f"カテゴリーのプロンプトフォルダを使用します: {base_path}")

        # サブカテゴリーが指定されていない、または存在しない場合はカテゴリーのパスを使用
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"プロンプトフォルダが見つかりません: {base_path}")

        return base_path

    def _load_prompt_files(self):
        """プロンプトファイルを読み込む"""
        # プロンプトフォルダのパスを取得
        prompt_folder_path = self._get_prompt_folder_path()

        # 各種プロンプトファイルのパスを生成
        positive_base_path = os.path.join(prompt_folder_path, self.POSITIVE_PROMPT_BASE_FILENAME)
        positive_optional_path = os.path.join(prompt_folder_path, self.POSITIVE_PROMPT_OPTIONAL_FILENAME)
        positive_pose_path = os.path.join(prompt_folder_path, self.POSITIVE_PROMPT_POSE_FILENAME)
        positive_selfie_path = os.path.join(prompt_folder_path, self.POSITIVE_PROMPT_SELFIE_FILENAME)
        negative_path = os.path.join(prompt_folder_path, self.NEGATIVE_PROMPT_FILENAME)
        cancel_seeds_path = os.path.join(prompt_folder_path, self.CANCEL_SEEDS_FILENAME)
        positive_cancel_pair_path = os.path.join(prompt_folder_path, self.POSITIVE_PROMPT_CANCEL_PAIR_FILENAME)

        # 各ファイルが存在するか確認し、存在しない場合はカテゴリのフォルダから読み込む
        base_path = os.path.join(self.PROMPTS_FOLDER, self.style, self.category)

        # 各ファイルを読み込む関数
        def load_json_file(file_path, fallback_path=None):
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif fallback_path and os.path.exists(fallback_path):
                self.logger.info(f"ファイルが見つかりません: {file_path}")
                self.logger.info(f"代わりにカテゴリのファイルを使用します: {fallback_path}")
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"ファイルが見つかりません: {file_path}")
                return {}

        # 各ファイルを読み込む（サブカテゴリのファイルが存在しない場合はカテゴリのファイルを使用）
        self.DATA_POSITIVE_BASE = load_json_file(
            positive_base_path,
            os.path.join(base_path, "positive_base.json")
        )
        self.DATA_POSITIVE_OPTIONAL = load_json_file(
            positive_optional_path,
            os.path.join(base_path, "positive_optional.json")
        )
        self.DATA_POSITIVE_POSE = load_json_file(
            positive_pose_path,
            os.path.join(base_path, "positive_pose.json")
        )
        self.DATA_POSITIVE_SELFIE = load_json_file(
            positive_selfie_path,
            os.path.join(base_path, "positive_selfie.json")
        )
        self.DATA_NEGATIVE = load_json_file(
            negative_path,
            os.path.join(base_path, "negative.json")
        )
        self.DATA_CANCEL_SEEDS = load_json_file(
            cancel_seeds_path,
            os.path.join(base_path, "cancel_seeds.json")
        )
        self.DATA_POSITIVE_CANCEL_PAIR = load_json_file(
            positive_cancel_pair_path,
            os.path.join(base_path, "positive_cancel_pair.json")
        )

    def run(self):
        """画像生成を実行"""
        try:
            # プロンプトを生成
            prompts = self.generate_prompts()

            # ドライランモードの場合は、プロンプトの生成のみを行う
            if self.dry_run:
                self.logger.info("ドライランモード: プロンプトの生成のみを行います")
                return prompts

            # 画像生成の実行
            total_batches = self.IMAGE_GENERATE_BATCH_EXECUTE_COUNT
            logging.info(f"画像生成バッチを開始します。合計バッチ数: {total_batches}")

            for i in range(total_batches):
                # 現在のバッチ番号をログに表示
                current_batch = i + 1
                logging.info(f"画像生成バッチ進捗: {current_batch}/{total_batches} ({(current_batch/total_batches)*100:.1f}%)")

                # 画像生成処理を実行
                self._generate_images(current_batch, total_batches)

            logging.info(f"画像生成バッチが完了しました。合計バッチ数: {total_batches}")

        except Exception as e:
            self.logger.error(f"エラーが発生しました: {e}")
            raise

    def generate_prompts(self, reuse_positive_base=None, reuse_positive_base_dict=None):
        """
        プロンプトを生成して返す（ドライラン用）

        Args:
            reuse_positive_base (list, optional): 再利用するベースプロンプトのリスト
            reuse_positive_base_dict (dict, optional): 再利用するベースプロンプトの辞書

        Returns:
            dict: 生成されたプロンプト情報
        """
        # プロンプトファイルを読み込む
        self._load_prompt_files()

        # プロンプトを生成
        positive_prompt, negative_prompt, seed, prompt_info = self._create_prompts(
            reuse_positive_base=reuse_positive_base,
            reuse_positive_base_dict=reuse_positive_base_dict
        )

        return {
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "prompt_info": prompt_info,
            "reusable_base_prompts": prompt_info["reusable_base_prompts"],
            "reusable_base_prompt_dict": prompt_info["reusable_base_prompt_dict"]
        }

    def _create_prompts(self, reuse_positive_base=None, reuse_positive_base_dict=None):
        """
        プロンプトを生成する内部メソッド

        Args:
            reuse_positive_base (list, optional): 再利用するベースプロンプトのリスト
            reuse_positive_base_dict (dict, optional): 再利用するベースプロンプトの辞書

        Returns:
            tuple: (positive_prompt, negative_prompt, seed, prompt_info)
                prompt_infoには生成されたプロンプト情報と、再利用可能なベースプロンプト情報が含まれる
        """
        # デバッグログを追加
        self.logger.info(f"_create_prompts開始。reuse_positive_base: {reuse_positive_base is not None}, reuse_positive_base_dict: {reuse_positive_base_dict is not None}")
        self.logger.debug(f"現在のDATA_POSITIVE_CANCEL_PAIR: {self.DATA_POSITIVE_CANCEL_PAIR}")

        # ランダムなシード値を生成
        seed = random.randint(0, 4294967295)

        # キャンセル対象のシード値かチェック、または閾値よりも小さい場合は再生成
        while str(seed) in self.DATA_CANCEL_SEEDS or seed <= self.CANCEL_MIN_SEED_VALUE:
            seed = random.randint(0, 4294967295)
            self.logger.info(f"キャンセル対象または閾値以下のシード値のため再生成します: {seed}")

        # ベースプロンプトを生成または再利用
        if reuse_positive_base is not None and reuse_positive_base_dict is not None:
            # 指定されたベースプロンプトを再利用
            positive_base_prompts = reuse_positive_base
            positive_base_prompt_dict = reuse_positive_base_dict
            self.logger.info("ベースプロンプトを再利用します")
        else:
            # 新しいベースプロンプトを生成
            # 一貫性のために、generate_random_promptsのみを使用
            self.logger.info("新しいベースプロンプトを生成します")
            positive_base_prompt_str, positive_base_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_BASE)
            positive_base_prompts = positive_base_prompt_str.split(", ") if positive_base_prompt_str else []
            self.logger.info(f"生成されたベースプロンプト: {positive_base_prompts}")
            self.logger.debug(f"生成されたベースプロンプト辞書: {json.dumps(positive_base_prompt_dict, indent=2, ensure_ascii=False)[:500]}...")

        # ポーズプロンプトを生成（セルフィーの場合はセルフィー用プロンプトを使用）
        if self.IS_SELFIE:
            # 一貫性のために、generate_random_promptsのみを使用
            self.logger.info("セルフィー用プロンプトを生成します")
            positive_pose_prompt_str, positive_pose_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_SELFIE)
            positive_pose_prompts = positive_pose_prompt_str.split(", ") if positive_pose_prompt_str else []
            self.logger.debug(f"生成されたセルフィープロンプト: {positive_pose_prompts}")
        else:
            # 一貫性のために、generate_random_promptsのみを使用
            self.logger.info("ポーズプロンプトを生成します")
            positive_pose_prompt_str, positive_pose_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_POSE)
            positive_pose_prompts = positive_pose_prompt_str.split(", ") if positive_pose_prompt_str else []
            self.logger.debug(f"生成されたポーズプロンプト: {positive_pose_prompts}")

        # オプショナルプロンプトを生成
        # 一貫性のために、generate_random_promptsのみを使用
        self.logger.info("オプショナルプロンプトを生成します")
        positive_optional_prompt_str, positive_optional_prompt_dict = self.generate_random_prompts(self.DATA_POSITIVE_OPTIONAL)
        positive_optional_prompts = positive_optional_prompt_str.split(", ") if positive_optional_prompt_str else []
        self.logger.debug(f"生成されたオプショナルプロンプト: {positive_optional_prompts}")

        # ネガティブプロンプトを生成
        # 一貫性のために、generate_random_promptsのみを使用
        self.logger.info("ネガティブプロンプトを生成します")
        negative_prompt_str, negative_prompt_dict = self.generate_random_prompts(self.DATA_NEGATIVE)
        negative_prompts = negative_prompt_str.split(", ") if negative_prompt_str else []

        # 元のプロンプトリストを保存（互換性チェック前）
        original_positive_prompts = positive_base_prompts + positive_pose_prompts + positive_optional_prompts
        self.logger.debug(f"互換性チェック前の元のプロンプト: {original_positive_prompts}")

        # プロンプトの組み合わせをチェックし、相性の悪い組み合わせを除外
        self.logger.info("プロンプトの互換性チェックを実行します")
        positive_prompts = self._check_prompt_compatibility(original_positive_prompts)
        self.logger.debug(f"互換性チェック後のプロンプト: {positive_prompts}")

        # 除外されたプロンプトを特定
        excluded_prompts = [p for p in original_positive_prompts if p not in positive_prompts]
        if excluded_prompts:
            self.logger.info(f"互換性チェックにより除外されたプロンプト: {', '.join(excluded_prompts)}")

            # 除外されたプロンプトに基づいて、各カテゴリの辞書を更新
            self._update_prompt_dict_based_on_exclusions(positive_base_prompt_dict, excluded_prompts)
            self._update_prompt_dict_based_on_exclusions(positive_pose_prompt_dict, excluded_prompts)
            self._update_prompt_dict_based_on_exclusions(positive_optional_prompt_dict, excluded_prompts)

        # 最終的なプロンプトを結合
        positive_prompt = ", ".join(positive_prompts)
        negative_prompt = ", ".join(negative_prompts)

        # 再利用可能なベースプロンプト情報を保存
        reusable_base_prompts = positive_base_prompts
        reusable_base_prompt_dict = positive_base_prompt_dict

        # プロンプト情報を辞書にまとめる
        prompt_info = {
            "positive_base_prompt_dict": positive_base_prompt_dict,
            "positive_pose_prompt_dict": positive_pose_prompt_dict,
            "positive_optional_prompt_dict": positive_optional_prompt_dict,
            "negative_prompt_dict": negative_prompt_dict,
            "reusable_base_prompts": reusable_base_prompts,
            "reusable_base_prompt_dict": reusable_base_prompt_dict,
            "seed": seed,
            "cancel_prompts": excluded_prompts
        }

        # デバッグログを追加
        self.logger.info(f"_create_prompts完了。最終的なプロンプト情報生成完了")
        self.logger.debug(f"最終的なポジティブプロンプト: {positive_prompt}")
        self.logger.debug(f"最終的なネガティブプロンプト: {negative_prompt}")

        # 特にWeapon Typeの情報をログに出力
        if "Weapon Type" in positive_base_prompt_dict:
            self.logger.info(f"Weapon Type情報: {json.dumps(positive_base_prompt_dict['Weapon Type'], indent=2, ensure_ascii=False)}")

        # LoRAを使用する場合、トリガーワードを追加
        if self.USE_LORA and self.LORA_NAME:
            try:
                from main import LORA_SETTINGS
                if self.LORA_NAME in LORA_SETTINGS:
                    lora_settings = LORA_SETTINGS[self.LORA_NAME]
                    trigger_word = lora_settings.get("trigger_word", "")
                    if trigger_word:
                        # トリガーワードを直接プロンプトリストに追加
                        positive_prompts.insert(0, trigger_word)  # 先頭に追加
                        # 最終的なプロンプトを更新
                        positive_prompt = ", ".join(positive_prompts)
                        self.logger.info(f"LoRAトリガーワード '{trigger_word}' を追加しました")
            except ImportError as e:
                self.logger.warning(f"警告: LoRA設定の取得中にエラーが発生しました: {e}")

        return positive_prompt, negative_prompt, seed, prompt_info

    def _update_prompt_dict_based_on_exclusions(self, prompt_dict, excluded_prompts):
        """
        除外されたプロンプトに基づいて、プロンプト辞書を更新する

        Args:
            prompt_dict (dict): 更新するプロンプト辞書
            excluded_prompts (list): 除外されたプロンプトのリスト
        """
        if not excluded_prompts:
            return  # 除外するプロンプトがない場合は何もしない

        self.logger.debug(f"プロンプト辞書の更新開始。除外対象プロンプト: {excluded_prompts}")

        # 各カテゴリについて処理
        for category, category_data in list(prompt_dict.items()):
            if isinstance(category_data, list):
                # 元のリストを保存
                original_prompts = category_data.copy()

                # リストから除外されたプロンプトを削除
                prompt_dict[category] = [p for p in category_data if p not in excluded_prompts]

                # 変更があった場合はログに出力
                if len(prompt_dict[category]) != len(original_prompts):
                    removed_prompts = [p for p in original_prompts if p in excluded_prompts]
                    self.logger.info(f"カテゴリ '{category}' から以下のプロンプトを除外しました: {', '.join(removed_prompts)}")

                # 空のリストになった場合は、カテゴリ自体を削除
                if not prompt_dict[category]:
                    del prompt_dict[category]
                    self.logger.info(f"カテゴリ '{category}' が空になったため削除しました")

        self.logger.debug(f"プロンプト辞書の更新完了")

    def _generate_random_prompts_from_data(self, data):
        """データからランダムなプロンプトを生成する"""
        selected_prompts = []

        for category, category_data in data.items():
            prompts = category_data.get("prompts", [])
            # キー名を修正（アンダースコアからスペースに変更）
            use_max_prompts = category_data.get("use_max_prompts", 0)
            use_min_prompts = category_data.get("use_min_prompts", 0)

            # 選択するプロンプト数を決定
            if use_max_prompts == 0:
                # 選択しない場合
                continue
            elif use_max_prompts == use_min_prompts:
                # 固定数選択する場合
                num_to_select = use_max_prompts
            else:
                # ランダムな数を選択する場合
                num_to_select = random.randint(use_min_prompts, use_max_prompts)

            # プロンプトを選択
            if num_to_select > 0 and prompts:
                selected = random.sample(prompts, min(num_to_select, len(prompts)))
                selected_prompts.extend(selected)

        return selected_prompts

    def _apply_prompt_cancel_pairs(self, prompts):
        """
        positive_cancel_pair.jsonで定義された相性の悪いプロンプトの組み合わせを適用する

        Args:
            prompts (list): チェックするプロンプトのリスト

        Returns:
            list: 相性の悪いプロンプトが除外されたプロンプトのリスト
        """
        self.logger.debug(f"=== 相性の悪いプロンプトの組み合わせを適用開始 ===")
        self.logger.debug(f"入力プロンプト: {prompts}")
        self.logger.debug(f"DATA_POSITIVE_CANCEL_PAIR: {self.DATA_POSITIVE_CANCEL_PAIR}")

        if not prompts or not hasattr(self, 'DATA_POSITIVE_CANCEL_PAIR') or not self.DATA_POSITIVE_CANCEL_PAIR:
            self.logger.debug("プロンプトが空か、キャンセルペア設定がないため、変更なしで終了します")
            return prompts

        # 元のプロンプトリストをコピー
        filtered_prompts = prompts.copy()
        removed_prompts = []

        # プロンプトリスト内に含まれるキーワードを検索
        matched_keys = []
        for prompt in prompts:
            prompt_lower = prompt.lower()
            self.logger.debug(f"プロンプトをチェック: {prompt} (lower: {prompt_lower})")

            # キーワードとしてプロンプトが定義されている場合
            for key in self.DATA_POSITIVE_CANCEL_PAIR:
                # 完全一致または単語の始まりの部分が一致する場合
                key_lower = key.lower()
                if prompt_lower == key_lower or prompt_lower.startswith(key_lower + " "):
                    self.logger.debug(f"キャンセルキーとマッチしました: {key}")
                    matched_keys.append(key)
                    break

        # 見つかったキーに基づいて、対応するキャンセル対象のプロンプトを除外
        for key in matched_keys:
            cancel_list = self.DATA_POSITIVE_CANCEL_PAIR[key]
            self.logger.debug(f"キー '{key}' に対するキャンセル対象リスト: {cancel_list}")

            # 削除対象のプロンプトをリストから探して削除
            for cancel_pattern in cancel_list:
                self.logger.debug(f"キャンセル対象パターン: {cancel_pattern}")

                cancel_pattern_lower = cancel_pattern.lower()
                for p in filtered_prompts.copy():
                    p_lower = p.lower()

                    # 様々なマッチングパターンをチェック
                    is_match = False

                    # 1. 完全一致
                    if p_lower == cancel_pattern_lower:
                        is_match = True
                    # 2. 単語の始まりの部分一致 (例: "looking at viewer" は "(looking at viewer:1.4)" にマッチ)
                    elif cancel_pattern_lower in p_lower:
                        # 括弧内のパラメータを考慮して部分一致を確認
                        # 例: "(looking at viewer" は "(looking at viewer:1.4)" にマッチする
                        base_pattern = cancel_pattern_lower.rstrip(")").strip()
                        if base_pattern in p_lower:
                            is_match = True

                    if is_match:
                        filtered_prompts.remove(p)
                        removed_prompts.append(p)
                        self.logger.info(f"相性の悪いプロンプト組み合わせのため削除: '{key}'と'{p}'")
                        self.logger.debug(f"プロンプト '{p}' を削除しました (パターン: {cancel_pattern})")

        # 除外されたプロンプトの数をログに出力
        excluded_count = len(removed_prompts)
        if excluded_count > 0:
            self.logger.info(f"相性チェックにより{excluded_count}個のプロンプトが除外されました: {', '.join(removed_prompts)}")
        else:
            self.logger.debug("除外されたプロンプトはありませんでした")

        self.logger.debug(f"フィルタリング後のプロンプト: {filtered_prompts}")
        self.logger.debug(f"=== 相性の悪いプロンプトの組み合わせを適用終了 ===")
        return filtered_prompts

    def _check_prompt_compatibility(self, prompts):
        """
        プロンプトの互換性をチェックし、最適化されたプロンプトリストを返す

        Args:
            prompts (list): プロンプトのリスト

        Returns:
            list: 最適化されたプロンプトのリスト
        """
        self.logger.debug(f"プロンプト互換性チェック開始: {prompts}")
        if not prompts:
            self.logger.debug("プロンプトが空のため、空のリストを返します")
            return []

        # 重複を除去
        unique_prompts = self._remove_duplicate_prompts(prompts)
        self.logger.debug(f"重複除去後のプロンプト: {unique_prompts}")

        # positive_cancel_pairを適用
        self.logger.debug("positive_cancel_pairを適用します")
        compatible_prompts = self._apply_prompt_cancel_pairs(unique_prompts)
        self.logger.debug(f"positive_cancel_pair適用後のプロンプト: {compatible_prompts}")

        # プロンプトの最適化
        optimized_prompts = self._optimize_prompts(compatible_prompts)
        self.logger.debug(f"最適化後のプロンプト: {optimized_prompts}")

        # プロンプトの品質チェック
        final_prompts = self._check_prompt_quality(optimized_prompts)
        self.logger.debug(f"品質チェック後の最終プロンプト: {final_prompts}")

        # 除外されたプロンプトの数をログに出力
        excluded_count = len(prompts) - len(final_prompts)
        if excluded_count > 0:
            self.logger.info(f"互換性チェックにより{excluded_count}個のプロンプトが除外されました")

        self.logger.debug(f"プロンプト互換性チェック終了")
        return final_prompts

    def _generate_images(self, current_batch, total_batches):
        """
        画像の生成を行います。生成された画像は、指定された出力フォルダに保存されます。

        Args:
            current_batch (int): 現在のバッチ番号
            total_batches (int): 総バッチ数

        Returns:
            None
        """
        # プロンプトの生成
        positive_prompt, negative_prompt, seed, prompt_info = self._create_prompts()

        # プロンプトとモデル情報をログに出力
        self.logger.info(f"画像生成: ポジティブプロンプト={positive_prompt}")
        self.logger.info(f"画像生成: ネガティブプロンプト={negative_prompt}")
        self.logger.info(f"画像生成: Seed値={seed}")
        self.logger.info(f"画像生成: モデルチェックポイント={self.SD_MODEL_CHECKPOINT}")
        self.logger.info(f"画像生成: モデル名（JSONに記録）={os.path.splitext(self.SD_MODEL_CHECKPOINT)[0]}")
        self.logger.info(f"画像生成: カスタムチェックポイント使用={self.USE_CUSTOM_CHECKPOINT}")

        # バッチ進捗情報をログに出力
        self.logger.info(f"バッチ {current_batch}/{total_batches} の画像生成を開始します")

        # 最初にモデルを切り替え
        if not self.set_model(self.SD_MODEL_CHECKPOINT):
            self.logger.error("モデルの切り替えに失敗したため、処理を中止します")
            return

        # 出力ディレクトリ構造を作成
        self._create_output_directories()

        # 現在の日時を取得してフォルダ名の一部に使用
        now = datetime.now()
        date_str = now.strftime("%Y%m%d-%H")

        # 出力フォルダのパスを生成
        output_folder_path = os.path.join(
            self.OUTPUT_FOLDER,
            self.OUTPUT_FOLDER_PREFIX.lstrip('/'),
            f"{date_str}-{seed}"
        )

        # フォルダが存在しない場合は作成
        os.makedirs(output_folder_path, exist_ok=True)

        # 画像生成のためのペイロードを作成
        payload = {
            **self.COMMON_PAYLOAD_SETTINGS,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
        }

        # 最新の画像サイズを使用するように更新
        payload["width"] = self.width
        payload["height"] = self.height

        # LoRAを使用する場合、LoRAの設定を追加
        if self.USE_LORA and self.LORA_NAME:
            self.logger.info(f"LoRA {self.LORA_NAME} を使用します")
            try:
                from main import LORA_SETTINGS
                if self.LORA_NAME in LORA_SETTINGS:
                    lora_settings = LORA_SETTINGS[self.LORA_NAME]
                    lora_weight = lora_settings.get("weight", 0.7)  # デフォルト値は0.7
                    # LoRAの設定をalwayson_scriptsに追加
                    payload["alwayson_scripts"] = {
                        "Additional Networks for Generating": {
                            "args": [
                                True,  # enabled
                                "LoRA",  # モジュールタイプ
                                [
                                    [
                                        f"{self.LORA_NAME}.safetensors",  # モデル名
                                        lora_weight,  # 重み
                                        0  # モデルのチャネル
                                    ]
                                ]
                            ]
                        }
                    }
                    self.logger.info(f"LoRA設定を追加しました: {self.LORA_NAME}, 重み: {lora_weight}")
                else:
                    self.logger.warning(f"警告: 指定されたLoRA '{self.LORA_NAME}' の設定が見つかりません")
            except ImportError as e:
                self.logger.warning(f"警告: LoRA設定の取得中にエラーが発生しました: {e}")

        # 透過背景の場合は設定を変更
        if self.IS_TRANSPARENT_BACKGROUND:
            try:
                # generate_images関数と同様に透過画像用のペイロードを追加
                payload = {**payload, **self.TRANPARENT_PAYLOAD}
                # 透過背景用のプロンプトを追加
                payload["prompt"] = "(no background: 1.3, white background: 1.3), " + payload["prompt"]
                self.logger.info(f"透過画像生成モードを有効化しました。使用スクリプト: {self.TRANPARENT_PAYLOAD['script_name']}")
            except Exception as e:
                self.logger.error(f"透過画像設定中にエラーが発生しました: {e}")
                # エラーが発生しても処理を続行

        # 結果を格納する辞書
        result_images = {}

        try:
            # オリジナル画像の生成
            self.logger.info(f"バッチ {current_batch}/{total_batches} - オリジナル画像 (1/{self.ANOTHER_VERSION_GENERATE_COUNT + 1}) の生成を開始します")
            self._generate_single_image(payload, output_folder_path, "00001", result_images, prompt_info)

            # オリジナル画像のSeed値を保存
            original_seed = seed

            # 再利用するベースプロンプトを取得
            reusable_base_prompts = prompt_info.get("reusable_base_prompts", [])
            reusable_base_prompt_dict = prompt_info.get("reusable_base_prompt_dict", {})

            # 別バージョンの画像を生成
            for i in range(1, self.ANOTHER_VERSION_GENERATE_COUNT + 1):
                # 進捗状況をログに出力
                version_number = i + 1
                total_versions = self.ANOTHER_VERSION_GENERATE_COUNT + 1
                self.logger.info(f"バッチ {current_batch}/{total_batches} - バージョン画像 ({version_number}/{total_versions}) の生成を開始します")

                # 別バージョン用のプロンプトを生成（ベースプロンプトを再利用）
                version_positive_prompt, version_negative_prompt, _, version_prompt_info = self._create_prompts(
                    reuse_positive_base=reusable_base_prompts,
                    reuse_positive_base_dict=reusable_base_prompt_dict
                )

                # オリジナル画像と同じSeed値を使用
                version_seed = original_seed

                # Seed値を更新
                version_prompt_info["seed"] = version_seed

                # 別バージョン用のペイロードを作成
                version_payload = {
                    **self.COMMON_PAYLOAD_SETTINGS,
                    "prompt": version_positive_prompt,
                    "negative_prompt": version_negative_prompt,
                    "seed": version_seed,
                }

                # 透過背景の場合は設定を変更
                if self.IS_TRANSPARENT_BACKGROUND:
                    try:
                        version_payload = {**version_payload, **self.TRANPARENT_PAYLOAD}
                        version_payload["prompt"] = "(no background: 1.3, white background: 1.3), " + version_payload["prompt"]
                    except Exception as e:
                        self.logger.error(f"透過画像設定中にエラーが発生しました: {e}")

                # 別バージョンの画像を生成
                filename = f"{str(i+1).zfill(5)}"
                self._generate_single_image(version_payload, output_folder_path, filename, result_images, version_prompt_info)

            return result_images

        except requests.exceptions.HTTPError as e:
            # HTTPエラーの詳細情報を取得
            self.logger.error(f"HTTPエラー: {e}")
            try:
                # eオブジェクトからresponseを取得
                response = e.response
                error_json = response.json()
                self.logger.error(f"サーバーからのエラー詳細: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
            except (json.JSONDecodeError, NameError, AttributeError):
                try:
                    # eオブジェクトからresponseを取得できるか確認
                    if hasattr(e, 'response'):
                        self.logger.error(f"サーバーからのレスポンス: {e.response.text}")
                    else:
                        self.logger.error("レスポンスオブジェクトが存在しません")
                except Exception:
                    self.logger.error("レスポンスオブジェクトが存在しません")
            except Exception as json_error:
                self.logger.error(f"エラー情報の解析中に例外が発生しました: {json_error}")

            # エラー発生時にも作成したフォルダを削除
            if 'created_folder_path' in locals() and created_folder_path and os.path.exists(created_folder_path):
                import shutil
                try:
                    shutil.rmtree(created_folder_path)
                    self.logger.info(f"エラー発生のため、フォルダを削除しました: {created_folder_path}")
                except Exception as e2:
                    self.logger.error(f"フォルダの削除中にエラーが発生しました: {e2}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API呼び出し中にエラーが発生しました: {e}")

            # リクエストの内容を表示
            try:
                self.logger.info(f"送信したリクエスト: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            except Exception as req_error:
                self.logger.error(f"リクエスト情報の表示中にエラーが発生しました: {req_error}")

            # エラー発生時にも作成したフォルダを削除
            if 'created_folder_path' in locals() and created_folder_path and os.path.exists(created_folder_path):
                import shutil
                try:
                    shutil.rmtree(created_folder_path)
                    self.logger.info(f"エラー発生のため、フォルダを削除しました: {created_folder_path}")
                except Exception as e2:
                    self.logger.error(f"フォルダの削除中にエラーが発生しました: {e2}")

        except Exception as e:
            self.logger.error(f"画像生成中に予期しないエラーが発生しました: {e}")

            # エラー発生時にも作成したフォルダを削除
            if 'created_folder_path' in locals() and created_folder_path and os.path.exists(created_folder_path):
                import shutil
                try:
                    shutil.rmtree(created_folder_path)
                    self.logger.info(f"エラー発生のため、フォルダを削除しました: {created_folder_path}")
                except Exception as e2:
                    self.logger.error(f"フォルダの削除中にエラーが発生しました: {e2}")

        return result_images

    def _generate_single_image(self, payload, output_folder_path, filename, result_images, prompt_info):
        """単一の画像を生成する内部メソッド"""
        try:
            # 武器タイプを抽出（RPGアイコンの武器カテゴリの場合のみ）
            weapon_type = None
            if self.style == "illustration" and self.category == "rpg_icon" and self.subcategory == "weapon":
                # デバッグログを追加
                logging.info(f"武器タイプ抽出を開始します。prompt_info: {json.dumps(prompt_info, indent=2, ensure_ascii=False)[:500]}...")

                # プロンプトから武器タイプを抽出
                if "positive_base_prompt_dict" in prompt_info and "Weapon Type" in prompt_info["positive_base_prompt_dict"]:
                    logging.info(f"positive_base_prompt_dict内のWeapon Type: {json.dumps(prompt_info['positive_base_prompt_dict']['Weapon Type'], indent=2, ensure_ascii=False)}")

                    # 辞書構造を確認して適切にアクセス
                    weapon_type_data = prompt_info["positive_base_prompt_dict"]["Weapon Type"]

                    # 新しい形式（selected_prompts）と古い形式の両方に対応
                    if isinstance(weapon_type_data, dict) and "selected_prompts" in weapon_type_data:
                        weapon_prompts = weapon_type_data["selected_prompts"]
                    elif isinstance(weapon_type_data, list):
                        weapon_prompts = weapon_type_data
                    else:
                        weapon_prompts = []

                    # 武器タイプを抽出
                    if weapon_prompts:
                        # 最初の武器タイプを使用
                        weapon_type = weapon_prompts[0].lower()
                        logging.info(f"抽出された武器タイプ: {weapon_type}")
                    else:
                        logging.warning("武器タイプが見つかりませんでした")
                else:
                    logging.warning("武器タイプ情報が見つかりませんでした")

            # 画像生成開始をログに記録
            logging.info(f"画像生成開始: {filename}")

            # 画像生成APIを呼び出す
            try:
                # 正しいエンドポイントを使用
                response = requests.post(url=self.TXT2IMG_URL, json=payload)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"画像生成中にエラーが発生しました: {e}")
                self.logger.error(f"HTTPエラー: {e}")
                try:
                    error_detail = response.json()
                    self.logger.error(f"サーバーからのエラー詳細: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    self.logger.error("サーバーからのエラー詳細を取得できませんでした")
                raise

            # レスポンスからJSONデータを取得
            r = response.json()

            # 画像処理用の変数を初期化
            images_processed_count = 0
            seed_value = 0
            parameters = ""
            self.current_parameters = ""  # 現在のパラメータをクラス変数に保存

            # 生成された画像を処理
            for i, image_data in enumerate(r['images']):
                images_processed_count += 1
                logging.info(f"透過画像生成時の画像処理回数: {images_processed_count}")
                # Base64エンコードされた画像データをデコード
                image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))

                # 透過画像生成時は最初の１つ目の r['images'] にのみ PNG 画像情報があるので、そこから各種値を取得
                # seed_value == 0 ではなく、最初の画像（images_processed_count == 1）から必ずPNGInfoを取得する
                if images_processed_count == 1:
                    try:
                        # ABG Removerを使用した場合、最初の画像にのみPNGInfoが含まれているため、
                        # ここで取得したPNGInfoを3つ目の透過画像用に保持する必要がある
                        png_payload = {
                            "image": "data:image/png;base64," + image_data
                        }
                        logging.info("最初の画像からPNGInfoを取得しています...")
                        logging.info(f"PNGInfo APIエンドポイント: {self.PNGINFO_URL}")
                        logging.info(f"PNGInfo APIペイロードの長さ: {len(json.dumps(png_payload))}")

                        # リクエスト送信前にデータの先頭部分をログに記録
                        image_data_preview = image_data[:100] + "..." if len(image_data) > 100 else image_data
                        logging.info(f"画像データプレビュー: {image_data_preview}")

                        response2 = requests.post(url=self.PNGINFO_URL, json=png_payload)
                        logging.info(f"PNGInfo APIステータスコード: {response2.status_code}")
                        response2.raise_for_status()

                        # PNGInfoを取得
                        info_text = response2.json().get("info", "")
                        if not info_text:
                            logging.error("PNGInfoが空でした！レスポンス全体を確認します。")
                            logging.error(f"PNGInfo API レスポンス: {json.dumps(response2.json(), indent=2, ensure_ascii=False)}")

                            # PNGInfoが空の場合、元のプロンプト情報からデフォルトのPNGInfoを生成
                            # payloadから直接情報を取得
                            # 元のプロンプトとネガティブプロンプトを取得
                            positive_prompt = payload.get("prompt", "")
                            negative_prompt = payload.get("negative_prompt", "")
                            seed = payload.get("seed", 0)

                            # デフォルトのPNGInfo文字列を生成
                            info_text = (
                                f"{positive_prompt}\n"
                                f"Negative prompt: {negative_prompt}\n"
                                f"Steps: {payload.get('steps', 50)}, "
                                f"Sampler: {payload.get('sampler_name', 'DPM++ 2M')}, "
                                f"CFG scale: {payload.get('cfg_scale', 7)}, "
                                f"Seed: {seed}, "
                                f"Size: {payload.get('width', 512)}x{payload.get('height', 768)}, "
                                f"Model: {self.SD_MODEL_CHECKPOINT}"
                            )
                            logging.info("デフォルトのPNGInfo情報を生成しました")
                        else:
                            logging.info(f"取得したPNGInfo: {info_text[:200]}...")  # 最初の200文字だけログに出力

                        # パラメータを保存
                        parameters = info_text if info_text else "デフォルトパラメータ（PNGInfoが取得できませんでした）"
                        self.current_parameters = parameters  # 現在のパラメータをクラス変数に保存
                        logging.info(f"保存したパラメータの長さ: {len(parameters)}")

                        # PNGInfoが取得できた場合のみ解析を行う
                        if info_text:
                            # PNGInfoを解析（先頭に「Prompt:」はない前提）
                            lines = info_text.split('\n')
                            self.current_png_info = {}

                            # 最初の行をプロンプトとして扱う
                            if lines:
                                prompt_line = lines[0].strip()
                                self.current_png_info["prompt"] = prompt_line
                                logging.info(f"最初の行からプロンプトを抽出しました: {prompt_line[:100]}...")

                            # 残りの行をパラメータとして解析
                            for line in lines[1:]:
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    key = key.strip()
                                    value = value.strip()
                                    self.current_png_info[key] = value

                                    # Seed値を取得
                                    if key.lower() == "seed":
                                        try:
                                            seed_value = int(value)
                                            logging.info(f"Seed値を抽出しました: {seed_value}")
                                        except ValueError:
                                            logging.warning(f"Seed値の変換に失敗しました: {value}")
                    except Exception as e:
                        logging.error(f"PNG情報の取得中にエラーが発生しました: {e}")

                # 透過画像生成時は３つ目の画像のみを保存するため、１つ目と２つ目はスキップ
                # ABG Removerの出力: 1つ目=元画像、2つ目=マスク画像、3つ目=透過背景画像
                if self.IS_TRANSPARENT_BACKGROUND and images_processed_count != 3:
                    continue

                # 画像のメタデータを設定
                pnginfo = PngImagePlugin.PngInfo()
                # 透過画像生成時に3つ目の画像にも1つ目の画像から取得したPNGInfoを適用する
                if self.IS_TRANSPARENT_BACKGROUND and images_processed_count == 3 and self.current_parameters:
                    logging.info(f"透過画像に元画像のPNGInfoを適用します。長さ: {len(self.current_parameters)}")
                    pnginfo.add_text("parameters", self.current_parameters)
                else:
                    if not parameters:
                        logging.warning("PNGInfoに設定するパラメータが空です。")
                        parameters = "自動生成された画像（詳細情報なし）"
                    logging.info(f"通常の方法でPNGInfoを設定します。長さ: {len(parameters)}")
                    pnginfo.add_text("parameters", parameters)

                # 画像ファイルパスを生成
                image_path = os.path.normpath(os.path.join(output_folder_path, filename + self.IMAGE_FILE_EXTENSION))

                # 画像を保存
                image.save(image_path, pnginfo=pnginfo)

                # 保存後にPNGInfoが正しく設定されたか確認（デバッグ用）
                if self.IS_TRANSPARENT_BACKGROUND and images_processed_count == 3:
                    try:
                        # 保存した画像を開いて確認
                        with Image.open(image_path) as saved_image:
                            if 'parameters' in saved_image.info:
                                logging.info(f"透過画像にPNGInfoが正しく保存されました。長さ: {len(saved_image.info['parameters'])}")
                            else:
                                logging.warning("透過画像にPNGInfoが保存されていません")
                    except Exception as e:
                        logging.error(f"保存した透過画像のPNGInfo確認中にエラーが発生しました: {e}")

                # 画像をJPG形式でも保存
                jpg_file_path = os.path.normpath(os.path.join(output_folder_path, filename + ".jpg"))
                image.convert("RGB").save(jpg_file_path, format="JPEG")

                # 結果を辞書に追加
                result_images[filename] = {
                    "path": image_path,
                    "seed": seed_value,
                    "parameters": parameters
                }

            # 関連画像（サムネイル、サンプル画像など）を生成
            self.generate_related_images(image, output_folder_path, filename, pnginfo)

            # prompt_infoから必要な情報を取得
            positive_base_prompt_dict = prompt_info["positive_base_prompt_dict"]
            positive_pose_prompt_dict = prompt_info["positive_pose_prompt_dict"]
            positive_optional_prompt_dict = prompt_info["positive_optional_prompt_dict"]
            negative_prompt_dict = prompt_info["negative_prompt_dict"]
            cancel_prompts = prompt_info["cancel_prompts"]

            # プロンプト情報をJSONファイルとして保存
            self.save_prompts_to_json(
                positive_base_prompt_dict,
                positive_pose_prompt_dict,
                positive_optional_prompt_dict,
                negative_prompt_dict,
                output_folder_path,
                filename,
                cancel_prompts
            )

            # 画像生成完了をログに記録
            logging.info(f"画像生成完了: {filename}")

            # 検証に成功したか最大試行回数に達した場合はループを終了
            return

        except Exception as e:
            logging.error(f"画像生成中にエラーが発生しました: {e}")
            raise e

    def _set_image_size_by_type(self):
        """画像タイプに基づいて画像サイズを設定する"""
        try:
            # LoRAを使用している場合、LoRAの設定から画像サイズを取得
            if self.USE_LORA and self.LORA_NAME:
                lora_settings = self.settings.get("lora_settings", {}).get(self.LORA_NAME, {})
                if lora_settings and "image_size" in lora_settings:
                    image_size = lora_settings["image_size"]
                    self.width = image_size.get("width", 768)
                    self.height = image_size.get("height", 512)
                    self.logger.info(f"LoRA {self.LORA_NAME} の設定に基づいて画像サイズを設定: {self.width}x{self.height}")
                    return

            # settings.jsonから画像サイズを取得
            if self.style in self.settings.get("default_image_sizes", {}):
                style_settings = self.settings["default_image_sizes"][self.style]
                if self.category in style_settings:
                    size_settings = style_settings[self.category]
                    self.width = size_settings.get("width", 512)
                    self.height = size_settings.get("height", 768)
                    self.logger.info(f"画像サイズを設定: {self.width}x{self.height}")
                    return

            # デフォルト値の設定
            self.width = 512
            self.height = 768
            self.logger.info(f"デフォルトの画像サイズを使用: {self.width}x{self.height}")

        except Exception as e:
            self.logger.error(f"画像サイズの設定中にエラーが発生しました: {e}")
            # エラーが発生した場合はデフォルト値を使用
            self.width = 512
            self.height = 768

    def _parse_png_info(self, info_text):
        """
        PNGInfoからプロンプト情報を抽出する

        Args:
            info_text (str): PNGInfo文字列

        Returns:
            dict: 抽出されたプロンプト情報
        """
        result = {}
        lines = info_text.split('\n')

        # 最初の行をプロンプトとして扱う
        if lines:
            result["prompt"] = lines[0].strip()

        # Negative promptを探す
        for i, line in enumerate(lines):
            if line.startswith("Negative prompt:"):
                result["negative_prompt"] = line[len("Negative prompt:"):].strip()
                break

        # Seedを探す
        seed_match = re.search(r"Seed:\s*(\d+)", info_text)
        if seed_match:
            result["seed"] = int(seed_match.group(1))

        # その他の情報を抽出
        for param in ["Steps", "Sampler", "CFG scale", "Size", "Model"]:
            param_match = re.search(rf"{param}:\s*([^,]+)", info_text)
            if param_match:
                result[param.lower().replace(" ", "_")] = param_match.group(1).strip()

        return result

    def _switch_model(self, model_name: str) -> None:
        """モデルを切り替える"""
        if self._model_switch_executed:
            return

        try:
            # モデル切り替えリクエスト
            option_payload = {
                "sd_model_checkpoint": model_name
            }
            response = requests.post(url=self.OPTIONS_URL, json=option_payload)
            response.raise_for_status()
            self.logger.info(f"モデル切り替えリクエスト送信完了: ステータスコード {response.status_code}")

            # 現在のモデルを更新
            self._current_model = model_name
            self._model_switch_executed = True

        except Exception as e:
            self.logger.error(f"モデル切り替え中にエラーが発生: {str(e)}")
            raise

    def _remove_duplicate_prompts(self, prompts):
        """
        重複するプロンプトを削除し、一意のプロンプトリストを返す

        Args:
            prompts (list): プロンプトのリスト

        Returns:
            list: 重複を除去したプロンプトのリスト
        """
        # 重複を除去（順序は保持）
        seen = set()
        unique_prompts = []
        for prompt in prompts:
            if prompt not in seen:
                seen.add(prompt)
                unique_prompts.append(prompt)
            else:
                logging.info(f"重複プロンプトを削除しました: {prompt}")

        return unique_prompts

    def _optimize_prompts(self, prompts):
        """
        プロンプトの最適化を行う

        Args:
            prompts (list): プロンプトのリスト

        Returns:
            list: 最適化されたプロンプトのリスト
        """
        if not prompts:
            return []

        optimized_prompts = []
        prompt_weights = {}  # プロンプトの重みを管理

        # プロンプトの重み付け
        for prompt in prompts:
            # 括弧内の重みを抽出
            weight_match = re.search(r'\(([^)]+)\)', prompt)
            if weight_match:
                weight_text = weight_match.group(1)
                # 重みの値を抽出（例: "1.3"）
                weight_value = re.search(r'(\d+\.?\d*)', weight_text)
                if weight_value:
                    prompt_weights[prompt] = float(weight_value.group(1))
                else:
                    prompt_weights[prompt] = 1.0
            else:
                prompt_weights[prompt] = 1.0

        # 重みの高いプロンプトを優先
        sorted_prompts = sorted(prompts, key=lambda x: prompt_weights.get(x, 1.0), reverse=True)

        # プロンプトの長さをチェック
        total_length = 0
        max_length = 500  # Stable Diffusionの制限

        for prompt in sorted_prompts:
            # プロンプトの長さを計算（カンマとスペースを考慮）
            prompt_length = len(prompt)
            if total_length + prompt_length + 2 <= max_length:  # +2 はカンマとスペース
                optimized_prompts.append(prompt)
                total_length += prompt_length + 2
            else:
                logging.warning(f"プロンプトが長すぎるため除外しました: {prompt[:50]}...")

        # プロンプトの品質チェック
        optimized_prompts = self._check_prompt_quality(optimized_prompts)

        return optimized_prompts

    def _check_prompt_quality(self, prompts):
        """
        プロンプトの品質をチェックし、問題のあるプロンプトを修正または除外する

        Args:
            prompts (list): プロンプトのリスト

        Returns:
            list: 品質チェック済みのプロンプトのリスト
        """
        quality_checked_prompts = []
        excluded_prompts = []

        for prompt in prompts:
            # 空のプロンプトをチェック
            if not prompt.strip():
                logging.warning("空のプロンプトを除外しました")
                excluded_prompts.append(prompt)
                continue

            # 特殊文字のチェック
            if re.search(r'[<>{}]', prompt):
                logging.warning(f"特殊文字を含むプロンプトを修正しました: {prompt}")
                # 特殊文字を除去
                prompt = re.sub(r'[<>{}]', '', prompt)

            # 重複する括弧のチェック
            if prompt.count('(') != prompt.count(')'):
                logging.warning(f"括弧の数が一致しないプロンプトを修正しました: {prompt}")
                # 括弧の数を調整
                prompt = re.sub(r'\([^)]*\)', '', prompt)

            # 重複するカンマのチェック
            if re.search(r',\s*,', prompt):
                logging.warning(f"重複するカンマを含むプロンプトを修正しました: {prompt}")
                # 重複するカンマを除去
                prompt = re.sub(r',\s*,', ',', prompt)

            # プロンプトの長さチェック
            if len(prompt) > 100:  # 個別のプロンプトの最大長
                logging.warning(f"長すぎるプロンプトを短縮しました: {prompt[:50]}...")
                # プロンプトを短縮
                prompt = prompt[:100] + "..."

            quality_checked_prompts.append(prompt)

        # 除外されたプロンプトをログに出力
        if excluded_prompts:
            logging.info(f"品質チェックにより除外されたプロンプト: {', '.join(excluded_prompts)}")

        return quality_checked_prompts

    def test_prompt_cancel_pair(self):
        """
        positive_cancel_pairの処理をテストするメソッド

        Returns:
            dict: テスト結果を含む辞書
        """
        self.logger.info("=== positive_cancel_pairのテスト開始 ===")

        # テスト用プロンプトの作成
        test_prompts = [
            "selfie",
            "(looking at viewer:1.4)",
            "Some other prompt"
        ]

        self.logger.info(f"テスト用プロンプト: {test_prompts}")
        self.logger.info(f"DATA_POSITIVE_CANCEL_PAIR: {self.DATA_POSITIVE_CANCEL_PAIR}")

        # プロンプトの互換性チェック実行
        filtered_prompts = self._apply_prompt_cancel_pairs(test_prompts.copy())
        self.logger.info(f"フィルタリング後のプロンプト: {filtered_prompts}")

        # 除外されたプロンプトを特定
        excluded_prompts = [p for p in test_prompts if p not in filtered_prompts]
        self.logger.info(f"除外されたプロンプト: {excluded_prompts}")

        # チェックが正常に機能しているかどうかの確認
        cancel_pair_working = any(p not in filtered_prompts for p in test_prompts if p != "selfie" and p != "Some other prompt")
        self.logger.info(f"positive_cancel_pair処理が機能しているか: {cancel_pair_working}")

        self.logger.info("=== positive_cancel_pairのテスト終了 ===")

        return {
            "original_prompts": test_prompts,
            "filtered_prompts": filtered_prompts,
            "excluded_prompts": excluded_prompts,
            "cancel_pair_working": cancel_pair_working
        }

    def _load_settings(self):
        """設定ファイルを読み込む"""
        try:
            settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            return {}
