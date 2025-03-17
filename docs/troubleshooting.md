# トラブルシューティング

このドキュメントでは、AutoImageGeneratorの使用中に発生する可能性のある問題と、その解決方法について説明します。

## Stable Diffusion API へのアクセスでエラーが出た場合

### 症状
- API接続エラーが発生する
- 「Connection refused」などのエラーメッセージが表示される

### 解決策
1. Stable Diffusion Web UIが正常に起動しているか確認してください
2. APIが有効になっているか確認してください
   - Web UIの「Settings」タブ→「API」セクションで「Enable API」がオンになっていることを確認
3. ファイアウォールの設定を確認してください
   - ポート7860が開放されているか確認
4. 詳細な情報は以下のリンクを参照してください
   - https://www.perplexity.ai/search/rokarupcnili-teta-stable-diffu-hZOzmrOKQTaxnE..nr35eA#1

## 画像生成が遅い場合

### 症状
- 画像生成に非常に時間がかかる
- プログラムが応答しなくなる

### 解決策
1. ハイレゾ生成を無効にしてみてください
   ```
   python main.py --style realistic --category female --subcategory normal --enable-hr false
   ```
2. GPUのリソースを確認してください
   - 他のアプリケーションがGPUリソースを消費していないか確認
3. Stable Diffusion Web UIの設定を調整してください
   - サンプリングステップ数を減らす
   - バッチサイズを小さくする

## モデルが見つからないエラー

### 症状
- 「Model not found」などのエラーメッセージが表示される

### 解決策
1. モデルファイルが正しい場所に配置されているか確認してください
   - `data\models\Stable-diffusion` フォルダ内に以下のファイルがあるか確認
     - beautifulRealistic_v60.safetensors
     - beautifulRealistic_v7.safetensors
2. モデル名が正しく指定されているか確認してください
   - コマンドラインオプションで指定したモデル名とStable Diffusion Web UIで認識されているモデル名が一致しているか確認

## 透過背景画像生成に関する問題

### 症状
- 透過背景が正しく生成されない
- 背景が透過されずに残る

### 解決策
1. 必要なモジュールがインストールされているか確認してください
   - 以下のリンクを参照してインストールを確認
     - https://www.perplexity.ai/search/stable-diffusion-web-ui-he-abg-bVWNoK55SCiEBdeBtUzk8w#0
2. プロンプト設定を確認してください
   - negative.jsonに背景を除外するプロンプトが含まれているか確認

## その他の問題

上記に該当しない問題が発生した場合は、以下の手順で対応してください：

1. ログファイルを確認する
   - `autoimagegenerator/logs` ディレクトリ内のログファイルを確認
2. Stable Diffusion Web UIのログを確認する
   - Dockerコンテナのログを確認
3. 設定ファイルを確認する
   - `settings.json` の内容が正しいか確認
4. 最新バージョンを使用しているか確認する
   - リポジトリから最新のコードを取得