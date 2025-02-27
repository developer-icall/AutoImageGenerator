# AutoImageGenerator テスト

このディレクトリには、AutoImageGeneratorの自動テスト機能が含まれています。

## テストの実行方法

1. 仮想環境をアクティブにします（使用している場合）
2. プロジェクトのルートディレクトリに移動します
3. 以下のコマンドを実行します：

```bash
cd .\autoimagegenerator\
python -m tests.run_tests
```

## テストオプション

テスト実行スクリプトには、以下のオプションがあります：

- `--pattern <パターン名>`: 特定のテストパターンのみを実行します
- `--style <スタイル>`: 特定のスタイル（realistic/illustration）のテストのみを実行します
- `--category <カテゴリ>`: 特定のカテゴリ（female/male/animal等）のテストのみを実行します
- `--subcategory <サブカテゴリ>`: 特定のサブカテゴリ（normal/selfie/transparent等）のテストのみを実行します
- `--model <モデル>`: 特定のモデル（brav6/brav7等）のテストのみを実行します
- `--list`: 利用可能なテストパターンを一覧表示します
- `--no-report`: テスト結果のHTMLレポートを生成しません
- `--no-clean`: テスト実行前に以前のテスト出力を削除しません

例：
```bash
# 利用可能なテストパターンを一覧表示
python -m tests.run_tests --list

# 特定のパターンのみを実行
python -m tests.run_tests --pattern realistic_female_normal

# 特定のスタイルとカテゴリのテストを実行
python -m tests.run_tests --style realistic --category female

# 特定のスタイルとカテゴリおよびサブカテゴリのテストを実行
python -m tests.run_tests --style realistic --category female --subcategory selfie
```

## テスト検証機能

テストでは以下の検証が行われます：

### 1. 画像生成バッチ数の検証

`image_generate_batch_execute_count`の設定値に基づいて、生成された画像フォルダの数が正しいかを検証します。

例えば、`image_generate_batch_execute_count`が2に設定されている場合、出力ディレクトリ（`/images/output/<style>/<category>/<subcategory>/`）に2つの日付-時間-seedフォルダが存在することを確認します。

### 2. バージョン数の検証

`another_version_generate_count`の設定値に基づいて、各シードフォルダ内のファイル数が正しいかを検証します。

例えば、`another_version_generate_count`が2に設定されている場合：
- 各シードフォルダの直下に3つのpng、3つのjpg、3つのjsonファイルが存在すること（オリジナル + 2つのバージョン）
- 各サブフォルダ（`sample`、`sample-thumbnail`、`thumbnail`）にそれぞれ3つのpngファイルが存在すること
- `enable_hr`が`true`に設定されている場合、`half-resolution`フォルダにも3つのpngファイルが存在すること

## テスト結果

テスト結果は以下の場所に保存されます：

- JSONレポート: `autoimagegenerator/tests/output/test_results.json`
- HTMLレポート: `autoimagegenerator/tests/reports/test_report_<タイムスタンプ>.html`
- ログ: `autoimagegenerator/tests/test_run.log` および `test_image_generation.log`

生成された画像は以下のディレクトリに保存されます：

```
autoimagegenerator/tests/output/images/<style>/<category>/<subcategory>/
```

例えば、リアルな女性の通常画像は以下のパスに保存されます：

```
autoimagegenerator/tests/output/images/realistic/female/normal/
```