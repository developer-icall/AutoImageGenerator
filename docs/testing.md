# 自動テスト機能

このドキュメントでは、AutoImageGeneratorの自動テスト機能について説明します。

## 概要

AutoImageGeneratorには、異なるパターンでの画像生成を自動的にテストする機能が含まれています。この機能を使用することで、システムが正常に動作しているかを確認できます。

## テスト実行手順

1. 仮想環境を有効化する
   ```
   .\venv\Scripts\activate
   ```

2. autoimagegeneratorディレクトリに移動する
   ```
   cd .\autoimagegenerator\
   ```

3. テストを実行する
   ```
   python -m tests.run_tests
   ```

   これにより、`tests/test_settings.json`に定義されたすべてのテストパターンが実行されます。

## テストオプション

テスト実行スクリプトは以下のコマンドラインオプションをサポートしています：

- **--pattern**: 特定のテストパターンのみを実行する
  ```
  python -m tests.run_tests --pattern realistic_female_normal
  ```

- **--list**: 利用可能なテストパターンを一覧表示する
  ```
  python -m tests.run_tests --list
  ```

- **--no-report**: テスト結果のHTMLレポートを生成しない
  ```
  python -m tests.run_tests --no-report
  ```

## テスト設定のカスタマイズ

テストの設定は `tests/test_settings.json` ファイルで管理されています。このファイルを編集することで、テストするパターンや設定をカスタマイズできます。

デフォルトでは、以下の3つのパターンがテストされます：
1. リアルテイストの女性の通常画像（brav7モデル）
2. リアルテイストの女性のセルフィー画像（brav6モデル）
3. リアルテイストの女性の透過背景画像（brav7モデル）

## 背景画像生成のテストパターン

背景画像生成のテストでは、以下のパターンが追加でテストされます：

1. リアルテイストの都市背景画像（landscapeRealisticモデル）
2. リアルテイストの自然背景画像（landscapeRealisticモデル）
3. リアルテイストの海背景画像（landscapeRealisticモデル）
4. リアルテイストの空背景画像（landscapeRealisticモデル）
5. リアルテイストの家背景画像（landscapeRealisticモデル）

これらのテストパターンは、`test_patterns` 配列に以下のように追加されます：

```json
{
    "name": "realistic_background_city",
    "style": "realistic",
    "category": "background",
    "subcategory": "city",
    "model": "landscapeRealistic",
    "enable_hr": true
},
{
    "name": "realistic_background_nature",
    "style": "realistic",
    "category": "background",
    "subcategory": "nature",
    "model": "landscapeRealistic",
    "enable_hr": true
},
{
    "name": "realistic_background_sea",
    "style": "realistic",
    "category": "background",
    "subcategory": "sea",
    "model": "landscapeRealistic",
    "enable_hr": true
},
{
    "name": "realistic_background_sky",
    "style": "realistic",
    "category": "background",
    "subcategory": "sky",
    "model": "landscapeRealistic",
    "enable_hr": true
},
{
    "name": "realistic_background_house",
    "style": "realistic",
    "category": "background",
    "subcategory": "house",
    "model": "landscapeRealistic",
    "enable_hr": true
}
```

## バイク画像生成のテストパターン

バイク画像生成のテストでは、以下のパターンが追加でテストされます：

1. リアル調のバイク画像（KawasakiNinja300 LoRA使用）
2. イラスト調のバイク画像（waifu_on_Motorcycle_v2 LoRA使用）
3. サイバーパンク調のバイク画像（cybervehiclev4 LoRA使用）

これらのテストパターンは、`test_patterns` 配列に以下のように追加されます：

```json
{
    "name": "realistic_vehicle_motorcycle_kawasaki",
    "style": "realistic",
    "category": "vehicle",
    "subcategory": "motorcycle",
    "model": "sd_xl_base_1.0",
    "use_lora": true,
    "lora_name": "KawasakiNinja300",
    "enable_hr": true
},
{
    "name": "illustration_vehicle_motorcycle_waifu",
    "style": "illustration",
    "category": "vehicle",
    "subcategory": "motorcycle",
    "model": "sd_xl_base_1.0",
    "use_lora": true,
    "lora_name": "waifu_on_Motorcycle_v2",
    "enable_hr": true
},
{
    "name": "realistic_vehicle_motorcycle_cyber",
    "style": "realistic",
    "category": "vehicle",
    "subcategory": "motorcycle",
    "model": "sd_xl_base_1.0",
    "use_lora": true,
    "lora_name": "cybervehiclev4",
    "enable_hr": true
}
```

## テスト結果の確認

テスト実行後、以下の場所にテスト結果が保存されます：

- **テスト結果JSON**: `tests/output/test_results.json`
- **テスト結果HTMLレポート**: `tests/reports/test_report_YYYYMMDD-HHMMSS.html`
- **テストログ**: `test_run.log` および `test_image_generation.log`

HTMLレポートには、各テストパターンの実行結果、実行時間、生成された画像の数などの情報が含まれています。

## テスト出力画像の確認

テストで生成された画像は `tests/output/images` ディレクトリに保存されます。各テストパターンの画像は、スタイル、カテゴリー、サブカテゴリーに基づいたサブディレクトリに整理されています。

例えば、リアルテイストの女性の通常画像のテスト結果は以下のパスに保存されます：
```
tests/output/images/realistic/female/normal/
```

また、背景画像のテスト結果は以下のようなパスに保存されます：
```
tests/output/images/realistic/background/city/
tests/output/images/realistic/background/nature/
tests/output/images/realistic/background/sea/
tests/output/images/realistic/background/sky/
tests/output/images/realistic/background/house/
```

また、バイク画像のテスト結果は以下のようなパスに保存されます：
```
tests/output/images/realistic/vehicle/motorcycle/
tests/output/images/illustration/vehicle/motorcycle/
```