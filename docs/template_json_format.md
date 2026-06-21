# テンプレートJSON フォーマットガイド

`txt2odf` では、出力される ODT（OpenDocument Text）ファイルの見た目や、テキストの変換ルールを JSON 形式のテンプレートファイルで細かく制御できます。
このドキュメントでは、設定項目の意味と書き方を、初心者の方にも分かりやすく解説します。

---

## 1. テンプレートの基本構造

テンプレートは大きく分けて `style`（見た目の設定）と `processing`（文章の処理設定）の2つのブロックで構成されています。

```json
{
  "style": {
    // ページサイズやフォント、行間などの設定
  },
  "processing": {
    // 空行の圧縮や、ルビ・傍点などの記法変換設定
  }
}
```

---

## 2. 各項目の詳細

### `style` ブロック（見た目の設定）

| 項目名 | 設定例 | 説明 |
| :--- | :--- | :--- |
| `page_size` | `"A4"`, `"A5"`, `"B5"` | 用紙のサイズを指定します。同人誌などの小説本であれば `"A5"`、一般的な書類であれば `"A4"` がよく使われます。 |
| `orientation` | `"portrait"`, `"landscape"` | ページの向きです。`"portrait"`（縦長）か `"landscape"`（横長）を指定します。 |
| `writing_mode` | `"vertical"`, `"horizontal"` | 文字の進む方向です。小説などの縦書きなら `"vertical"`、横書きなら `"horizontal"` を指定します。 |
| `line_height` | `1.5`, `1.75`, `2.0` など | 行間（行送り）の広さを指定します。数値が大きいほど行と行の間が広がります。縦書きでルビを多用する場合は `1.75` や `2.0` など広めに取るのがおすすめです。 |
| `font_family` | `"Noto Serif JP"` など | 使用するフォント（書体）の名前を指定します。明朝体なら `"Noto Serif JP"` や `"MS Mincho"`、ゴシック体なら `"Noto Sans JP"` などを指定します。 |

#### `font_size`（文字の大きさ）
本文や見出しごとの文字サイズ（pt）を設定します。
```json
"font_size": {
  "body": 11.5,  // 本文の大きさ
  "h1": 20,      // 大見出し（章タイトルなど）
  "h2": 16,      // 中見出し
  "h3": 14       // 小見出し
}
```

#### `emphasis`（傍点・強調の表現方法）
カクヨム記法の傍点（《《テキスト》》）をワープロソフト上でどのように表示させるかを **配列（`[ ]`）** で指定します。ワープロソフトの仕様により、縦書きと横書きで最適な設定が異なります。

*   `"text-emphasize"` : 標準の傍点プロパティを使用します。（横書きで綺麗に表示されます）
*   `"bold"` : 文字を**太字**にして強調します。（縦書きで傍点が本文から離れてしまう環境で無難におすすめです）
*   `"italic"` : 文字を*斜体*にします。
*   `"ruby"` : ルビの仕組みを使って傍点（・）を振ります。（少し点が小さくなります）

**【記述例】**
```json
// 太字にする場合
"emphasis": ["bold"]

// 横書きなどで標準の傍点を使う場合
"emphasis": ["text-emphasize"]

// 太字かつ斜体にする場合
"emphasis": ["bold", "italic"]
```
*(※ 注意: `"text-emphasize"` と `"ruby"` は競合するため、同時に指定するとエラーになります)*

---

### `processing` ブロック（文章の処理設定）

| 項目名 | 設定例 | 説明 |
| :--- | :--- | :--- |
| `markup` | `"kakuyomu"`, `"none"` | `"kakuyomu"` にすると、テキスト内のルビ（`\|漢字《かんじ》`）や傍点を自動で認識して ODT 上のルビに変換します。 |

#### `blank_lines`（空行の処理）
テキストファイル特有の余分な改行を自動で整理する機能です。
```json
"blank_lines": {
  "mode": "compress",
  "custom_rules": []
}
```
`mode` には以下のいずれかを指定します。
*   `"none"` : 何もせず、元のテキストの改行をそのまま出力します。
*   `"compress"` : スマートフォン向けによく使われる「段落ごとの単一の空行」をすべて**削除**して詰めつつ、シーン区切りなどの「複数行の空行」は1行の空行に**圧縮**します。（書籍化時の標準的な処理）
*   `"dialogue_narrative"` : 「会話文（「」）と地の文の間にある単一の空行」のみを削除して詰めます。地の文同士の間の空行や、シーン区切りなどの複数行の空行は**そのまま残します**。
*   `"dialogue_narrative_compress"` : 上記の `dialogue_narrative` の処理に加え、シーン区切りなどの「複数行の空行」を1行の空行に**圧縮**します。
*   `"custom"` : `custom_rules` に定義した独自の正規表現ルールを用いて、テキストの置換・整形を行います。

#### `custom_rules`（独自の置換ルール）
`mode` が `"custom"` の場合、ここに指定した正規表現を使って独自のテキスト処理を行うことができます。ルールは上から順に適用されます。

**【記述例】**
```json
"blank_lines": {
  "mode": "custom",
  "custom_rules": [
    {
      "pattern": "\\n{3,}",
      "replace": "\\n\\n"
    },
    {
      "pattern": "（笑）",
      "replace": "(笑)"
    }
  ]
}
```
*   `"pattern"`: 検索する正規表現を指定します（JSON内の文字列として記述するため、`\n` は `\\n` のようにエスケープが必要です）。
*   `"replace"`: 置換後の文字列を指定します（省略時は空文字として扱われ、マッチした部分が削除されます）。

---

## 3. そのまま使える設定サンプル

### サンプルA: 小説執筆向け（A5サイズ・縦書き）
同人誌や文庫本などを意識した、縦書きで読みやすい設定です。縦書きの仕様上、傍点記号がズレやすいため、強調表現には太字（bold）を採用しています。

```json
{
  "style": {
    "page_size": "A5",
    "orientation": "portrait",
    "writing_mode": "vertical",
    "line_height": 1.75,
    "font_family": "Noto Serif JP",
    "font_size": {
      "body": 10.5,
      "h1": 16,
      "h2": 14,
      "h3": 12
    },
    "emphasis": ["bold"]
  },
  "processing": {
    "blank_lines": {
      "mode": "dialogue_narrative",
      "custom_rules": []
    },
    "markup": "kakuyomu"
  }
}
```

### サンプルB: レポート・資料向け（A4サイズ・横書き）
一般的な書類や横書きのレポート向けの設定です。傍点表現（text-emphasize）が綺麗に機能します。

```json
{
  "style": {
    "page_size": "A4",
    "orientation": "portrait",
    "writing_mode": "horizontal",
    "line_height": 2.0,
    "font_family": "Noto Sans JP",
    "font_size": {
      "body": 11,
      "h1": 18,
      "h2": 14,
      "h3": 12
    },
    "emphasis": ["text-emphasize"]
  },
  "processing": {
    "blank_lines": {
      "mode": "compress",
      "custom_rules": []
    },
    "markup": "kakuyomu"
  }
}
```
