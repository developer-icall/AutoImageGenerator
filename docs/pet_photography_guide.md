# petPhotographyモデルの使用ガイド

このドキュメントでは、`petPhotography`モデル（petPhotographyAlbumOf_v10HomeEdition.safetensors）を使用して、リアルテイストの猫や犬の画像を生成する方法について説明します。

## 概要

`petPhotography`モデルは、リアルテイストの猫や犬の画像を生成するために特化したモデルです。このモデルを使用することで、高品質なペット写真を簡単に生成できます。

## 基本的な使用方法

### 前提条件

1. Stable Diffusion Web UIが起動していること
2. petPhotographyAlbumOf_v10HomeEdition.safetensorsモデルがStable Diffusion Web UIに登録されていること

### コマンドライン実行

以下のコマンドで、`petPhotography`モデルを使用して猫や犬の画像を生成できます：

```bash
# 猫の画像を生成
python main.py --style realistic --category animal --subcategory cat --model petPhotography

# 犬の画像を生成
python main.py --style realistic --category animal --subcategory dog --model petPhotography
```

## 専用スクリプトの使用

より簡単に`petPhotography`モデルを使用するために、以下の専用スクリプトが用意されています：

### 1. プロンプト設定のセットアップ

最初に、`petPhotography`モデル用のプロンプト設定ファイルをセットアップします：

```bash
python setup_pet_photography_prompts.py
```

このスクリプトは以下の処理を行います：
- `prompts/realistic/animal/cat`と`prompts/realistic/animal/dog`のディレクトリ構造を作成
- 各ディレクトリに必要なプロンプト設定ファイルを配置

### 2. テスト実行

プロンプト設定が正しく機能するかテストするには：

```bash
python test_pet_photography.py --dry-run
```

このスクリプトは、実際の画像生成を行わずにプロンプト生成のみをテストします。

### 3. 画像生成

実際に画像を生成するには：

```bash
# 猫の画像のみを生成
python generate_pet_images.py --subcategory cat

# 犬の画像のみを生成
python generate_pet_images.py --subcategory dog

# 猫と犬の両方の画像を生成
python generate_pet_images.py --subcategory all

# 複数バッチの画像を生成（例：3バッチ）
python generate_pet_images.py --subcategory all --count 3
```

## プロンプト設定のカスタマイズ

`petPhotography`モデル用のプロンプト設定は以下のファイルで管理されています：

- 猫用：`prompts/realistic/animal/cat/`以下の各JSONファイル
- 犬用：`prompts/realistic/animal/dog/`以下の各JSONファイル

これらのファイルを編集することで、生成される画像の特徴をカスタマイズできます。

### 主なプロンプト設定ファイル

- **positive_base.json**: 基本的な特徴（猫/犬の種類、毛の特徴など）
- **positive_optional.json**: 背景、アクセサリー、構図など
- **positive_pose.json**: ポーズ、表情など
- **negative.json**: 生成したくない要素

## トラブルシューティング

### 画像が生成されない場合

1. Stable Diffusion Web UIが起動しているか確認してください
2. petPhotographyAlbumOf_v10HomeEdition.safetensorsモデルがStable Diffusion Web UIに正しく登録されているか確認してください
3. プロンプト設定ファイルが正しく配置されているか確認してください

### 生成された画像の品質が低い場合

1. `--enable-hr true`オプションを追加して、ハイレゾ画像生成を有効にしてください
2. プロンプト設定ファイルの内容を調整してください

## 高度な使用方法

### カスタムプロンプトの追加

`setup_pet_photography_prompts.py`スクリプトを編集することで、デフォルトのプロンプト設定をカスタマイズできます。

例えば、特定の猫種や犬種を追加したい場合は、`CAT_SPECIFIC_PROMPTS`や`DOG_SPECIFIC_PROMPTS`の定義を編集します。

### 画像サイズの変更

画像サイズを変更するには、以下のように`--width`と`--height`オプションを追加します：

```bash
python main.py --style realistic --category animal --subcategory cat --model petPhotography --width 768 --height 768
```

## 出力画像の例

生成された画像は以下のディレクトリに保存されます：

- 猫の画像：`images/output/realistic/animal/cat/[日時-Seed値]/`
- 犬の画像：`images/output/realistic/animal/dog/[日時-Seed値]/`

各ディレクトリには、元画像とともに以下のサブディレクトリが作成されます：
- `thumbnail/`: サムネイル画像
- `sample/`: サンプル画像（透かし入り）
- `sample-thumbnail/`: サンプルサムネイル画像
- `half-resolution/`: 半分の解像度の画像