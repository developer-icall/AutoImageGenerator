新しい画像生成AIモデルを追加し、それを用いてリアルテイストまたはイラストテイストの男女画像を生成できるようにしたいです

# 仕様
- 追加するモデルの checkpoint
    1. kohakuXLBeta_beta7.safetensors
- kohakuXLBeta_beta7.safetensors は以下に該当する画像を生成する
    - 大項目(style): イラストテイスト画像(illustration)
    - 中項目(category): male/female


- 生成された画像の出力先は上記に沿ったフォルダを作成し保存


# 画像フォルダ構造パターン

- docs/folder_structure.md を参照してください


# プロンプト保存フォルダ構造パターン

- docs/prompt_settings.md を必ず参照してください
- 仕様上必要な positive_pose.json, positive_selfie.json も作成して


# 関連ファイル
@main.py @auto_image_generator.py @settings.json

# 関連フォルダ
@prompts

---
以下のステップで進みたいですが、各ステップ毎に動作確認をするためのテストコードも合わせて作成しつつ実装を進めてください

1. main.py の起動オプションを追加

それではステップ1からお願いします

