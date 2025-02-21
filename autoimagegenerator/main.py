from auto_image_generator import AutoImageGenerator
import sys
import time
import json
import argparse

# 定数定義
IMAGE_STYLES = {
    "realistic": {
        "female": {
            "models": ["brav6", "brav7"],
            "types": ["normal", "transparent", "selfie"]
        },
        "male": {
            "models": ["brav6", "brav7"],
            "types": ["normal", "transparent", "selfie"]
        },
        "animal": {
            "types": ["dog", "cat", "bird", "fish", "other"],
            "models": []  # 未確定
        }
    },
    "illustration": {
        "female": {
            "models": [],  # 未確定
            "types": ["normal", "transparent", "selfie"]
        },
        "male": {
            "models": [],  # 未確定
            "types": ["normal", "transparent", "selfie"]
        },
        "animal": {
            "types": ["dog", "cat", "bird", "fish", "other"],
            "models": []  # 未確定
        },
        "background": {
            "types": ["nature", "city", "sea", "sky", "other"],
            "models": []  # 未確定
        },
        "rpg_icon": {
            "types": ["weapon", "monster", "other"],
            "models": ["RPGIcon"]
        },
        "vehicle": {
            "types": ["car", "ship", "airplane", "other"],
            "models": []  # 未確定
        },
        "other": {
            "types": [],
            "models": []  # 未確定
        }
    }
}

SD_MODEL_CHECKPOINTS = {
    "brav6": "beautifulRealistic_v60.safetensors",
    "brav7": "beautifulRealistic_v7.safetensors",
    "brav7_men": "beautifulRealistic_v7.safetensors",
    "rpg_icon": "RPGIcon.safetensors"  # RPGIcon用のモデル
}

SD_MODEL_SCRITPS = {

}

OUTPUT_FOLDER_MEN_PREFIX = "-men"

OUTPUT_FOLDER_TRANSPARENT_BACKGROUND_PREFIX = "-transparent"

OUTPUT_FOLDER_SELFIE_PREFIX = "-selfie"

# settings.json から設定を読み込む
with open('settings.json', 'r') as f:
    settings = json.load(f)

def validate_image_type(style, category, subcategory):
    """画像タイプの組み合わせが有効かチェック"""
    if style not in IMAGE_STYLES:
        return False

    if category not in IMAGE_STYLES[style]:
        return False

    if subcategory:
        if "types" not in IMAGE_STYLES[style][category]:
            return False
        if subcategory not in IMAGE_STYLES[style][category]["types"]:
            return False

    return True

def get_output_folder_prefix(args):
    """出力フォルダのプレフィックスを生成"""
    prefix = f"/{args.style}/{args.category}"
    if args.subcategory:
        prefix += f"/{args.subcategory}"
    return prefix

def get_default_model(category):
    """カテゴリーに基づいてデフォルトのモデルを返す"""
    if category == "male":
        return "brav7_men"
    elif category == "rpg_icon":
        return "rpg_icon"
    else:
        return "brav6"

def main():
    parser = argparse.ArgumentParser(description='画像生成プログラム')

    # 必須の引数
    parser.add_argument('--style', required=True, choices=['realistic', 'illustration'],
                        help='画像スタイル (realistic/illustration)')
    parser.add_argument('--category', required=True,
                        help='カテゴリー (female/male/animal/background/rpg_icon/vehicle/other)')

    # オプションの引数
    parser.add_argument('--subcategory',
                        help='サブカテゴリー (normal/transparent/selfie/dog/cat etc...)')
    parser.add_argument('--model',
                        help='使用するモデル (デフォルトはカテゴリーに応じて自動選択)')
    parser.add_argument('--enable-hr', type=str, choices=['true', 'false'], default='true',
                        help='ハイレゾ画像生成の有効/無効 (true/false, デフォルト: true)')

    args = parser.parse_args()

    # 画像タイプの組み合わせをバリデーション
    if not validate_image_type(args.style, args.category, args.subcategory):
        print("エラー: 無効な画像タイプの組み合わせです")
        sys.exit(1)

    # モデルの選択
    if not args.model:
        # カテゴリーに応じてデフォルトモデルを選択
        model = get_default_model(args.category)
    else:
        model = args.model

    # モデルの存在確認
    if model not in SD_MODEL_CHECKPOINTS:
        print(f"エラー: 指定されたモデル '{model}' は存在しません")
        sys.exit(1)

    # 透過背景の判定
    is_transparent = args.subcategory == "transparent"

    # セルフィーの判定
    is_selfie = args.subcategory == "selfie"

    # 出力フォルダのプレフィックスを生成
    output_folder_prefix = get_output_folder_prefix(args)

    # 処理の開始時間を記録
    start_time = time.time()

    # AutoImageGenerator インスタンスを作成
    auto_image_generator = AutoImageGenerator(
        image_generate_batch_execute_count=settings.get("image_generate_batch_execute_count", 2),
        another_version_generate_count=settings.get("another_version_generate_count", 12),
        input_folder="../images/input",
        output_folder="../images/output",
        prompts_folder="./prompts",
        url="http://localhost:7860",
        sd_model_checkpoint=SD_MODEL_CHECKPOINTS[model],
        sd_model_prefix=model,
        enable_hr=args.enable_hr.lower() == 'true',
        output_folder_prefix=output_folder_prefix,
        is_transparent_background=is_transparent,
        is_selfie=is_selfie
    )

    # 画像生成の実行
    auto_image_generator.run()

    # 処理の終了時間を記録と表示
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"処理にかかった時間: {elapsed_time}秒")

if __name__ == "__main__":
    main()