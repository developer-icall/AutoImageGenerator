#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
petPhotographyモデルを使用して猫と犬の画像を生成するためのコマンドラインスクリプト
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

def generate_pet_images(subcategory, count=1, dry_run=False):
    """
    指定されたサブカテゴリー（猫/犬）の画像を生成する

    Args:
        subcategory (str): 生成する動物のサブカテゴリー（'cat'または'dog'）
        count (int): 生成するバッチの数
        dry_run (bool): ドライランモードかどうか
    """
    # 現在のスクリプトのディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # main.pyのパスを取得
    main_script = os.path.join(current_dir, 'main.py')

    # コマンドライン引数を構築
    cmd = [
        sys.executable,  # 現在のPythonインタプリタ
        main_script,
        '--style', 'realistic',
        '--category', 'animal',
        '--subcategory', subcategory,
        '--model', 'petPhotography'
    ]

    # ドライランモードの場合は引数を追加
    if dry_run:
        cmd.append('--dry-run')

    print(f"=== {subcategory}の画像生成開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"実行コマンド: {' '.join(cmd)}")

    # 指定された回数だけコマンドを実行
    for i in range(count):
        print(f"\n--- バッチ {i+1}/{count} の実行 ---")
        try:
            # サブプロセスとしてmain.pyを実行
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # リアルタイムで出力を表示
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            # エラー出力を取得
            stderr = process.stderr.read()
            if stderr:
                print(f"エラー: {stderr}")

            # 終了コードを確認
            if process.returncode != 0:
                print(f"警告: プロセスが終了コード {process.returncode} で終了しました")

        except Exception as e:
            print(f"エラー: {e}")
            return False

    print(f"\n=== {subcategory}の画像生成終了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    return True

def main():
    parser = argparse.ArgumentParser(description='petPhotographyモデルを使用して猫と犬の画像を生成する')
    parser.add_argument('--subcategory', choices=['cat', 'dog', 'all'], default='all',
                        help='生成する動物のサブカテゴリー (cat/dog/all, デフォルト: all)')
    parser.add_argument('--count', type=int, default=1,
                        help='生成するバッチの数 (デフォルト: 1)')
    parser.add_argument('--dry-run', action='store_true',
                        help='実際の画像生成を行わず、プロンプトの生成だけを行う')

    args = parser.parse_args()

    # 生成する動物のサブカテゴリーを決定
    subcategories = []
    if args.subcategory == 'all':
        subcategories = ['cat', 'dog']
    else:
        subcategories = [args.subcategory]

    # 各サブカテゴリーで画像生成を実行
    for subcategory in subcategories:
        success = generate_pet_images(subcategory, args.count, args.dry_run)
        if not success:
            print(f"{subcategory}の画像生成中にエラーが発生しました")

    print("\n全ての処理が完了しました")

if __name__ == "__main__":
    main()