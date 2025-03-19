import unittest
import json
import os
import logging
from unittest.mock import patch, mock_open
from auto_image_generator import AutoImageGenerator

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLoraImageSize(unittest.TestCase):
    """LoRAの画像サイズ設定のテストクラス"""

    def setUp(self):
        """テスト開始前の準備"""
        # テスト用の設定
        self.test_settings = {
            "image_generate_batch_execute_count": 1,
            "another_version_generate_count": 1,
            "default_image_sizes": {
                "realistic": {
                    "female": {"width": 512, "height": 768},
                    "vehicle": {"width": 768, "height": 512}
                }
            },
            "lora_settings": {
                "KawasakiNinja300": {
                    "model": "sd_xl_base_1.0",
                    "weight": 0.8,
                    "trigger_word": "kawasakininja300, motorcycle, realistic",
                    "image_size": {
                        "width": 768,
                        "height": 512
                    }
                },
                "waifu_on_Motorcycle_v2": {
                    "model": "sd_xl_base_1.0",
                    "weight": 0.7,
                    "trigger_word": "waifu on motorcycle, illustration, anime style",
                    "image_size": {
                        "width": 512,
                        "height": 768
                    }
                }
            }
        }

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": []}')
    @patch('auto_image_generator.AutoImageGenerator._load_settings')
    def test_kawasaki_ninja_image_size(self, mock_load_settings, mock_open_file):
        """KawasakiNinja300 LoRAの画像サイズ設定をテスト"""
        logger.info("KawasakiNinja300 LoRAの画像サイズ設定をテスト")
        # モックの設定
        mock_load_settings.return_value = self.test_settings

        # LoRAを使用した状態でインスタンスを作成
        generator = AutoImageGenerator(
            use_lora=True,
            lora_name="KawasakiNinja300"
        )

        # 画像サイズが正しく設定されているか確認
        self.assertEqual(generator.width, 768, "KawasakiNinja300の幅が768に設定されていません")
        self.assertEqual(generator.height, 512, "KawasakiNinja300の高さが512に設定されていません")
        logger.info("KawasakiNinja300の画像サイズテストが成功しました")

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": []}')
    @patch('auto_image_generator.AutoImageGenerator._load_settings')
    def test_waifu_motorcycle_image_size(self, mock_load_settings, mock_open_file):
        """waifu_on_Motorcycle_v2 LoRAの画像サイズ設定をテスト"""
        logger.info("waifu_on_Motorcycle_v2 LoRAの画像サイズ設定をテスト")
        # モックの設定
        mock_load_settings.return_value = self.test_settings

        # LoRAを使用した状態でインスタンスを作成
        generator = AutoImageGenerator(
            use_lora=True,
            lora_name="waifu_on_Motorcycle_v2"
        )

        # 画像サイズが正しく設定されているか確認
        self.assertEqual(generator.width, 512, "waifu_on_Motorcycle_v2の幅が512に設定されていません")
        self.assertEqual(generator.height, 768, "waifu_on_Motorcycle_v2の高さが768に設定されていません")
        logger.info("waifu_on_Motorcycle_v2の画像サイズテストが成功しました")

    @patch('builtins.open', new_callable=mock_open, read_data='{"test": []}')
    @patch('auto_image_generator.AutoImageGenerator._load_settings')
    def test_default_image_size(self, mock_load_settings, mock_open_file):
        """デフォルトの画像サイズ設定をテスト"""
        logger.info("デフォルトの画像サイズ設定をテスト")
        # モックの設定
        mock_load_settings.return_value = self.test_settings

        # LoRAを使用しない状態でインスタンスを作成
        generator = AutoImageGenerator(
            style="realistic",
            category="female"
        )

        # 画像サイズが正しく設定されているか確認
        self.assertEqual(generator.width, 512, "デフォルトの幅が512に設定されていません")
        self.assertEqual(generator.height, 768, "デフォルトの高さが768に設定されていません")
        logger.info("デフォルトの画像サイズテストが成功しました")

if __name__ == '__main__':
    unittest.main()