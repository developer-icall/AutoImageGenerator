新しい画像生成AIモデルを追加し、それを用いてリアルテイストまたはイラストテイストの男女画像や、動物などの画像を生成できるようにしたいです

# 仕様
- 追加するモデルの checkpoint
    1. landscapeRealistic_v20WarmColor.safetensors
- landscapeRealistic_v20WarmColor.safetensors は以下に該当する画像を生成する
    - 大項目(style): リアルテイスト画像(realistic)
    - 中項目(category): 背景
    - 小項目(subcategory) - 中項目=背景
        - city
        - nature
        - sea
        - sky
        - house

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
    - house は追加で他はある想定
2. realistic/background で各種小項目ごとの prompts を追加。できるだけ多くのパターンの画像を生成できるよう、最適なプロンプトを設計し作成する
    - /promps/realistic/background/city
    - /promps/realistic/background/nature
    - /promps/realistic/background/sea
    - /promps/realistic/background/sky
    - /promps/realistic/background/house
3. illustration/background 以下で作成したプロンプトと同じものを realistic/background フォルダ以下に配置し、illustration を指定しているプロンプトは realistic に変換
4. ステップ2、ステップ3 で作成したプロンプトを使用して、実際に各小項目ごとに画像を生成できるようにする

それではステップ1からお願いします

