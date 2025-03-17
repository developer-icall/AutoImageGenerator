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

新しいテストパターンを追加するには、`test_patterns` 配列に新しいオブジェクトを追加します：

```json
{
    "name": "パターン名",
    "style": "スタイル",
    "category": "カテゴリー",
    "subcategory": "サブカテゴリー",
    "model": "モデル名",
    "enable_hr": false
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