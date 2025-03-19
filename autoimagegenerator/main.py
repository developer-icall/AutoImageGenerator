import sys
import time
import json
import argparse
import os
import logging
from datetime import datetime

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
        },
        "vehicle": {
            "types": ["car", "ship", "airplane", "motorcycle", "other"],
            "models": ["sd_xl_base_1.0"]  # SDXL Base 1.0モデルを追加
        },
        "background": {
            "types": ["city", "nature", "sea", "sky", "house"],
            "models": ["landscapeRealistic"]  # landscapeRealisticモデルを追加
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
            "types": ["nature", "city", "sea", "sky", "other", "house"],
            "models": ["landscapeRealistic"]  # landscapeRealisticモデルを設定
        },
        "rpg_icon": {
            "types": ["weapon", "monster", "other"],
            "models": ["photoRealRPG", "RPGIcon"]
        },
        "vehicle": {
            "types": ["car", "ship", "airplane", "motorcycle", "other"],
            "models": ["sd_xl_base_1.0"]  # SDXL Base 1.0モデルを追加
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
    "petPhotography": "petPhotographyAlbumOf_v10HomeEdition.safetensors",  # ペット写真用モデル
    "sd_xl_base_1.0": "sd_xl_base_1.0.safetensors",  # SDXL Base 1.0モデル
    "landscapeRealistic": "landscapeRealistic_v20WarmColor.safetensors"  # landscapeRealisticモデル
}

# LoRAの設定
LORA_SETTINGS = {
    "cars-000008": {
        "model": "sd_xl_base_1.0",
        "weight": 0.7,
        "trigger_word": "aw0k car"
    },
    "KawasakiNinja300": {
        "model": "sd_xl_base_1.0",
        "weight": 0.8,
        "trigger_word": "kawasakininja300, motorcycle, realistic"
    },
    "waifu_on_Motorcycle_v2": {
        "model": "sd_xl_base_1.0",
        "weight": 0.7,
        "trigger_word": "waifu on motorcycle, illustration, anime style"
    },
    "cybervehiclev4": {
        "model": "sd_xl_base_1.0",
        "weight": 0.75,
        "trigger_word": "cyberpunk vehicle, futuristic motorcycle"
    }
}

SD_MODEL_SCRITPS = {

}

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
        print(f"エラー: 無効なスタイル '{style}' が指定されました")
        return False

    # カテゴリーが有効かチェック
    if category not in IMAGE_STYLES[style]:
        print(f"エラー: 無効なカテゴリー '{category}' が指定されました")
        return False

    # サブカテゴリーが指定されている場合のみチェック
    if subcategory:
        # カテゴリーにtypesが定義されていない場合は、サブカテゴリーは無視して有効とする
        if "types" not in IMAGE_STYLES[style][category]:
            return True

        # サブカテゴリーが定義されたリストにない場合はエラー
        if subcategory not in IMAGE_STYLES[style][category]["types"]:
            print(f"エラー: 無効なサブカテゴリー '{subcategory}' が指定されました")
            print(f"有効なサブカテゴリー: {', '.join(IMAGE_STYLES[style][category]['types'])}")
            return False

        return True

    return True

def get_output_folder_prefix(args):
    """出力フォルダのプレフィックスを生成"""
    prefix = f"{args.style}/{args.category}"
    if args.subcategory:
        prefix += f"/{args.subcategory}"
    return prefix

