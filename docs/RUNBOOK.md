# A「安心・安全」ページ 運用記録（RUNBOOK）

最終更新：2026-11-02　／　対象：www.ak-analytics.jp の「安心・安全」ページ

このファイルは、Aページを**誰が・いつやっても同じ結果になる**ように、仕組み・手順・決めごとを残したものです。
Claude に作業を頼むときは「docs/RUNBOOK.md のとおりに」と伝えてください。

---

## 1. 全体の仕組み

```
薫さん ──PP──▶ Claude ──PR──▶ GitHub k-yoshida-spec/ka-anshin
                                 │ マージ（main）
                                 ├─▶ Cloudflare Pages  https://ka-anshin.pages.dev/      … 本番の配信
                                 └─▶ GitHub Pages      https://k-yoshida-spec.github.io/ka-anshin/ … 予備
                                            │
旧Wixエディタ「安心・安全」ページ ◀── カスタムエレメント ka-anshin（#customElement1）が ka-anshin.js を読み込む
        │ フォーム送信（CustomEvent 'ka-submit'）
        ▼
ページコード src/pages/安心・安全.he56q.js（GitHub k-yoshida-spec/site-b）
        │ wixData.insert
        ▼
Wix CMS コレクション Inquiries
```

- Wix 側は「器」だけ。文章・画像・レイアウト・動きはすべて ka-anshin リポジトリにある。
- 更新は **PR をマージするだけ**。Wix の「公開」は不要（配信元のファイルが変わるため）。
- Cloudflare は `Cache-Control: max-age=0, must-revalidate` なので、デプロイ完了と同時に反映。

## 2. 場所とアカウント

| もの | 場所 | 備考 |
|---|---|---|
| 元データ | GitHub `k-yoshida-spec/ka-anshin`（Public） | main が公開版 |
| ページコード | GitHub `k-yoshida-spec/site-b`（Private） | Wix の GitHub 連携。Wix では読み取り専用 |
| 本番配信 | Cloudflare Pages プロジェクト `ka-anshin`（k-yoshida@ak-analytics.jp） | Build: `python3 tools/build.py` / Output: `dist` / Branch: `main` |
| 予備配信 | GitHub Pages（Source: GitHub Actions） | `.github/workflows/deploy.yml` が main で公開 |
| Wix サイト | 「K&Aプロジェクト」metaSiteId `a26fe21f-fcb9-47ef-9927-b9dc5d8a1257` | 旧エディタ＝ブランチ **Original-Branch** |
| カスタムエレメント | 安心・安全ページ、ID `#customElement1`、タグ `ka-anshin` | サーバーURL `https://ka-anshin.pages.dev/ka-anshin.js` |
| お問い合わせ保存先 | Wix CMS `Inquiries` | 権限「コンテンツを収集」：追加＝すべての訪問者／閲覧＝共同管理者 |
| PC 側の複製 | `C:\Users\kraft\Documents\github\ka-anshin` | バックアップ兼作業場所。`gh_token.txt` を置く（.gitignore 済み） |
| Claude 用キー | Fine-grained token `ka-anshin-claude` | 対象 ka-anshin・site-b／Contents・Pull requests・Workflows＝Read and write／期限 2027-01-31 |

## 3. リポジトリ ka-anshin の中身

| パス | 役割 |
|---|---|
| `content/a.json` | 文章（キー → 文章、461項目＋`meta.description`）。**更新は基本ここだけ** |
| `src/template.html` | レイアウトと動き。文章の位置は `⟦キー⟧`、画像は `{{FACE}}` などの記号 |
| `src/ce_header.js` / `ce_footer.js` | カスタムエレメントの外枠（Shadow DOM、高さ自動調整、`sent` 属性で送信結果を表示） |
| `src/ce_submit.js` | フォーム送信部分（入力チェック → `ka-submit` イベント → 15秒で応答なしならエラー表示） |
| `assets/img/` | 画像（webp/jpg、文字なし） |
| `tools/build.py` | `dist/index.html`（単体ページ）・`dist/ka-anshin.js`（カスタムエレメント）・`dist/img/`・`dist/test-ce.html` を生成 |
| `tools/source_extract.py` / `source_diff.py` | 更新資料（pptx/docx/xlsx/pdf/txt/md）の抽出と、同じ形式の前回分（`sources/last-<形式>.json`）との差分 |
| `tools/check_update_record.py` | PR に承認済みの更新リストがあるかの検査（Actions） |
| `docs/updates/` | 更新リストと承認の記録（`TEMPLATE.md` が雛形） |
| `tools/content_diff.py` | サイトの「変更前→変更後」一覧（文章キー＋テンプレートの変更行） |
| `sources/last-<形式>.json` | 最後にサイトへ反映した資料のテキスト（形式ごとの差分の基準） |
| `tools/check.py` | 公開前チェック。1280px と 390px で全ページを開き、JSエラー・横はみ出し・画像切れ・カスタムエレメントの高さを検査。失敗なら終了コード1 |
| `.github/workflows/deploy.yml` | PR：ビルド＋チェック＋スクリーンショット添付／main：GitHub Pages へ公開 |

