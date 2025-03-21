# バイク画像生成機能

このドキュメントでは、AutoImageGeneratorのバイク画像生成機能について説明します。

## 概要

バイク画像生成機能は、以下の3つのスタイルでバイク画像を生成できます：

1. リアル調のバイク画像（KawasakiNinja300 LoRA）
2. イラスト調のバイク画像（waifu_on_Motorcycle_v2 LoRA）
3. サイバーパンク調のバイク画像（cybervehiclev4 LoRA）

## 使用可能なLoRA

### KawasakiNinja300
- 用途：リアルなバイク画像の生成
- 推奨重み：0.7-0.9
- 主なキーワード：
  - `sitting on bike`
  - `on motorcycle`
  - `standing in front of motorcycle`
  - `vehicle focus`
- バイクウェア関連キーワード：
  - `gloves`
  - `helmet`
  - `motorcycle helmet`
  - `biker clothes`
- アングル指定：
  - `front view`
  - `side view`
  - `back view`

### waifu_on_Motorcycle_v2
- 用途：イラスト調のバイク画像生成
- 特徴：2D、2.5Dスタイルに適合
- 推奨画像サイズ：512x768
- 適用範囲：全身および上半身のイラスト

### cybervehiclev4
- 用途：サイバーパンク調のバイク画像生成
- 使用可能なキーワード：
  - `motorcycle`
  - `sports car`
  - `police style`
  - `luxury sedan`
  - `military style`

## プロンプト設定

### ベースプロンプト（positive_base.json）
- バイクの種類（Vehicle Type）
- スタイル（Style）
- 詳細（Details）
- ライダー（Rider）
- ライダーギア（Rider Gear）

### ポーズプロンプト（positive_pose.json）
- ポーズ（Pose）
- アングル（Angle）
- 構図（Composition）
- カメラ設定（Camera Settings）

### オプショナルプロンプト（positive_optional.json）
- 色（Color）
- 環境（Environment）
- 照明（Lighting）
- 時間帯（Time of Day）
- 天候（Weather）
- 車両詳細（Vehicle Details）
- ライダーポーズ（Rider Pose）
- シーン（Scene）

### ネガティブプロンプト（negative.json）
- 品質関連の除外
- 不要な要素の除外
- スタイル関連の除外

## 使用例

### リアル調のバイク画像生成
```bash
python main.py --style realistic --category vehicle --subcategory motorcycle --use-lora --lora-name KawasakiNinja300
```

### イラスト調のバイク画像生成
```bash
python main.py --style illustration --category vehicle --subcategory motorcycle --use-lora --lora-name waifu_on_Motorcycle_v2
```

### サイバーパンク調のバイク画像生成
```bash
python main.py --style realistic --category vehicle --subcategory motorcycle --use-lora --lora-name cybervehiclev4
```

### プロンプトのみを確認（ドライラン）
```bash
python main.py --style realistic --category vehicle --subcategory motorcycle --use-lora --lora-name KawasakiNinja300 --dry-run
```

## 画像サイズ設定

バイク画像生成では、以下のデフォルト画像サイズが設定されています：

- 幅：768ピクセル
- 高さ：512ピクセル

この設定は`settings.json`で変更可能です：

```json
{
  "default_image_sizes": {
    "realistic": {
      "vehicle": {
        "width": 768,
        "height": 512
      }
    },
    "illustration": {
      "vehicle": {
        "width": 768,
        "height": 512
      }
    }
  }
}
```

## 注意事項

1. ライダーが写っている場合、フルフェイスヘルメットを着用させ、顔が見えないようにプロンプトで調整しています。
2. バイク単体の画像生成も可能です。
3. 各LoRAの特性に応じて、適切なプロンプトを自動的に選択します。
4. イラスト調の場合は、アニメやマンガ調の要素が自動的に追加されます。
5. リアル調の場合は、写実的な要素が自動的に追加されます。