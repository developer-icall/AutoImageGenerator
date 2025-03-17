RPGIcon を用いて武器や防具などの画像を生成できるようにしたいです

# 仕様
- モデルの checkpoint: RPGIcon.safetensors
- RPGIconは以下に該当する画像を生成する
    - 大項目(style): イラストテイスト画像(illustration)
    - 中項目(category): RPGアイコン
    - 小項目(subcategory):
        - 武器・防具
        - モンスター
        - その他
- 生成された画像の出力先は上記に沿ったフォルダを作成し保存


# 画像フォルダ構造パターン

## 大項目（スタイル）
/images/output/illustration   # イラストテイスト

## 中項目（カテゴリー）
/images/output/illustration/rpg_icon    # RPGアイコン

## 小項目（サブカテゴリー）

### RPGアイコン（rpg_icon）
/images/output/illustration/rpg_icon/weapon   # 武器・防具
/images/output/illustration/rpg_icon/monster  # モンスター
/images/output/illustration/rpg_icon/other    # その他


# プロンプト保存フォルダ構造パターン

README.md の「AutoImageGenerator プロンプト設定ファイル仕様書」を参照してください



## 生成時に動的に作成されるフォルダ

画像生成時には大項目・中項目・小項目に応じたフォルダの下に、作成日時と生成された画像の Seed 値を含むフォルダが作成されます。
例) 20250221-12-2934224203

既に実装されている機能なので、今回の修正においてこの機能が消えないよう注意してください。


## サムネイル・サンプル画像

生成時に動的に作成されるフォルダ内には以下のサブフォルダが作成され、それぞれの仕様に応じた画像が保存されます。
既に実装されている機能なので、今回の修正においてこの機能が消えないよう注意してください。

/thumbnail          # サムネイル画像
/sample             # サンプル画像（透かし入り）
/sample-thumbnail   # サンプルサムネイル画像（透かし入り）
/half-resolution    # 半分の解像度の画像


# 関連ファイル
@main.py @auto_image_generator.py @settings.json

# 関連フォルダ
@prompts

---
以下のステップで進みたいですが、各ステップ毎に動作確認をするためのテストコードも合わせて作成しつつ実装を進めてください
1. main.py の起動オプションを追加(既にある想定だが確認)
2. RPGIcon で各種小項目ごとの prompts を追加。できるだけ多くのパターンの画像を生成できるよう、最適なプロンプトを設計し作成する
    - /promps/illustration/rpg_icon/weapon   # 武器・防具
    - /promps/illustration/rpg_icon/monster  # モンスター
    - /promps/illustration/rpg_icon/other    # その他
3. ステップ2で作成したプロンプトを使用して、実際に各小項目ごとに画像を生成できるようにする


それではステップ1からお願いします

