仕様変更があるので実装お願いします

# 仕様
- 生成する画像タイプを指定するオプションについて以下仕様を追加および変更
    - 大項目として以下の2つを用意
        - リアルテイスト画像
        - ゲーム、イラスト風画像
    - 各大項目の中には以下の中・小項目を用意
        - リアルテイスト画像
            - 女性(モデルは brav6 または brav7を使用)
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 男性(モデルは brav6 または brav7を使用)
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 動物(モデルは未確定、今後モデルを選定し追加予定。小項目ごとにモデルを指定できるようにする)
                - 犬
                - 猫
                - 鳥
                - 魚
                - その他
        - ゲーム、イラスト風画像
            - 女性(モデルは未確定、今後モデルを選定し追加予定。複数のモデルを指定できるようにする)
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 男性(モデルは未確定、今後モデルを選定し追加予定。複数のモデルを指定できるようにする)
                - 通常画像
                - 透明背景画像
                - セルフィー画像
            - 動物(モデルは未確定、今後モデルを選定し追加予定。小項目ごとにモデルを指定できるようにする)
                - 犬
                - 猫
                - 鳥
                - 魚
                - その他
            - 背景(モデルは未確定、今後モデルを選定し追加予定)
                - 自然
                - 都市
                - 海
                - 空
                - その他
            - RPGアイコン(モデルは RPGIcon を使用)
                - 武器・防具
                - モンスター
                - その他
            - 乗り物(モデルは未確定、今後モデルを選定し追加予定)
                - 車
                - 船
                - 飛行機
                - その他
            - その他(モデルは未確定、今後モデルを選定し追加予定)

- 生成する画像タイプを指定する main.py のオプションを追加
- 各画像タイプに応じた prompts 以下のフォルダを追加および既存プロンプトの整理
    - @prompts

# 画像フォルダ構造パターン

## 大項目（スタイル）
/images/output/realistic      # リアルテイスト
/images/output/illustration   # イラストテイスト

## 中項目（カテゴリー）
/images/output/<style>/female      # 女性
/images/output/<style>/male        # 男性
/images/output/<style>/animal      # 動物
/images/output/<style>/background  # 背景
/images/output/<style>/rpg_icon    # RPGアイコン
/images/output/<style>/vehicle     # 乗り物

## 小項目（サブカテゴリー）
### 人物（female, male）
/images/output/<style>/<category>/normal      # 通常
/images/output/<style>/<category>/transparent # 透過
/images/output/<style>/<category>/selfie      # セルフィー

### 動物（animal）
/images/output/<style>/animal/dog    # 犬
/images/output/<style>/animal/cat    # 猫
/images/output/<style>/animal/bird   # 鳥
/images/output/<style>/animal/fish   # 魚
/images/output/<style>/animal/other  # その他

### 背景（background）
/images/output/<style>/background/nature  # 自然
/images/output/<style>/background/city    # 都市
/images/output/<style>/background/sea     # 海
/images/output/<style>/background/sky     # 空
/images/output/<style>/background/other   # その他

### RPGアイコン（rpg_icon）
/images/output/<style>/rpg_icon/weapon   # 武器・防具
/images/output/<style>/rpg_icon/monster  # モンスター
/images/output/<style>/rpg_icon/other    # その他

### 乗り物（vehicle）
/images/output/<style>/vehicle/car       # 車
/images/output/<style>/vehicle/ship      # 船
/images/output/<style>/vehicle/airplane  # 飛行機
/images/output/<style>/vehicle/other     # その他

## サムネイル・サンプル画像
各フォルダ内に以下のサブフォルダを配置：
/thumbnail           # サムネイル画像
/sample             # サンプル画像（透かし入り）
/sample-thumbnail   # サンプルサムネイル画像（透かし入り）
/half-resolution    # 半分の解像度の画像

注意：<style>には 'realistic' または 'illustration' が入ります

# 関連ファイル
@main.py @auto_image_generator.py @settings.json

# 関連フォルダ
@prompts

---
以下のステップで進みたいですが、各ステップ毎に動作確認ができる状態で実装を進めてください
1. main.py の起動オプションを追加
2. 生成する画像タイプに応じた prompts を追加
3. 生成する画像タイプに応じた画像保存先フォルダを追加
4. 生成する画像タイプに応じたモデルおよび prompts を使用して画像を生成する処理の実装
5. 生成した画像を画像タイプに応じた保存先フォルダに保存する処理の実装
6. 生成した画像をサムネイル・サンプル画像として画像タイプに応じた保存先フォルダ以下に保存する処理の実装
7. 生成した画像を半分の解像度の画像として画像タイプに応じた保存先フォルダ以下に保存する処理の実装
8. 新しい仕様を @readme.md に反映

それではステップ1からお願いします

