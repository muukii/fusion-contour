# Testing Guide - Rhino-Contour Add-in

このガイドでは、段階的にアドインをテストして動作を確認します。

## Phase 1: 最小限のアドイン起動確認 ✓

### テスト内容
- アドインが正常に読み込まれる
- UIボタンが表示される
- シンプルなダイアログが開く
- メッセージボックスが表示される

### テスト手順

1. **Fusion 360を起動**

2. **アドインパネルを開く**
   - メニュー: `ユーティリティ → Add-Ins`
   - または: `Shift+S`

3. **アドインを実行**
   - "My Add-Ins" タブを選択
   - リストから "Rhino-Contour" を探す
   - "Run" ボタンをクリック

4. **UIボタンを確認**
   - ツールバーの "Scripts and Add-Ins" パネルを確認
   - "Test Hello" ボタンが表示されているはず

5. **コマンドを実行**
   - "Test Hello" ボタンをクリック
   - ダイアログが開くことを確認
   - "OK" ボタンをクリック
   - "Hello from Rhino-Contour Add-in!" メッセージが表示されることを確認

### 期待される結果
- ✓ エラーなくアドインが起動
- ✓ UIボタンが表示される
- ✓ ダイアログが開く
- ✓ メッセージボックスが表示される

### デバッグ情報の確認

`DEBUG = True` が `config.py` に設定されているため、詳細なログが表示されます：

- **Text Commands ウィンドウ** (Fusion 360内):
  ```
  Command Dialog Sample Command Created Event
  Command Dialog Sample Command Execute Event
  ✓ Command executed successfully!
  ```

### トラブルシューティング

**問題**: アドインがリストに表示されない
- **解決**: ファイルパスを確認
  - 正しい場所: `/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/`

**問題**: エラーメッセージが表示される
- **解決**: Text Commands ウィンドウでエラーの詳細を確認
- Fusion 360のログファイルを確認

**問題**: ボタンが表示されない
- **解決**: アドインを一度停止して再実行
- Fusion 360を再起動

---

## Phase 2: Contour基本機能のテスト準備

### テスト内容
- Contourコマンドボタンの追加
- 基本的なダイアログの表示確認
- 入力パラメータの検証

### 準備
Phase 1が成功したら、`commands/__init__.py`を以下のように変更：

```python
# Contourコマンドを有効化
from .contour import entry as contour

commands = [
    commandDialog,  # テスト用に残す
    contour,        # メイン機能
]
```

### テスト手順
1. アドインを停止して再実行
2. "Contour" ボタンがツールバーに表示されることを確認
3. ボタンをクリックしてダイアログが開くことを確認
4. 各入力フィールドが正しく表示されることを確認：
   - Bodies (ボディ選択)
   - Base Point (基準点)
   - Direction (方向)
   - Distance (間隔)

---

## Phase 3: Contour機能の簡易版実装

### テスト内容
- 1つのボディでシンプルな輪郭抽出
- プレーン生成の確認
- エラーハンドリングの確認

### テスト手順
1. Fusion 360でシンプルな立方体を作成
2. Contourコマンドを実行
3. 立方体を選択
4. 基準点を選択（例：原点）
5. 方向を選択（例：Z軸）
6. 間隔を設定（例：10mm）
7. OKをクリック
8. スケッチに輪郭線が作成されることを確認

---

## Phase 4: Contour機能の完全実装とテスト

### テスト内容
- 複数ボディの処理
- 複雑な形状での輪郭抽出
- さまざまな方向での処理
- パフォーマンステスト

### テスト手順
1. 複数の異なる形状を作成
2. さまざまなパラメータで輪郭抽出をテスト
3. エッジケースの確認：
   - 非常に小さい間隔
   - 非常に大きい間隔
   - 交差しない平面
   - 複雑なジオメトリ

---

## 現在の状態

**有効なコマンド:**
- `commandDialog` (Test Hello) - Phase 1テスト用

**無効化されているコマンド:**
- `paletteShow` - コメントアウト済み
- `paletteSend` - コメントアウト済み
- `contour` - コメントアウト済み（後で有効化）

これにより、最小限の構成でテストを開始できます。

