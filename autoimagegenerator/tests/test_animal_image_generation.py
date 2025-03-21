import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# テスト対象のモジュールへのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_image_generator import AutoImageGenerator

class TestAnimalImageGeneration(unittest.TestCase):
    """動物画像生成のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        # 共通の設定
        self.common_settings = {
            "image_generate_batch_execute_count": 1,
            "another_version_generate_count": 1,
            "input_folder": "./images/input",
            "output_folder": "./images/output",
            "prompts_folder": "./prompts",
            "url": "http://localhost:7860",
            "enable_hr": False,
            "width": 512,
            "height": 512
        }

    @patch('auto_image_generator.AutoImageGenerator._switch_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_images')
    @patch('auto_image_generator.requests.post')
    def test_illustration_bird_generation(self, mock_post, mock_generate_images, mock_switch_model):
        """イラストスタイルの鳥画像生成テスト"""
        # モックの設定
        mock_post.return_value.json.return_value = {"images": ["base64_encoded_image"]}
        mock_generate_images.return_value = {"images": ["base64_encoded_image"]}

        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            **self.common_settings,
            sd_model_checkpoint="animagineXL40_v4Opt.safetensors",
            sd_model_prefix="animagineXL",
            output_folder_prefix="/illustration/animal/bird",
            is_transparent_background=False,
            is_selfie=False,
            style="illustration",
            category="animal",
            subcategory="bird"
        )

        # モデル切り替えフラグをリセット
        generator._model_switch_executed = False

        # モデルを切り替え
        generator.set_model("animagineXL40_v4Opt.safetensors")

        # プロンプト生成のテスト
        prompts = generator.generate_prompts()

        # プロンプトの内容を検証
        self.assertIn("positive_prompt", prompts)
        self.assertIn("negative_prompt", prompts)
        self.assertIn("bird", prompts["positive_prompt"].lower())

        # 画像生成のテスト
        generator.run()

        # モデル切り替えが呼ばれたことを確認
        mock_switch_model.assert_called_once()

        # 画像生成が呼ばれたことを確認
        mock_generate_images.assert_called()

    @patch('auto_image_generator.AutoImageGenerator._switch_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_images')
    @patch('auto_image_generator.requests.post')
    def test_realistic_bird_generation(self, mock_post, mock_generate_images, mock_switch_model):
        """リアルスタイルの鳥画像生成テスト"""
        # モックの設定
        mock_post.return_value.json.return_value = {"images": ["base64_encoded_image"]}
        mock_generate_images.return_value = {"images": ["base64_encoded_image"]}

        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            **self.common_settings,
            sd_model_checkpoint="yayoiMix_v25.safetensors",
            sd_model_prefix="yayoiMix",
            output_folder_prefix="/realistic/animal/bird",
            is_transparent_background=False,
            is_selfie=False,
            style="realistic",
            category="animal",
            subcategory="bird"
        )

        # モデル切り替えフラグをリセット
        generator._model_switch_executed = False

        # モデルを切り替え
        generator.set_model("yayoiMix_v25.safetensors")

        # プロンプト生成のテスト
        prompts = generator.generate_prompts()

        # プロンプトの内容を検証
        self.assertIn("positive_prompt", prompts)
        self.assertIn("negative_prompt", prompts)
        self.assertIn("bird", prompts["positive_prompt"].lower())
        self.assertIn("realistic", prompts["positive_prompt"].lower())

        # 画像生成のテスト
        generator.run()

        # モデル切り替えが呼ばれたことを確認
        mock_switch_model.assert_called_once()

        # 画像生成が呼ばれたことを確認
        mock_generate_images.assert_called()

    @patch('auto_image_generator.AutoImageGenerator._switch_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_images')
    @patch('auto_image_generator.requests.post')
    def test_illustration_cat_generation(self, mock_post, mock_generate_images, mock_switch_model):
        """イラストスタイルの猫画像生成テスト"""
        # モックの設定
        mock_post.return_value.json.return_value = {"images": ["base64_encoded_image"]}
        mock_generate_images.return_value = {"images": ["base64_encoded_image"]}

        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            **self.common_settings,
            sd_model_checkpoint="animagineXL40_v4Opt.safetensors",
            sd_model_prefix="animagineXL",
            output_folder_prefix="/illustration/animal/cat",
            is_transparent_background=False,
            is_selfie=False,
            style="illustration",
            category="animal",
            subcategory="cat"
        )

        # モデル切り替えフラグをリセット
        generator._model_switch_executed = False

        # モデルを切り替え
        generator.set_model("animagineXL40_v4Opt.safetensors")

        # プロンプト生成のテスト
        prompts = generator.generate_prompts()

        # プロンプトの内容を検証
        self.assertIn("positive_prompt", prompts)
        self.assertIn("negative_prompt", prompts)
        self.assertIn("cat", prompts["positive_prompt"].lower())

        # 画像生成のテスト
        generator.run()

        # モデル切り替えが呼ばれたことを確認
        mock_switch_model.assert_called_once()

        # 画像生成が呼ばれたことを確認
        mock_generate_images.assert_called()

    @patch('auto_image_generator.AutoImageGenerator._switch_model')
    @patch('auto_image_generator.AutoImageGenerator._generate_images')
    @patch('auto_image_generator.requests.post')
    def test_realistic_cat_generation(self, mock_post, mock_generate_images, mock_switch_model):
        """リアルスタイルの猫画像生成テスト"""
        # モックの設定
        mock_post.return_value.json.return_value = {"images": ["base64_encoded_image"]}
        mock_generate_images.return_value = {"images": ["base64_encoded_image"]}

        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            **self.common_settings,
            sd_model_checkpoint="yayoiMix_v25.safetensors",
            sd_model_prefix="yayoiMix",
            output_folder_prefix="/realistic/animal/cat",
            is_transparent_background=False,
            is_selfie=False,
            style="realistic",
            category="animal",
            subcategory="cat"
        )

        # モデル切り替えフラグをリセット
        generator._model_switch_executed = False

        # モデルを切り替え
        generator.set_model("yayoiMix_v25.safetensors")

        # プロンプト生成のテスト
        prompts = generator.generate_prompts()

        # プロンプトの内容を検証
        self.assertIn("positive_prompt", prompts)
        self.assertIn("negative_prompt", prompts)
        self.assertIn("cat", prompts["positive_prompt"].lower())
        self.assertIn("realistic", prompts["positive_prompt"].lower())

        # 画像生成のテスト
        generator.run()

        # モデル切り替えが呼ばれたことを確認
        mock_switch_model.assert_called_once()

        # 画像生成が呼ばれたことを確認
        mock_generate_images.assert_called()

if __name__ == '__main__':
    unittest.main()