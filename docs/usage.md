# 使用方法

このドキュメントでは、AutoImageGeneratorの詳細な使用方法について説明します。

## 基本的な使用方法

1. 仮想環境を有効化します
   ```
   .\.venv\Scripts\activate
   ```

2. 実行環境のパスへ移動します
   ```
   cd .\autoimagegenerator\
   ```

3. 以下のコマンドでプログラムを実行します
   ```
   poetry run python main.py --style realistic --category female --subcategory normal
   ```

4. `./AutoImageGenerator/images/output` 以下に画像が生成されることを確認します

## 設定ファイル

### settings.json

- `./autoimagegenerator/sample.settings.json` をコピーして `settings.json` を作成し、以下を設定します
  - `image_generate_batch_execute_count`: 何件の人物について画像を一括作成するか指定
  - `another_version_generate_count`: 同じ人物につき何件の画像を作成するか指定
  - `lora_settings`: LoRAの設定を指定
    ```json
    {
      "lora_settings": {
        "cars-000008": {
          "model": "sd_xl_base_1.0",
          "weight": 0.7,
          "trigger_word": "cars-000008"
        }
      }
    }
    ```

## コマンドライン引数の詳細

`main.py` は以下のコマンドライン引数をサポートしています。これらの引数を使用することで、画像生成の動作をカスタマイズできます：

### 必須の引数

- **--style**: 画像スタイル
  - `realistic`: リアルテイスト画像
  - `illustration`: イラストテイスト画像

- **--category**: カテゴリー
  - `female`: 女性
  - `male`: 男性
  - `animal`: 動物
  - `background`: 背景（realistic/illustration）
  - `rpg_icon`: RPGアイコン（illustrationのみ）
  - `vehicle`: 乗り物（illustrationのみ）
  - `other`: その他（illustrationのみ）

### オプションの引数

- **--subcategory**: サブカテゴリー
  - 人物（female/male）の場合:
    - `normal`: 通常画像
    - `transparent`: 透過背景画像
    - `selfie`: セルフィー画像
  - 動物の場合:
    - `dog`: 犬
    - `cat`: 猫
    - `bird`: 鳥
    - `fish`: 魚
    - `other`: その他
  - 背景の場合:
    - `city`: 都市
    - `nature`: 自然
    - `sea`: 海
    - `sky`: 空
    - `house`: 家
  - 乗り物の場合:
    - `car`: 車
    - `ship`: 船
    - `airplane`: 飛行機
    - `motorcycle`: バイク
    - `other`: その他

- **--model**: 使用するモデル（デフォルトはカテゴリーに応じて自動選択）
  - `brav6`: Beautiful Realistic Asians v6
  - `brav7`: Beautiful Realistic Asians v7
  - `brav7_men`: Beautiful Realistic Asians v7（男性向け）
  - `photoRealRPG`: RPGアイコン用モデル（photoRealV15_photorealv21.safetensors）
  - `RPGIcon`: RPGIcon.safetensorsモデル
  - `animagineXL`: イラストテイスト画像用モデル（animagineXL40_v4Opt.safetensors）
  - `yayoiMix`: リアルテイスト画像用モデル（yayoiMix_v25.safetensors）
  - `petPhotography`: ペット写真用モデル（petPhotographyAlbumOf_v10HomeEdition.safetensors）
  - `sd_xl_base_1.0`: SDXL Base 1.0モデル（LoRA使用時）
  - `landscapeRealistic`: 背景画像用モデル（landscapeRealistic_v20WarmColor.safetensors）
  - `kawaiiRealisticAnime`: イラストテイスト画像用モデル（kawaiiRealisticAnime_a06.safetensors）
  - `kohakuXLBeta`: イラストテイスト画像用モデル（kohakuXLBeta_beta7.safetensors）

- **--enable-hr**: ハイレゾ画像生成の有効/無効
  - `true`: 有効（デフォルト）
  - `false`: 無効

