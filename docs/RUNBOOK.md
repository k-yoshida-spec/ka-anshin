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
| `tools/ppt_extract.py` / `ppt_diff.py` | PP の本文・ノート抽出と、前回反映分（`ppt/last.json`）との差分 |
| `tools/content_diff.py` | サイトの「変更前→変更後」一覧（文章キー＋テンプレートの変更行） |
| `ppt/last.json` | 最後にサイトへ反映した PP のテキスト（差分の基準） |
| `tools/check.py` | 公開前チェック。1280px と 390px で全ページを開き、JSエラー・横はみ出し・画像切れ・カスタムエレメントの高さを検査。失敗なら終了コード1 |
| `.github/workflows/deploy.yml` | PR：ビルド＋チェック＋スクリーンショット添付／main：GitHub Pages へ公開 |

ビルドの要点：
- `⟦キー⟧` を `content/a.<lang>.json`（無ければ `a.json`）で置換。未定義キー・空文字・残った `{{…}}` があればビルド失敗。
- 画像は単体ページでは相対パス `img/…`、カスタムエレメントでは `KA_B + "img/…"`（`KA_B` は `document.currentScript.src` の場所。取れなければ `--base`／環境変数 `KA_BASE`）。
- CSS は `:root` → `.kroot`、`body` → `.kroot` に置換して Shadow DOM 内で効かせる。

## 4. 定常作業：PP（更新資料）からページ更新まで

薫さんの作業は ①PPを渡す ③一覧を確認してマージ の2つ。②④は Claude（スキル `a-site-update`）が行う。

| 段階 | 誰 | やること | 使う道具 |
|---|---|---|---|
| ① 渡す | 薫さん | PP をチャットに貼る、または `Documents\github\ka-anshin\PP\` に置いて「Aサイトを更新して」 | — |
| ② 差分を出す | Claude | PP を抽出し、前回反映分 `ppt/last.json` と比べる | `tools/ppt_extract.py` `tools/ppt_diff.py` |
| ③ 反映案を作る | Claude | 作業ブランチで `content/a.json`（文章）と、必要なら `src/template.html`（金額・リンク・構成）を直す | — |
| ④ 確認材料を作る | Claude | ビルド → 「変更前→変更後」一覧 → push → PR（一覧を本文に）→ Actions の自動チェック合格を確認 | `tools/build.py` `tools/content_diff.py` |
| ⑤ 承認 | 薫さん | 一覧を読み、PR を「Merge pull request」→「Confirm merge」 | — |
| ⑥ 公開確認 | Claude | Cloudflare の公開完了後、`https://ka-anshin.pages.dev/test-ce.html` で新しい文言が出ることを確認 | Chrome |

### 4-1. コマンド（薫さんの PC 上、`$HOME/mnt/ka-anshin` で実行）

```bash
# 準備（毎回）
T=$(tr -d ' \r\n' < gh_token.txt); A="Authorization: Basic $(printf 'x-access-token:%s' "$T" | base64 -w0)"
git -c http.extraHeader="$A" fetch -q origin && git checkout -q -B update-YYYYMMDD origin/main

# ② 差分
python3 tools/ppt_extract.py "PP/<新しいPP>.pptx" /tmp/new.json
python3 tools/ppt_diff.py ppt/last.json /tmp/new.json      # 「変更なし」なら終了（薫さんに報告）

# ③ 反映：差分を読んで content/a.json の該当キーを書き換える
#    キーの探し方: grep -n "<今の文言の一部>" content/a.json
#    金額などの数字だけの文字列・リンク先は src/template.html にある（grep で探す）
#    反映し終えたら基準を更新: cp /tmp/new.json ppt/last.json

# ④ 確認材料
python3 tools/build.py                       # 未定義キー・空文字・記号の残りがあれば失敗
python3 tools/content_diff.py origin/main > /tmp/diff.md   # PR本文と薫さんへの一覧
git add -A && git commit -m "PP反映: <資料名>" && git -c http.extraHeader="$A" push -u origin update-YYYYMMDD
# PR作成: POST https://api.github.com/repos/k-yoshida-spec/ka-anshin/pulls  body=/tmp/diff.md
# Actions: GET /repos/k-yoshida-spec/ka-anshin/actions/runs?per_page=3 で conclusion=success を確認
```

### 4-2. 判断のルール

- PP の文章とサイトの文章は 1対1 ではない。PP の**意味の変更**（サービス名、提供内容、料金・時間、資格、表現の方針）をサイトの該当箇所に反映する。言い回しだけの違いは反映しない。
- どのキーをどう変えたかは必ず「変更前→変更後」一覧で薫さんに見せ、マージ（公開）は薫さんだけが行う。
- 迷う箇所（PP にあってサイトに置き場がない、サイトにあって PP から消えた）は、勝手に足し引きせず一覧の下に「確認したいこと」として書く。
- 1回の PR は1つの資料分。表示崩れは Actions の `tools/check.py`（1280px/390px、JSエラー、はみ出し、画像、カスタムエレメント）で止まる。
- 公開後に問題があれば PR の「Revert」で戻す（6章）。

### 4-3. 検証記録

- 2026-11-02：「A 安心・安全 サービスのご案内 1.pptx」（11枚）を抽出し `ppt/last.json` を基準として登録。同一資料の差分＝「変更なし」、1行変更＝該当スライドの差分が出ること、文章キー変更・テンプレート（金額）変更が `content_diff.py` の一覧に出ることを確認。

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