ビルドの要点：
- `⟦キー⟧` を `content/a.<lang>.json`（無ければ `a.json`）で置換。未定義キー・空文字・残った `{{…}}` があればビルド失敗。
- 画像は単体ページでは相対パス `img/…`、カスタムエレメントでは `KA_B + "img/…"`（`KA_B` は `document.currentScript.src` の場所。取れなければ `--base`／環境変数 `KA_BASE`）。
- CSS は `:root` → `.kroot`、`body` → `.kroot` に置換して Shadow DOM 内で効かせる。

## 4. 定常作業：更新資料からページ更新まで（更新リスト＋2段階承認）

**どの更新も必ず「更新リスト」を作り、薫さんの承認を2回通す。** 資料の形式は問わない（PP・Word・Excel・PDF・テキスト／チャットのメモ・画像・Claude Docs）。

| 段階 | 誰 | やること | 記録 |
|---|---|---|---|
| ① 資料を渡す | 薫さん | チャットに貼る、または `Documents\github\ka-anshin\PP\` に置いて「Aサイトを更新して」 | — |
| ② 差分を出す | Claude | `source_extract.py` で抽出し、同じ形式の前回分 `sources/last-<形式>.json` と `source_diff.py` で比較。前回分が無い形式・メモ・画像は、資料と今のサイトを直接突き合わせる | — |
| ③ 更新リストを作る | Claude | `docs/updates/YYYYMMDD-<資料名>.md`（雛形 `TEMPLATE.md`）に No・ページ/場所・変更前・変更後・根拠・判断（反映/保留/要確認）と「確認したいこと」を書き、チャットで提示 | 更新リスト |
| ④ **承認①：内容の承認** | 薫さん | 更新リストを見て「全件承認」または「No.○は除外／こう直す」と返信 | 承認者・承認日・承認の内容をリストに記入 |
| ⑤ 反映 | Claude | 承認された項目だけを `content/a.json`／`src/template.html` に反映。`build.py` → `content_diff.py` の結果が承認リストと一致することを確認。基準 `sources/last-<形式>.json` を更新 | — |
| ⑥ PR | Claude | 更新リストと実際の変更一覧を本文にして PR。Actions が「承認済みの更新リストがあるか」＋ビルド＋画面チェック | PR |
| ⑦ **承認②：公開の承認** | 薫さん | PR を確認して「Merge pull request」→「Confirm merge」 | GitHub のマージ記録 |
| ⑧ 公開確認 | Claude | `https://ka-anshin.pages.dev/test-ce.html` で新しい文言を確認し、報告 | — |

承認①の無い PR は、Actions の `tools/check_update_record.py` が止める（`content/` `src/` `assets/` を変える PR に、承認者・承認日・No.1 以降の表を持つ `docs/updates/YYYYMMDD-*.md` が必要）。

### 4-1. コマンド（薫さんの PC 上、`$HOME/mnt/ka-anshin`）

```bash
T=$(tr -d ' \r\n' < gh_token.txt); A="Authorization: Basic $(printf 'x-access-token:%s' "$T" | base64 -w0)"
rm -f .git/*.lock; git -c http.extraHeader="$A" fetch -q origin && git checkout -q -B update-YYYYMMDD origin/main
python3 tools/source_extract.py "PP/<資料>" /tmp/new.json          # pptx/docx/xlsx/pdf/txt/md
python3 tools/source_diff.py sources/last-<形式>.json /tmp/new.json
cp docs/updates/TEMPLATE.md docs/updates/YYYYMMDD-<資料名>.md       # ③ 更新リストを書く → ④ 承認を記入
# ⑤ 反映（キー探し: grep -n "<今の文言>" content/a.json／金額・リンクは src/template.html）
python3 tools/build.py && python3 tools/content_diff.py origin/main > /tmp/diff.md
cp /tmp/new.json sources/last-<形式>.json
git add -A && git commit -m "更新: <資料名>" && git -c http.extraHeader="$A" push -u origin update-YYYYMMDD
# ⑥ PR: POST /repos/k-yoshida-spec/ka-anshin/pulls（body＝更新リスト＋/tmp/diff.md）→ Actions の success を確認
```

### 4-2. 判断のルール

