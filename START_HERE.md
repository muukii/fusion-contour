# 🎯 START HERE - Rhino-Contour Add-in

## ようこそ！

このアドインは、RhinoスタイルのContour（輪郭線）機能をFusion 360に追加します。
段階的にテストしながら動作確認できるように準備されています。

---

## 📖 ドキュメント一覧

読む順番におすすめを並べています：

| ドキュメント | 目的 | いつ読む？ |
|-------------|------|-----------|
| **QUICKSTART.md** ⭐ | すぐに始める | **最初に読む** |
| **STATUS.md** | 現在の状態 | 今どの段階か確認したいとき |
| **README.md** | 完全なドキュメント | 機能の詳細を知りたいとき |
| **TESTING.md** | 詳細なテスト手順 | 問題が起きたとき |
| **CLAUDE.md** | 開発者ガイド | コードを変更したいとき |

---

## 🚀 クイックスタート（3ステップ）

### Step 1: Phase 1テスト（1分）

最小限の動作確認をします。

1. Fusion 360を起動
2. `Shift+S` → "Rhino-Contour" → **Run**
3. "Rhino Contour Test" ボタンをクリック → OK
4. "Hello" メッセージが表示 → ✅ 成功！

**失敗した場合:** `TESTING.md` のトラブルシューティングを参照

---

### Step 2: Contour機能を有効化（1分）

`commands/__init__.py` を編集：

**変更前:**
```python
from .commandDialog import entry as commandDialog
# from .contour import entry as contour  # ← コメントアウト中

commands = [
    commandDialog,
    # contour,  # ← コメントアウト中
]
```

**変更後:**
```python
from .commandDialog import entry as commandDialog
from .contour import entry as contour  # ← アンコメント

commands = [
    commandDialog,
    contour,  # ← アンコメント
]
```

アドインを **Stop** → **Run** で再起動

---

### Step 3: Contourコマンドをテスト（3分）

1. **円柱を作成**
   - Create → Cylinder
   - 直径: 50mm、高さ: 100mm

2. **Rhino Contour コマンドを実行**
   - ツールバーの "Rhino Contour" ボタンをクリック

3. **パラメータ設定**
   - **Bodies**: 円柱をクリック
   - **Base Point**: 円柱の底面中心をクリック
   - **Direction**: ブラウザから Origin → Z Axis を選択
   - **Distance**: `10 mm`

4. **実行**
   - **OK** をクリック
   - "Successfully created XX contour curves!" → ✅ 成功！
   - 水平な円の輪郭線が10mm間隔で生成されます

---

## 📊 現在の状態

```
┌─────────────────────────────────────────┐
│  Phase 1: 基本動作確認                   │
│  ✅ テストコマンドが動作                 │
│  ✅ エラーハンドリング完了               │
│  ✅ ログ機能確認済み                     │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Phase 2: Contour機能有効化              │
│  ⚠️ commands/__init__.py を編集が必要   │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Phase 3-4: Contour機能テスト            │
│  ✅ 実装完了（テスト待ち）               │
│  - 複数ボディ対応                        │
│  - エラーハンドリング                    │
│  - 詳細なログ出力                        │
└─────────────────────────────────────────┘
```

---

## 🎓 主な機能

### Contourコマンドでできること

- ✅ **複数ボディ選択**: 一度に複数のボディの輪郭線を生成
- ✅ **柔軟な方向指定**: エッジ、面、構成軸から選択
- ✅ **カスタマイズ可能な間隔**: 任意の距離で輪郭線を作成
- ✅ **自動範囲計算**: ボディの範囲を自動判定
- ✅ **詳細なログ**: DEBUG=True で詳細な情報を表示

---

## 🐛 問題が起きたら

### エラーが表示される

1. **Text Commands ウィンドウ**を開く（ツール → Text Commands を表示）
2. エラーメッセージを確認
3. `TESTING.md` のトラブルシューティング参照

### ボタンが表示されない

1. アドインを **Stop** → **Run**
2. それでもダメなら Fusion 360 を再起動

### 輪郭線が生成されない

- ボディが方向の平面と交差しているか確認
- 距離が適切か確認（大きすぎないか）
- Text Commands ウィンドウでログを確認

---

## 📁 プロジェクト構造（簡易版）

```
Rhino-Contour/
├── 📄 START_HERE.md          ← このファイル
├── 📄 QUICKSTART.md          ← すぐに始める
├── 📄 STATUS.md              ← 現在の状態
├── 📄 README.md              ← 完全なドキュメント
├── 📄 TESTING.md             ← テスト手順
├── 📄 CLAUDE.md              ← 開発者ガイド
│
├── 🐍 Rhino-Contour.py       ← エントリーポイント
├── ⚙️ config.py              ← 設定（DEBUG=True）
│
├── 📂 commands/
│   ├── __init__.py           ← コマンド登録 ⚠️ ここを編集
│   ├── commandDialog/        ← テストコマンド
│   └── contour/              ← メインのContour機能
│
└── 📂 lib/
    └── fusionAddInUtils/     ← ユーティリティ
```

---

## ✅ チェックリスト

進捗を確認しましょう：

- [ ] このファイル（START_HERE.md）を読んだ
- [ ] Phase 1: テストコマンドが動作した
- [ ] Phase 2: commands/__init__.py を編集した
- [ ] Phase 2: アドインを再起動した
- [ ] Phase 3: Contourボタンが表示された
- [ ] Phase 3: 円柱で輪郭線を生成した
- [ ] Phase 4: 他の形状でもテストした

すべてチェックが付いたら完了です！🎉

---

## 🎯 次のステップ

1. **今すぐ:** `QUICKSTART.md` を開く
2. **Phase 1テスト:** 最小限の動作確認（1分）
3. **Phase 2-4:** Contour機能のテスト（5分）
4. **応用:** さまざまな形状で試す

---

## 💡 ヒント

### デバッグモード

`config.py` で設定済み：
```python
DEBUG = True  # 詳細なログが表示されます
```

### ログの確認場所

- **Text Commands ウィンドウ** (Fusion 360内)
- **Python Console** (スクリプトエディタ)

### 便利なショートカット

- `Shift+S`: アドインパネルを開く
- `Ctrl+C`: Text Commands をクリア

---

## 🎊 準備完了！

すべての準備が整っています。
**次は `QUICKSTART.md` を開いて始めましょう！**

質問や問題があれば、各ドキュメントを参照してください。
すべてのドキュメントには詳しい説明とトラブルシューティングが含まれています。

**Happy Contouring! 🎨**

