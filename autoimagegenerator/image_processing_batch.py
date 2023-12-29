from auto_image_generator import AutoImageGenerator
import sys
import time
import os

# 定数定義
SD_MODEL_CHECKPOINTS = {
    "brav6": "Brav6.safetensors",
    "brav7": "beautifulRealistic_v7.safetensors"
}

# サムネイル用画像の保存先フォルダのパス
THUMBNAIL_FOLDER = "/thumbnail"

# Sample文字が入っている等倍画像の保存先フォルダのパス
WITH_SAMPLE_TEXT_FOLDER = "/sample"

# Sample文字が入っていサムネイル用画像の保存先フォルダのパス
WITH_SAMPLE_THUMBNAIL_FOLDER = "/sample-thumbnail"

IMAGE_PROCESSING_INPUT_FOLDER = "../images/output"

target_is_sample = False
sd_model_checkpoint = "Brav6.safetensors"  # デフォルト値

processing_mode = "create_collage"

if len(sys.argv) > 1:
    if sys.argv[1].lower() == "recreate_collage":  # 引数を小文字に変換して比較
        processing_mode = "recreate_collage"
    if sys.argv[1].lower() == "create_sample":  # 引数を小文字に変換して比較
        processing_mode = "create_sample"
    if sys.argv[1].lower() == "recreate_sample":  # 引数を小文字に変換して比較
        processing_mode = "recreate_sample"

if len(sys.argv) > 2:
    if sys.argv[2].lower() == "sample":  # 引数を小文字に変換して比較
        target_is_sample = True

arg_sd_model = "brav6"

def get_thumbnail_subfolders(folder_path, is_sample=True):
    subfolders = []
    for entry in os.scandir(folder_path):
        parent = entry.path.replace("\\", "/")
        if entry.is_dir():
            if is_sample:
                subfolder_path = parent + WITH_SAMPLE_THUMBNAIL_FOLDER
            else:
                subfolder_path = parent + THUMBNAIL_FOLDER
            subfolders.append({"thunmail": subfolder_path, "parent": parent})
    return subfolders

# 処理の開始時間を記録
start_time = time.time()

# AutoImageGenerator インスタンスを作成
auto_image_generator = AutoImageGenerator(
    image_generate_batch_execute_count=100,
    another_version_generate_count=11,
    input_folder="../images/input",
    output_folder="../images/output",
    prompts_folder="./prompts",
    url="http://192.168.1.130:7860",
    sd_model_checkpoint=sd_model_checkpoint,
    sd_model_prefix=arg_sd_model,
    enable_hr=True
)

# sd_model_checkpoint="beautifulRealistic_v7.safetensors"

subfolders = get_thumbnail_subfolders(IMAGE_PROCESSING_INPUT_FOLDER, target_is_sample)

for folder_path in subfolders:
    print(f"processing_mode: {processing_mode}")
    
    if processing_mode == "create_collage" or processing_mode == "recreate_collage":
        is_recreate = False
        if processing_mode == "recreate_collage":
            is_recreate = True
        print(f"thunmail folder_path: {folder_path['thunmail']}")
        output_path = folder_path['parent']
        if target_is_sample:
            output_path = folder_path['parent'] + "/sample"
        # AutoImageGenerator の create_image_collage メソッドを呼び出してまとめ画像生成処理を実行
        auto_image_generator.create_image_collage(folder_path['thunmail'], output_path, 3, 4, is_recreate)
    if processing_mode == "create_sample" or processing_mode == "recreate_sample":
        is_recreate = False
        if processing_mode == "recreate_sample":
            is_recreate = True
        # AutoImageGenerator の create_image_sample メソッドを呼び出してsample画像生成処理を実行
        auto_image_generator.create_image_sample(folder_path['parent'], is_recreate)

# 処理の終了時間を記録
end_time = time.time()

# 経過時間を計算
elapsed_time = end_time - start_time

# 経過時間を表示
print(f"処理にかかった時間: {elapsed_time}秒")