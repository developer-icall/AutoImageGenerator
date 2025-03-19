import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime

# テスト対象のモジュールへのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ログディレクトリの作成
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, f"test_image_type_model_selection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
    ]
)
logger = logging.getLogger(__name__)

from auto_image_generator import AutoImageGenerator

class TestImageTypeModelSelection(unittest.TestCase):
    """画像タイプに応じたモデル選択をテストするクラス"""

    def setUp(self):
        """テスト前の準備"""
        # モックの設定
        self.patcher = patch('auto_image_generator.requests')
        self.mock_requests = self.patcher.start()

        # ディレクトリ作成をモック化
        self.patcher_os = patch('auto_image_generator.os.makedirs')
        self.mock_os_makedirs = self.patcher_os.start()

        # ファイル読み込みをモック化
        self.patcher_open = patch('builtins.open', create=True)
        self.mock_open = self.patcher_open.start()
        self.mock_open.return_value.__enter__.return_value.read.return_value = '{}'

        # jsonロードをモック化
        self.patcher_json = patch('auto_image_generator.json.load')
        self.mock_json_load = self.patcher_json.start()
        self.mock_json_load.return_value = {}

    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.patcher.stop()
        self.patcher_os.stop()
        self.patcher_open.stop()
        self.patcher_json.stop()

    def test_realistic_female_model_selection(self):
        """リアルテイスト女性画像のモデル選択テスト"""
        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            style="realistic",
            category="female",
            subcategory="normal",
            sd_model_prefix="brav7"
        )

        # モデル選択結果を検証
        self.assertEqual(generator.model, "brav7")

    def test_realistic_male_model_selection(self):
        """リアルテイスト男性画像のモデル選択テスト"""
        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            style="realistic",
            category="male",
            subcategory="normal",
            sd_model_prefix="brav7"
        )

        # モデル選択結果を検証
        self.assertEqual(generator.model, "brav7_men")

    def test_realistic_animal_model_selection(self):
        """リアルテイスト動物画像のモデル選択テスト"""
        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            style="realistic",
            category="animal",
            subcategory="dog",
            sd_model_prefix="brav6"
        )

        # モデル選択結果を検証
        self.assertEqual(generator.model, "petPhotography")

    def test_illustration_rpg_icon_model_selection(self):
        """イラストRPGアイコン画像のモデル選択テスト"""
        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            style="illustration",
            category="rpg_icon",
            subcategory="weapon",
            sd_model_prefix="brav6"
        )

        # モデル選択結果を検証
        self.assertEqual(generator.model, "photoRealRPG")

    def test_illustration_female_model_selection(self):
        """イラスト女性画像のモデル選択テスト"""
        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            style="illustration",
            category="female",
            subcategory="normal",
            sd_model_prefix="brav6"
        )

        # モデル選択結果を検証
        self.assertEqual(generator.model, "brav7")

    def test_illustration_male_model_selection(self):
        """イラスト男性画像のモデル選択テスト"""
        # テスト対象のインスタンス作成
        generator = AutoImageGenerator(
            style="illustration",
            category="male",
            subcategory="normal",
            sd_model_prefix="brav6"
        )

        # モデル選択結果を検証
        self.assertEqual(generator.model, "brav7_men")

if __name__ == '__main__':
    unittest.main()