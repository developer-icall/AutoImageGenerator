import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールへのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テスト対象のモジュールをインポート
from auto_image_generator import AutoImageGenerator

class TestLandscapeRealistic(unittest.TestCase):
    """landscapeRealisticモデルを使用した背景画像生成のテスト"""

    def setUp(self):
        """テスト前の準備"""
        # モックの設定
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "images": ["base64encodedimage"],
            "parameters": {},
            "info": "{}"
        }

    @patch('auto_image_generator.requests.post')
    def test_generate_city_background(self, mock_post):
        """都市背景画像の生成テスト"""
        # モックの設定
        mock_post.return_value = self.mock_response

        # テスト用のAutoImageGeneratorインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=1,
            sd_model_checkpoint="landscapeRealistic_v20WarmColor.safetensors",
            sd_model_prefix="landscapeRealistic",
            style="realistic",
            category="background",
            subcategory="city",
            enable_hr=False
        )

        # _generate_imagesメソッドをモック化
        generator._generate_images = MagicMock()

        # 実行
        generator.run()

        # プロンプトフォルダのパスが正しいか確認
        expected_path = os.path.normpath(os.path.join(generator.PROMPTS_FOLDER, "realistic", "background", "city"))
        actual_path = os.path.normpath(generator._get_prompt_folder_path())
        self.assertEqual(actual_path, expected_path)

        # モデルのチェックポイントが正しいか確認
        self.assertEqual(
            generator.SD_MODEL_CHECKPOINT,
            "landscapeRealistic_v20WarmColor.safetensors"
        )

        # _generate_imagesが呼び出されたことを確認
        generator._generate_images.assert_called_once()

    @patch('auto_image_generator.requests.post')
    def test_generate_nature_background(self, mock_post):
        """自然背景画像の生成テスト"""
        # モックの設定
        mock_post.return_value = self.mock_response

        # テスト用のAutoImageGeneratorインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=1,
            sd_model_checkpoint="landscapeRealistic_v20WarmColor.safetensors",
            sd_model_prefix="landscapeRealistic",
            style="realistic",
            category="background",
            subcategory="nature",
            enable_hr=False
        )

        # _generate_imagesメソッドをモック化
        generator._generate_images = MagicMock()

        # 実行
        generator.run()

        # プロンプトフォルダのパスが正しいか確認
        expected_path = os.path.normpath(os.path.join(generator.PROMPTS_FOLDER, "realistic", "background", "nature"))
        actual_path = os.path.normpath(generator._get_prompt_folder_path())
        self.assertEqual(actual_path, expected_path)

        # _generate_imagesが呼び出されたことを確認
        generator._generate_images.assert_called_once()

    @patch('auto_image_generator.requests.post')
    def test_generate_illustration_background(self, mock_post):
        """イラスト背景画像の生成テスト"""
        # モックの設定
        mock_post.return_value = self.mock_response

        # テスト用のAutoImageGeneratorインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=1,
            sd_model_checkpoint="landscapeRealistic_v20WarmColor.safetensors",
            sd_model_prefix="landscapeRealistic",
            style="illustration",
            category="background",
            subcategory="city",
            enable_hr=False
        )

        # _generate_imagesメソッドをモック化
        generator._generate_images = MagicMock()

        # 実行
        generator.run()

        # プロンプトフォルダのパスが正しいか確認
        expected_path = os.path.normpath(os.path.join(generator.PROMPTS_FOLDER, "illustration", "background", "city"))
        actual_path = os.path.normpath(generator._get_prompt_folder_path())
        self.assertEqual(actual_path, expected_path)

        # _generate_imagesが呼び出されたことを確認
        generator._generate_images.assert_called_once()

    @patch('auto_image_generator.requests.post')
    def test_generate_house_background(self, mock_post):
        """家の背景画像の生成テスト"""
        # モックの設定
        mock_post.return_value = self.mock_response

        # テスト用のAutoImageGeneratorインスタンスを作成
        generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,
            another_version_generate_count=1,
            sd_model_checkpoint="landscapeRealistic_v20WarmColor.safetensors",
            sd_model_prefix="landscapeRealistic",
            style="realistic",
            category="background",
            subcategory="house",
            enable_hr=False
        )

        # _generate_imagesメソッドをモック化
        generator._generate_images = MagicMock()

        # 実行
        generator.run()

        # プロンプトフォルダのパスが正しいか確認
        expected_path = os.path.normpath(os.path.join(generator.PROMPTS_FOLDER, "realistic", "background", "house"))
        actual_path = os.path.normpath(generator._get_prompt_folder_path())
        self.assertEqual(actual_path, expected_path)

        # _generate_imagesが呼び出されたことを確認
        generator._generate_images.assert_called_once()

if __name__ == '__main__':
    unittest.main()