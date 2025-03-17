新しい画像生成AIモデルを追加し、それを用いてリアルテイストまたはイラストテイストの男女画像や、動物などの画像を生成できるようにしたいです

# 仕様
- 追加するモデルの checkpoint
    1. animagineXL40_v4Opt.safetensors
    2. yayoiMix_v25.safetensors
- animagineXL40_v4Opt は以下に該当する画像を生成する
    - 大項目(style): イラストテイスト画像(illustration)
    - 中項目(category): 男性、女性、動物
    - 小項目(subcategory) - 中項目=男性、女性
        - normal
        - selfie
        - transparent
    - 小項目(subcategory) - 中項目=動物
        - bird
        - cat
        - dog
        - fish
- yayoiMix_v25 は以下に該当する画像を生成する
    - 大項目(style): リアルテイスト画像(realistic)
    - 中項目(category): 男性、女性、動物
    - 小項目(subcategory) - 中項目=男性、女性
        - normal
        - selfie
        - transparent
    - 小項目(subcategory) - 中項目=動物
        - bird
        - cat
        - dog
        - fish

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
1. main.py の起動オプションを追加(既にある想定だが確認)
2. illustration/animal で各種小項目ごとの prompts を追加。できるだけ多くのパターンの画像を生成できるよう、最適なプロンプトを設計し作成する
    - /promps/illustration/animal/bird
    - /promps/illustration/animal/cat
    - /promps/illustration/animal/dog
    - /promps/illustration/animal/fish
3. illustration/animal 以下で作成したプロンプトと同じものを realistic/animal フォルダ以下に配置
3. ステップ2、ステップ3 で作成したプロンプトを使用して、実際に各小項目ごとに画像を生成できるようにする


それではステップ1からお願いします

