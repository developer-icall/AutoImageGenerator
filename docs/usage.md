# 使用方法

このドキュメントでは、AutoImageGeneratorの詳細な使用方法について説明します。

## 基本的な使用方法

1. 仮想環境を有効化します
   ```
   .\venv\Scripts\activate
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
  - `background`: 背景（illustrationのみ）
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
  - その他のカテゴリーについては仕様書を参照

- **--model**: 使用するモデル（デフォルトはカテゴリーに応じて自動選択）
  - `brav6`: Beautiful Realistic Asians v6
  - `brav7`: Beautiful Realistic Asians v7
  - `rpg_icon`: RPGアイコン用モデル

- **--enable-hr**: ハイレゾ画像生成の有効/無効
  - `true`: 有効（デフォルト）
  - `false`: 無効

## 使用例

以下は、いくつかの使用例です：

```bash
# リアルテイストの女性の通常画像を生成（brav7モデルを指定）
python main.py --style realistic --category female --subcategory normal --model brav7

# リアルテイストの女性のセルフィー画像を生成（brav6モデルを指定）
python main.py --style realistic --category female --subcategory selfie --model brav6

# リアルテイストの女性の透過背景画像を生成（ハイレゾ無効）
python main.py --style realistic --category female --subcategory transparent --enable-hr false

# イラストテイストのRPGアイコン（武器）を生成
python main.py --style illustration --category rpg_icon --subcategory weapon
```