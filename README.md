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

## インストール手順

### 本プロジェクト実行に必要なインストール手順

1. Pythonをインストールする
    - Python 3.10.6 で動作確認済み
2. Python 仮想環境の作成
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
3. 仮想環境にて以下のコマンドでライブラリをインストールする
    ```
    # pip を最新版に更新
    python -m pip install --upgrade pip

    # 必要なモジュールをインストール
    (venv) PS C:\GitHub\AutoImageGenerator> poetry install
    ```

### 本プロジェクトから呼び出す Stable Diffusion WEB UI 実行に必要なインストール手順

- [Docker で Stable Diffusion web UI をセットアップする](https://zenn.dev/st_little/articles/setup-stable-diffusion-web-ui-in-docker)を参考にインストール
- Docker Desktop がインストールされていない場合は先にインストールしてください
    - [Windows 11にDocker Desktopを入れる手順（令和5年最新版） #DockerDesktop - Qiita](https://qiita.com/zembutsu/items/a98f6f25ef47c04893b3)

### 必要な画像生成AIモデルのインストール手順

1. 以下から Brav6 および Brav7 のモデルをダウンロード
    - [Beautiful Realistic Asians - v7 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/25494/brabeautiful-realistic-asians-v2)
2. Stable Diffusion Web UI Docker のインストールフォルダ以下にある `data\models\Stable-diffusion` フォルダ内にダウンロードしたモデルファイルを配置
    - 例: `C:\Users\k.hongou\Dev\stable-diffusion-webui-docker\data\models\Stable-diffusion`
        - Brav6.safetensors
        - beautifulRealistic_v7.safetensors