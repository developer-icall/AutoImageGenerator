# 要件定義ドキュメント

このフォルダには、Auto Image Generator プロジェクトの要件定義ドキュメントが含まれています。

## フォルダ構成
- `requirements/` - 機能要件の詳細ドキュメント
- `specifications/` - 技術仕様書
- `diagrams/` - システム構成図やフローチャートなど

## 機能要件の記載例

新機能を作るので実装お願いします

# 仕様
- 新しく awesomeRPGIcon2000 というモデルを使用して画像を生成できるようにする
- 使用するモデル名は `awesomeRPGIcon2000_awesomeRPGIcon2000.safetensors`
- プロンプトは autoimagegenerator/prompts/RPGIcon いかにあるものを使用する

# 関連ファイル
@main.py @auto_image_generator.py

---
以下のステップで進みたいです
1. main.py 起動時のパラメータで awesomeRPGIcon2000 を指定できるようにする
2. 実際に awesomeRPGIcon2000 を使用して、RPGIcon 専用のプロンプトを使用して画像を生成できるようにする
3. 保存先は autoimagegenerator/images/output 以下に RPGIcon という名前のフォルダを作成し、その中に保存する

それではステップ1からお願いします

- 参考: https://zenn.dev/jessicazu/articles/7a46a7e15c153f