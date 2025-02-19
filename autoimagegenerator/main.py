from auto_image_generator import AutoImageGenerator
import sys
import time
import json
import argparse

# 定数定義
SD_MODEL_CHECKPOINTS = {
    "brav6": "beautifulRealistic_v60.safetensors",
    "brav7": "beautifulRealistic_v7.safetensors",
    "brav7_men": "beautifulRealistic_v7.safetensors",
    "rpgicon": "awesomeRPGIcon2000_awesomeRPGIcon2000.safetensors"
}

SD_MODEL_SCRITPS = {

}

OUTPUT_FOLDER_MEN_PREFIX = "-men"

OUTPUT_FOLDER_TRANSPARENT_BACKGROUND_PREFIX = "-transparent"

OUTPUT_FOLDER_SELFIE_PREFIX = "-selfie"

OUTPUT_FOLDER_RPGICON_PREFIX = "-rpgicon"

# settings.json から設定を読み込む
with open('settings.json', 'r') as f:
    settings = json.load(f)

image_generate_batch_execute_count = settings.get("image_generate_batch_execute_count", 2)
another_version_generate_count = settings.get("another_version_generate_count", 12)

arg_sd_model = "brav6"

output_folder_prefix = ""
is_transparent_background = False
is_selfie = False

def parse_args():
    parser = argparse.ArgumentParser(description='AI Image Generator')

    # 画像スタイルの指定
    parser.add_argument(
        '--style',
        choices=['realistic', 'illustration'],
        default='realistic',
        help='画像スタイル (realistic: リアルテイスト, illustration: ゲーム・イラスト風)'
    )

    # カテゴリーの指定
    parser.add_argument(
        '--category',
        choices=['female', 'male', 'animal', 'background', 'rpg_icon', 'vehicle', 'other'],
        default='female',
        help='画像カテゴリー'
    )

    # サブカテゴリーの指定
    parser.add_argument(
        '--subcategory',
        help='画像サブカテゴリー（カテゴリーに応じて指定可能な値が変わります）'
    )

    # モデルの指定（オプション）
    parser.add_argument(
        '--model',
        help='使用するモデル名（未指定の場合はカテゴリーのデフォルトモデルを使用）'
    )

    return parser.parse_args()

def validate_subcategory(args):
    """サブカテゴリーの値を検証する"""
    valid_subcategories = {
        'female': ['normal', 'transparent', 'selfie'],
        'male': ['normal', 'transparent', 'selfie'],
        'animal': ['dog', 'cat', 'bird', 'fish', 'other'],
        'background': ['nature', 'city', 'sea', 'sky', 'other'],
        'rpg_icon': ['weapon', 'monster', 'other'],
        'vehicle': ['car', 'ship', 'airplane', 'other']
    }

    if args.category in valid_subcategories:
        if args.subcategory not in valid_subcategories[args.category]:
            raise ValueError(
                f"カテゴリー '{args.category}' に対する不正なサブカテゴリーです。"
                f"有効な値: {', '.join(valid_subcategories[args.category])}"
            )

def main():
    args = parse_args()
    validate_subcategory(args)

    # コマンドライン引数から指定されたモデルチェックポイントの値を取得
    if args.model:
        arg_sd_model = args.model.lower()  # 引数を小文字に変換して比較
        sd_model_checkpoint = SD_MODEL_CHECKPOINTS.get(arg_sd_model)
    else:
        sd_model_checkpoint = "beautifulRealistic_v60.safetensors"  # デフォルト値
    is_transparent_background = False
    is_selfie = False

    if args.subcategory == "transparent":
        is_transparent_background = True

    if args.subcategory == "selfie":
        is_selfie = True

    if arg_sd_model == "brav7_men":
        output_folder_prefix = OUTPUT_FOLDER_MEN_PREFIX
    elif arg_sd_model == "rpgicon":
        output_folder_prefix = OUTPUT_FOLDER_RPGICON_PREFIX

    if is_transparent_background:
        output_folder_prefix = output_folder_prefix + OUTPUT_FOLDER_TRANSPARENT_BACKGROUND_PREFIX

    if is_selfie:
        output_folder_prefix = output_folder_prefix + OUTPUT_FOLDER_SELFIE_PREFIX

    print(f"sd_model_checkpoint: {sd_model_checkpoint}")

    # 処理の開始時間を記録
    start_time = time.time()

    # AutoImageGenerator インスタンスを作成
    auto_image_generator = AutoImageGenerator(
        image_generate_batch_execute_count=image_generate_batch_execute_count,
        another_version_generate_count=another_version_generate_count,
        input_folder="../images/input",
        output_folder="../images/output",
        prompts_folder="./prompts",
        url="http://localhost:7860",
        sd_model_checkpoint=sd_model_checkpoint,
        sd_model_prefix=arg_sd_model,
        enable_hr=True,
        output_folder_prefix=output_folder_prefix,
        is_transparent_background=is_transparent_background,
        is_selfie=is_selfie
    )

    # AutoImageGenerator の run メソッドを呼び出して処理を実行
    auto_image_generator.run()

    # 処理の終了時間を記録
    end_time = time.time()

    # 経過時間を計算
    elapsed_time = end_time - start_time

    # 経過時間を表示
    print(f"処理にかかった時間: {elapsed_time}秒")

if __name__ == "__main__":
    main()