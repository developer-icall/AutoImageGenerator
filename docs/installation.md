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
2. 以下から追加モデルをダウンロード
    - [Photo Real V1.5 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/97373/photo-real-v15)
    - [Awesome RPG Icon 2000 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/14483/awesome-rpg-icon-2000)
    - [Animagine XL 4.0 | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/1188071/animagine-xl-40)
    - [YayoiMix | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/83096/yayoimix)
    - [Pet Photography Album of Animals | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/267871/pet-photography-album-of-animals-cats-and-dogs)
    - [Stable Diffusion XL Base 1.0 | Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/sd_xl_base_1.0.safetensors)
    - [Landscape Realistic | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/85137?modelVersionId=148587)
    - [Kawaii Realistic Anime Mix | Stable Diffusion Checkpoint | Civitai](https://civitai.com/models/104100/kawaii-realistic-anime-mix)
3. Stable Diffusion Web UI Docker のインストールフォルダ以下にある `data\models\Stable-diffusion` フォルダ内にダウンロードしたモデルファイルを配置
    - 例: `C:\Users\k.hongou\Dev\stable-diffusion-webui-docker\data\models\Stable-diffusion`
        - beautifulRealistic_v60.safetensors
        - beautifulRealistic_v7.safetensors
        - photoRealV15_photorealv21.safetensors
        - RPGIcon.safetensors
        - animagineXL40_v4Opt.safetensors
        - yayoiMix_v25.safetensors
        - petPhotographyAlbumOf_v10HomeEdition.safetensors
        - sd_xl_base_1.0.safetensors
        - landscapeRealistic_v20WarmColor.safetensors
        - kawaiiRealisticAnime_a06.safetensors

### 必要なLoRAのインストール

1. 以下からLoRAモデルをダウンロード
    - [JDM Cars XL | LoRA | Civitai](https://civitai.com/models/257037/jdm-cars-xl)
    - [Kawasaki Ninja 300 | LoRA | Civitai](https://civitai.com/models/183116/kawasaki-ninja-300)
    - [Waifu on Motorcycle | LoRA | Civitai](https://civitai.com/models/24864/waifu-on-motorcycle)
    - [Cyberpunk Vehicles | LoRA | Civitai](https://civitai.com/models/116165/cyberpunk-vehicles)
2. Stable Diffusion Web UI Docker のインストールフォルダ以下にある `data\models\Lora` フォルダ内にダウンロードしたLoRAファイルを配置
    - 例: `C:\Users\k.hongou\Dev\stable-diffusion-webui-docker\data\models\Lora`
        - cars-000008.safetensors
        - KawasakiNinja300.safetensors
        - waifu_on_Motorcycle_v2.safetensors
        - cybervehiclev4.safetensors

### 背景透過写真を生成するために必要なモジュールのインストール

- 以下を参考にインストールしてください
    - https://www.perplexity.ai/search/stable-diffusion-web-ui-he-abg-bVWNoK55SCiEBdeBtUzk8w#0

## 必要な拡張機能のインストール

### Additional Networks（LoRA使用時に必要）

1. Stable Diffusion Web UIを起動します

2. 「Extensions」タブを開きます

3. 「Install from URL」タブを開きます

4. 以下のURLを入力して「Install」ボタンをクリックします：
    ```
    https://github.com/kohya-ss/sd-webui-additional-networks
    ```

5. インストール完了後、Web UIを再起動して拡張機能を有効化します

6. 「Settings」タブで以下の設定を確認します：
   - 「Additional Networks」セクションが存在すること
   - 「Enable」がチェックされていること

7. 「Additional Networks」タブが表示されていることを確認します
   - タブが表示されない場合は、Web UIを再度再起動してください

### トラブルシューティング

LoRA使用時に「Script 'Additional Networks for Generating' not found」エラーが発生した場合：
1. Web UIが正常に起動していることを確認
2. 「Extensions」タブで「Additional Networks」が正しくインストールされていることを確認
3. Web UIを再起動して拡張機能を再読み込み
4. 問題が解決しない場合は、拡張機能を一度アンインストールして再インストール