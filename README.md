# AutoImageGenerator

## 概要

本プロジェクトは、Python から Stable Diffusion の API を呼び出して、画像生成を自動で行うためのシステムです。

## 機能

- 指定フォルダ(autoimagegenerator/prompts)以下にある各フォルダ内に各種プロンプトを記載し、そこからランダムに抽出して生成する画像を指定できます
- 画像生成に使用するモデルを起動時のパラメータで指定可能(現状Brav6(女性), Brav7(女性)およびBrav7(男性)が指定可能)
    - [Beautiful Realistic Asians - v7 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/25494/brabeautiful-realistic-asians-v2)からダウンロード可能
- 男性 or 女性およびそれぞれ透過写真、セルフィー写真を起動時のパラメータで指定して生成可能

## 使用方法
1. 下記 インストール手順 に従って諸々セットアップする
2. venv を activate する
    ```
    .\venv\Scripts\activate
    ```
3. 実行環境のパスへ移動
    ```
    cd .\autoimagegenerator\
    ```
4. `poetry run python main.py` でファイルを実行する
5. `./AutoImageGenerator/images/output` 以下に画像が生成されることを確認

## main.py 起動オプション詳細

`main.py` は以下のコマンドライン引数をサポートしています。これらの引数を使用することで、画像生成の動作をカスタマイズできます：

1. **必須の引数**:
   - **--style**: 画像スタイル
     - `realistic`: リアルテイスト画像
     - `illustration`: イラストテイスト画像
   - **--category**: カテゴリー
     - `female`: 女性
     - `male`: 男性
     - `animal`: 動物
     - `background`: 背景（illustrationのみ）
     - `rpg_icon`: RPGアイコン（illustrationのみ）
     - `vehicle`: 乗り物（illustrationのみ）
     - `other`: その他（illustrationのみ）

2. **オプションの引数**:
   - **--subcategory**: サブカテゴリー
     - 人物（female/male）の場合:
       - `normal`: 通常画像
       - `transparent`: 透過背景画像
       - `selfie`: セルフィー画像
     - 動物の場合:
       - `dog`: 犬
       - `cat`: 猫
       - `bird`: 鳥
       - `fish`: 魚
       - `other`: その他
     - その他のカテゴリーについては仕様書を参照
   - **--model**: 使用するモデル（デフォルトはカテゴリーに応じて自動選択）
     - `brav6`: Beautiful Realistic Asians v6
     - `brav7`: Beautiful Realistic Asians v7
     - `rpg_icon`: RPGアイコン用モデル
   - **--enable-hr**: ハイレゾ画像生成の有効/無効
     - `true`: 有効（デフォルト）
     - `false`: 無効

### 使用例

以下は、いくつかの使用例です：

```bash
# リアルテイストの女性の通常画像を生成（brav7モデルを指定）
python main.py --style realistic --category female --subcategory normal --model brav7

# リアルテイストの女性のセルフィー画像を生成（brav6モデルを指定）
python main.py --style realistic --category female --subcategory selfie --model brav6

# リアルテイストの女性の透過背景画像を生成（ハイレゾ無効）
python main.py --style realistic --category female --subcategory transparent --enable-hr false

# イラストテイストのRPGアイコン（武器）を生成
python main.py --style illustration --category rpg_icon --subcategory weapon
```

## 自動テスト機能

AutoImageGeneratorには、異なるパターンでの画像生成を自動的にテストする機能が含まれています。この機能を使用することで、システムが正常に動作しているかを確認できます。

### テスト実行手順

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

### テストオプション

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

### テスト設定のカスタマイズ

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

### テスト結果の確認

テスト実行後、以下の場所にテスト結果が保存されます：

- **テスト結果JSON**: `tests/output/test_results.json`
- **テスト結果HTMLレポート**: `tests/reports/test_report_YYYYMMDD-HHMMSS.html`
- **テストログ**: `test_run.log` および `test_image_generation.log`

HTMLレポートには、各テストパターンの実行結果、実行時間、生成された画像の数などの情報が含まれています。

### テスト出力画像の確認

