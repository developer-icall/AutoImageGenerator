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

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 直接インポート
from autoimagegenerator.auto_image_generator import AutoImageGenerator

class TestImageSave(unittest.TestCase):
    """画像保存機能のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        # テスト用のディレクトリを作成
        self.test_output_dir = "./test_output"
        self.test_input_dir = "./test_input"
        self.test_prompts_dir = "./test_prompts"

        # 基本ディレクトリを作成
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_input_dir, exist_ok=True)
        os.makedirs(self.test_prompts_dir, exist_ok=True)

        # テスト用のサンプル画像を作成
        self.create_test_sample_image()

        # テスト用のプロンプトファイルを作成
        self.create_test_prompt_files()

        # テスト用のsettings.jsonを作成
        self.create_test_settings()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用のディレクトリを削除
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        if os.path.exists(self.test_input_dir):
            shutil.rmtree(self.test_input_dir)
        if os.path.exists(self.test_prompts_dir):
            shutil.rmtree(self.test_prompts_dir)

    def create_test_sample_image(self):
        """テスト用のサンプル画像を作成"""
        # サンプル画像を作成
        img = Image.new('RGB', (100, 100), color='red')
        img.save(os.path.join(self.test_input_dir, 'sample.png'))

    def create_test_prompt_files(self):
        """テスト用のプロンプトファイルを作成"""
        # テスト用のプロンプトファイルを作成するディレクトリ
        prompt_dirs = [
            os.path.join(self.test_prompts_dir, "realistic", "female"),
            os.path.join(self.test_prompts_dir, "realistic", "male"),
            os.path.join(self.test_prompts_dir, "illustration", "female"),
            os.path.join(self.test_prompts_dir, "illustration", "animal")
        ]

        # 各ディレクトリを作成
        for dir_path in prompt_dirs:
            os.makedirs(dir_path, exist_ok=True)

            # 必要なすべてのプロンプトファイルを作成
            prompt_files = {
                "positive_base.json": '{"Prompts": ["test prompt"]}',
                "positive_pose.json": '{"Prompts": ["test pose prompt"]}',
                "positive_optional.json": '{"Prompts": ["test optional prompt"]}',
                "positive_selfie.json": '{"Prompts": ["test selfie prompt"]}',
                "negative.json": '{"Prompts": ["test negative prompt"]}',
                "cancel_seeds.json": '{"Seeds": [1234567890]}',
                "positive_cancel_pair.json": '{"Pairs": []}'
            }

            # 各ファイルを作成
            for filename, content in prompt_files.items():
                with open(os.path.join(dir_path, filename), 'w') as f:
                    f.write(content)

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
            prompts_folder=self.test_prompts_dir,
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
            prompts_folder=self.test_prompts_dir,
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
            prompts_folder=self.test_prompts_dir,
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

        # 実際のメソッドを呼び出し
        result = generator.generate_images(positive_prompts, negative_prompts, payload, 0)

        # 結果の検証
        self.assertTrue(len(result) > 0, "画像が生成されていません")

        # 保存先フォルダのパスを取得
        folder_path = list(result.keys())[0]

        # 正しいパスに保存されているか確認
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
            self.assertIn(part, relative_folder_path, f"保存先フォルダに {part} が含まれていません")

        # 画像ファイルが存在するか確認
        image_data = list(result.values())[0]
        filename = image_data['filename']
        image_path = os.path.join(folder_path, filename + ".png")
        self.assertTrue(os.path.exists(image_path), f"画像ファイルが存在しません: {image_path}")

        # サブフォルダが作成されているか確認
        subfolders = ["thumbnail", "sample", "sample-thumbnail", "half-resolution"]
        for subfolder in subfolders:
            subfolder_path = os.path.join(folder_path, subfolder)
            self.assertTrue(os.path.exists(subfolder_path), f"サブフォルダが存在しません: {subfolder_path}")

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
            {"style": "realistic", "category": "male", "subcategory": "transparent"},
            {"style": "illustration", "category": "female", "subcategory": "selfie"},
            {"style": "illustration", "category": "animal", "subcategory": "dog"}
        ]

        for case in test_cases:
            # テスト対象のインスタンスを作成
            generator = AutoImageGenerator(
                image_generate_batch_execute_count=1,
                another_version_generate_count=0,
                input_folder=self.test_input_dir,
                output_folder=self.test_output_dir,
                prompts_folder=self.test_prompts_dir,
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

            # 実際のメソッドを呼び出し
            result = generator.generate_images(positive_prompts, negative_prompts, payload, 0)

            # 結果の検証
            self.assertTrue(len(result) > 0, f"{case} の画像が生成されていません")

            # 保存先フォルダのパスを取得
            folder_path = list(result.keys())[0]

            # 正しいパスに保存されているか確認
            # 絶対パスから相対パスの部分を抽出して比較
            relative_folder_path = os.path.relpath(folder_path, os.path.dirname(os.path.abspath(__file__)))
            expected_path_parts = [
                "test_output",
                case["style"],
                case["category"],
                case["subcategory"]
            ]

            # フォルダパスに期待される部分が含まれているか確認
            for part in expected_path_parts:
                self.assertIn(part, relative_folder_path, f"{case} の保存先フォルダに {part} が含まれていません")

            # 画像ファイルが存在するか確認
            image_data = list(result.values())[0]
            filename = image_data['filename']
            image_path = os.path.join(folder_path, filename + ".png")
            self.assertTrue(os.path.exists(image_path), f"画像ファイルが存在しません: {image_path}")

            # サブフォルダが作成されているか確認
            subfolders = ["thumbnail", "sample", "sample-thumbnail", "half-resolution"]
            for subfolder in subfolders:
                subfolder_path = os.path.join(folder_path, subfolder)
                self.assertTrue(os.path.exists(subfolder_path), f"サブフォルダが存在しません: {subfolder_path}")

if __name__ == '__main__':
    unittest.main()