def get_default_model(category, use_lora=False, lora_name=None):
    """カテゴリーに基づいてデフォルトのモデルを返す"""
    # LoRAを使用する場合、LoRAの設定から適切なモデルを選択
    if use_lora and lora_name and lora_name in LORA_SETTINGS:
        return LORA_SETTINGS[lora_name]["model"]

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
    elif category == "background":
        # 背景カテゴリーの場合はlandscapeRealisticモデルをデフォルトとして使用
        return "landscapeRealistic"
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
                        help='生成する画像の幅 (デフォルト: settings.jsonの設定に従う)')
    parser.add_argument('--height', type=int,
                        help='生成する画像の高さ (デフォルト: settings.jsonの設定に従う)')
    parser.add_argument('--use-lora', action='store_true',
                        help='LoRAを使用するかどうか')
    parser.add_argument('--lora-name', choices=list(LORA_SETTINGS.keys()),
                        help='使用するLoRAの名前 (例: KawasakiNinja300, waifu_on_Motorcycle_v2, cybervehiclev4)')
    parser.add_argument('--prompts-folder',
                        help='プロンプトフォルダのパス (デフォルト: autoimagegenerator/prompts)')
    parser.add_argument('--debug', action='store_true',
                        help='デバッグモードを有効にする（DEBUGレベルのログを表示）')

    args = parser.parse_args()

    # ロガーの設定
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    # ログディレクトリの作成
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # main.pyログ用のサブディレクトリを作成
    main_log_dir = os.path.join(log_dir, 'main')
    os.makedirs(main_log_dir, exist_ok=True)

    # ファイル出力用ハンドラ
    log_file = os.path.join(main_log_dir, f"main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # コンソール出力用ハンドラ
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 起動オプションをログに出力
    logger.info("=== 起動オプション ===")
    logger.info(f"スタイル: {args.style}")
    logger.info(f"カテゴリー: {args.category}")
    logger.info(f"サブカテゴリー: {args.subcategory if args.subcategory else '未指定'}")
    logger.info(f"モデル: {args.model if args.model else '自動選択'}")
    logger.info(f"モデルチェックポイント: {args.model_checkpoint if args.model_checkpoint else '自動選択'}")
    logger.info(f"ハイレゾ: {args.enable_hr}")
    logger.info(f"ドライラン: {args.dry_run}")
    logger.info(f"画像サイズ: {args.width}x{args.height if args.height else '自動'}")
    logger.info(f"LoRA使用: {args.use_lora}")
    logger.info(f"LoRA名: {args.lora_name if args.lora_name else '未指定'}")
    logger.info(f"プロンプトフォルダ: {args.prompts_folder if args.prompts_folder else 'デフォルト'}")
    logger.info(f"デバッグモード: {args.debug}")
    logger.info("==================")

    # 画像タイプの組み合わせが有効かチェック
    if not validate_image_type(args.style, args.category, args.subcategory):
        sys.exit(1)

    # LoRAの使用チェック
    if args.use_lora:
        if not args.lora_name:
            print("エラー: --use-loraが指定されていますが、--lora-nameが指定されていません")
            sys.exit(1)
        if args.lora_name not in LORA_SETTINGS:
            print(f"エラー: 指定されたLoRA '{args.lora_name}' は設定に存在しません")
            print(f"利用可能なLoRA: {', '.join(LORA_SETTINGS.keys())}")
            sys.exit(1)
        if args.model and args.model != LORA_SETTINGS[args.lora_name]["model"]:
            print(f"警告: 指定されたモデル '{args.model}' はLoRA '{args.lora_name}' の推奨モデル '{LORA_SETTINGS[args.lora_name]['model']}' と異なります")

    # モデルの選択
    if not args.model:
        args.model = get_default_model(args.category, args.use_lora, args.lora_name)
    else:
        # --modelオプションが指定された場合、そのモデルを強制的に使用
        if args.model not in SD_MODEL_CHECKPOINTS:
            print(f"エラー: 指定されたモデル '{args.model}' は利用できません")
            print(f"利用可能なモデル: {', '.join(SD_MODEL_CHECKPOINTS.keys())}")
            sys.exit(1)
        print(f"指定されたモデル '{args.model}' を使用します")

    # モデルチェックポイントの選択
    if not args.model_checkpoint:
        if args.model in SD_MODEL_CHECKPOINTS:
            args.model_checkpoint = SD_MODEL_CHECKPOINTS[args.model]
        else:
            print(f"エラー: モデル '{args.model}' のチェックポイントが見つかりません")
            sys.exit(1)

    # プロンプトフォルダのパスを設定
    if not args.prompts_folder:
        args.prompts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts')

    # 出力フォルダのプレフィックスを設定
    output_folder_prefix = get_output_folder_prefix(args)

    # AutoImageGeneratorのインスタンスを作成
    from auto_image_generator import AutoImageGenerator
    generator = AutoImageGenerator(
        image_generate_batch_execute_count=settings.get("image_generate_batch_execute_count", 2),
        another_version_generate_count=settings.get("another_version_generate_count", 12),
        input_folder="./images/input",
        output_folder="./images/output",
        prompts_folder=args.prompts_folder,
        url="http://localhost:7860",
        sd_model_checkpoint=args.model_checkpoint,
        sd_model_prefix=args.model,
        enable_hr=args.enable_hr.lower() == 'true',
        output_folder_prefix=output_folder_prefix,
        is_transparent_background=args.subcategory == "transparent",
        is_selfie=args.subcategory == "selfie",
        style=args.style,
        category=args.category,
        subcategory=args.subcategory,
        width=args.width,
        height=args.height,
        use_custom_checkpoint=False,
        use_lora=args.use_lora,
        lora_name=args.lora_name,
        dry_run=args.dry_run,
        debug_mode=args.debug
    )

    # 画像生成の実行
    if args.dry_run:
        print("ドライランモード: プロンプトの生成のみを行います")
        prompts = generator.generate_prompts()
        print("生成されたプロンプト:")
        print(json.dumps(prompts, indent=2, ensure_ascii=False))
    else:
        generator.run()

if __name__ == "__main__":
    main()