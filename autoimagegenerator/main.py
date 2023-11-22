from auto_image_generator import AutoImageGenerator
import time

# 処理の開始時間を記録
start_time = time.time()

# AutoImageGenerator インスタンスを作成
auto_image_generator = AutoImageGenerator(
    image_generate_batch_execute_count=100,
    another_version_generate_count=11,
    input_folder="../images/input",
    output_folder="../images/output",
    prompts_folder="./prompts",
    url="http://localhost:7860",
    sd_model_checkpoint="Brav6.safetensors",
    enable_hr=True
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