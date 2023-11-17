from auto_image_generator import AutoImageGenerator

# AutoImageGenerator インスタンスを作成
auto_image_generator = AutoImageGenerator(
    image_generate_batch_execute_count=300,
    another_version_generate_count=11,
    input_folder="../images/input",
    output_folder="../images/output",
    prompts_folder="./prompts",
    url="http://localhost:7860",
    sd_model_checkpoint="Brav6.safetensors",
    enable_hr=False
)

# sd_model_checkpoint="beautifulRealistic_v7.safetensors"

# AutoImageGenerator の run メソッドを呼び出して処理を実行
auto_image_generator.run()