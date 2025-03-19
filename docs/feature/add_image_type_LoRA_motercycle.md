新しいLoRAを追加し、それを用いてリアルテイストのバイクの画像を生成できるようにしたいです

# 仕様

- 以下新しいサブカテゴリを追加しバイクの画像を保存できるようにする
    - realistic/vehicle/motorcycle
    - illustration/vehicle/motorcycle
- 新しい LoRA と使用するモデルのチェックポイントの組み合わせを指定できるようにする
    - 追加する LoRA
        - KawasakiNinja300.safetensors
        - waifu_on_Motorcycle_v2.safetensors
        - cybervehiclev4.safetensors
    - 組み合わせるモデル
        - sd_xl_base_1.0.safetensors
- sd_xl_base_1.0.safetensors と KawasakiNinja300.safetensors の組み合わせでは以下に該当する画像を生成する
    - 大項目(style): リアルテイスト画像(realistic)
    - 中項目(category): 乗り物(vehicle)
    - 小項目(subcategory) - 中項目=乗り物
        - motorcycle
- sd_xl_base_1.0.safetensors と waifu_on_Motorcycle_v2.safetensors の組み合わせでは以下に該当する画像を生成する
    - 大項目(style): イラストテイスト画像(illustration)
    - 中項目(category): 乗り物(vehicle)
    - 小項目(subcategory) - 中項目=乗り物
        - motorcycle
- sd_xl_base_1.0.safetensors と cybervehiclev4.safetensors の組み合わせでは以下に該当する画像を生成する
    - 大項目(style): リアルテイスト画像(realistic) および イラストテイスト画像(illustration)
    - 中項目(category): 乗り物(vehicle)
    - 小項目(subcategory) - 中項目=乗り物
        - motorcycle
- 使用する LoRA によって生成する画像サイズを設定できるようにする。設定ファイルは `autoimagegenerator/settings.json(sample.settings.json)` を使用

# 追加する LoRA に関する情報

- KawasakiNinja300.safetensors
    - Keywords can be used: kawasakininja300
    ```
    This model is better to use between 0.7-0.9 weights

    Keywords can be useful: sitting on bike, on motorcycle, standing in front of motorcycle, vehicle focus

    Biker suit keywords: gloves, helmet, motorcycle helmet, biker clothes

    To change the angle, you can use: front view, side view, back view
    You can also change the color of the car by writing: "your_color" bike
    ```
- waifu_on_Motorcycle_v2.safetensors
    - This LoRA can set your waifu on motorcycles
    - Works well on most 2D, 2.5D. Suitable for full body figure and upper body
    - perfectly work with 512x768
- cybervehiclev4.safetensors
    ```
    Some possible keywords to try:

    car
    van
    motorcycle
    av (for flying vehicles. Doesn't work terribly well, but there are a few images in the dataset)

    sports car
    police style
    luxury sedan
    military style
    ```

# 生成画像保存先フォルダ構造パターン

docs/folder_structure.md を参照してください


# プロンプト保存フォルダ構造パターン

docs/prompt_settings.md を参照してください



# 関連ファイル
@main.py @auto_image_generator.py @settings.json

# 関連フォルダ
@prompts

---
以下のステップで進みたいですが、各ステップ毎に動作確認をするためのテストコードも合わせて作成しつつ実装を進めてください

1. sd_xl_base_1.0.safetensors と以下 LoRA を組み合わせて使用して画像生成するための設定項目などの追加
    - KawasakiNinja300.safetensors
    - waifu_on_Motorcycle_v2.safetensors
    - cybervehiclev4.safetensors
2. autoimagegenerator/settings.json(sample.settings.json) に使用する LoRA 毎にバイク用の画像サイズ(768x512)の設定を追加し、その設定を適用できるようプログラムも修正
3. main.py の起動オプションを追加
    - 今回追加する LoRA を使用して画像生成するための処理追加
4. realistic/vihicle/motorcycle の画像生成に必要なプロンプトファイルの作成(プロンプトファイルを作成する際は必ず、docs/prompt_settings.mdを参照して)
    - バイク単体を生成できるパターンは必須
    - バイクに人が乗っているパターンはフルフェイスのヘルメットにして、人の顔が映らないようにプロンプトで調整する
5. illustration/vihicle/motorcycle の画像生成に必要なプロンプトファイルの作成(プロンプトファイルを作成する際は必ず、docs/prompt_settings.mdを参照して)
    - バイク単体を生成できるパターンは必須
    - バイクに人が乗っているパターンはフルフェイスのヘルメットにして、人の顔が映らないようにプロンプトで調整する
6. バイク画像生成関連のテストコードを追加し、既存のテストも含めて全て通ることを確認

それではステップ1からお願いします

