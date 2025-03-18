新しいモデルとLoRAを追加し、それを用いてリアルテイストまたはイラストテイストの車の画像を生成できるようにしたいです

# 仕様
- LoRA を使用して画像を生成できるようにする
- LoRA と使用するモデルのチェックポイントの組み合わせを指定できるようにする
- 追加するモデル
    - sd_xl_base_1.0.safetensors
- 追加する LoRA
    1. cars-000008.safetensors
- sd_xl_base_1.0.safetensors と cars-000008.safetensors の組み合わせでは以下に該当する画像を生成する
    - 大項目(style): リアルテイスト画像(realistic) および イラストテイスト画像(illustration)
    - 中項目(category): 乗り物(vehicle)
    - 小項目(subcategory) - 中項目=乗り物
        - car

- 生成された画像の出力先は上記に沿ったフォルダを作成し保存


# 画像フォルダ構造パターン

docs/folder_structure.md を参照してください


# プロンプト保存フォルダ構造パターン

docs/prompt_settings.md を参照してください



# 関連ファイル
@main.py @auto_image_generator.py @settings.json

# 関連フォルダ
@prompts

---
以下のステップで進みたいですが、各ステップ毎に動作確認をするためのテストコードも合わせて作成しつつ実装を進めてください
1. sd_xl_base_1.0.safetensors と cars-000008.safetensors を組み合わせて使用して画像生成するための設定項目などの追加
2. main.py の起動オプションを追加
    - LoRA を使用して画像生成するための処理追加
    - sd_xl_base_1.0.safetensors を使用して画像生成するための処理追加
3. realistic/vihicle/car の画像生成に必要なプロンプトファイルの作成
4. illustration/vihicle/car の画像生成に必要なプロンプトファイルの作成

それではステップ1からお願いします

