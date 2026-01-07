# Quick Start Guide - Rhino-Contour

このガイドでは、最短でRhino-Contourアドインをテストできます。

## 🚀 5分でテスト開始

### Step 1: Phase 1テスト（最小限の動作確認）

現在の設定で、まずは最小限のテストコマンドが動作することを確認します。

1. **Fusion 360を起動**

2. **アドインを実行**
   - `Shift+S` を押す（またはユーティリティ → Add-Ins）
   - "My Add-Ins" タブ
   - "Rhino-Contour" を探して **Run** をクリック

3. **テストボタンをクリック**
   - ツールバーに "Rhino Contour Test" ボタンが表示されます
   - クリックするとダイアログが開きます
   - **OK** をクリック
   - "Hello from Rhino-Contour Add-in!" というメッセージが表示されれば成功！✓

**結果:**
- ✅ 成功: 次のステップへ進む
- ❌ 失敗: Text Commandsウィンドウでエラーを確認

---

### Step 2: Contour機能を有効化

Phase 1が成功したら、メインのContour機能を有効にします。

**ファイル編集:** `commands/__init__.py`

現在の内容：
```python
from .commandDialog import entry as commandDialog
# from .contour import entry as contour

commands = [
    commandDialog,
    # contour,
]
```

↓ 以下のように変更：

```python
from .commandDialog import entry as commandDialog
from .contour import entry as contour

commands = [
    commandDialog,  # テスト用に残す
    contour,        # メイン機能
]
```

---

### Step 3: Contourコマンドのテスト

1. **アドインを再実行**
   - Fusion 360のアドインパネルで "Rhino-Contour" を **Stop**
   - 再度 **Run** をクリック

2. **ツールバーを確認**
   - "Rhino Contour Test" ボタン（テスト用）
   - "Rhino Contour" ボタン（メイン機能）← これが新しく追加されます

3. **簡単なテスト形状を作成**
   - `Create → Cylinder` で円柱を作成
   - 直径: 50mm
   - 高さ: 100mm

4. **Contourコマンドを実行**
   - "Rhino Contour" ボタンをクリック
   - ダイアログが開きます

5. **パラメータを設定**
   - **Bodies**: 円柱のボディをクリック
   - **Base Point**: 円柱の下の中心点をクリック
   - **Direction**: 
     - ブラウザから "Origin" → "Z Axis" を選択
     - または円柱の側面（垂直エッジ）を選択
   - **Distance**: `10 mm` と入力

6. **実行**
   - **OK** をクリック
   - 処理が完了すると、"Successfully created XX contour curves!" というメッセージが表示されます
   - スケッチに水平な円の輪郭線が10mm間隔で作成されます ✓

---

## 📋 期待される結果

### Phase 1 完了
- ✅ アドインが起動
- ✅ テストボタンが表示
- ✅ ダイアログが開く
- ✅ メッセージが表示

### Phase 2-4 完了
- ✅ Contourボタンが表示
- ✅ Contourダイアログが開く
- ✅ 輪郭線が正しく生成される
- ✅ 成功メッセージが表示

---

## 🐛 トラブルシューティング

### 問題: アドインがリストに表示されない

**確認:**
```bash
# ターミナルで確認（Mac）
ls -la "/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/"
```

必要なファイルがあるか確認：
- `Rhino-Contour.py` ✓
- `Rhino-Contour.manifest` ✓
- `config.py` ✓
- `commands/` フォルダ ✓

### 問題: ボタンが表示されない

**解決策:**
1. アドインを Stop して再度 Run
2. Fusion 360を再起動
3. `config.py` の `DEBUG = True` になっているか確認

### 問題: エラーメッセージが表示される

**確認場所:**
1. **Text Commands ウィンドウ** (Fusion 360内)
   - メニュー: `ツール → Text Commands を表示`
   - 詳細なログが表示されます

2. **Python Console** (スクリプトエディタ)
   - エラーのスタックトレースが表示されます

### 問題: 輪郭線が作成されない

**チェックリスト:**
- [ ] ボディを選択しましたか？
- [ ] 基準点を選択しましたか？
- [ ] 方向を選択しましたか？
- [ ] 距離が0より大きいですか？
- [ ] ボディが選択した方向の平面と交差していますか？

**デバッグ:**
Text Commandsウィンドウで以下のようなログを確認：
```
=== Starting Contour Generation ===
Bodies: 1
Base point: (0.0, 0.0, 0.0)
Direction: (0.0, 0.0, 1.0)
Distance: 1.0 cm
Contour: min=-5.0, max=5.0, start=-5.0, num_planes=11
Contour: offset=-5.0, curves=1
...
✓ Successfully created 11 contour curves!
=== Contour Generation Completed ===
```

---

## 🎯 次のステップ

### より複雑な形状でテスト

1. **自由形状の作成**
   - `Create → Form` でT-Splineの形状を作成
   - Contourコマンドで異なる方向から輪郭線を作成

2. **複数ボディ**
   - 複数のボディを作成
   - すべて選択してContourコマンドを実行

3. **異なる方向**
   - X軸、Y軸、Z軸で試す
   - 傾いた面の法線方向で試す
   - エッジの方向で試す

4. **異なる間隔**
   - 1mm（細かい）
   - 50mm（粗い）
   - 不規則な値（例：7.5mm）

### パフォーマンステスト

- 非常に複雑な形状
- 非常に小さい間隔（例：0.5mm）
- 多数のボディ（10個以上）

---

## 📚 詳細情報

- **完全なドキュメント:** `README.md`
- **開発者ガイド:** `CLAUDE.md`
- **詳細なテスト手順:** `TESTING.md`

---

## ✅ チェックリスト

段階的に確認していきましょう：

- [ ] Phase 1: テストコマンドが動作する
- [ ] Phase 2: Contourボタンが表示される
- [ ] Phase 3: Contourダイアログが開く
- [ ] Phase 4: 輪郭線が正しく生成される
- [ ] 応用: 複雑な形状でテスト完了

すべてチェックが付いたら、アドインは正常に動作しています！🎉