テストで生成された画像は `tests/output/images` ディレクトリに保存されます。各テストパターンの画像は、スタイル、カテゴリー、サブカテゴリーに基づいたサブディレクトリに整理されています。

例えば、リアルテイストの女性の通常画像のテスト結果は以下のパスに保存されます：
```
tests/output/images/realistic/female/normal/
```

## インストール手順

### Cursor or VSCode で使用する拡張機能をインストール

- VSCode の場合
```
Get-Content extensions.txt | ForEach-Object { code --install-extension $_ }
```

- Cursor の場合
    - extensions.txt を参考に手動でインストールしてください

### 本プロジェクト実行に必要なインストール手順

1. Pythonをインストールする
    - Python 3.10.6 で動作確認済み
2. Poetry をインストールする
    - PoetryはPythonの依存関係管理ツールで、以下の手順でインストールできます。
    1. **Poetryのインストールスクリプトを実行する**
       Poetryの公式インストールスクリプトを使用してインストールします。以下のコマンドをPowerShellまたはコマンドプロンプトで実行してください。

        ```powershell
        (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
        ```

    2. **環境変数の設定**

       インストールが完了したら、Poetryのパスを環境変数に追加する必要があります。通常、Poetryはユーザーディレクトリの下にインストールされます。例えば、`C:\Users\<YourUsername>\AppData\Roaming\Python\Scripts`にインストールされることが多いです。

       環境変数の設定は以下の手順で行います：

        - 「システムのプロパティ」を開く
        - 「環境変数」をクリック
        - 「ユーザー環境変数」または「システム環境変数」で`Path`を選択し、「編集」をクリック
        - Poetryのインストールパスを追加

    3. **Poetryの動作確認**

       コマンドプロンプトまたはPowerShellで以下のコマンドを実行し、Poetryが正しくインストールされているか確認します。

        ```powershell
        poetry --version
        ```

       正しくインストールされていれば、Poetryのバージョンが表示されます。

3. Python 仮想環境の作成
    1. カレントディレクトリにて以下を実行
        ```
        python -m venv venv
        ```
    2. 仮想環境を開始
        ```
        .\venv\Scripts\activate
        # 以下のように表示されていればOK
        (venv) PS C:\GitHub\AutoImageGenerator>
        ```
        - ※エラーが出るようであれば管理者権限で PowerShell を起動し、上記コマンドを実行することで解消される可能性があります
4. 仮想環境にて以下のコマンドでライブラリをインストールする
    ```
    # pip を最新版に更新
    python -m pip install --upgrade pip

    # 必要なモジュールをインストール
    (venv) PS C:\GitHub\AutoImageGenerator> poetry install
    ```

### 設定

#### settings.json

- ./autoimagegenerator/sample.settings.json をコピーして settings.json を作成し以下を設定
    - image_generate_batch_execute_count: 何件の人物について画像を一括作成するか指定
    - another_version_generate_count: 同じ人物につき何件の画像を作成するか指定

### 本プロジェクトから呼び出す Stable Diffusion WEB UI 実行に必要なインストール手順

