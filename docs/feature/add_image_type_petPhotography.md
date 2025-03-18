新しい画像生成AIモデルを追加し、それを用いてリアルテイストまたはイラストテイストの男女画像や、動物などの画像を生成できるようにしたいです

# 仕様
- 追加するモデルの checkpoint
    1. petPhotographyAlbumOf_v10HomeEdition.safetensors
- petPhotographyAlbumOf_v10HomeEdition.safetensors は以下に該当する画像を生成する
    - 大項目(style): リアルテイスト画像(realistic)
    - 中項目(category): 動物
    - 小項目(subcategory) - 中項目=動物
        - cat
        - dog

- 生成された画像の出力先は上記に沿ったフォルダを作成し保存


# 画像フォルダ構造パターン

docs/folder_structure.md を参照してください


# プロンプト保存フォルダ構造パターン

docs/prompt_settings.md を参照してください



# 関連ファイル
@main.py @auto_image_generator.py @settings.json

# 関連フォルダ
@prompts

---
以下のステップで進みたいですが、各ステップ毎に動作確認をするためのテストコードも合わせて作成しつつ実装を進めてください
1. main.py の起動オプションを追加

それではステップ1からお願いします

