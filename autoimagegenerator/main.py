import sys
import time
import json
import argparse
import os

# 定数定義
IMAGE_STYLES = {
    "realistic": {
        "female": {
            "models": ["brav6", "brav7", "yayoiMix"],
            "types": ["normal", "transparent", "selfie"]
        },
        "male": {
            "models": ["brav6", "brav7", "yayoiMix"],
            "types": ["normal", "transparent", "selfie"]
        },
        "animal": {
            "types": ["dog", "cat", "bird", "fish", "other"],
            "models": ["yayoiMix", "petPhotography"]  # petPhotographyモデルを追加
        }
    },
    "illustration": {
        "female": {
            "models": ["animagineXL"],  # animagineXLを追加
            "types": ["normal", "transparent", "selfie"]
        },
        "male": {
            "models": ["animagineXL"],  # animagineXLを追加
            "types": ["normal", "transparent", "selfie"]
        },
        "animal": {
            "types": ["dog", "cat", "bird", "fish", "other"],
            "models": ["animagineXL"]  # animagineXL40_v4Optモデルを追加
        },
        "background": {
            "types": ["nature", "city", "sea", "sky", "other"],
            "models": []  # 未確定
        },
        "rpg_icon": {
            "types": ["weapon", "monster", "other"],
            "models": ["photoRealRPG", "RPGIcon"]
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
    "photoRealRPG": "photoRealV15_photorealv21.safetensors",  # photoRealV15_photorealv21モデル
    "RPGIcon": "RPGIcon.safetensors",  # RPGIcon用モデル
    "animagineXL": "animagineXL40_v4Opt.safetensors",  # animagineXL40_v4Optモデル
    "yayoiMix": "yayoiMix_v25.safetensors",  # yayoiMix_v25モデル
    "petPhotography": "petPhotographyAlbumOf_v10HomeEdition.safetensors"  # ペット写真用モデル
}

SD_MODEL_SCRITPS = {

}

OUTPUT_FOLDER_MEN_PREFIX = "-men"

OUTPUT_FOLDER_TRANSPARENT_BACKGROUND_PREFIX = "-transparent"

OUTPUT_FOLDER_SELFIE_PREFIX = "-selfie"

# settings.json から設定を読み込む
try:
    # 現在のファイルのディレクトリパスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(current_dir, 'settings.json')

    with open(settings_path, 'r') as f:
        settings = json.load(f)
except FileNotFoundError:
    # settings.jsonが見つからない場合はデフォルト値を使用
    settings = {
        "image_generate_batch_execute_count": 2,
        "another_version_generate_count": 12
    }
    print(f"警告: {settings_path} が見つかりません。デフォルト設定を使用します。")

def validate_image_type(style, category, subcategory):
    """画像タイプの組み合わせが有効かチェック"""
    # スタイルが有効かチェック
    if style not in IMAGE_STYLES:
        return False

    # カテゴリーが有効かチェック
    if category not in IMAGE_STYLES[style]:
        return False

    # サブカテゴリーが指定されている場合のみチェック
    if subcategory:
        # カテゴリーにtypesが定義されていない場合は、サブカテゴリーは無視して有効とする
        if "types" not in IMAGE_STYLES[style][category]:
            return True

        # サブカテゴリーが定義されたリストにない場合でも、
        # auto_image_generator.pyで対応するようになったので有効とする
        return True

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
        # RPGアイコンの場合は、環境変数またはデフォルト設定に基づいてモデルを選択
        # 環境変数RPG_ICON_MODELが設定されている場合はその値を使用
        rpg_icon_model = os.environ.get("RPG_ICON_MODEL", "photoRealRPG")
        if rpg_icon_model in ["photoRealRPG", "RPGIcon"]:
            return rpg_icon_model
        else:
            return "photoRealRPG"
    elif category == "animal":
        # 動物カテゴリーの場合はpetPhotographyモデルをデフォルトとして使用
        return "petPhotography"
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
    parser.add_argument('--model-checkpoint',
                        help='使用するモデルチェックポイントファイル名を直接指定 (例: RPGIcon.safetensors)')
    parser.add_argument('--enable-hr', type=str, choices=['true', 'false'], default='true',
                        help='ハイレゾ画像生成の有効/無効 (true/false, デフォルト: true)')
    parser.add_argument('--dry-run', action='store_true',
                        help='実際の画像生成を行わず、プロンプトの生成だけを行う')
    parser.add_argument('--width', type=int,
                        help='画像の幅 (デフォルトは画像タイプに応じて自動設定)')
    parser.add_argument('--height', type=int,
                        help='画像の高さ (デフォルトは画像タイプに応じて自動設定)')

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

    # モデルチェックポイントの選択
    if args.model_checkpoint:
        # モデルチェックポイントが直接指定された場合は、それを使用
        model_checkpoint = args.model_checkpoint
        print(f"指定されたモデルチェックポイント '{model_checkpoint}' を使用します")
    else:
        # モデル名に対応するチェックポイントを使用
        model_checkpoint = SD_MODEL_CHECKPOINTS[model]

    # ドライランモードの場合は、必要なモジュールのインポートをスキップ
    if args.dry_run:
        try:
            from auto_image_generator import AutoImageGenerator
        except ImportError as e:
            print(f"警告: {e}")
            print("ドライランモードでは一部の機能が制限されます")

            # 引数の表示
            print("\n--- 指定された引数 ---")
            print(f"スタイル: {args.style}")
            print(f"カテゴリー: {args.category}")
            print(f"サブカテゴリー: {args.subcategory}")
            print(f"モデル: {model}")
            print(f"モデルチェックポイント: {model_checkpoint}")
            print(f"ハイレゾ画像生成: {args.enable_hr}")
            print("----------------------\n")

            print("ドライランモードで実行しました。実際の画像生成は行われません。")
            sys.exit(0)
    else:
        # 通常モードでは必要なモジュールをインポート
        try:
            from auto_image_generator import AutoImageGenerator
        except ImportError as e:
            print(f"エラー: {e}")
            print("必要なモジュールがインストールされていません。")
            print("pip install requests pillow tqdm を実行してください。")
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
        category=args.category,
        subcategory=args.subcategory,
        width=args.width,
        height=args.height,
        use_custom_checkpoint=args.model_checkpoint is not None
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