- 資料とサイトの文章は 1対1 ではない。**意味の変更**（サービス名、提供内容、料金・時間、資格、表現の方針）だけを更新リストに載せる。言い回しだけの違いは載せない。
- 置き場が合わない・資料から消えた・読み取りが不確か（PDF の表、画像）なものは「要確認」にして勝手に反映しない。
- 承認①で除外・修正された内容はリストの「承認の内容」に残し、その通りに反映する。承認後にリスト外の変更を足さない（足すなら承認①からやり直す）。
- 1回の PR は1つの資料分。公開後の問題は PR の「Revert」で戻す（6章）。

### 4-3. 検証記録（2026-11-02）

- PP（11枚）を抽出して `sources/last-pptx.json` を基準に登録。同一資料＝「変更なし」、1行変更＝該当スライドの差分が出ることを確認。
- Word（見出しで節分け・表も取得）、Excel（シートごと）、PDF（ページごと。表の文字を取りこぼすことがある）、Markdown/テキストの抽出を確認。前回分が無い形式は「比較なし」と出ることを確認。
- `content_diff.py` が文章キーの変更とテンプレート（金額）の変更を一覧に出すことを確認。
- `check_update_record.py`：更新リスト無し→NG、承認日（承認者）空欄→NG、承認済み→OK を確認。

## 5. フォーム（お問い合わせ）

- エレメント → `ka-submit`（detail: area, role, issues[], interests[], company, name, email, tel, message, source）
- ページコード（site-b `src/pages/安心・安全.he56q.js`）が `Inquiries` に insert：title, company, name, email, tel, message, detail
- 成否をエレメントの属性 `sent` に `ok-<時刻>` / `ng-<時刻>` で返し、画面に「送信しました」または失敗メッセージ。
- ページコードの変更も site-b へ PR → マージで Wix エディタに自動反映。**ページコードの変更だけは Wix で「公開」が必要。**
- 未設定：メール通知（Wix オートメーション）。

## 6. 障害時と切り戻し

| 症状 | 対応 |
|---|---|
| 更新後に表示が崩れた | 該当 PR の「Revert」→ 戻し PR をマージ |
| Cloudflare 停止で本文が出ない | Wix の「ソースを選択」→ サーバーURLを `https://k-yoshida-spec.github.io/ka-anshin/ka-anshin.js` → 公開。復旧後に戻す |
| GitHub 停止 | 公開中ページは影響なし。更新のみ待つ |
| フォームが ng になる | `Inquiries` の存在・コレクションID・権限を確認。ブラウザのコンソールに `Inquiries insert failed` |
| GitHub アカウント／リポジトリ消失 | PC の `Documents\github\ka-anshin`（全履歴あり）から新リポジトリへ push、Cloudflare を再接続 |

## 7. これまでの経緯（2026-11-02 時点）

1. 旧 Wix エディタでの手作業再現は工数が大きく、テンプレート販売の前提（安価な提供）に合わないと判断。
2. Wix Headless の静的ドロップ＋カスタムエレメントで A ページを丸ごと埋め込む方式に変更（手動 ZIP ドロップ）。
3. フォームを Velo ページコード＋CMS へつなぐ設計を追加。
4. PP（「A 安心・安全 サービスのご案内 1.pptx」）の内容を反映：ヒーローのラベル、01 の三者の課題、「産業保健専門職」、02 の文言、LP 5本、料金プラン（※1）、今泉の資格。
5. 手動ドロップをやめ、GitHub＋Cloudflare Pages（本番）＋GitHub Pages（予備）で自動公開する方式へ移行。文章を `content/a.json` に分離し、画像を JS から外した（JS 約680KB → 約89KB）。
6. Wix のサーバーURLを Cloudflare に切り替え。CMS `Inquiries` を作成し、site-b にページコードを追加。

## 8. 残作業

- [ ] 公開中ページでフォームのテスト送信 → `Inquiries` に入ることを確認
- [ ] GitHub リカバリーコードの再発行（チャットに添付されたため）
- [ ] main への直接 push を禁止するルール（ka-anshin・site-b）
- [ ] UptimeRobot で `https://ka-anshin.pages.dev/ka-anshin.js` を監視
- [ ] お問い合わせのメール通知（Wix オートメーション）
- [ ] キー `ka-anshin-claude` の更新（期限 2027-01-31 の前）
- [ ] 薫さん PC に Playwright が無いため `check.py` は GitHub Actions で実行（ローカルは build.py まで）
- [ ] 高画質キャラ画像の差し替え（ビーバー・フクロウの困り顔、全員の笑顔）

かんたん手順書（薫さん向け）：Claude Docs「Aページ更新 かんたん手順書」 https://claude.ai/artifact/CKWRAT6wt8RzUF7dYS8Br9
