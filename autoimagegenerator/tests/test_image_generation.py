import os
import sys
import unittest
import json
import shutil
import glob
import re
from pathlib import Path
import logging
import time
from datetime import datetime

# 親ディレクトリをパスに追加して、autoimagegeneratorモジュールをインポートできるようにする
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_image_generator import AutoImageGenerator

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_image_generation.log')
    ]
)
logger = logging.getLogger(__name__)

class TestImageGeneration(unittest.TestCase):
    """画像生成のテストクラス"""

    @classmethod
    def setUpClass(cls):
        """テスト開始前の準備"""
        # プロジェクトのルートディレクトリを取得
        cls.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

        # テスト用の設定を読み込む
        try:
            # 一時設定ファイルが存在する場合はそちらを優先して読み込む
            temp_settings_file = os.path.join(os.path.dirname(__file__), 'temp_test_settings.json')
            if os.path.exists(temp_settings_file):
                with open(temp_settings_file, 'r', encoding='utf-8') as f:
                    cls.settings = json.load(f)
                logger.info("一時設定ファイルから設定を読み込みました")
            else:
                with open(os.path.join(os.path.dirname(__file__), 'test_settings.json'), 'r', encoding='utf-8') as f:
                    cls.settings = json.load(f)
                logger.info("通常の設定ファイルから設定を読み込みました")
        except FileNotFoundError:
            # テスト設定ファイルがない場合はデフォルト設定を使用
            cls.settings = {
                "image_generate_batch_execute_count": 1,
                "another_version_generate_count": 1,
                "url": "http://localhost:7860",
                "test_patterns": [
                    {
                        "name": "realistic_female_normal",
                        "style": "realistic",
                        "category": "female",
                        "subcategory": "normal",
                        "model": "brav7",
                        "enable_hr": False
                    },
                    {
                        "name": "realistic_female_selfie",
                        "style": "realistic",
                        "category": "female",
                        "subcategory": "selfie",
                        "model": "brav6",
                        "enable_hr": False
                    },
                    {
                        "name": "realistic_female_transparent",
                        "style": "realistic",
                        "category": "female",
                        "subcategory": "transparent",
                        "model": "brav7",
                        "enable_hr": False
                    }
                ]
            }
            # テスト設定ファイルを作成
            os.makedirs(os.path.dirname(__file__), exist_ok=True)
            with open(os.path.join(os.path.dirname(__file__), 'test_settings.json'), 'w', encoding='utf-8') as f:
                json.dump(cls.settings, f, indent=4, ensure_ascii=False)
            logger.info("デフォルト設定を使用します")

        # テスト結果保存用のディレクトリを作成
        cls.test_output_dir = Path(os.path.join(os.path.dirname(__file__), "output"))
        cls.test_output_dir.mkdir(parents=True, exist_ok=True)

        # テスト結果のログファイル
        cls.test_results_file = cls.test_output_dir / "test_results.json"

        # 既存のテスト結果ファイルを削除（毎回初期化）
        if cls.test_results_file.exists():
            try:
                cls.test_results_file.unlink()
                logger.info(f"既存のテスト結果ファイルを削除しました: {cls.test_results_file}")
            except Exception as e:
                logger.warning(f"テスト結果ファイルの削除中にエラーが発生しました: {e}")

        cls.test_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": []
        }

    def setUp(self):
        """各テストケース実行前の準備"""
        # テスト開始時間を記録
        self.start_time = time.time()

    def tearDown(self):
        """各テストケース実行後の処理"""
        # テスト終了時間を記録
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        logger.info(f"テスト実行時間: {self.elapsed_time:.2f}秒")

    @classmethod
    def tearDownClass(cls):
        """全テスト終了後の処理"""
        # テスト結果をJSONファイルに保存
        with open(cls.test_results_file, 'w', encoding='utf-8') as f:
            json.dump(cls.test_results, f, indent=4, ensure_ascii=False)

        logger.info(f"テスト結果を {cls.test_results_file} に保存しました")

    def test_image_generation_patterns(self):
        """異なるパターンでの画像生成をテストする"""
        for pattern in self.settings["test_patterns"]:
            with self.subTest(pattern=pattern["name"]):
                logger.info(f"テストパターン '{pattern['name']}' を開始します")

                # テスト結果を格納する辞書
                test_result = {
                    "pattern": pattern["name"],
                    "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "success": False,
                    "error": None,
                    "output_path": None,
                    "elapsed_time": 0,
                    "validation_results": {}
                }

                pattern_start_time = time.time()

                try:
                    # 出力フォルダのプレフィックスを設定
                    output_folder_prefix = f"/{pattern['style']}/{pattern['category']}/{pattern['subcategory']}"

                    # 絶対パスを使用
                    input_folder = os.path.join(self.project_root, "images", "input")
                    output_folder = os.path.join(os.path.dirname(__file__), "output", "images")
                    prompts_folder = os.path.join(self.project_root, "autoimagegenerator", "prompts")

                    # ディレクトリが存在するか確認
                    if not os.path.exists(prompts_folder):
                        logger.error(f"プロンプトフォルダが存在しません: {prompts_folder}")
                        # プロンプトフォルダが存在しない場合は作成
                        os.makedirs(prompts_folder, exist_ok=True)
                        logger.info(f"プロンプトフォルダを作成しました: {prompts_folder}")

                    if not os.path.exists(input_folder):
                        logger.error(f"入力フォルダが存在しません: {input_folder}")
                        # 入力フォルダが存在しない場合は作成
                        os.makedirs(input_folder, exist_ok=True)
                        logger.info(f"入力フォルダを作成しました: {input_folder}")

                    # 出力フォルダが存在しない場合は作成
                    os.makedirs(output_folder, exist_ok=True)

                    # パスの情報をログに出力
                    logger.info(f"プロジェクトルート: {self.project_root}")
                    logger.info(f"入力フォルダ: {input_folder}")
                    logger.info(f"出力フォルダ: {output_folder}")
                    logger.info(f"プロンプトフォルダ: {prompts_folder}")

                    # AutoImageGeneratorインスタンスを作成
                    # モデル名に応じて適切なモデルファイル名を設定
                    model_checkpoints = {
                        "brav6": "beautifulRealistic_v60.safetensors",
                        "brav7": "beautifulRealistic_v7.safetensors",
                        "brav7_men": "beautifulRealistic_v7.safetensors",
                        "rpg_icon": "RPGIcon.safetensors"
                    }

                    # モデル名からモデルファイル名を取得（存在しない場合はそのまま使用）
                    model_checkpoint = model_checkpoints.get(pattern["model"], f"{pattern['model']}.safetensors")

                    # 設定から画像生成数とバージョン数を取得
                    image_generate_batch_execute_count = self.settings["image_generate_batch_execute_count"]
                    another_version_generate_count = self.settings["another_version_generate_count"]

                    logger.info(f"画像生成バッチ実行数: {image_generate_batch_execute_count}")
                    logger.info(f"別バージョン生成数: {another_version_generate_count}")

                    generator = AutoImageGenerator(
                        image_generate_batch_execute_count=image_generate_batch_execute_count,
                        another_version_generate_count=another_version_generate_count,
                        input_folder=input_folder,
                        output_folder=output_folder,
                        prompts_folder=prompts_folder,
                        url=self.settings["url"],
                        sd_model_checkpoint=model_checkpoint,
                        sd_model_prefix=pattern["model"],
                        enable_hr=pattern.get("enable_hr", False),
                        output_folder_prefix=output_folder_prefix,
                        is_transparent_background=pattern["subcategory"] == "transparent",
                        is_selfie=pattern["subcategory"] == "selfie",
                        style=pattern["style"],
                        category=pattern["category"],
                        subcategory=pattern["subcategory"]
                    )

                    # 画像生成を実行
                    generator.run()

                    # 出力ディレクトリを確認
                    output_path = Path(os.path.join(output_folder, pattern['style'], pattern['category'], pattern['subcategory']))

                    # 出力ディレクトリが存在し、中に画像ファイルがあるか確認
                    if output_path.exists():
                        # 1. image_generate_batch_execute_countの検証
                        # 日付-時間-seedのフォーマットのフォルダ数をカウント
                        seed_folders = [f for f in output_path.glob("*") if f.is_dir() and re.match(r"\d{8}-\d{2}-\d+", f.name)]

                        # 検証結果を記録
                        batch_count_valid = len(seed_folders) == image_generate_batch_execute_count
                        test_result["validation_results"]["batch_count_valid"] = batch_count_valid
                        test_result["validation_results"]["expected_batch_count"] = image_generate_batch_execute_count
                        test_result["validation_results"]["actual_batch_count"] = len(seed_folders)

                        logger.info(f"バッチ数検証: 期待値={image_generate_batch_execute_count}, 実際={len(seed_folders)}, 結果={'成功' if batch_count_valid else '失敗'}")

                        # 2. another_version_generate_countの検証
                        version_validation_results = []

                        for seed_folder in seed_folders:
                            seed_folder_path = str(seed_folder)
                            version_result = {
                                "seed_folder": seed_folder.name,
                                "files_validation": {}
                            }

                            # 期待されるファイル数（オリジナル + another_version_generate_count）
                            expected_file_count = another_version_generate_count + 1

                            # 直下のファイル検証
                            png_files = list(seed_folder.glob("*.png"))
                            jpg_files = list(seed_folder.glob("*.jpg"))
                            json_files = list(seed_folder.glob("*.json"))

                            png_valid = len(png_files) == expected_file_count
                            jpg_valid = len(jpg_files) == expected_file_count
                            json_valid = len(json_files) == expected_file_count

                            version_result["files_validation"]["root"] = {
                                "png": {"expected": expected_file_count, "actual": len(png_files), "valid": png_valid},
                                "jpg": {"expected": expected_file_count, "actual": len(jpg_files), "valid": jpg_valid},
                                "json": {"expected": expected_file_count, "actual": len(json_files), "valid": json_valid}
                            }

                            # サブフォルダの検証
                            for subfolder in ["sample", "sample-thumbnail", "thumbnail"]:
                                subfolder_path = seed_folder / subfolder
                                if subfolder_path.exists():
                                    subfolder_png_files = list(subfolder_path.glob("*.png"))
                                    subfolder_png_valid = len(subfolder_png_files) == expected_file_count

                                    version_result["files_validation"][subfolder] = {
                                        "png": {"expected": expected_file_count, "actual": len(subfolder_png_files), "valid": subfolder_png_valid}
                                    }
                                else:
                                    version_result["files_validation"][subfolder] = {
                                        "error": f"{subfolder}フォルダが存在しません"
                                    }

                            # enable_hrが有効な場合、half-resolutionフォルダも検証
                            if pattern.get("enable_hr", False):
                                hr_folder_path = seed_folder / "half-resolution"
                                if hr_folder_path.exists():
                                    hr_png_files = list(hr_folder_path.glob("*.png"))
                                    hr_png_valid = len(hr_png_files) == expected_file_count

                                    version_result["files_validation"]["half-resolution"] = {
                                        "png": {"expected": expected_file_count, "actual": len(hr_png_files), "valid": hr_png_valid}
                                    }
                                else:
                                    version_result["files_validation"]["half-resolution"] = {
                                        "error": "half-resolutionフォルダが存在しません"
                                    }

                            # 全体の検証結果
                            all_valid = all([
                                png_valid, jpg_valid, json_valid,
                                version_result["files_validation"].get("sample", {}).get("png", {}).get("valid", False),
                                version_result["files_validation"].get("sample-thumbnail", {}).get("png", {}).get("valid", False),
                                version_result["files_validation"].get("thumbnail", {}).get("png", {}).get("valid", False)
                            ])

                            # enable_hrが有効な場合、half-resolutionの検証も含める
                            if pattern.get("enable_hr", False):
                                all_valid = all_valid and version_result["files_validation"].get("half-resolution", {}).get("png", {}).get("valid", False)

                            version_result["all_valid"] = all_valid
                            version_validation_results.append(version_result)

                            logger.info(f"シード {seed_folder.name} の検証結果: {'成功' if all_valid else '失敗'}")

                        test_result["validation_results"]["version_validation"] = version_validation_results

                        # 全体の検証結果
                        all_versions_valid = all([result["all_valid"] for result in version_validation_results])
                        test_result["validation_results"]["all_versions_valid"] = all_versions_valid

                        # 総合判定
                        test_result["success"] = batch_count_valid and all_versions_valid
                        test_result["output_path"] = str(output_path)

                        if test_result["success"]:
                            logger.info(f"テストパターン '{pattern['name']}' が成功しました。")
                        else:
                            error_message = []
                            if not batch_count_valid:
                                error_message.append(f"バッチ数が一致しません（期待値: {image_generate_batch_execute_count}, 実際: {len(seed_folders)}）")
                            if not all_versions_valid:
                                error_message.append("一部のバージョンファイル検証に失敗しました")

                            error_str = "; ".join(error_message)
                            logger.error(f"テストパターン '{pattern['name']}' が失敗しました: {error_str}")
                            test_result["error"] = error_str
                    else:
                        logger.error(f"テストパターン '{pattern['name']}' が失敗しました。出力ディレクトリが存在しません。")
                        test_result["error"] = "出力ディレクトリが存在しません"

                except Exception as e:
                    logger.exception(f"テストパターン '{pattern['name']}' の実行中にエラーが発生しました: {e}")
                    test_result["error"] = str(e)

                # テスト実行時間を記録
                pattern_end_time = time.time()
                pattern_elapsed_time = pattern_end_time - pattern_start_time
                test_result["elapsed_time"] = pattern_elapsed_time
                test_result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # テスト結果を追加
                self.test_results["results"].append(test_result)

                # テスト結果をログに出力
                logger.info(f"テストパターン '{pattern['name']}' の実行時間: {pattern_elapsed_time:.2f}秒")

                # テスト結果に基づいてアサーション
                self.assertTrue(test_result["success"], f"テストパターン '{pattern['name']}' が失敗しました: {test_result['error']}")

if __name__ == "__main__":
    unittest.main()