- [Docker で Stable Diffusion web UI をセットアップする](https://zenn.dev/st_little/articles/setup-stable-diffusion-web-ui-in-docker)を参考にインストール
    - `docker compose --profile auto up --build` 実行時に依存関係エラーが発生した場合は Dockerfile 54行目付近に以下を追加することで正常に完了できる可能性があります
        - `RUN pip install --upgrade typing_extensions`
- Docker Desktop がインストールされていない場合は先にインストールしてください
    - [Windows 11にDocker Desktopを入れる手順（令和5年最新版） #DockerDesktop - Qiita](https://qiita.com/zembutsu/items/a98f6f25ef47c04893b3)

#### 4x-UltraSharpのインストール

1. ダウンロード:
   Hugging Faceのウェブサイト (https://huggingface.co/lokCX/4x-Ultrasharp) にアクセスし、「Files and versions」をクリックします。「4x-UltraSharp.pth」ファイルをダウンロード

2. ファイルの配置:
   ダウンロードした「4x-UltraSharp.pth」ファイルを、Stable Diffusion WebUIのインストールディレクトリ内の「models/ESRGAN/」フォルダに配置
    - フォルダがなければ作成して配置

3. WebUIの再起動:
   Stable Diffusion WebUIを再起動して、新しいアップスケーラーを読み込ませます


### 必要な画像生成AIモデルのインストール手順

1. 以下から Brav6 および Brav7 のモデルをダウンロード
    - [Beautiful Realistic Asians - v7 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/25494/brabeautiful-realistic-asians-v2)
2. Stable Diffusion Web UI Docker のインストールフォルダ以下にある `data\models\Stable-diffusion` フォルダ内にダウンロードしたモデルファイルを配置
    - 例: `C:\Users\k.hongou\Dev\stable-diffusion-webui-docker\data\models\Stable-diffusion`
        - beautifulRealistic_v60.safetensors
        - beautifulRealistic_v7.safetensors

### 背景透過写真を生成するために必要なモジュールのインストール

- 以下を参考にインストールしてください
    - https://www.perplexity.ai/search/stable-diffusion-web-ui-he-abg-bVWNoK55SCiEBdeBtUzk8w#0

## トラブルシューティング

### stable diffusion API へのアクセスでエラーが出た場合の対策

- https://www.perplexity.ai/search/rokarupcnili-teta-stable-diffu-hZOzmrOKQTaxnE..nr35eA#1





# AutoImageGenerator プロンプト設定ファイル仕様書

## 1. フォルダ構成

```
autoimagegenerator/prompts/
├── [style]/
│   ├── [category]/
│   │   ├── [subcategory]/（必要に応じてサブカテゴリ以下に各プロンプト設定ファイルを配置）
│   │   ├── positive_base.json
│   │   ├── positive_optional.json
│   │   ├── positive_pose.json
│   │   ├── positive_selfie.json
│   │   ├── negative.json
│   │   ├── cancel_seeds.json
│   │   └── positive_cancel_pair.json
```

- **style**: 画像スタイル（例: realistic, illustration）
- **category**: カテゴリー（例: female, male, animal）
- **subcategory**: サブカテゴリー（必要に応じて）

## 2. プロンプト設定ファイルの基本構造

すべてのプロンプト設定ファイルは以下の基本構造に従います：

```json
{
  "プロンプト分類名": {
    "prompts": [
      "プロンプト1",
      "プロンプト2",
      "プロンプト3",
      ...
    ],
    "use_max_prompts": 数値,
    "use_min_prompts": 数値
  },
  "別のプロンプト分類名": {
    ...
  }
}
```

- **プロンプト分類名**: 任意の名前（例: "Base Positive Prompt", "Hair Type"）
- **prompts**: 選択対象となるプロンプトの配列
- **use_max_prompts**: 最大選択数（この分類から最大何個のプロンプトを選ぶか）
- **use_min_prompts**: 最小選択数（この分類から最低何個のプロンプトを選ぶか）

### 選択ルール例

- `"use_max_prompts": 1, "use_min_prompts": 1` → 必ず1つだけ選択
- `"use_max_prompts": 2, "use_min_prompts": 0` → 0〜2個をランダムに選択
- `"use_max_prompts": 0, "use_min_prompts": 0` → 選択しない（オプション）

## 3. 各プロンプト設定ファイルの役割

### 3.1 positive_base.json

基本となるプロンプト設定。同一人物の異なるバージョンを生成する際も、このプロンプトは固定されます。
同じ seed でかつ同じベースプロンプトを指定しつつ、後述の `positive_optional.json` や `positive_pose.json` で服装やポーズのプロンプトを指定することで、同じ人物の異なる服装・ポーズの画像を生成します。

**主な分類例**:
- **Base Positive Prompt**: 基本的な画質や人物の指定
- **Women/Men Type**: 人物タイプ（アイドル、モデルなど）
- **Body Type**: 体型の指定
- **Hair Type**: 髪型の指定
- **Hair Color**: 髪の色の指定

```json
{
  "Base Positive Prompt": {
    "prompts": ["(8k, RAW photo, best quality, masterpiece:1.2), (1girl:1.3), (looking at viewer:1.4)"],
    "use_max_prompts": 1,
    "use_min_prompts": 1
  },
      "Women Type": {
        "prompts": [
          "Famous Japanese Male Idols",
          "japanese cool men",
          "japanese men",
          "Male Athletes in Japan",
          "Japanese male fashion models",
          "Famous Korean Male Idols",
          "Korean cool men",
          "Korean men",
          "Male Athletes in Korean",
          "Korean male fashion models"
        ],
        "use max prompts": 1,
        "use min prompts": 1
      }
    }
  ...
}
```

### 3.2 positive_optional.json

オプション的なプロンプト設定。服装、アクセサリー、場所、構図などを指定します。

**主な分類例**:
- **Cloth**: 服装（ドレス、Tシャツなど）
- **Accessory**: アクセサリー（ネックレス、イヤリングなど）
- **Place**: 場所（部屋、ビーチなど）
- **composition**: 構図（顔アップ、上半身など）

### 3.3 positive_pose.json

ポーズや表情に関するプロンプト設定。

**主な分類例**:
- **pose**: 体のポーズ（座る、立つなど）
- **Face**: 表情（笑顔、真顔など）

### 3.4 positive_selfie.json

自撮り写真用のポーズ設定。`subcategory`が`selfie`の場合に`positive_pose.json`の代わりに使用されます。

**主な分類例**:
- **pose**: 自撮りポーズ（右手でセルフィー、両手でセルフィーなど）
- **Face**: 表情（笑顔など）

### 3.5 negative.json

生成したくない要素を指定するプロンプト。すべての画像生成に適用されます。

```json
{
  "Base Negative Prompt": {
    "prompts": ["((3hands, 3arms, 3legs:1.2, 4 fingers:1.4)), (nsfw:1.3), (worst quality:2)"],
    "use_max_prompts": 1,
    "use_min_prompts": 1
  }
}
```

### 3.6 cancel_seeds.json

使用したくないseed値のリスト。これらのseed値は画像生成に使用されません。
過去に画像生成した際に seed 値によっては望ましくない画像が生成されることがあり、二度とその seed 値を使用して画像を生成しないように指定する seed 値を設定するためのファイル。

```json
{
  "Seeds": ["1893787056", "237044424"]
}
```

### 3.7 positive_cancel_pair.json

相性の悪いプロンプトの組み合わせを指定します。キーとなるプロンプトが選択された場合、配列内のプロンプトは削除されます。

```json
{
  "bikini": [
    "bed room",
    "street",
    "Park"
  ],
  "dress": [
    "woman with left hand in pockets"
  ]
}
```

例: "bikini"が選択された場合、"bed room"、"street"、"Park"は削除されます（ビキニ姿で街中にいる不自然な画像を防ぐため）。

## 4. プロンプト設定のテクニック

### 4.1 出現頻度の調整

同じプロンプトを複数回リストに追加することで、選択される確率を高めることができます。

```json
"Hair Color": {
  "prompts": [
    "Dark brown hair",
    "Dark brown hair",  // 複数回追加して選択確率を上げる
    "Dark brown hair",
    "black hair",
    "blonde hair"
  ],
  "use_max_prompts": 1,
  "use_min_prompts": 1
}
```

### 4.2 プロンプトの重み付け

プロンプト内で`:1.2`のような表記を使用して、特定の要素の重みを調整できます。

```
"(8k, RAW photo, best quality, masterpiece:1.2), (1girl:1.3), (looking at viewer:1.4)"
```

- `masterpiece:1.2` → masterpiece の重みを1.2倍に
- `1girl:1.3` → 1girl の重みを1.3倍に

## 5. 使用例

リアルな女性の画像を生成する場合：

1. `positive_base.json`から基本的な人物設定（髪型、髪色など）を選択
2. `positive_optional.json`から服装、場所、構図などを選択
3. `positive_pose.json`または`positive_selfie.json`からポーズと表情を選択
4. `negative.json`から除外要素を適用
5. `positive_cancel_pair.json`を参照して不適切な組み合わせを除外
6. `cancel_seeds.json`を参照して使用しないseed値を除外

これらの設定を組み合わせることで、多様でありながらも自然な画像生成が可能になります。
