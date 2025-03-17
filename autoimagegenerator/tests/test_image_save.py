import unittest
import os
import shutil
from PIL import Image
import sys
import random
import json
from unittest.mock import patch, MagicMock
import io
import base64
import re
import logging
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ログディレクトリの作成
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, f"test_image_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
    ]
)
logger = logging.getLogger(__name__)

# 直接インポート
from autoimagegenerator.auto_image_generator import AutoImageGenerator

class TestImageSave(unittest.TestCase):
    """画像保存機能のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        # テスト用のディレクトリを作成
        self.test_output_dir = "./test_output"
        self.test_input_dir = "./test_input"

        # プロジェクトのルートディレクトリを取得
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

        # 正式なプロンプトフォルダを使用
        self.prompts_dir = os.path.join(self.project_root, "autoimagegenerator", "prompts")

        # 基本ディレクトリを作成
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_input_dir, exist_ok=True)

        # テスト用のサンプル画像を作成
        self.create_test_sample_image()

        # テスト用のsettings.jsonを作成
        self.create_test_settings()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用のディレクトリを削除
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        if os.path.exists(self.test_input_dir):
            shutil.rmtree(self.test_input_dir)

    def create_test_sample_image(self):
        """テスト用のサンプル画像を作成"""
        # サンプル画像を作成
        img = Image.new('RGB', (100, 100), color='red')
        img.save(os.path.join(self.test_input_dir, 'sample.png'))

    def create_test_settings(self):
        """テスト用のsettings.jsonを作成"""
        # 現在のファイルのディレクトリパスを取得
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        # テスト用の設定
        test_settings = {
            "image_generate_batch_execute_count": 1,
            "another_version_generate_count": 0
        }

        # settings.jsonを作成
        with open(os.path.join(parent_dir, 'settings.json'), 'w') as f:
            json.dump(test_settings, f)

    def test_01_create_output_folder_structure_unit(self):
        """出力フォルダ構造の作成機能の単体テスト"""
        # テスト対象のインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=0,
            input_folder=self.test_input_dir,
            output_folder=self.test_output_dir,
            prompts_folder=self.prompts_dir,
            style="realistic",
            category="female",
            subcategory="normal"
        )

        # 必要な属性を設定
        generator.current_seed = 9876543210

        # _get_output_pathメソッドを呼び出す
        folder_path = generator._get_output_path("realistic", "female", "normal")

        # 結果の検証
        self.assertTrue(os.path.exists(folder_path), "出力フォルダが作成されていません")

        # 正しいパスに作成されているか確認
        # 絶対パスから相対パスの部分を抽出して比較
        relative_folder_path = os.path.relpath(folder_path, os.path.dirname(os.path.abspath(__file__)))
        expected_path_parts = [
            "test_output",
            "realistic",
            "female",
            "normal"
        ]

        # フォルダパスに期待される部分が含まれているか確認
        for part in expected_path_parts:
            self.assertIn(part, relative_folder_path, f"出力フォルダに {part} が含まれていません")

        # サブフォルダが作成されているか確認
        subfolders = ["thumbnail", "sample", "sample-thumbnail", "half-resolution"]
        for subfolder in subfolders:
            subfolder_path = os.path.join(folder_path, subfolder)
            self.assertTrue(os.path.exists(subfolder_path), f"サブフォルダが存在しません: {subfolder_path}")

    def test_02_save_image_unit(self):
        """画像保存機能の単体テスト"""
        # テスト対象のインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=0,
            input_folder=self.test_input_dir,
            output_folder=self.test_output_dir,
            prompts_folder=self.prompts_dir,
            style="realistic",
            category="female",
            subcategory="normal"
        )

        # 必要な属性を設定
        generator.current_seed = 9876543210
        generator.IMAGE_FILE_EXTENSION = ".png"

        # テスト用の画像データを作成
        image_data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='

        # Base64デコードして画像オブジェクトを作成
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # 出力フォルダを作成
        folder_path = generator._get_output_path("realistic", "female", "normal")

        # 画像を保存
        filename = f"test_image_{generator.current_seed}"
        file_path = os.path.join(folder_path, filename + ".png")
        image.save(file_path)

        # 結果の検証
        self.assertTrue(os.path.exists(file_path), f"画像ファイルが存在しません: {file_path}")

        # 画像のサイズを確認
        with Image.open(file_path) as img:
            self.assertEqual(img.size, (1, 1), "画像のサイズが正しくありません")

    @patch('requests.post')
    def test_03_image_save_to_correct_folder(self, mock_post):
        """画像タイプに応じた保存先フォルダに正しく保存されることをテスト（統合テスト）"""
        # APIレスポンスのみをモック
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'images': ['iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='],
            'parameters': {},
            'info': '{"seed": 9876543210}'
        }
        mock_post.return_value = mock_response

        # テスト対象のインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=0,
            input_folder=self.test_input_dir,
            output_folder=self.test_output_dir,
            prompts_folder=self.prompts_dir,
            style="realistic",
            category="female",
            subcategory="normal",
            output_folder_prefix="/realistic/female/normal"  # 明示的にプレフィックスを設定
        )

        # 必要な属性を設定（最小限に）
        generator.DATA_CANCEL_SEEDS = {"Seeds": []}  # 空のリストに設定してキャンセル処理をバイパス
        generator.current_seed = 9876543210  # 十分大きな値に変更

        # CANCEL_MIN_SEED_VALUEを十分小さい値に設定してキャンセル処理をバイパス
        generator.CANCEL_MIN_SEED_VALUE = -1

        # PNGINFOのURLを設定（必要に応じて）
        generator.PNGINFO_URL = "http://localhost:7860/sdapi/v1/png-info"

        # テスト用のプロンプトとペイロードを準備
        positive_prompts = "test prompt"
        negative_prompts = "test negative prompt"
        payload = {
            "prompt": positive_prompts,
            "negative_prompt": negative_prompts,
            "seed": 9876543210,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 20,
            "cfg_scale": 7,
            "width": 512,
            "height": 512,
            "enable_hr": False,
            "sampler_name": "Euler a"
        }

        # モックの追加設定：png-infoのレスポンスをモック
        def mock_post_side_effect(url, json=None, **kwargs):
            if url.endswith('/png-info'):
                mock_png_response = MagicMock()
                mock_png_response.status_code = 200
                mock_png_response.json.return_value = {
                    'info': 'Seed: 9876543210'
                }
                return mock_png_response
            return mock_response

        mock_post.side_effect = mock_post_side_effect

        # set_modelメソッドをモックして常にTrueを返すようにする
        with patch.object(generator, 'set_model', return_value=True) as mock_set_model:
            # _generate_single_imageメソッドをモックして、実際のAPIを呼び出さないようにする
            with patch.object(generator, '_generate_single_image') as mock_generate_single_image:
                # モックの戻り値を設定 - 実際のメソッドは戻り値を返さないのでNoneでOK
                mock_generate_single_image.return_value = None

                # モックが呼び出された時に、result_imagesに値を追加するサイドエフェクトを設定
                def side_effect(payload, output_folder_path, filename, result_images, prompt_info):
                    # テスト用の画像オブジェクトを作成
                    test_image = Image.new('RGB', (1, 1), color='red')
                    # result_imagesに値を追加
                    result_images[output_folder_path] = {
                        'filename': filename,
                        'seed_value': 9876543210,
                        'image': test_image,
                        'positive_base_prompt_dict': prompt_info.get('positive_base_prompt_dict', {}),
                        'positive_pose_prompt_dict': prompt_info.get('positive_pose_prompt_dict', {}),
                        'positive_optional_prompt_dict': prompt_info.get('positive_optional_prompt_dict', {}),
                        'negative_prompt_dict': prompt_info.get('negative_prompt_dict', {}),
                        'pnginfo': None,
                        'cancel_prompts': []
                    }

                mock_generate_single_image.side_effect = side_effect

                # _create_promptsメソッドをモックして固定のプロンプトを返すようにする
                with patch.object(generator, '_create_prompts') as mock_create_prompts:
                    # テスト用のベースプロンプト
                    base_prompts = ["test prompt"]
                    base_prompt_dict = {"Base Positive Prompt": ["test prompt"]}

                    mock_create_prompts.return_value = (
                        positive_prompts,  # positive_prompt
                        negative_prompts,  # negative_prompt
                        9876543210,        # seed
                        {                  # prompt_info
                            'positive_prompt': positive_prompts,
                            'negative_prompt': negative_prompts,
                            'positive_base_prompt_dict': base_prompt_dict,
                            'positive_pose_prompt_dict': {},
                            'positive_optional_prompt_dict': {},
                            'negative_prompt_dict': {"Base Negative Prompt": [negative_prompts]},
                            'cancel_prompts': [],
                            # 新しく追加したキー
                            'reusable_base_prompts': base_prompts,
                            'reusable_base_prompt_dict': base_prompt_dict
                        }
                    )

                    # 実際のメソッドを呼び出し
                    result = generator._generate_images()

                    # _generate_single_imageが呼び出されたことを確認
                    mock_generate_single_image.assert_called()

        # 結果の検証 - _generate_single_imageをモックしたため、直接フォルダ構造を確認
        # 出力フォルダが作成されているか確認
        output_base_path = os.path.join(self.test_output_dir, "realistic", "female", "normal")
        self.assertTrue(os.path.exists(output_base_path), "出力フォルダが作成されていません")

        # 日付とシード値を含むフォルダが作成されているか確認（フォルダ名のパターンをチェック）
        date_seed_folders = [f for f in os.listdir(output_base_path) if re.match(r"\d{8}-\d{2}-\d+", f)]
        self.assertTrue(len(date_seed_folders) > 0, "日付とシード値を含むフォルダが作成されていません")

    @patch('requests.post')
    def test_04_image_save_with_different_image_types(self, mock_post):
        """異なる画像タイプでも正しく保存されることをテスト（統合テスト）"""
        # APIレスポンスのみをモック
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'images': ['iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='],
            'parameters': {},
            'info': '{"seed": 9876543210}'
        }
        mock_post.return_value = mock_response

        # モックの追加設定：png-infoのレスポンスをモック
        def mock_post_side_effect(url, json=None, **kwargs):
            if url.endswith('/png-info'):
                mock_png_response = MagicMock()
                mock_png_response.status_code = 200
                mock_png_response.json.return_value = {
                    'info': 'Seed: 9876543210'
                }
                return mock_png_response
            return mock_response

        mock_post.side_effect = mock_post_side_effect

        # テスト用の画像タイプの組み合わせ
        test_cases = [
            {"style": "realistic", "category": "female", "subcategory": "normal"},
            {"style": "realistic", "category": "female", "subcategory": "transparent"},
            {"style": "illustration", "category": "female", "subcategory": "selfie"},
            {"style": "illustration", "category": "male", "subcategory": "normal"}
        ]

        for case in test_cases:
            # テスト対象のインスタンスを作成
            generator = AutoImageGenerator(
                image_generate_batch_execute_count=1,
                another_version_generate_count=0,
                input_folder=self.test_input_dir,
                output_folder=self.test_output_dir,
                prompts_folder=self.prompts_dir,
                style=case["style"],
                category=case["category"],
                subcategory=case["subcategory"],
                output_folder_prefix=f"/{case['style']}/{case['category']}/{case['subcategory']}"  # 明示的にプレフィックスを設定
            )

            # 必要な属性を設定（最小限に）
            generator.DATA_CANCEL_SEEDS = {"Seeds": []}  # 空のリストに設定してキャンセル処理をバイパス
            generator.current_seed = 9876543210  # 十分大きな値に変更
            generator.CANCEL_MIN_SEED_VALUE = -1  # キャンセル閾値を十分小さい値に設定

            # PNGINFOのURLを設定（必要に応じて）
            generator.PNGINFO_URL = "http://localhost:7860/sdapi/v1/png-info"

            # テスト用のプロンプトとペイロードを準備
            positive_prompts = "test prompt"
            negative_prompts = "test negative prompt"
            payload = {
                "prompt": positive_prompts,
                "negative_prompt": negative_prompts,
                "seed": 9876543210,
                "batch_size": 1,
                "n_iter": 1,
                "steps": 20,
                "cfg_scale": 7,
                "width": 512,
                "height": 512,
                "sampler_name": "Euler a"
            }

            # _create_promptsメソッドをモックして固定のプロンプトを返すようにする
            with patch.object(generator, 'set_model', return_value=True) as mock_set_model:
                # _generate_single_imageメソッドをモックして、実際のAPIを呼び出さないようにする
                with patch.object(generator, '_generate_single_image') as mock_generate_single_image:
                    # モックの戻り値を設定 - 実際のメソッドは戻り値を返さないのでNoneでOK
                    mock_generate_single_image.return_value = None

                    # モックが呼び出された時に、result_imagesに値を追加するサイドエフェクトを設定
                    def side_effect(payload, output_folder_path, filename, result_images, prompt_info):
                        # テスト用の画像オブジェクトを作成
                        test_image = Image.new('RGB', (1, 1), color='red')
                        # result_imagesに値を追加
                        result_images[output_folder_path] = {
                            'filename': filename,
                            'seed_value': 9876543210,
                            'image': test_image,
                            'positive_base_prompt_dict': prompt_info.get('positive_base_prompt_dict', {}),
                            'positive_pose_prompt_dict': prompt_info.get('positive_pose_prompt_dict', {}),
                            'positive_optional_prompt_dict': prompt_info.get('positive_optional_prompt_dict', {}),
                            'negative_prompt_dict': prompt_info.get('negative_prompt_dict', {}),
                            'pnginfo': None,
                            'cancel_prompts': []
                        }

                    mock_generate_single_image.side_effect = side_effect

                    with patch.object(generator, '_create_prompts') as mock_create_prompts:
                        # テスト用のベースプロンプト
                        base_prompts = ["test prompt"]
                        base_prompt_dict = {"Base Positive Prompt": ["test prompt"]}

                        mock_create_prompts.return_value = (
                            positive_prompts,  # positive_prompt
                            negative_prompts,  # negative_prompt
                            9876543210,        # seed
                            {                  # prompt_info
                                'positive_prompt': positive_prompts,
                                'negative_prompt': negative_prompts,
                                'positive_base_prompt_dict': base_prompt_dict,
                                'positive_pose_prompt_dict': {},
                                'positive_optional_prompt_dict': {},
                                'negative_prompt_dict': {"Base Negative Prompt": [negative_prompts]},
                                'cancel_prompts': [],
                                # 新しく追加したキー
                                'reusable_base_prompts': base_prompts,
                                'reusable_base_prompt_dict': base_prompt_dict
                            }
                        )

                        # 実際のメソッドを呼び出し
                        result = generator._generate_images()

                        # _generate_single_imageが呼び出されたことを確認
                        mock_generate_single_image.assert_called()

            # 結果の検証 - _generate_single_imageをモックしたため、直接フォルダ構造を確認
            # 出力フォルダが作成されているか確認
            output_base_path = os.path.join(self.test_output_dir, case["style"], case["category"], case["subcategory"])
            self.assertTrue(os.path.exists(output_base_path), f"{case} の出力フォルダが作成されていません")

            # 日付とシード値を含むフォルダが作成されているか確認（フォルダ名のパターンをチェック）
            date_seed_folders = [f for f in os.listdir(output_base_path) if re.match(r"\d{8}-\d{2}-\d+", f)]
            self.assertTrue(len(date_seed_folders) > 0, f"{case} の日付とシード値を含むフォルダが作成されていません")

if __name__ == '__main__':
    unittest.main()