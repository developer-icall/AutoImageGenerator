import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールへのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テスト対象のモジュールをインポート
from main import validate_image_type, get_default_model, IMAGE_STYLES, SD_MODEL_CHECKPOINTS

class TestMain(unittest.TestCase):
    """main.pyの機能をテストするクラス"""

    def test_validate_image_type_background(self):
        """背景画像タイプのバリデーションテスト"""
        # 有効な組み合わせ
        self.assertTrue(validate_image_type("realistic", "background", "city"))
        self.assertTrue(validate_image_type("realistic", "background", "nature"))
        self.assertTrue(validate_image_type("realistic", "background", "sea"))
        self.assertTrue(validate_image_type("realistic", "background", "sky"))
        self.assertTrue(validate_image_type("realistic", "background", "house"))

        # 無効な組み合わせ
        self.assertFalse(validate_image_type("realistic", "background", "invalid"))
        self.assertFalse(validate_image_type("invalid", "background", "city"))
        self.assertFalse(validate_image_type("realistic", "invalid", "city"))

    def test_image_styles_background(self):
        """IMAGE_STYLESの背景カテゴリー設定テスト"""
        # realistic/backgroundの設定を確認
        self.assertIn("background", IMAGE_STYLES["realistic"])
        self.assertIn("types", IMAGE_STYLES["realistic"]["background"])
        self.assertIn("models", IMAGE_STYLES["realistic"]["background"])

        # house が追加されているか確認
        self.assertIn("house", IMAGE_STYLES["realistic"]["background"]["types"])

        # landscapeRealisticがモデルに含まれているか確認
        self.assertIn("landscapeRealistic", IMAGE_STYLES["realistic"]["background"]["models"])

    def test_model_checkpoints_background(self):
        """SD_MODEL_CHECKPOINTSの背景モデル設定テスト"""
        # landscapeRealisticがSD_MODEL_CHECKPOINTSに含まれているか確認
        self.assertIn("landscapeRealistic", SD_MODEL_CHECKPOINTS)

        # landscapeRealisticの設定が正しいか確認
        self.assertEqual(
            SD_MODEL_CHECKPOINTS["landscapeRealistic"],
            "landscapeRealistic_v20WarmColor.safetensors"
        )

    def test_get_default_model_background(self):
        """背景画像のデフォルトモデル選択テスト"""
        # backgroundカテゴリのデフォルトモデルがlandscapeRealisticか確認
        self.assertEqual(get_default_model("background"), "landscapeRealistic")

if __name__ == '__main__':
    unittest.main()