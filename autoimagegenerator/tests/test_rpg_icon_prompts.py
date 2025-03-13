import os
import json
import sys
import unittest
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
        logging.FileHandler(os.path.join(log_dir, f"test_rpg_icon_prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"))
    ]
)
logger = logging.getLogger(__name__)

# AutoImageGeneratorクラスのインポートはコメントアウト
# from auto_image_generator import AutoImageGenerator

class TestRPGIconPrompts(unittest.TestCase):
    """RPGIcon用のプロンプト設定ファイルをテストするクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prompts_dir = os.path.join(self.base_dir, "prompts")

        # RPGIcon用のプロンプトフォルダパス
        self.weapon_prompts_dir = os.path.join(self.prompts_dir, "illustration", "rpg_icon", "weapon")
        self.monster_prompts_dir = os.path.join(self.prompts_dir, "illustration", "rpg_icon", "monster")
        self.other_prompts_dir = os.path.join(self.prompts_dir, "illustration", "rpg_icon", "other")

    def test_folder_structure(self):
        """フォルダ構造が正しいかテスト"""
        # 各フォルダが存在するか確認
        self.assertTrue(os.path.exists(self.weapon_prompts_dir), "weapon フォルダが存在しません")
        self.assertTrue(os.path.exists(self.monster_prompts_dir), "monster フォルダが存在しません")
        self.assertTrue(os.path.exists(self.other_prompts_dir), "other フォルダが存在しません")

    def test_weapon_prompt_files(self):
        """武器・防具用のプロンプト設定ファイルが正しいかテスト"""
        # 必要なファイルが存在するか確認
        files = [
            "positive_base.json",
            "positive_optional.json",
            "positive_pose.json",
            "positive_selfie.json",
            "negative.json",
            "cancel_seeds.json",
            "positive_cancel_pair.json"
        ]

        for file in files:
            file_path = os.path.join(self.weapon_prompts_dir, file)
            self.assertTrue(os.path.exists(file_path), f"{file} が存在しません")

            # JSONとして正しく読み込めるか確認
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    self.assertIsInstance(json_data, dict, f"{file} が正しいJSON形式ではありません")
            except json.JSONDecodeError:
                self.fail(f"{file} が正しいJSON形式ではありません")

    def test_monster_prompt_files(self):
        """モンスター用のプロンプト設定ファイルが正しいかテスト"""
        # 必要なファイルが存在するか確認
        files = [
            "positive_base.json",
            "positive_optional.json",
            "positive_pose.json",
            "positive_selfie.json",
            "negative.json",
            "cancel_seeds.json",
            "positive_cancel_pair.json"
        ]

        for file in files:
            file_path = os.path.join(self.monster_prompts_dir, file)
            self.assertTrue(os.path.exists(file_path), f"{file} が存在しません")

            # JSONとして正しく読み込めるか確認
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    self.assertIsInstance(json_data, dict, f"{file} が正しいJSON形式ではありません")
            except json.JSONDecodeError:
                self.fail(f"{file} が正しいJSON形式ではありません")

    def test_other_prompt_files(self):
        """その他用のプロンプト設定ファイルが正しいかテスト"""
        # 必要なファイルが存在するか確認
        files = [
            "positive_base.json",
            "positive_optional.json",
            "positive_pose.json",
            "positive_selfie.json",
            "negative.json",
            "cancel_seeds.json",
            "positive_cancel_pair.json"
        ]

        for file in files:
            file_path = os.path.join(self.other_prompts_dir, file)
            self.assertTrue(os.path.exists(file_path), f"{file} が存在しません")

            # JSONとして正しく読み込めるか確認
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    self.assertIsInstance(json_data, dict, f"{file} が正しいJSON形式ではありません")
            except json.JSONDecodeError:
                self.fail(f"{file} が正しいJSON形式ではありません")

    # AutoImageGeneratorクラスのテストはスキップ
    # def test_auto_image_generator_load(self):
    #     """AutoImageGeneratorクラスでプロンプト設定ファイルが正しく読み込めるかテスト"""
    #     # AutoImageGeneratorインスタンスを作成
    #     auto_image_generator = AutoImageGenerator(
    #         image_generate_batch_execute_count=1,
    #         another_version_generate_count=1,
    #         input_folder="../images/input",
    #         output_folder="../images/output",
    #         prompts_folder="./prompts",
    #         url="http://localhost:7860",
    #         sd_model_checkpoint="photoRealV15_photorealv21.safetensors",
    #         sd_model_prefix="rpg_icon",
    #         enable_hr=True,
    #         output_folder_prefix="/illustration/rpg_icon/weapon",
    #         is_transparent_background=False,
    #         is_selfie=False,
    #         style="illustration",
    #         category="rpg_icon",
    #         subcategory="weapon"
    #     )
    #
    #     # プロンプトフォルダのパスが正しく設定されているか確認
    #     expected_path = os.path.join(self.prompts_dir, "illustration", "rpg_icon", "weapon")
    #     self.assertEqual(auto_image_generator._get_prompt_folder_path(), expected_path)

if __name__ == "__main__":
    unittest.main()