- **--use-lora**: LoRAを使用して画像を生成する（オプション）
  - 指定時: LoRAを使用
  - 未指定時: LoRAを使用しない

- **--lora-name**: 使用するLoRAの名前
  - `cars-000008`: 車のLoRA
  - `KawasakiNinja300`: リアルなバイク画像生成用LoRA
  - `waifu_on_Motorcycle_v2`: イラスト調のバイク画像生成用LoRA
  - `cybervehiclev4`: サイバーパンク調のバイク画像生成用LoRA

## 使用例

以下は、いくつかの使用例です：

```bash
# リアルテイストの女性の通常画像を生成（brav7モデルを指定）
python main.py --style realistic --category female --subcategory normal --model brav7

# リアルテイストの女性のセルフィー画像を生成（brav6モデルを指定）
python main.py --style realistic --category female --subcategory selfie --model brav6

# リアルテイストの女性の透過背景画像を生成（ハイレゾ無効）
python main.py --style realistic --category female --subcategory transparent --enable-hr false

# イラストテイストのRPGアイコン（武器）をphotoRealRPGモデルで生成
python main.py --style illustration --category rpg_icon --subcategory weapon --model photoRealRPG

# イラストテイストのRPGアイコン（武器）をRPGIconモデルを使用して生成
python main.py --style illustration --category rpg_icon --subcategory weapon --model RPGIcon

# イラストテイストの動物（犬）画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category animal --subcategory dog --model animagineXL

# イラストテイストの動物（猫）画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category animal --subcategory cat --model animagineXL

# イラストテイストの動物（鳥）画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category animal --subcategory bird --model animagineXL

# イラストテイストの動物（魚）画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category animal --subcategory fish --model animagineXL

# リアルテイストの動物（犬）画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category animal --subcategory dog --model yayoiMix

# リアルテイストの動物（猫）画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category animal --subcategory cat --model yayoiMix

# リアルテイストの動物（鳥）画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category animal --subcategory bird --model yayoiMix

# リアルテイストの動物（魚）画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category animal --subcategory fish --model yayoiMix

# リアルテイストの猫画像を生成（petPhotographyモデルを指定）
python main.py --style realistic --category animal --subcategory cat --model petPhotography

# リアルテイストの犬画像を生成（petPhotographyモデルを指定）
python main.py --style realistic --category animal --subcategory dog --model petPhotography

# イラストテイストの女性の通常画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category female --subcategory normal --model animagineXL

# イラストテイストの女性のセルフィー画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category female --subcategory selfie --model animagineXL

# イラストテイストの女性の透過背景画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category female --subcategory transparent --model animagineXL

# イラストテイストの男性の通常画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category male --subcategory normal --model animagineXL

# イラストテイストの男性のセルフィー画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category male --subcategory selfie --model animagineXL

# イラストテイストの男性の透過背景画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category male --subcategory transparent --model animagineXL

# リアルテイストの女性の通常画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category female --subcategory normal --model yayoiMix

# リアルテイストの女性のセルフィー画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category female --subcategory selfie --model yayoiMix

# リアルテイストの女性の透過背景画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category female --subcategory transparent --model yayoiMix

# リアルテイストの男性の通常画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category male --subcategory normal --model yayoiMix

# リアルテイストの男性のセルフィー画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category male --subcategory selfie --model yayoiMix

# リアルテイストの男性の透過背景画像を生成（yayoiMixモデルを指定）
python main.py --style realistic --category male --subcategory transparent --model yayoiMix

# リアルテイストの車の画像を生成（SDXL Base 1.0モデルとLoRAを使用）
python main.py --style realistic --category vehicle --subcategory car --use-lora --lora-name cars-000008

# イラストテイストの車の画像を生成（animagineXLモデルを指定）
python main.py --style illustration --category vehicle --subcategory car --model animagineXL

# リアルテイストの車の画像を生成（SDXL Base 1.0モデルとLoRAを使用、モデルを明示的に指定）
python main.py --style realistic --category vehicle --subcategory car --use-lora --lora-name cars-000008 --model sd_xl_base_1.0

# リアルテイストの都市背景画像を生成（landscapeRealisticモデルを指定）
python main.py --style realistic --category background --subcategory city --model landscapeRealistic

# リアルテイストの自然背景画像を生成（landscapeRealisticモデルを指定）
python main.py --style realistic --category background --subcategory nature --model landscapeRealistic

# リアルテイストの海背景画像を生成（landscapeRealisticモデルを指定）
python main.py --style realistic --category background --subcategory sea --model landscapeRealistic

# リアルテイストの空背景画像を生成（landscapeRealisticモデルを指定）
python main.py --style realistic --category background --subcategory sky --model landscapeRealistic

# リアルテイストの家背景画像を生成（landscapeRealisticモデルを指定）
python main.py --style realistic --category background --subcategory house --model landscapeRealistic

# kawaiiRealisticAnimeモデルを使用した画像生成の例

# イラストテイストの女性の通常画像を生成（kawaiiRealisticAnimeモデルを指定）
python main.py --style illustration --category female --subcategory normal --model kawaiiRealisticAnime

# イラストテイストの女性のセルフィー画像を生成（kawaiiRealisticAnimeモデルを指定）
python main.py --style illustration --category female --subcategory selfie --model kawaiiRealisticAnime

# イラストテイストの女性の透過背景画像を生成（kawaiiRealisticAnimeモデルを指定）
python main.py --style illustration --category female --subcategory transparent --model kawaiiRealisticAnime

# イラストテイストの男性の通常画像を生成（kawaiiRealisticAnimeモデルを指定）
python main.py --style illustration --category male --subcategory normal --model kawaiiRealisticAnime

# イラストテイストの男性のセルフィー画像を生成（kawaiiRealisticAnimeモデルを指定）
python main.py --style illustration --category male --subcategory selfie --model kawaiiRealisticAnime

# イラストテイストの男性の透過背景画像を生成（kawaiiRealisticAnimeモデルを指定）
python main.py --style illustration --category male --subcategory transparent --model kawaiiRealisticAnime

# kohakuXLBetaモデルを使用した画像生成の例

# イラストテイストの女性の通常画像を生成（kohakuXLBetaモデルを指定）
python main.py --style illustration --category female --subcategory normal --model kohakuXLBeta

# イラストテイストの女性のセルフィー画像を生成（kohakuXLBetaモデルを指定）
python main.py --style illustration --category female --subcategory selfie --model kohakuXLBeta

# イラストテイストの女性の透過背景画像を生成（kohakuXLBetaモデルを指定）
python main.py --style illustration --category female --subcategory transparent --model kohakuXLBeta

# イラストテイストの男性の通常画像を生成（kohakuXLBetaモデルを指定）
python main.py --style illustration --category male --subcategory normal --model kohakuXLBeta

# イラストテイストの男性のセルフィー画像を生成（kohakuXLBetaモデルを指定）
python main.py --style illustration --category male --subcategory selfie --model kohakuXLBeta

# イラストテイストの男性の透過背景画像を生成（kohakuXLBetaモデルを指定）
python main.py --style illustration --category male --subcategory transparent --model kohakuXLBeta

# バイク画像生成の例

# リアル調のバイク画像を生成（KawasakiNinja300 LoRAを使用）
python main.py --style realistic --category vehicle --subcategory motorcycle --use-lora --lora-name KawasakiNinja300

# イラスト調のバイク画像を生成（waifu_on_Motorcycle_v2 LoRAを使用）
python main.py --style illustration --category vehicle --subcategory motorcycle --use-lora --lora-name waifu_on_Motorcycle_v2

# サイバーパンク調のバイク画像を生成（cybervehiclev4 LoRAを使用）
python main.py --style realistic --category vehicle --subcategory motorcycle --use-lora --lora-name cybervehiclev4

# ドライランモードでプロンプトのみを確認
python main.py --style realistic --category vehicle --subcategory motorcycle --use-lora --lora-name KawasakiNinja300 --dry-run