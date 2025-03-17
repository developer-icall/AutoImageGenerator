# インストール手順

このドキュメントでは、AutoImageGeneratorのインストール方法について説明します。

## 開発環境のセットアップ

### Cursor または VSCode で使用する拡張機能をインストール

- VSCode の場合
```
Get-Content extensions.txt | ForEach-Object { code --install-extension $_ }
```

- Cursor の場合
    - extensions.txt を参考に手動でインストールしてください

## 本プロジェクト実行に必要なインストール手順

### 1. Pythonのインストール
- Python 3.10.6 で動作確認済み

### 2. Poetry のインストール
PoetryはPythonの依存関係管理ツールで、以下の手順でインストールできます。

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

### 3. Python 仮想環境の作成

1. カレントディレクトリにて以下を実行
    ```
    python -m venv .venv
    ```
2. 仮想環境を開始
    ```
    .\.venv\Scripts\activate
    # 以下のように表示されていればOK
    (.venv) PS C:\GitHub\AutoImageGenerator>
    ```
    - ※エラーが出るようであれば管理者権限で PowerShell を起動し、上記コマンドを実行することで解消される可能性があります

### 4. 必要なライブラリのインストール

仮想環境にて以下のコマンドでライブラリをインストールします。

```
# pip を最新版に更新
python -m pip install --upgrade pip

# 必要なモジュールをインストール
(.venv) PS C:\GitHub\AutoImageGenerator> poetry install
```

## Stable Diffusion Web UI のセットアップ

### Stable Diffusion Web UI のインストール

- [Docker で Stable Diffusion web UI をセットアップする](https://zenn.dev/st_little/articles/setup-stable-diffusion-web-ui-in-docker)を参考にインストール
    - `docker compose --profile auto up --build` 実行時に依存関係エラーが発生した場合は Dockerfile 54行目付近に以下を追加することで正常に完了できる可能性があります
        - `RUN pip install --upgrade typing_extensions`
- Docker Desktop がインストールされていない場合は先にインストールしてください
    - [Windows 11にDocker Desktopを入れる手順（令和5年最新版） #DockerDesktop - Qiita](https://qiita.com/zembutsu/items/a98f6f25ef47c04893b3)

### 4x-UltraSharpのインストール

1. ダウンロード:
   Hugging Faceのウェブサイト (https://huggingface.co/lokCX/4x-Ultrasharp) にアクセスし、「Files and versions」をクリックします。「4x-UltraSharp.pth」ファイルをダウンロード

2. ファイルの配置:
   ダウンロードした「4x-UltraSharp.pth」ファイルを、Stable Diffusion WebUIのインストールディレクトリ内の「models/ESRGAN/」フォルダに配置
    - フォルダがなければ作成して配置

3. WebUIの再起動:
   Stable Diffusion WebUIを再起動して、新しいアップスケーラーを読み込ませます

### 必要な画像生成AIモデルのインストール

1. 以下から Brav6 および Brav7 のモデルをダウンロード
    - [Beautiful Realistic Asians - v7 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/25494/brabeautiful-realistic-asians-v2)
2. Stable Diffusion Web UI Docker のインストールフォルダ以下にある `data\models\Stable-diffusion` フォルダ内にダウンロードしたモデルファイルを配置
    - 例: `C:\Users\k.hongou\Dev\stable-diffusion-webui-docker\data\models\Stable-diffusion`
        - beautifulRealistic_v60.safetensors
        - beautifulRealistic_v7.safetensors

### 背景透過写真を生成するために必要なモジュールのインストール

- 以下を参考にインストールしてください
    - https://www.perplexity.ai/search/stable-diffusion-web-ui-he-abg-bVWNoK55SCiEBdeBtUzk8w#0