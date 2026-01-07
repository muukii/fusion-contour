# Rhino-Contour Add-in for Fusion 360

Fusion 360用のRhinoスタイルのContour（輪郭線）機能を提供するアドインです。

## 概要

このアドインは、選択したボディに対して平行な平面群との交線を作成し、等高線のような輪郭線を生成します。Rhinocerosの`Contour`コマンドと同様の機能を提供します。

## 機能

- **複数ボディ対応**: 複数のボディを同時に選択して輪郭線を作成
- **柔軟な方向指定**: エッジ、面の法線、構成軸（X/Y/Z）から方向を選択
- **カスタマイズ可能な間隔**: 任意の距離で輪郭線を生成
- **自動範囲計算**: ボディの範囲を自動的に計算して最適な輪郭線を生成

## インストール

このアドインは以下の場所にインストールされています：

```
/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/
```

## 使用方法

### 1. アドインの起動

1. Fusion 360を開く
2. **ユーティリティ → Add-Ins** をクリック（またはShift+S）
3. "My Add-Ins" タブを選択
4. "Rhino-Contour" を選択
5. **Run** をクリック

### 2. Contourコマンドの実行

1. ツールバーの **Scripts and Add-Ins** パネルから **Rhino Contour** ボタンをクリック

2. ダイアログで以下のパラメータを設定：

   - **Bodies**: 輪郭線を作成したいボディを選択（複数選択可）
   - **Base Point**: 輪郭線を生成する平面群の基準点
     - 頂点
     - スケッチ点
     - 構成点
   - **Direction**: 輪郭線を生成する平面の法線方向
     - 直線エッジ
     - 平面の法線
     - 構成軸（X/Y/Z軸など）
   - **Distance**: 輪郭線の間隔（例：10mm）

3. **OK** をクリックして実行

### 3. 結果

- すべての輪郭線が1つのスケッチ（"Contours"という名前）に作成されます
- 作成された曲線の数がメッセージボックスに表示されます

## 使用例

### 例1: 円柱の水平輪郭線

1. 円柱を作成
2. Base Point: 原点
3. Direction: Z軸
4. Distance: 5mm
→ 水平な円の輪郭線が5mm間隔で作成されます

### 例2: 自由形状の垂直輪郭線

1. 複雑な形状のボディを選択
2. Base Point: 任意の頂点
3. Direction: X軸
4. Distance: 10mm
→ X方向に10mm間隔で輪郭線が作成されます

### 例3: 面の法線方向の輪郭線

1. ボディを選択
2. Base Point: ボディ上の点
3. Direction: 傾いた面を選択
4. Distance: 8mm
→ 選択した面に垂直な方向に8mm間隔で輪郭線が作成されます

## トラブルシューティング

### アドインが起動しない

- Fusion 360を再起動してください
- アドインのフォルダが正しい場所にあるか確認してください

### ボタンが表示されない

- アドインを一度停止して、再度実行してください
- Text Commandsウィンドウでエラーメッセージを確認してください

### 輪郭線が作成されない

- ボディが選択した方向の平面群と交差しているか確認してください
- 距離が大きすぎないか確認してください
- Text Commandsウィンドウでログを確認してください

### デバッグモード

`config.py`で`DEBUG = True`に設定すると、詳細なログが表示されます：

```python
DEBUG = True  # デバッグモードON
```

ログは以下の場所で確認できます：
- Fusion 360のText Commandsウィンドウ
- Fusion 360のログファイル

## 開発者向け情報

### プロジェクト構造

```
Rhino-Contour/
├── Rhino-Contour.py          # エントリーポイント
├── config.py                  # グローバル設定
├── commands/
│   ├── __init__.py           # コマンド登録
│   ├── commandDialog/        # テストコマンド
│   └── contour/              # メインのContourコマンド
│       ├── __init__.py
│       ├── entry.py          # Contourコマンド実装
│       └── resources/        # アイコン
├── lib/
│   └── fusionAddInUtils/     # ユーティリティ関数
└── CLAUDE.md                  # AI開発ガイド
```

### テストガイド

段階的なテスト手順については `TESTING.md` を参照してください。

### カスタマイズ

#### 会社名の変更

`config.py`で会社名を変更できます：

```python
COMPANY_NAME = 'YourCompany'
```

#### UIの配置変更

`commands/contour/entry.py`で以下を変更：

```python
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'
IS_PROMOTED = True
```

## ライセンス

このプロジェクトはAutodeskのFusion 360 Add-inテンプレートをベースにしています。

## 技術詳細

### アルゴリズム

1. 選択されたボディのバウンディングボックスから、方向ベクトルに沿った範囲を計算
2. 指定された間隔で平面群を生成
3. 各平面とボディの交線を`Sketch.intersectWithSketchPlane()`メソッドで計算
4. すべての交線を1つの出力スケッチにコピー

### 対応曲線タイプ

- 直線（Line）
- 円弧（Arc）
- 円（Circle）
- 楕円（Ellipse）
- フィットスプライン（Fitted Spline）
- 固定スプライン（Fixed Spline / NURBS）

### 制限事項

- 非常に複雑なジオメトリでは処理に時間がかかる場合があります
- 間隔が非常に小さい場合、大量の曲線が生成される可能性があります

## 更新履歴

### Version 1.0.0
- 初版リリース
- 基本的なContour機能の実装
- 複数ボディ対応
- エラーハンドリングとログの改善

## サポート

問題や質問がある場合は、TESTING.mdを参照して段階的にテストしてください。

