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
2. 実行環境のパスへ移動
    ```
    cd .\autoimagegenerator\
    ```
3. `poetry run python main.py` でファイルを実行する
4. `./AutoImageGenerator/images/output` 以下に画像が生成されることを確認

## main.py 起動オプション詳細

`main.py` は以下のコマンドライン引数をサポートしています。これらの引数を使用することで、画像生成の動作をカスタマイズできます。

1. **モデルチェックポイント**: 
   - **引数**: `arg_sd_model`
   - **説明**: 使用するモデルのチェックポイントを指定します。
   - **オプション**:
     - `brav6`: デフォルトのモデル。
     - `brav7`: バージョン7のモデル。
     - `brav7_men`: バージョン7の男性用モデル。

   - **使用例**: 
     ```bash
     python main.py brav7
     ```

2. **透明背景**:
   - **引数**: `is_transparent_background`
   - **説明**: 生成される画像の背景を透明にするかどうかを指定します。
   - **オプション**: `true` または `false`（デフォルト）
   - **使用例**: 
     ```bash
     python main.py brav6 true
     ```

3. **セルフィー**:
   - **引数**: `is_selfie`
   - **説明**: セルフィー画像を生成するかどうかを指定します。
   - **オプション**: `true` または `false`（デフォルト）
   - **使用例**: 
     ```bash
     python main.py brav6 false true
     ```

### 使用例

以下は、`brav7` モデルを使用し、透明背景でセルフィー画像を生成する例です。

```bash
python main.py brav7 true true
```

このコマンドは、`beautifulRealistic_v7.safetensors` モデルを使用し、透明な背景のセルフィー画像を生成します。


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

## トラブルシューティング

### stable diffusion API へのアクセスでエラーが出た場合の対策

- https://www.perplexity.ai/search/rokarupcnili-teta-stable-diffu-hZOzmrOKQTaxnE..nr35eA#1