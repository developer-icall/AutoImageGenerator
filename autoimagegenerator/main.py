from auto_image_generator import AutoImageGenerator
import sys
import time

# 定数定義
SD_MODEL_CHECKPOINTS = {
    "brav6": "Brav6.safetensors",
    "brav7": "  ",
    "brav7_men": "beautifulRealistic_v7.safetensors"
}

SD_MODEL_SCRITPS = {
    
}

OUTPUT_FOLDER_MEN_PREFIX = "-men"

OUTPUT_FOLDER_TRANSPARENT_BACKGROUND_PREFIX = "-transparent"

arg_sd_model = "brav6"

output_folder_prefix = ""
is_transparent_background = False

# コマンドライン引数から指定されたモデルチェックポイントの値を取得
if len(sys.argv) > 1:
    arg_sd_model = sys.argv[1].lower()  # 引数を小文字に変換して比較
    sd_model_checkpoint = SD_MODEL_CHECKPOINTS.get(arg_sd_model)
else:
    sd_model_checkpoint = "Brav6.safetensors"  # デフォルト値

if len(sys.argv) > 2:
    if sys.argv[2].lower() == "true":  # 引数を小文字に変換して比較
        is_transparent_background = True


if arg_sd_model == "brav7_men":
    output_folder_prefix = OUTPUT_FOLDER_MEN_PREFIX

if is_transparent_background:
    output_folder_prefix = output_folder_prefix + OUTPUT_FOLDER_TRANSPARENT_BACKGROUND_PREFIX

print(f"sd_model_checkpoint: {sd_model_checkpoint}")

# 処理の開始時間を記録
start_time = time.time()

# AutoImageGenerator インスタンスを作成
auto_image_generator = AutoImageGenerator(
    image_generate_batch_execute_count=30,
    another_version_generate_count=11,
    input_folder="../images/input",
    output_folder="../images/output",
    prompts_folder="./prompts",
    url="http://192.168.1.130:7860",
    sd_model_checkpoint=sd_model_checkpoint,
    sd_model_prefix=arg_sd_model,
    enable_hr=True,
    output_folder_prefix=output_folder_prefix,
    is_transparent_background=is_transparent_background
)

# sd_model_checkpoint="beautifulRealistic_v7.safetensors"

# AutoImageGenerator の run メソッドを呼び出して処理を実行
auto_image_generator.run()

# 処理の終了時間を記録
end_time = time.time()

# 経過時間を計算
elapsed_time = end_time - start_time

# 経過時間を表示
print(f"処理にかかった時間: {elapsed_time}秒")