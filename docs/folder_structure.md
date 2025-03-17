# 生成画像フォルダ仕様

このドキュメントでは、AutoImageGeneratorが生成する画像のフォルダ構造について説明します。

## 生成時に動的に作成されるフォルダ

画像生成時には大項目・中項目・小項目に応じたフォルダの下に、作成日時と生成された画像の Seed 値を含むフォルダが作成されます。

例）
```
autoimagegenerator/images/output/realistic/female/normal/20250221-12-2934224203/
```

フォルダ名の形式は以下の通りです：
- `YYYYMMDD-HH-SEEDVALUE`
  - `YYYYMMDD`: 年月日
  - `HH`: 時間
  - `SEEDVALUE`: 生成に使用されたSeed値

## サブフォルダ構造

生成時に動的に作成されるフォルダ内には以下のサブフォルダが作成され、それぞれの仕様に応じた画像が保存されます。

```
/thumbnail          # サムネイル画像
/sample             # サンプル画像（透かし入り）
/sample-thumbnail   # サンプルサムネイル画像（透かし入り）
/half-resolution    # 半分の解像度の画像
```

### サブフォルダの役割

- **thumbnail**: 元画像のサムネイル版（小さいサイズ）
- **sample**: 透かし入りのサンプル画像（配布用）
- **sample-thumbnail**: 透かし入りのサンプル画像のサムネイル版
- **half-resolution**: 元画像の半分の解像度の画像（軽量版）

## 出力ディレクトリ構造の例

以下は、実際の出力ディレクトリ構造の例です：

```
autoimagegenerator/images/output/
├── realistic/
│   ├── female/
│   │   ├── normal/
│   │   │   ├── 20250221-12-2934224203/
│   │   │   │   ├── 00001.png                # 元画像
│   │   │   │   ├── thumbnail/
│   │   │   │   │   └── 00001.png            # サムネイル画像
│   │   │   │   ├── sample/
│   │   │   │   │   └── 00001.png            # サンプル画像（透かし入り）
│   │   │   │   ├── sample-thumbnail/
│   │   │   │   │   └── 00001.png            # サンプルサムネイル画像
│   │   │   │   └── half-resolution/
│   │   │   │       └── 00001.png            # 半分の解像度の画像
│   │   │   └── 20250221-13-3847583921/
│   │   │       └── ...
│   │   ├── selfie/
│   │   │   └── ...
│   │   └── transparent/
│   │       └── ...
│   └── male/
│       └── ...
└── illustration/
    └── ...
```