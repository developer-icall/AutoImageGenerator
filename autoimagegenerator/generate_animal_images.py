#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
動物画像生成用のコマンドラインスクリプト
"""

import argparse
import sys
import os
import time

# 現在のディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_image_generator import AutoImageGenerator

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='動物画像生成スクリプト')

    # 必須の引数
    parser.add_argument('--style', required=True, choices=['realistic', 'illustration'],
                        help='画像スタイル (realistic/illustration)')
    parser.add_argument('--subcategory', required=True, choices=['bird', 'cat', 'dog', 'fish'],
                        help='動物の種類 (bird/cat/dog/fish)')

    # オプションの引数
    parser.add_argument('--type', choices=['normal', 'transparent', 'selfie'],
                        default='normal', help='画像タイプ (normal/transparent/selfie)')
    parser.add_argument('--enable-hr', type=str, choices=['true', 'false'], default='false',
                        help='ハイレゾ画像生成の有効/無効 (true/false, デフォルト: false)')
    parser.add_argument('--dry-run', action='store_true',
                        help='実際の画像生成を行わず、プロンプトの生成だけを行う')
    parser.add_argument('--count', type=int, default=1,
                        help='生成する画像の数 (デフォルト: 1)')
    parser.add_argument('--width', type=int, default=512,
                        help='画像の幅 (デフォルト: 512)')
    parser.add_argument('--height', type=int, default=512,
                        help='画像の高さ (デフォルト: 512)')

    args = parser.parse_args()

    # モデルの選択
    if args.style == 'illustration':
        model = 'animagineXL'
        model_checkpoint = 'animagineXL40_v4Opt.safetensors'
    else:  # realistic
        model = 'yayoiMix'
        model_checkpoint = 'yayoiMix_v25.safetensors'

    # 透過背景の判定
    is_transparent = args.type == 'transparent'

    # セルフィーの判定
    is_selfie = args.type == 'selfie'

    # 出力フォルダのプレフィックスを生成
    output_folder_prefix = f"/{args.style}/animal/{args.subcategory}"

    # 処理の開始時間を記録
    start_time = time.time()

    # AutoImageGenerator インスタンスを作成
    auto_image_generator = AutoImageGenerator(
        image_generate_batch_execute_count=args.count,
        another_version_generate_count=0,
        input_folder="./images/input",
        output_folder="./images/output",
        prompts_folder="./prompts",
        url="http://localhost:7860",
        sd_model_checkpoint=model_checkpoint,
        sd_model_prefix=model,
        enable_hr=args.enable_hr.lower() == 'true',
        output_folder_prefix=output_folder_prefix,
        is_transparent_background=is_transparent,
        is_selfie=is_selfie,
        style=args.style,
        category="animal",
        subcategory=args.subcategory,
        width=args.width,
        height=args.height
    )

    # 画像生成の実行
    if args.dry_run:
        # ドライラン（プロンプトの生成だけを行う）
        print("ドライラン: 実際の画像生成は行いません")
        prompts = auto_image_generator.generate_prompts()
        print("生成されるプロンプト:")
        print(f"ポジティブプロンプト: {prompts['positive_prompt']}")
        print(f"ネガティブプロンプト: {prompts['negative_prompt']}")
    else:
        # 実際の画像生成を実行
        auto_image_generator.run()

    # 処理の終了時間を記録と表示
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"処理にかかった時間: {elapsed_time}秒")

if __name__ == "__main__":
    main()