import os

def create_subfolders(path):
    """サブフォルダを作成する"""
    os.makedirs(os.path.join(path, "thumbnail"), exist_ok=True)
    os.makedirs(os.path.join(path, "sample"), exist_ok=True)
    os.makedirs(os.path.join(path, "sample-thumbnail"), exist_ok=True)
    os.makedirs(os.path.join(path, "half-resolution"), exist_ok=True)

def create_output_folders():
    """出力フォルダ構造を作成する"""
    base_path = "../images/output"

    # スタイル（大項目）
    styles = ["realistic", "illustration"]

    # カテゴリー（中項目）とそのサブカテゴリー（小項目）
    categories = {
        "female": ["normal", "transparent", "selfie"],
        "male": ["normal", "transparent", "selfie"],
        "animal": ["dog", "cat", "bird", "fish", "other"],
        "background": ["nature", "city", "sea", "sky", "other"],
        "rpg_icon": ["weapon", "monster", "other"],
        "vehicle": ["car", "ship", "airplane", "other"]
    }

    for style in styles:
        # スタイルフォルダを作成
        style_path = os.path.join(base_path, style)
        os.makedirs(style_path, exist_ok=True)

        # カテゴリーとサブカテゴリーのフォルダを作成
        for category, subcategories in categories.items():
            category_path = os.path.join(style_path, category)
            os.makedirs(category_path, exist_ok=True)

            for subcategory in subcategories:
                subcategory_path = os.path.join(category_path, subcategory)
                os.makedirs(subcategory_path, exist_ok=True)

                # サブフォルダ（thumbnail, sample等）を作成
                create_subfolders(subcategory_path)

if __name__ == "__main__":
    create_output_folders()