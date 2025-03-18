#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
petPhotographyモデル用のプロンプト設定ファイルを適切なフォルダに配置するスクリプト
"""

import os
import json
import shutil
from pathlib import Path

# プロンプトファイルの基本構造
PROMPT_TEMPLATES = {
    "positive_base.json": {
        "Base Positive Prompt": {
            "prompts": [
                "(8k, RAW photo, best quality, masterpiece:1.2), (realistic:1.3), (photorealistic:1.3), (detailed:1.2)"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        },
        "Pet Type": {
            "prompts": [
                "(cute pet:1.4)",
                "(adorable pet:1.4)",
                "(beautiful pet:1.4)",
                "(lovely pet:1.4)"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        }
    },
    "positive_optional.json": {
        "Background": {
            "prompts": [
                "in a living room",
                "in a garden",
                "on a sofa",
                "on a bed",
                "in a park",
                "on a carpet",
                "by the window",
                "in natural light",
                "in studio lighting"
            ],
            "use_max_prompts": 2,
            "use_min_prompts": 0
        },
        "Accessories": {
            "prompts": [
                "with a collar",
                "with a bow tie",
                "with a ribbon",
                "with a bandana",
                "with a pet toy"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 0
        },
        "Composition": {
            "prompts": [
                "close-up portrait",
                "full body shot",
                "side profile",
                "looking at camera",
                "from above"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        }
    },
    "positive_pose.json": {
        "Pose": {
            "prompts": [
                "sitting",
                "standing",
                "lying down",
                "playing",
                "sleeping",
                "running",
                "jumping"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        },
        "Expression": {
            "prompts": [
                "happy expression",
                "curious expression",
                "alert expression",
                "relaxed expression",
                "playful expression"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 0
        }
    },
    "negative.json": {
        "Base Negative Prompt": {
            "prompts": [
                "((deformed)), ((disfigured)), ((poor details)), ((bad anatomy)), ((bad proportions)), ((poorly drawn)), ((extra limbs)), ((mutation)), ((mutated)), ((ugly)), ((disgusting)), ((blurry)), ((grainy)), ((human)), ((person)), ((people))"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        }
    },
    "cancel_seeds.json": {
        "Seeds": []
    },
    "positive_cancel_pair.json": {}
}

# 猫用の特別なプロンプト
CAT_SPECIFIC_PROMPTS = {
    "positive_base.json": {
        "Cat Type": {
            "prompts": [
                "(domestic cat:1.4)",
                "(tabby cat:1.4)",
                "(persian cat:1.4)",
                "(siamese cat:1.4)",
                "(maine coon cat:1.4)",
                "(bengal cat:1.4)",
                "(ragdoll cat:1.4)",
                "(british shorthair cat:1.4)",
                "(scottish fold cat:1.4)",
                "(sphynx cat:1.4)"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        },
        "Cat Features": {
            "prompts": [
                "fluffy fur",
                "short fur",
                "long fur",
                "striped pattern",
                "spotted pattern",
                "solid color",
                "multicolored",
                "bright eyes",
                "pointed ears",
                "bushy tail"
            ],
            "use_max_prompts": 2,
            "use_min_prompts": 1
        }
    }
}

# 犬用の特別なプロンプト
DOG_SPECIFIC_PROMPTS = {
    "positive_base.json": {
        "Dog Type": {
            "prompts": [
                "(labrador retriever:1.4)",
                "(golden retriever:1.4)",
                "(german shepherd:1.4)",
                "(bulldog:1.4)",
                "(beagle:1.4)",
                "(poodle:1.4)",
                "(siberian husky:1.4)",
                "(chihuahua:1.4)",
                "(shih tzu:1.4)",
                "(border collie:1.4)",
                "(dachshund:1.4)",
                "(corgi:1.4)",
                "(pomeranian:1.4)",
                "(dalmatian:1.4)"
            ],
            "use_max_prompts": 1,
            "use_min_prompts": 1
        },
        "Dog Features": {
            "prompts": [
                "fluffy fur",
                "short fur",
                "long fur",
                "floppy ears",
                "pointed ears",
                "curly tail",
                "straight tail",
                "spotted coat",
                "solid color",
                "multicolored"
            ],
            "use_max_prompts": 2,
            "use_min_prompts": 1
        }
    }
}

def create_directory_structure():
    """
    petPhotographyモデル用のディレクトリ構造を作成する
    """
    # 現在のスクリプトのディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # プロジェクトのルートディレクトリを取得（autoimagegeneratorの親ディレクトリ）
    project_root = os.path.dirname(current_dir)

    # プロンプトフォルダのパスを取得（プロジェクトルート直下のpromptsフォルダ）
    prompts_dir = os.path.join(project_root, 'prompts')

    # スタイルとカテゴリーのパスを作成
    style_dir = os.path.join(prompts_dir, 'realistic')
    category_dir = os.path.join(style_dir, 'animal')

    # サブカテゴリーのパスを作成
    cat_dir = os.path.join(category_dir, 'cat')
    dog_dir = os.path.join(category_dir, 'dog')

    # ディレクトリが存在しない場合は作成
    for directory in [prompts_dir, style_dir, category_dir, cat_dir, dog_dir]:
        os.makedirs(directory, exist_ok=True)

    print(f"ディレクトリ構造を作成しました:")
    print(f"- {cat_dir}")
    print(f"- {dog_dir}")

    return {
        'cat': cat_dir,
        'dog': dog_dir
    }

def create_prompt_files(directories):
    """
    各サブカテゴリー用のプロンプトファイルを作成する

    Args:
        directories (dict): サブカテゴリー名とディレクトリパスのマッピング
    """
    # 猫用のプロンプトファイルを作成
    create_subcategory_prompt_files(directories['cat'], 'cat', CAT_SPECIFIC_PROMPTS)

    # 犬用のプロンプトファイルを作成
    create_subcategory_prompt_files(directories['dog'], 'dog', DOG_SPECIFIC_PROMPTS)

    print("\nプロンプトファイルの作成が完了しました")

def create_subcategory_prompt_files(directory, subcategory, specific_prompts):
    """
    特定のサブカテゴリー用のプロンプトファイルを作成する

    Args:
        directory (str): プロンプトファイルを作成するディレクトリパス
        subcategory (str): サブカテゴリー名（'cat'または'dog'）
        specific_prompts (dict): サブカテゴリー固有のプロンプト
    """
    print(f"\n{subcategory.capitalize()}用のプロンプトファイルを作成中...")

    # 各プロンプトファイルを作成
    for filename, template in PROMPT_TEMPLATES.items():
        # サブカテゴリー固有のプロンプトがある場合はマージ
        if filename in specific_prompts:
            # テンプレートをコピー
            merged_template = template.copy()

            # サブカテゴリー固有のプロンプトを追加
            for category, prompts in specific_prompts[filename].items():
                merged_template[category] = prompts
        else:
            merged_template = template

        # ファイルパスを作成
        file_path = os.path.join(directory, filename)

        # JSONファイルとして保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_template, f, ensure_ascii=False, indent=2)

        print(f"  - {filename} を作成しました")

def main():
    print("petPhotographyモデル用のプロンプト設定ファイルをセットアップします")

    # ディレクトリ構造を作成
    directories = create_directory_structure()

    # プロンプトファイルを作成
    create_prompt_files(directories)

    print("\nセットアップが完了しました")
    print("以下のコマンドでテストを実行できます:")
    print("python test_pet_photography.py --dry-run")
    print("\n実際の画像生成を行うには:")
    print("python generate_pet_images.py --subcategory cat --dry-run")
    print("python generate_pet_images.py --subcategory dog --dry-run")
    print("\nドライランモードを無効にするには --dry-run オプションを削除してください")

if __name__ == "__main__":
    main()