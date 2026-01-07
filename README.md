# Split with Planes - Fusion 360 Add-in

Fusion 360用のボディ分割アドインです。2点間を指定した分割数で等間隔に分割します。

## 機能

- 複数のボディを一度に分割
- スタート/エンド点で方向と距離を指定
- 分割数を自由に設定（1〜100）
- Construction Planesを自動作成・自動削除

## 使い方

### 1. アドインを起動
- Fusion 360を開く
- `Shift+S` → "Rhino-Contour" → **Run**

### 2. コマンドを実行
- ツールバーの **"Split with Planes"** ボタンをクリック

### 3. パラメータ設定

| パラメータ | 説明 |
|-----------|------|
| **Bodies** | 分割したいボディを選択（複数可） |
| **Start Point** | 開始点（頂点・スケッチ点・構成点） |
| **End Point** | 終了点（頂点・スケッチ点・構成点） |
| **Number of Divisions** | 分割数（デフォルト: 5） |

### 4. 実行
- **OK** をクリック
- ボディが指定した数に分割されます

## 使用例

### 立方体を5分割
1. 立方体を作成
2. Bodies: 立方体を選択
3. Start Point: 底面の頂点
4. End Point: 上面の頂点（真上）
5. Number of Divisions: 5
6. OK → 5つのボディに分割

```
分割前:           分割後:
┌─────────┐      ┌─────────┐
│         │      ├─────────┤
│         │  →   ├─────────┤
│         │      ├─────────┤
│         │      ├─────────┤
└─────────┘      └─────────┘
```

## 制限事項

- 方向はX/Y/Z軸に平行である必要があります
- 斜め方向の分割は現在サポートされていません

## インストール場所

```
/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/
```

## ファイル構成

```
Rhino-Contour/
├── Rhino-Contour.py      # エントリーポイント
├── config.py             # 設定（DEBUG=True/False）
├── commands/
│   └── contour/
│       └── entry.py      # メイン実装
└── lib/
    └── fusionAddInUtils/ # ユーティリティ
```

## トラブルシューティング

### ボタンが表示されない
- アドインを Stop → Run で再起動

### エラーが発生する
- Text Commands ウィンドウでログを確認
- `config.py` で `DEBUG = True` に設定

### 分割されない
- Start/End点がX/Y/Z軸に平行か確認
- ボディが平面と交差しているか確認

## ライセンス

Autodesk Fusion 360 Add-in テンプレートベース
