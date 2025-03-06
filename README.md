# AutoImageGenerator

## 概要

本プロジェクトは、Python から Stable Diffusion の API を呼び出して、画像生成を自動で行うためのシステムです。プロンプト設定ファイルを使用して、多様な画像を効率的に生成できます。

## 主な機能

- 指定フォルダ(autoimagegenerator/prompts)以下にある各種プロンプトをランダムに組み合わせて画像を生成
- 複数の画像生成AIモデルに対応（Brav6, Brav7など）
- 様々なカテゴリ（女性、男性、動物など）とスタイル（リアル、イラストなど）に対応
- 透過背景画像やセルフィー画像など、多様な画像タイプの生成をサポート
- 自動テスト機能による動作確認

## クイックスタート

1. 必要なソフトウェアをインストール
   - Python 3.10.6以上
   - Poetry
   - Docker（Stable Diffusion Web UI用）

2. 仮想環境を有効化
   ```
   .\venv\Scripts\activate
   ```

3. 実行環境のパスへ移動
   ```
   cd .\autoimagegenerator\
   ```

4. 画像生成を実行
   ```
   poetry run python main.py --style realistic --category female --subcategory normal
   ```

5. `./AutoImageGenerator/images/output` 以下に生成された画像を確認

## 詳細ドキュメント

より詳細な情報については、以下のドキュメントを参照してください：

- [インストール手順](docs/installation.md) - 環境構築とセットアップの詳細
- [使用方法](docs/usage.md) - 詳細な使用方法とコマンドライン引数
- [自動テスト機能](docs/testing.md) - テスト機能の使用方法
- [生成画像フォルダ仕様](docs/folder_structure.md) - 出力ディレクトリ構造の説明
- [プロンプト設定ファイル仕様](docs/prompt_settings.md) - プロンプト設定の詳細
- [トラブルシューティング](docs/troubleshooting.md) - 一般的な問題と解決策

## 使用例

```bash
# リアルテイストの女性の通常画像を生成（brav7モデルを指定）
python main.py --style realistic --category female --subcategory normal --model brav7

# リアルテイストの女性のセルフィー画像を生成
python main.py --style realistic --category female --subcategory selfie

# イラストテイストのRPGアイコンを生成
python main.py --style illustration --category rpg_icon
```

## 必要なモデル

- [Beautiful Realistic Asians - v7](https://civitai.com/models/25494/brabeautiful-realistic-asians-v2) - リアルな人物画像生成用モデル

## ライセンス

このプロジェクトは独自ライセンスの下で提供されています。詳細については、プロジェクト管理者にお問い合わせください。
