import os
import sys
import unittest
import subprocess
import json
import logging
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ログディレクトリの作成
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, f"test_rpg_icon_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
    ]
)
logger = logging.getLogger(__name__)

class TestRPGIconGeneration(unittest.TestCase):
    """RPGIcon用の画像生成をテストするクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_rpg_icon_folder_structure(self):
        """RPGIcon用のフォルダ構造が正しいかテスト"""
        # プロンプトフォルダのパスを取得
        prompts_dir = os.path.join(self.base_dir, "prompts")

        # RPGIcon用のプロンプトフォルダパス
        rpg_icon_dir = os.path.join(prompts_dir, "illustration", "rpg_icon")

        # フォルダが存在するか確認
        self.assertTrue(os.path.exists(rpg_icon_dir), "RPGIcon用のフォルダが存在しません")

        # サブフォルダが存在するか確認
        weapon_dir = os.path.join(rpg_icon_dir, "weapon")
        monster_dir = os.path.join(rpg_icon_dir, "monster")
        other_dir = os.path.join(rpg_icon_dir, "other")

        self.assertTrue(os.path.exists(weapon_dir), "weapon フォルダが存在しません")
        self.assertTrue(os.path.exists(monster_dir), "monster フォルダが存在しません")
        self.assertTrue(os.path.exists(other_dir), "other フォルダが存在しません")

        # 各フォルダに必要なファイルが存在するか確認
        required_files = [
            "positive_base.json",
            "positive_optional.json",
            "positive_pose.json",
            "positive_selfie.json",
            "negative.json",
            "cancel_seeds.json",
            "positive_cancel_pair.json"
        ]

        for folder in [weapon_dir, monster_dir, other_dir]:
            for file in required_files:
                file_path = os.path.join(folder, file)
                self.assertTrue(os.path.exists(file_path), f"{os.path.basename(folder)} フォルダに {file} が存在しません")

if __name__ == "__main__":
    unittest.main()