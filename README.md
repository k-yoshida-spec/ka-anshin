# ka-anshin

合同会社K&Aプロジェクト「A 安心・安全」ページ（Wixカスタムエレメント `ka-anshin`）の元データ。

| 場所 | 中身 |
|---|---|
| `content/a.json` | 文章（キー → 文章）。更新は基本ここだけ。翻訳は `a.en.json` を追加 |
| `docs/RUNBOOK.md` | 仕組み・手順・経緯の記録（作業前にまず読む） |
| `src/template.html` | レイアウトと動き。文章の位置は `⟦キー⟧` |
| `src/ce_*.js` | Wixカスタムエレメントの外枠・フォーム送信部分 |
| `assets/img/` | 画像 |
| `tools/build.py` | `dist/`（index.html・ka-anshin.js・img/）を生成 |
| `tools/check.py` | 公開前チェック（JSエラー・390px/1280pxのはみ出し・画像・カスタムエレメント） |

## 公開の流れ
1. 変更はブランチで行い、PRを作る（Actionsがビルドとチェックを実行し、スクリーンショットを添付）
2. 内容を確認して main にマージ
3. main への反映で GitHub Pages（予備）と Cloudflare Pages（本番）に自動公開

## 手元で確認
```
python3 tools/build.py && python3 tools/check.py
```
