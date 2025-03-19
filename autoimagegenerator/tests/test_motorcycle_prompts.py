import unittest
import os
import json
from unittest.mock import patch, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auto_image_generator import AutoImageGenerator


class TestMotorcyclePrompts(unittest.TestCase):

    def setUp(self):
        """テストの前準備"""
        # テスト用のプロンプトフォルダパス
        self.realistic_prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts/realistic/vehicle/motorcycle")
        self.illustration_prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts/illustration/vehicle/motorcycle")

        # 必須ファイルのリスト
        self.required_files = [
            "positive_base.json",
            "positive_optional.json",
            "positive_pose.json",
            "positive_selfie.json",
            "negative.json",
            "cancel_seeds.json",
            "positive_cancel_pair.json"
        ]

    def test_required_files_exist(self):
        """必須ファイルが存在することを確認"""
        # リアル調のプロンプトファイルを確認
        for file in self.required_files:
            file_path = os.path.join(self.realistic_prompt_path, file)
            self.assertTrue(os.path.exists(file_path), f"リアル調の{file}が存在しません")

        # イラスト調のプロンプトファイルを確認
        for file in self.required_files:
            file_path = os.path.join(self.illustration_prompt_path, file)
            self.assertTrue(os.path.exists(file_path), f"イラスト調の{file}が存在しません")

    def test_positive_base_content(self):
        """positive_base.jsonの内容を確認"""
        # リアル調のプロンプトを確認
        with open(os.path.join(self.realistic_prompt_path, "positive_base.json"), "r", encoding="utf-8") as f:
            realistic_data = json.load(f)
            self.assertIn("Vehicle Type", realistic_data)
            self.assertIn("Brand", realistic_data)
            self.assertIn("Style", realistic_data)
            self.assertIn("Details", realistic_data)
            self.assertIn("Rider", realistic_data)
            self.assertIn("Rider Gear", realistic_data)

        # イラスト調のプロンプトを確認
        with open(os.path.join(self.illustration_prompt_path, "positive_base.json"), "r", encoding="utf-8") as f:
            illustration_data = json.load(f)
            self.assertIn("Vehicle Type", illustration_data)
            self.assertIn("Style", illustration_data)
            self.assertIn("Details", illustration_data)
            self.assertIn("Rider", illustration_data)
            self.assertIn("Rider Gear", illustration_data)

    def test_negative_content(self):
        """negative.jsonの内容を確認"""
        # リアル調のプロンプトを確認
        with open(os.path.join(self.realistic_prompt_path, "negative.json"), "r", encoding="utf-8") as f:
            realistic_data = json.load(f)
            self.assertIn("Base Negative Prompt", realistic_data)
            self.assertIn("prompts", realistic_data["Base Negative Prompt"])
            self.assertIn("use_max_prompts", realistic_data["Base Negative Prompt"])
            self.assertIn("use_min_prompts", realistic_data["Base Negative Prompt"])

        # イラスト調のプロンプトを確認
        with open(os.path.join(self.illustration_prompt_path, "negative.json"), "r", encoding="utf-8") as f:
            illustration_data = json.load(f)
            self.assertIn("Base Negative Prompt", illustration_data)
            self.assertIn("prompts", illustration_data["Base Negative Prompt"])
            self.assertIn("use_max_prompts", illustration_data["Base Negative Prompt"])
            self.assertIn("use_min_prompts", illustration_data["Base Negative Prompt"])

    def test_positive_cancel_pair_content(self):
        """positive_cancel_pair.jsonの内容を確認"""
        # リアル調のプロンプトを確認
        with open(os.path.join(self.realistic_prompt_path, "positive_cancel_pair.json"), "r", encoding="utf-8") as f:
            realistic_data = json.load(f)
            self.assertIsInstance(realistic_data, dict)
            self.assertIn("scooter", realistic_data)
            self.assertIn("dirt bike", realistic_data)
            self.assertIn("cafe racer", realistic_data)

        # イラスト調のプロンプトを確認
        with open(os.path.join(self.illustration_prompt_path, "positive_cancel_pair.json"), "r", encoding="utf-8") as f:
            illustration_data = json.load(f)
            self.assertIsInstance(illustration_data, dict)
            self.assertIn("scooter", illustration_data)
            self.assertIn("dirt bike", illustration_data)
            self.assertIn("cafe racer", illustration_data)
            self.assertIn("anime style", illustration_data)
            self.assertIn("manga style", illustration_data)

    def test_cancel_seeds_content(self):
        """cancel_seeds.jsonの内容を確認"""
        # リアル調のプロンプトを確認
        with open(os.path.join(self.realistic_prompt_path, "cancel_seeds.json"), "r", encoding="utf-8") as f:
            realistic_data = json.load(f)
            self.assertIn("Seeds", realistic_data)
            self.assertIsInstance(realistic_data["Seeds"], list)

        # イラスト調のプロンプトを確認
        with open(os.path.join(self.illustration_prompt_path, "cancel_seeds.json"), "r", encoding="utf-8") as f:
            illustration_data = json.load(f)
            self.assertIn("Seeds", illustration_data)
            self.assertIsInstance(illustration_data["Seeds"], list)

    def test_image_size_settings(self):
        """画像サイズ設定のテスト"""
        # テスト用の設定
        test_settings = {
            "default_image_sizes": {
                "realistic": {
                    "vehicle": {"width": 768, "height": 512}
                },
                "illustration": {
                    "vehicle": {"width": 768, "height": 512}
                }
            }
        }

        # プロンプトフォルダのパスを設定
        prompts_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")

        # リアル調の画像サイズを確認
        with patch('auto_image_generator.AutoImageGenerator._load_settings', return_value=test_settings):
            generator = AutoImageGenerator(
                style="realistic",
                category="vehicle",
                subcategory="motorcycle",
                prompts_folder=prompts_folder
            )
            self.assertEqual(generator.width, 768)
            self.assertEqual(generator.height, 512)

        # イラスト調の画像サイズを確認
        with patch('auto_image_generator.AutoImageGenerator._load_settings', return_value=test_settings):
            generator = AutoImageGenerator(
                style="illustration",
                category="vehicle",
                subcategory="motorcycle",
                prompts_folder=prompts_folder
            )
            self.assertEqual(generator.width, 768)
            self.assertEqual(generator.height, 512)


if __name__ == '__main__':
    unittest.main()