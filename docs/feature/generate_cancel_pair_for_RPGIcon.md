# 依頼内容

- `/AutoImageGenerator/autoimagegenerator/prompts` 以下の各スタイル/カテゴリ/サブカテゴリ内の各画像生成時に使用するプロンプトが記載されている「各画像生成時に使用するプロンプト設定ファイル」を順番に全て読み込み、プロンプトの組み合わせとして相性の悪いものがあれば `positive_cancel_pair.json` に追加してください。
    - フォルダ構成やプロンプト設定ファイルの仕様は `/AutoImageGenerator/autoimagegenerator/docs/prompt_settings.md`に記載しているので参照してください
- 組み合わせの相性をチェックする必要があるのは `positive_base.json`, `positive_optional.json`, `positive_pose.json` に記載のあるものだけです。他のファイルは必要ありません
- 相性が悪いと判断する例は以下です
    - `with silver edge` と `modern gun`: 現代の銃に銀の刃はない
    - `futuristic design` と `runic axe`: 未来的なデザインなルーンの斧は違和感がある
    - `wooden grip` と `crystal staff`: 素材が合わない

# 特記事項

- 特になし

# 関連ファイル, フォルダ

- `/AutoImageGenerator/autoimagegenerator/prompts/<style>/<category>/`
    - `positive_base.json`
    - `positive_optional.json`
    - `positive_pose.json`
    - `positive_cancel_pair.json`

---
以下のステップで進みたいですが、各ステップ毎に先へ進んでいいか確認してください

1. `/AutoImageGenerator/autoimagegenerator/prompts/realistic/female` フォルダ以下にあるプロンプトファイルについて作業をして
2. `/AutoImageGenerator/autoimagegenerator/prompts/realistic/male` フォルダ以下にあるプロンプトファイルについて作業をして
3. `/AutoImageGenerator/autoimagegenerator/prompts/illustration` フォルダ以下にあるプロンプトファイルについて作業をして

それではステップ1からお願いします
