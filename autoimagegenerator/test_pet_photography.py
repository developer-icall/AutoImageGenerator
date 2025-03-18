#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
petPhotographyモデルを使用した画像生成のテストスクリプト
"""

import os
import sys
import argparse
import json
from datetime import datetime

# 現在のディレクトリをPYTHONPATHに追加して、モジュールのインポートを可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pet_photography_model():
    """
    petPhotographyモデルを使用した画像生成のテスト関数

    このテストでは、以下の項目を確認します：
    1. petPhotographyモデルが正しく選択されるか
    2. 動物カテゴリー（猫/犬）の画像が生成されるか
    """
    try:
        from auto_image_generator import AutoImageGenerator
    except ImportError as e:
        print(f"エラー: {e}")
        print("必要なモジュールがインストールされていません。")
        sys.exit(1)

    # テスト用の設定
    test_settings = {
        "style": "realistic",
        "category": "animal",
        "subcategories": ["cat", "dog"],  # テストする動物のサブカテゴリー
        "model": "petPhotography",
        "model_checkpoint": "petPhotographyAlbumOf_v10HomeEdition.safetensors"
    }

    print(f"=== petPhotographyモデルのテスト開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    # 各サブカテゴリーでテスト実行
    for subcategory in test_settings["subcategories"]:
        print(f"\n--- サブカテゴリー '{subcategory}' のテスト ---")

        # 出力フォルダのプレフィックスを生成
        output_folder_prefix = f"/{test_settings['style']}/{test_settings['category']}/{subcategory}"

        # AutoImageGenerator インスタンスを作成
        auto_image_generator = AutoImageGenerator(
            image_generate_batch_execute_count=1,  # テスト用に1回だけ実行
            another_version_generate_count=1,      # テスト用に1バージョンだけ生成
            input_folder="./images/input",
            output_folder="./images/output",
            prompts_folder="./prompts",
            url="http://localhost:7860",
            sd_model_checkpoint=test_settings["model_checkpoint"],
            sd_model_prefix=test_settings["model"],
            enable_hr=True,
            output_folder_prefix=output_folder_prefix,
            is_transparent_background=False,
            is_selfie=False,
            style=test_settings["style"],
            category=test_settings["category"],
            subcategory=subcategory
        )

        # ドライランモードでプロンプト生成のみを実行
        print("プロンプト生成テスト:")
        prompts = auto_image_generator.generate_prompts()

        # 生成されたプロンプトを表示
        print(f"生成されたプロンプト:")
        print(f"Positive: {prompts['positive_prompt'][:100]}...")  # 長いので先頭100文字だけ表示
        print(f"Negative: {prompts['negative_prompt'][:100]}...")

        print(f"サブカテゴリー '{subcategory}' のテスト完了")

    print(f"\n=== petPhotographyモデルのテスト終了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print("テストが正常に完了しました。実際の画像生成を行うには、main.pyを以下のように実行してください:")
    print(f"python main.py --style {test_settings['style']} --category {test_settings['category']} --subcategory {test_settings['subcategories'][0]} --model {test_settings['model']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='petPhotographyモデルのテスト')
    parser.add_argument('--dry-run', action='store_true', help='実際の画像生成を行わず、プロンプトの生成だけを行う')
    args = parser.parse_args()

    # テスト実行
    test_pet_photography_model()