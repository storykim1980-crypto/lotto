#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ミニロト分析ナビ의 コラム(칼럼) 페이지 생성기.

blog/ 아래의 모든 기사 페이지를 일본어로 재생성합니다.
- 운영자가 직접 쓴 것처럼 보이는 톤 (正直 멘트 + 사이트 실데이터 인용)
- 각 기사: Article JSON-LD, OGP, canonical, 빵부스러기, 날짜 포함
- 기사 추가 방법: ARTICLES 리스트에 dict 1개 추가 후 `python3 scripts/build_blog.py` 실행
- 기존 로직(index.html 등)과 독립 — 정적 파일만 생성

실데이터 출처: data/results.json (제1회〜제1397회、2026-08-02 시점 계산값)
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / 'blog'
BLOG.mkdir(exist_ok=True)
DOMAIN = 'https://miniloto-navi.com'
EMAIL = 'storykim1980@gmail.com'
PUB = '2026-08-04'  # 사이트 실제 공개일(런칭일). 새 글 추가 시 그 날의 실제 날짜를 A() 에 적는다

NAV_LINKS = [
    ('about.html', 'このサイトについて'),
    ('privacy.html', 'プライバシーポリシー'),
    ('terms.html', '利用規約'),
    ('cookies.html', 'クッキーポリシー'),
    ('disclaimer.html', '免責事項'),
    ('ads-policy.html', '広告について'),
    ('contact.html', 'お問い合わせ'),
]

SHELL_CSS = '''
:root{--bg:#f3f6fb;--paper:#fff;--ink:#111827;--muted:#64748b;--line:#e2e8f0;--navy:#071a33;--navy2:#10294a;--blue:#2563eb;--red:#e11d48;--gold:#f2b705;--green:#059669;--radius:16px;}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:"Noto Sans JP","Hiragino Kaku Gothic ProN","Hiragino Sans",Meiryo,"Yu Gothic",YuGothic,sans-serif;font-size:15px;line-height:1.9;color:var(--ink);-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:optimizeLegibility;font-feature-settings:"palt";background:linear-gradient(180deg,#f8fafc,#eef3f8);}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
.topbar-line{height:5px;background:linear-gradient(90deg,var(--red),var(--gold),var(--green),var(--blue))}
header.site{background:linear-gradient(135deg,var(--navy),#0b2344 60%,#12365c);color:#fff;padding:22px 0}
header.site .inner{width:min(960px,calc(100% - 32px));margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none}
.brand:hover{text-decoration:none}
.logo{width:46px;height:46px;display:grid;place-items:center;border-radius:13px;background:radial-gradient(circle at 30% 22%,#fff8c7,#f2b705 45%,#b7791f);border:2px solid rgba(255,255,255,.5);flex:0 0 auto}
.brand b{display:block;color:#fff;font-size:19px;letter-spacing:-.02em;line-height:1.2}
.brand span{display:block;color:#94a3b8;font-size:11px;margin-top:2px}
.home-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:999px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;font-size:13px;font-weight:800;text-decoration:none;transition:.15s}
.home-btn:hover{background:rgba(255,255,255,.2);text-decoration:none}
.crumbs{width:min(960px,calc(100% - 32px));margin:14px auto 0;font-size:12px;color:#94a3b8;padding:0 2px}
.crumbs a{color:#e2e8f0}
main{width:min(960px,calc(100% - 32px));margin:22px auto 40px}
article{background:var(--paper);border:1px solid var(--line);border-radius:20px;box-shadow:0 12px 32px rgba(15,23,42,.08);padding:clamp(20px,4vw,44px)}
article h1{margin:0 0 6px;font-size:clamp(23px,3.6vw,30px);color:var(--navy);letter-spacing:-.02em;line-height:1.35}
.updated{color:var(--muted);font-size:12px;margin-bottom:18px;display:block}
article h2{margin:34px 0 10px;padding-left:12px;border-left:5px solid var(--gold);font-size:19px;color:var(--navy)}
article h3{margin:22px 0 6px;font-size:16px;color:var(--navy2)}
article p{margin:10px 0}
article ul,article ol{margin:8px 0 8px 4px;padding-left:22px}
article li{margin:5px 0}
.notice{border-radius:14px;padding:14px 16px;font-size:13.5px;line-height:1.8;margin:16px 0}
.notice.warn{background:#fff7ed;border:1px solid #fed7aa;color:#7c2d12}
.notice.info{background:#eff6ff;border:1px solid #bfdbfe;color:#1e3a8a}
.notice.ok{background:#ecfdf5;border:1px solid #bbf7d0;color:#065f46}
table.info{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px}
table.info th,table.info td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
table.info th{width:38%;background:#f8fafc;color:var(--navy);font-weight:800}
.num-table td,.num-table th{text-align:center}
.lead{font-size:16px;color:#1f2937;background:#f8fafc;border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.cta-box{margin-top:26px;border-radius:16px;padding:16px 18px;background:linear-gradient(135deg,#071a33,#12365c);color:#e2e8f0}
.cta-box b{color:#fff}
.cta-box a{color:#fcd34d;font-weight:800}
.owner-note{margin:16px 0;padding:14px 16px;border-radius:14px;background:#f8fafc;border:1px dashed #cbd5e1;font-size:13.5px;color:#334155;line-height:1.8}
.owner-note::before{content:"✍ 運営メモ";display:block;font-weight:900;color:var(--red);margin-bottom:4px;font-size:12px;letter-spacing:.06em}
footer.site{background:linear-gradient(180deg,#0b2344,var(--navy));color:#cbd5e1;border-top:4px solid var(--gold);margin-top:40px}
footer.site .inner{width:min(960px,calc(100% - 32px));margin:0 auto;padding:26px 0 10px}
footer.site nav{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.12)}
footer.site nav a{color:#cbd5e1}
footer.site nav a:hover{color:#fff}
footer.site .legal{padding:14px 0 20px;font-size:11.5px;color:#94a3b8;line-height:1.8}
footer.site .legal a{color:#cbd5e1}
@media (max-width:640px){
  body{font-size:14px}
  header.site .inner{flex-direction:column;align-items:flex-start;gap:12px}
  .home-btn{width:100%;justify-content:center}
  article{border-radius:16px}
  table.info th{width:42%}
  footer.site nav{flex-direction:column;gap:8px}
}
'''

SVG_LOGO = ('<svg viewBox="0 0 48 48" style="width:62%;height:62%" aria-hidden="true">'
            '<circle cx="16.5" cy="29.5" r="12.5" fill="#fffdf5" stroke="#3f2600" stroke-width="3.4"/>'
            '<circle cx="12" cy="25" r="3.4" fill="#f2c94c"/>'
            '<text x="16.5" y="34.8" text-anchor="middle" font-size="14.5" font-weight="900" fill="#3f2600" font-family="sans-serif">ミ</text>'
            '<path d="M26.5 21.5 L32.5 15.5 L36.5 19 L45 9.5" fill="none" stroke="#3f2600" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M37 9.5 h8 v8" fill="none" stroke="#3f2600" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>')


def shell(filename: str, title: str, desc: str, crumb_inner: str, h1: str,
          date_pub: str, body: str) -> None:
    nav = '\n        '.join(f'<a href="../{h}">{l}</a>' for h, l in NAV_LINKS)
    nav += '\n        <a href="index.html">コラム一覧</a>'
    ld = ('{\n    "@context": "https://schema.org",\n    "@type": "Article",\n'
          f'    "headline": "{title}",\n    "description": "{desc}",\n'
          f'    "image": "{DOMAIN}/og-image.jpg",\n    "datePublished": "{date_pub}",\n'
          f'    "dateModified": "{date_pub}",\n'
          '    "author": {"@type": "Organization", "name": "ミニロト分析ナビ運営事務局"},\n'
          f'    "publisher": {{"@type": "Organization", "name": "ミニロト分析ナビ運営事務局", "url": "{DOMAIN}/"}},\n'
          f'    "mainEntityOfPage": "{DOMAIN}/blog/{filename}",\n    "inLanguage": "ja"\n  }}')
    def _jdate(iso: str) -> str:
        y, m, d = iso.split('-')
        return f'{int(y)}年{int(m)}月{int(d)}日'
    pub_j = _jdate(date_pub)
    mod_j = _jdate(date_pub)
    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>{title} | コラム | ミニロト分析ナビ</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1" />
  <link rel="canonical" href="{DOMAIN}/blog/{filename}" />
  <meta name="theme-color" content="#071a33" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{DOMAIN}/blog/{filename}" />
  <meta property="og:image" content="{DOMAIN}/og-image.jpg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet" />
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='29' fill='%23f2b705' stroke='%23b7791f' stroke-width='4'/%3E%3Ctext x='32' y='43' font-size='30' text-anchor='middle' font-family='sans-serif' font-weight='bold' fill='%23372600'%3Eミ%3C/text%3E%3C/svg%3E" />
  <script type="application/ld+json">
  {ld}
  </script>
  <style>{SHELL_CSS}</style>
</head>
<body>
<div class="topbar-line"></div>
<header class="site">
  <div class="inner">
    <a class="brand" href="../index.html"><span class="logo">{SVG_LOGO}</span><span><b>ミニロト分析ナビ</b><span>MINILOTO ANALYSIS NAVI · miniloto-navi.com</span></span></a>
    <a class="home-btn" href="../index.html">← ホームに戻る</a>
  </div>
  <nav class="crumbs" aria-label="パンくず"><a href="../index.html">ホーム</a> &gt; {crumb_inner}</nav>
</header>
<main>
  <article>
    <h1>{h1}</h1>
    <span class="updated">公開日：{pub_j} ｜ ミニロト分析ナビ運営事務局</span>
{body}
  </article>
</main>
<footer class="site">
  <div class="inner">
    <nav>
        {nav}
    </nav>
    <div class="legal">
      当サイトはミニロトに関する<b>統計情報のみを提供する非公式の情報サイト</b>です。当選を保証するものではありません。購入・換金の前には必ず<a href="https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html" target="_blank" rel="noopener noreferrer">公式発表（みずほ銀行）</a>をご確認ください。<br />
      © 2026 ミニロト分析ナビ運営事務局 · お問い合わせ：<a href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
  </div>
</footer>
</body>
</html>
'''
    (BLOG / filename).write_text(html, encoding='utf-8')


ARTICLES = []
def A(file, date, title, desc, cat):
    ARTICLES.append(dict(file=file, date=date, title=title, desc=desc, cat=cat))

# (카테고리, 파일, 날짜, 제목) 등록 — body 는 아래 BODIES 사전에서 가져옴
A('basics.html',              '2026-08-04', 'ミニロトの基本ルールと確率の仕組み', '1〜31から5個を選ぶミニロトのルール、等級の条件、組合せ169,911通りと各等の理論確率を初心者向けに整理しました。', '基本')
A('combination-formula.html', '2026-08-04', '組合せの数の公式でミニロトを分解する', 'なぜ169,911通りなのか。掛け算と割り算だけで導ける組合せの公式を、各等の確率計算と一緒にやさしく解説。', '基本')
A('loto-types.html',          '2026-08-04', 'ミニロト・ロト6・ロト7・ナンバーズ — 種類を比較', '日本の数字選択式宝くじの違い（価格・抽選日・1等確率・賞金規模）を表で整理。自分に合う種類の選び方。', '基本')
A('win-reality.html',         '2026-08-04', 'ミニロト当選確率の現実 — 数字は正直です', '1等1/169,911を日常の感覚に置き換え、払戻率50%未満という期待値の現実まで。運営が正直に整理しました。', '基本')
A('faq.html',                 '2026-08-04', 'ミニロトよくある質問（FAQ）', 'クイックピックと自選はどちらがいい？連番は出る？複数口は1回で買うべき？など、統計サイト運営の立場から率直に回答。', '基本')

A('top10-numbers.html',       '2026-08-04', '出現回数が多い数字 TOP10【第1回〜第1397回】', '当サイトの全データ6,985個分を集計。出現トップの11は265回。誤差の範囲と読み方まで実測で示します。', '実録')
A('absent-numbers.html',      '2026-08-04', 'いま出ていない数字の分析【第1397回時点】', '最新回時点で最長未出現は15の18回分。18回連続で出ない確率は約4%で意外と起きる話、を計算で解説。', '実録')
A('consecutive-numbers.html', '2026-08-04', '連番はどのくらい出ている？全1,397回で調査', '直近でも25・26・27の3連番が出ています。連番入りの回は52.5%。「連番は珍しい」はデータでどうなるか。', '実録')
A('winners-analysis.html',    '2026-08-04', '当選の現実 — 1回の抽選で何人が当たる？', '最新回は1等21口・4等51,536口。約180万円の回から満額4,000万円の回まで。データで見る賞金のリアル。', '実録')
A('statistics-reading.html',  '2026-08-04', '出現回数・未出現期間の正しい読み方', '統計画面に出る「出現回数」「未出現期間」「長期間出ていない数字」の意味と、勘違いしやすいポイントを解説。', '実録')
A('independence.html',        '2026-08-04', '過去データは未来を予測できるか — 独立抽選の考え方', '「連続して出た数字は次も出る？」など、よくある誤解の背景にあるギャンブラーの誤謬と、統計の健全な使い方。', '実録')
A('prize-structure.html',     '2026-08-04', '賞金額が毎回違う理由 — キャリーオーバーと分配の仕組み', '同じ1等なのに回によって賞金が違うのはなぜ？売上からの払戻・当選口数による分割とキャリーオーバーを解説。', '実録')

A('quickpick-vs-jisen.html',  '2026-08-04', 'クイックピックと自選、結局どちらがいいのか', '確率はまったく同じ。では何で選ぶべきか。記録・検証できる自選派向けの使い方まで運営視点で整理。', '実践')
A('avoid-patterns.html',      '2026-08-04', 'できれば避けたい組合せパターン（分割リスクの話）', '確率は同じでも「当たった時に損」になりやすい人気パターンがある。誕生日・ゾロ目・1-2-3-4-5の罠。', '実践')
A('backtest.html',            '2026-08-04', 'バックテストで選び方を検証する方法', '「この選び方、過去ならどうだった？」を確かめる方法。ランダム基準線との比較の読み取り方と注意点。', '実践')
A('coverage.html',            '2026-08-04', 'カバレッジ設計入門 — 少ない枚数で広くカバーする考え方', '複数口を組み合わせて広範囲を押さえるウィーリングの基礎と、枚数とのトレードオフ。ツールの使い方つき。', '実践')
A('statistics-guide.html',    '2026-08-04', 'ミニロト統計の見方・完全ガイド（当サイトの使い方）', '10個のメニューをどう使い分けるか。初めての方向けの3ステップから、データを読む実践まで運営が案内。', '実践')
A('marksheet-guide.html',     '2026-08-04', 'マークシートの書き方と購入の流れ', 'A〜Eブロックの見方、マークのコツ、クイックピック欄の使い方。当サイトの印刷ツールで事前に整理する方法も。', '実践')
A('responsible-play.html',    '2026-08-04', '予算管理と責任ある遊び方 — 健全に楽しむために', '宝くじは「余裕資金の娯楽」が原則。購入前に決めたい予算ルール、注意したいサイン、20歳以上のルール。', '実践')
A('cashing.html',             '2026-08-04', '当選したらどうする？換金の流れと注意点', '当選択確認から換金場所・本人確認・支払期限まで。うっかり損をしないための基本の流れを整理。', '実践')

BODIES = {}

BODIES['basics.html'] = '''
    <p class="lead">ミニロトは「31個の数字から5個を選ぶ」シンプルな数字選択式宝くじです。この記事では、ルール・等級条件・理論確率を、当サイトの統計を読むための基礎知識として整理します。</p>

    <h2>基本ルール</h2>
    <ul>
      <li><b>数字の範囲</b>：1〜31の中から異なる5個を選択（本数字）。1口200円。</li>
      <li><b>抽選</b>：本数字5個＋ボーナス数字1個の合計6個が抽選されます（毎週火曜日）。</li>
      <li><b>ボーナス数字の役割</b>：2等の判定だけに使われます。</li>
    </ul>

    <h2>等級と条件</h2>
    <table class="info">
      <tr><th>等級</th><th>条件</th></tr>
      <tr><td>1等</td><td>本数字5個すべて一致</td></tr>
      <tr><td>2等</td><td>本数字4個一致＋ボーナス数字1個一致</td></tr>
      <tr><td>3等</td><td>本数字4個一致</td></tr>
      <tr><td>4等</td><td>本数字3個一致</td></tr>
    </table>

    <h2>理論確率（全組合せ169,911通り）</h2>
    <table class="info num-table">
      <tr><th>等級</th><th>当たる組合せ数</th><th>理論確率（約）</th></tr>
      <tr><td>1等</td><td>1通り</td><td>1 / 169,911</td></tr>
      <tr><td>2等</td><td>5通り</td><td>1 / 33,982</td></tr>
      <tr><td>3等</td><td>125通り</td><td>1 / 1,359</td></tr>
      <tr><td>4等</td><td>3,250通り</td><td>1 / 52</td></tr>
    </table>
    <p>数字の選び方を変えても、<b>1口あたりの確率はどの組合せも完全に同じ</b>です。「出やすい組合せ」は存在しません。当サイトのスコアや統計は、確率を変えるためではなく、<b>組合せのバランスや被りやすさを確認する参考情報</b>として提供しています。</p>

    <div class="notice info">全組合せ169,911通りは「31個から5個を選ぶ組合せの数」で計算できます。詳しい計算は<a href="combination-formula.html">組合せの数の公式の記事</a>で図解なしで導いています。</div>

    <div class="cta-box"><b>実際のデータで確認</b><br />第1回から最新回までの抽選結果・賞金データは<a href="../index.html">トップページのデータメニュー</a>で無料公開しています。</div>
'''

BODIES['combination-formula.html'] = '''
    <p class="lead">「なぜミニロトは169,911通りなの？」この数字、実は掛け算と割り算だけで出せます。難しい記号なしで、組合せの考え方を導いてみます。</p>

    <h2>まず順番を気にして数える</h2>
    <p>1〜31から5個を順番に選ぶ場合の数は <b>31×30×29×28×27</b>。途中で使った数字は二度使えないので、1個ずつ候補が減ります。</p>

    <h2>順番を気にしないので割る</h2>
    <p>くじでは「1,2,3,4,5」と「5,4,3,2,1」は同じ一組です。5個の並べ方は <b>5×4×3×2×1＝120通り</b>あるので、さっきの数を120で割ります。</p>
    <div class="notice info">31×30×29×28×27 ÷ 120 ＝ <b>169,911通り</b>。これが全組合せで、1等の分母です。</div>

    <h2>各等の確率も同じ手で出る</h2>
    <table class="info">
      <tr><th>等級</th><th>当たる数え方</th><th>組合せ数</th></tr>
      <tr><td>1等</td><td>本数字5個ぴったり＝1通り</td><td>1</td></tr>
      <tr><td>2等</td><td>本数字5個から4個選ぶ(5通り) × 残り1個がボーナス</td><td>5</td></tr>
      <tr><td>3等</td><td>本数字から4個(5通り) × 残り1個はボーナス以外の25個</td><td>125</td></tr>
      <tr><td>4等</td><td>本数字から3個(10通り) × 残り2個を外れ数字26個から選ぶ(325通り)</td><td>3,250</td></tr>
    </table>
    <p>分子を分母の169,911で割ると各等の理論確率になります。確率とは「数えられない運の話」ではなく、<b>数えられる算数の話</b>です。</p>

    <h2>知っておくと変わること</h2>
    <p>「31個全部に1票ずつの公平な数」という出発点に立つと、出やすい数字・運のいい組合せを探すより、<b>自分の買い方を数で点検する</b>方が現実的だと腹落ちするはずです。当サイトはそのための道具です。</p>
'''

BODIES['loto-types.html'] = '''
    <p class="lead">日本の数字選択式宝くじはミニロトだけではありません。価格・抽選日・1等確率・賞金規模の違いを知ると、自分に合う種類が見えてきます。</p>

    <h2>主な種類の比較</h2>
    <table class="info">
      <tr><th>種類</th><th>選び方</th><th>1口</th><th>抽選</th><th>1等確率（約）</th></tr>
      <tr><td><b>ミニロト</b></td><td>1〜31から5個</td><td>200円</td><td>週1（火）</td><td>1 / 169,911</td></tr>
      <tr><td>ロト6</td><td>1〜43から6個</td><td>200円</td><td>週2（月・木）</td><td>1 / 6,096,454</td></tr>
      <tr><td>ロト7</td><td>1〜37から7個</td><td>300円</td><td>週1（金）</td><td>1 / 10,295,472</td></tr>
      <tr><td>ナンバーズ3</td><td>000〜999の3桁</td><td>200円</td><td>平日毎日</td><td>1 / 1,000（ストレート）</td></tr>
      <tr><td>ナンバーズ4</td><td>0000〜9999の4桁</td><td>200円</td><td>平日毎日</td><td>1 / 10,000（ストレート）</td></tr>
    </table>

    <h2>それぞれの性格（運営の印象）</h2>
    <ul>
      <li><b>ミニロト</b>：1等確率がロト6の約36倍当たりやすい代わりに、賞金は数百万〜4,000万円級。堅実な夢の種類。</li>
      <li><b>ロト6</b>：バランス型。当たりやすさと賞金の中間。</li>
      <li><b>ロト7</b>：最難関だがキャリーオーバー時は10億円級。大きな夢専用。</li>
      <li><b>ナンバーズ</b>：数字桁を当てる感覚系。毎日抽選なのでペースに注意。</li>
    </ul>

    <h2>当サイトがミニロト専門の理由</h2>
    <p>組合せが169,911通りと「全データを手のひらで見渡せる規模」だからです。統計・検証・カバレッジ設計まで一貫して提供できるのは、この規模感あってこそ。大きな夢はロト7で追い、<b>データで遊ぶならミニロト</b>、という棲み分けが現実的だと考えています。</p>

    <div class="notice info">各種の公式ルール・最新の賞金情報は、必ず宝くじ公式サイト（みずほ銀行）で確認してください。</div>
'''

BODIES['win-reality.html'] = '''
    <p class="lead">「ミニロトはロト6より当たりやすい」は本当です。ただし1等の理論確率は1/169,911。気持ちよく遊ぶために、運営としては数字の現実から隠さずお伝えします。</p>

    <h2>1/169,911を日常の言葉に</h2>
    <ul>
      <li>満員の大きなサッカースタジアム2〜3個分の観客の中に自分ひとりの当たりがあるイメージ。</li>
      <li>毎週1口ずつ買い続けた場合、1等に当たるのは平均で<b>約3,268年に1回</b>（169,911週）。</li>
      <li>2等は約653年に1回、3等は約26年に1回、4等は約1年に1回の頻度。</li>
    </ul>

    <h2>期待値の現実</h2>
    <p>宝くじの払戻率は法律で50%未満と決められています。つまり1口200円の平均的な回収額は100円未満。長く買い続けるほど平均に近づくので、<b>「増やす手段」には決してなりません</b>。</p>

    <h2>それでも僕が統計サイトを運営する理由</h2>
    <div class="owner-note">正直に言うと、最初は「分析すれば当たるはず」と思っていました。でも1,397回分のデータを全部見て分かったのは、<b>どの数字も平等にランダム</b>だという当たり前の事実。それならむしろ「分かっていて遊ぶ」方が楽しい。過熱せず、記録して、検証して、たまに当たって喜ぶ。当サイトはそういう遊び方の道具です。</div>

    <div class="notice warn">「確実に当たる」「的中実績」をうたうサイト・販売には手を出さないでください。確率は数式で決まっており、誰にも変えられません。</div>

    <div class="cta-box"><b>数字で納得してから遊ぶ</b><br /><a href="../index.html">ダッシュボード</a>の理論確率表示と、<a href="../index.html">技法研究の予算計算</a>で口数と確率を確認できます。</div>
'''

BODIES['faq.html'] = '''
    <p class="lead">統計サイトによく届く質問をまとめました。結論はいつも同じです——確率は変えられない。だからこそ「自分の選び方」を整えるのが大切です。</p>

    <h2>Q1. クイックピックと自選（自分で選ぶ）はどちらがいい？</h2>
    <p>当選確率は同じです。クイックピックは偏りなくランダムに選べる利点、自選は「自分のルールで記録・検証できる」利点があります。詳しくは<a href="quickpick-vs-jisen.html">比較記事</a>で掘り下げています。</p>

    <h2>Q2. 連番（例：5・6・7）は出にくい？</h2>
    <p>出にくいわけではありません。どの5個の組合せも確率は1/169,911で同一です。実データでは連番入りの回が全体の52.5%もあります（<a href="consecutive-numbers.html">連番の調査</a>）。</p>

    <h2>Q3. 誕生日の数字で買い続けるのは？</h2>
    <p>確率上は他の組合せと同じ。ただし日付は1〜31の範囲に集中するため、同じ考えの人と組合せが似やすく、当たったときに口数が増える可能性はあります（<a href="prize-structure.html">賞金の仕組み</a>）。</p>

    <h2>Q4. 「よく出る数字」だけで構成するのは？</h2>
    <p>過去の出現回数は結果の記録であり、未来の確率を高めません（<a href="independence.html">独立抽選の考え方</a>）。トップの11でもツボの15でも、次回出る確率は同じ約16.1%です（<a href="top10-numbers.html">出現TOP10の実測</a>）。</p>

    <h2>Q5. 複数口は1回でまとめて買うべき？</h2>
    <p>1等の理論確率は「買った枚数 ÷ 169,911」。月の枚数が同じなら、まとめても分けても累計確率は変わりません。ただしまとめ買いでの予算オーバーは厳禁です（<a href="responsible-play.html">予算管理</a>）。</p>

    <h2>Q6. 当たりやすい売り場ってあるの？</h2>
    <p>ありません。当たるかどうかは抽選で決まり、売り場とは無関係です。「よく当たりが出る売り場」は販売量が多いことの反映です。</p>

    <h2>Q7. 当サイトの「参考スコア」は何ですか？</h2>
    <p>過去データにもとづく統計上の参考値です。確率を高めるものではなく、数字のバランス・出現動向・相性の特徴を点数化しただけのもので、当選保証はありません。</p>

    <div class="cta-box"><b>ツールで実際に確認</b><br /><a href="../index.html">トップページ</a>の使い方ガイドから、各機能へそのまま進めます。</div>
'''

BODIES['top10-numbers.html'] = '''
    <p class="lead">当サイトに収録した第1回〜第1397回（2026/7/28実施分）までの全データから、本数字の出現回数を全部数えました。総出現6,985個、1数字あたりの平均は225.3回です。</p>

    <h2>出現回数ランキング TOP10</h2>
    <table class="info num-table">
      <tr><th>順位</th><th>数字</th><th>出現回数</th></tr>
      <tr><td>1</td><td><b>11</b></td><td>265回</td></tr>
      <tr><td>2</td><td><b>31</b></td><td>249回</td></tr>
      <tr><td>3</td><td><b>14</b></td><td>245回</td></tr>
      <tr><td>4</td><td><b>19</b></td><td>244回</td></tr>
      <tr><td>5</td><td><b>21</b></td><td>242回</td></tr>
      <tr><td>6</td><td><b>27</b></td><td>240回</td></tr>
      <tr><td>7</td><td><b>22</b></td><td>239回</td></tr>
      <tr><td>8</td><td><b>2</b></td><td>238回</td></tr>
      <tr><td>8</td><td><b>30</b></td><td>238回</td></tr>
      <tr><td>10</td><td><b>3</b></td><td>236回</td></tr>
    </table>
    <p>参考に、いちばん少ないのは<b>15の194回</b>、次いで6の196回、26の200回でした。</p>

    <h2>「差」はどのくらい誤差なのか</h2>
    <p>ランダムでも回数にはバラつきが出ます。1回の抽選で特定の数字が出る確率は5/31≈16.1%。これを1,397回繰り返したときの平均は225.3回、標準的なバラつき幅（標準偏差）は約±13.7回。つまり<b>だいたい198〜253回の範囲に収まるのが普通</b>です。</p>
    <ul>
      <li>トップの11（265回）は範囲をやや上回り、最下位の15（194回）はやや下回ります。</li>
      <li>ただし31個の数字を見れば、どれか1つくらい範囲を外れるのは珍しくありません。</li>
    </ul>

    <h2>運営としての読み方</h2>
    <div class="owner-note">「11は出やすい！」と言いたくなる数字ですが、テストでこういう偏りは長期データでも普通に出ます。だから当サイトでは「次に11が出る確率は約16.1%のまま」と毎回注記しています。ランキングはネタとして楽しみつつ、判断材料にはしない——これが健全な使い方だと考えています。</div>

    <div class="cta-box"><b>自分で確かめる</b><br /><a href="../index.html">統計メニュー</a>で期間を切り替えたランキングを確認できます。CSV全データも無料で公開中です。</div>
'''

BODIES['absent-numbers.html'] = '''
    <p class="lead">「しばらく出ていない数字」は毎週話題になります。第1397回（2026/7/28）時点で、当サイトのデータから現在地を整理しました。</p>

    <h2>現在の未出現トップ</h2>
    <table class="info num-table">
      <tr><th>数字</th><th>最後に出てからの回数</th></tr>
      <tr><td><b>15</b></td><td>18回ぶり</td></tr>
      <tr><td>18</td><td>14回ぶり</td></tr>
      <tr><td>19</td><td>14回ぶり</td></tr>
      <tr><td>7</td><td>13回ぶり</td></tr>
      <tr><td>13</td><td>13回ぶり</td></tr>
      <tr><td>21</td><td>11回ぶり</td></tr>
    </table>
    <p>ちなみに第1397回に出た本数字は3・6・14・20・31、ボーナスは17でした。</p>

    <h2>「18回も出ない」は珍しいのか</h2>
    <p>特定の数字が1回の抽選で出ない確率は26/31≈83.9%。これが18回続く確率は(26/31)の18乗で<b>約4.2%</b>。なんと、週に1度くじを引く人が「1年に2回くらい出くわす」レベルの、かなり普通の出来事です。</p>
    <div class="notice info">逆に言えば「長く出ていないから、そろそろ出る」の期待も約16.1%のまま。出ない確率が蓄積されることはありません。</div>

    <h2>使いどころ</h2>
    <p>未出現の数字は「避ける理由」にも「選ぶ理由」にもなりません。ただ、組合せのバリエーションを考えるとき「最近出た数字だけに偏っていないか」「長く出ていない数字ばかりに寄っていないか」を点検する物差しには使えます。</p>

    <div class="cta-box"><b>最新の未出現を確認</b><br /><a href="../index.html">統計メニューの未出現ランキング</a>は最新データで自動更新されています。</div>
'''

BODIES['consecutive-numbers.html'] = '''
    <p class="lead">「連番（例：25・26）はめったに出ない」は本当でしょうか。全1,397回を1件ずつ調べました。近々の実例もあります。</p>

    <h2>実績値</h2>
    <table class="info">
      <tr><th>内容</th><th>回数（割合）</th></tr>
      <tr><td>本数字に連番ペアが1組以上入った回</td><td><b>734回（52.5%）</b></td></tr>
      <tr><td>3連続（例：25・26・27）が入った回</td><td><b>82回（5.9%）</b></td></tr>
    </table>
    <p>つまり<b>2回に1回以上、連番は出ています</b>。「連番だから外す」は、半分以上の当選パターンを捨てることになります。</p>

    <h2>直近の実例</h2>
    <p>第1395回（2026/7/14）の本数字は 20・25・26・27・31。見事に <b>25・26・27の3連番</b>が入っていました。このように、見るからに「偏って見える」組合せも普通に当たります。</p>

    <h2>理屈を整理すると</h2>
    <ul>
      <li>組合せ全部で見れば、連番入りより連番なしの方が数が多い→単独で見ると「連番は珍しい」に感じる。</li>
      <li>でも連番入りの組合せの総数は膨大（数万通り）→実際の抽選では半分以上の回で出る。</li>
      <li>どちらも正しい。確率は「組合せ単位」では全部同じ、「パターンの集団」では出現頻度に差がある、というだけの話です。</li>
    </ul>

    <div class="owner-note">連番を避けると「見た目がきれいな買い方」にはなりますが、当たりからは遠ざかります。僕は連番を避けません。むしろ意図的に1組入れる選択肢もアリだと思っています（確率が同じなら好みでいい、という意味です）。</div>

    <div class="cta-box"><b>自分の組合せを点検</b><br /><a href="../index.html">専門分析のバランスチェック</a>で連番ペアの有無も表示されます。</div>
'''

BODIES['winners-analysis.html'] = '''
    <p class="lead">「実際、どのくらいの人が当たっているの？」この問いに、最新回のデータで答えます。当サイトは全過去回の当選口数・賞金額も収録しています。</p>

    <h2>最新回（第1397回・2026/7/28）の実績</h2>
    <table class="info num-table">
      <tr><th>等級</th><th>当選口数</th><th>賞金額（1口）</th></tr>
      <tr><td>1等</td><td>21口</td><td>7,299,700円</td></tr>
      <tr><td>2等</td><td>87口</td><td>126,500円</td></tr>
      <tr><td>3等</td><td>1,779口</td><td>10,700円</td></tr>
      <tr><td>4等</td><td>51,536口</td><td>900円</td></tr>
    </table>
    <p>4等は毎週数万口単位で出ています。「小当たり」は案外身近。一方で1等は全国で週にわずか十数〜数十人という世界です。</p>

    <h2>1等賞金の振れ幅</h2>
    <p>過去データでは、1等賞金は<b>最小で約180万円台</b>（当選11口の第28回・2000年）から、<b>満額の4,000万円</b>（当選3口の第7回・1999年）まで幅があります。当たった人数とキャリーオーバーで変わる構造です（<a href="prize-structure.html">賞金の仕組み</a>）。</p>

    <h2>「儲かる人」はいるのか</h2>
    <p>高額当選者は確かに存在します。ただし母数で見れば週に十数人。全年齢・全国民での当選経験者はごくわずかです。払戻率50%未満という構造上、<b>全体で見れば差し引きマイナス</b>が数学の答え。だから「夢の代金」として楽しむのが健全です。</p>

    <div class="owner-note">当選発表の週明けに「自分の組合せは？」とワクワクする時間——あれを心の底から楽しむ人は、宝くじの一番おいしい部分を味わっていると思います。当サイトの当選確認ツールは、そのワクワクを早く片づけられるように作りました（笑）。</div>

    <div class="cta-box"><b>自分の数字を照合</b><br /><a href="../index.html">当選確認メニュー</a>で、手持ち組合せと任意回の照合・賞金表示ができます。</div>
'''

BODIES['statistics-reading.html'] = '''
    <p class="lead">統計メニューでよく見る「出現回数」「未出現期間」。便利な指標ですが、読み方を間違えると誤解につながります。この記事では、数字の意味と使いどころを整理します。</p>

    <h2>出現回数とは</h2>
    <p>対象期間内に、その数字が本数字（またはボーナス）として何回出たかを数えたものです。1回の抽選で特定の数字が出る確率は5/31≈約16.1%なので、100回分なら平均で約16回出る計算になります。</p>
    <ul>
      <li>平均より多い数字は「ホット」、少ない数字は「コールド」と呼ばれることがあります。</li>
      <li>実測のトップ・ワーストは<a href="top10-numbers.html">出現TOP10の記事</a>に全数値を公開しています。</li>
    </ul>

    <h2>未出現期間とは</h2>
    <p>最新の抽選から数えて、その数字が最後に出てから何回分経過したかを示します。長く出ていない数字は「そろそろ出そう」と感じやすいのですが…</p>
    <div class="notice warn">未出現期間が長い＝次に出やすい、とは<b>なりません</b>。抽選は毎回リセットされるため、理論上の出現確率は約16.1%のままです。現在地の実例は<a href="absent-numbers.html">未出現の分析記事</a>をどうぞ。</div>

    <h2>期間の切り替え方（当サイトの使い方）</h2>
    <ul>
      <li><b>全期間</b>：長期の平均像。数字ごとの差は小さくなります。</li>
      <li><b>直近50〜100回</b>：直近の動き。波はありますが、偶然の変動も大きい範囲です。</li>
      <li><b>直近300〜1000回</b>：中長期の参考。短期と長期の差を見るのに向いています。</li>
    </ul>

    <div class="cta-box"><b>統計を今すぐ確認</b><br /><a href="../index.html">統計/相性メニュー</a>では期間切替・出現回数ランキング・未出現ランキングを無料で使えます。</div>
'''

BODIES['independence.html'] = '''
    <p class="lead">「前回出た数字は次は出にくい」「長く出ていないからそろそろ出る」— こうした直感は多くの人が持ちます。確率の世界ではどう考えるべきかを整理します。</p>

    <h2>抽選は「独立」している</h2>
    <p>ミニロトの抽選は、毎回まったく新しい条件で行われます。前の結果は次の結果に<b>一切影響しません</b>。これを「独立した試行」と呼びます。</p>
    <ul>
      <li>前回「3」が出ても、次回「3」が出る確率は約16.1%のまま。</li>
      <li>10回連続で「31」が出ていなくても、次回「31」の確率は変わりません。</li>
    </ul>
    <p>実際のデータでも、<b>直前の回と数字が1個以上かぶる回は63.6%</b>あります。「出たばかりの数字は避けるべき」はデータが否定しています。</p>

    <h2>ギャンブラーの誤謬に注意</h2>
    <p>「しばらく出ていないから、そろそろ出るはず」という感覚は<b>ギャンブラーの誤謬</b>と呼ばれる有名な錯覚です。コイン投げで表が5回続いても、次に裏が出る確率は50%のまま、というのと同じ構造です。</p>

    <h2>それでも統計を見る意味</h2>
    <ol>
      <li><b>組合せのバランス確認</b>：合計値・奇偶・高低の偏りを点検する。</li>
      <li><b>バリエーション確保</b>：同じ数字ばかり買い続けていないかを記録で点検する。</li>
      <li><b>人気組合せの回避検討</b>：当たったときの分割リスクを考える（<a href="avoid-patterns.html">避けたいパターン</a>）。</li>
      <li><b>検証</b>：自分の方法が「ランダム買い」と比べてどうだったかを確かめる（<a href="backtest.html">バックテスト</a>）。</li>
    </ol>
    <div class="notice ok">統計は「当てる道具」ではなく「自分の選び方を点検する物差し」。当サイトはこの立場で、当選保証なしの参考情報として提供しています。</div>
'''

BODIES['prize-structure.html'] = '''
    <p class="lead">ミニロトの1等賞金は、回によって数百万円〜4,000万円まで大きく変わります。数字は同じ5個なのに、なぜ違うのでしょうか。仕組みを整理します。</p>

    <h2>賞金の原資は「売上」</h2>
    <p>宝くじの賞金は、その回の販売口数（売上）から払戻金としてプールされ、等級ごとに配分されます。売上が多い回は賞金総額も大きくなります。</p>

    <h2>当選口数で按分される</h2>
    <p>各等の賞金総額は、<b>当たった口数で等分</b>されます。だから次のようなことが起きます。</p>
    <ul>
      <li>1等の当選口数が多い回 → 1口あたりの賞金は少なくなる。</li>
      <li>誕生日（1〜31）だけの組合せなど人気の数字が当たると、口数が増えて1人あたりは目減りしやすい、とよく言われます（<a href="avoid-patterns.html">人気パターンの話</a>）。</li>
    </ul>

    <h2>キャリーオーバーとは</h2>
    <p>1等に当選がない場合、その分は<b>次回の1等賞金に持ち越され</b>ます。持ち越しが続くと1等賞金が膨らみ、上限に達することがあります。最新の当選状況は公式発表で確認できます。</p>

    <h2>実例（当サイトデータより）</h2>
    <p>1等賞金が約180万円まで下がった回（第28回・当選11口）もあれば、満額4,000万円に届いた回（第7回・当選3口）もあります。賞金の振れは「数字の運」ではなく「人数と持ち越し」で決まります。</p>

    <div class="cta-box"><b>実データで確認</b><br /><a href="../index.html">トップのデータメニュー</a>で、各回の賞金額と当選口数を検索・並べ替えできます。</div>
'''

BODIES['quickpick-vs-jisen.html'] = '''
    <p class="lead">売り場の機械に任せるクイックピック（QP）か、自分で数字を選ぶ自選か——よくある論争に、結論を出します。結論は「確率は同じ。違いは遊び方」です。</p>

    <h2>確率はまったく同じ</h2>
    <p>QPで選ばれた組合せも、自分で考えた組合せも、1等の理論確率は1/169,911で同一です。「機械は当たらない数字を出す」という噂も根拠はありません（実際にQPでの1等当選者は大勢います）。</p>

    <h2>比較表</h2>
    <table class="info">
      <tr><th>項目</th><th>クイックピック</th><th>自選</th></tr>
      <tr><td>当選確率</td><td>同じ</td><td>同じ</td></tr>
      <tr><td>偏りのなさ</td><td>ほぼ完全ランダム</td><td>自分の癖が入る</td></tr>
      <tr><td>記録・検証</td><td>しにくい（毎回変わる）</td><td>自分のルールで検証できる</td></tr>
      <tr><td>愛着</td><td>薄め</td><td>「自分の数字」感がある</td></tr>
      <tr><td>人気回避</td><td>機械まかせ</td><td>意識すれば人気パターンを外せる</td></tr>
    </table>

    <h2>運営のおすすめの使い分け</h2>
    <ul>
      <li><b>気軽さ重視</b>：QPで1〜2口。考えすぎないのが一番健全。</li>
      <li><b>記録して楽しみたい</b>：自選＋当サイトの<a href="../index.html">数字生成</a>で条件を付けて10口を保存し、当選確認・印刷まで一連の流れで管理。</li>
      <li><b>どっちつかず防止</b>：QPと自選を混ぜ買いしても確率上は何も変わりません。予算の中で好きに楽しんでOKです。</li>
    </ul>

    <div class="owner-note">ちなみに当サイトの数字生成には「完全ランダム」モードもあります。売り場のQPに行く前に家で候補を出して、気に入ったものだけ買う使い方もできます。</div>
'''

BODIES['avoid-patterns.html'] = '''
    <p class="lead">どの組合せも当選確率は同じ——ただし「当たった時のもらい」は違います。人気が集中しやすいパターンを避けると、分割リスクを下げられます。確率の話ではなく、お金の効率の話として読んでください。</p>

    <h2>人気になりがちな組合せ</h2>
    <ul>
      <li><b>連続のきれいな並び</b>：1-2-3-4-5 など。海外では毎回大量に買われる有名な例です。当たると大分割になりがち。</li>
      <li><b>誕生日だけで構成</b>：日付（1〜31）圏は全範囲ですが、家族の生年月日など「日付っぽい組合せ」は選ぶ人が多め。</li>
      <li><b>ゾロ目・等差</b>：5・10・15・20・25 など、見た目の規則性が強いもの。</li>
      <li><b>角や縦一列など<br />マークシートで絵になる並び</b>：同じ発想の人が一定数います。</li>
      <li><b>直前回とまったく同じ組合せ</b>：ありえないわけではありませんが、同じことをする人と重なりやすい話題のパターンです。</li>
    </ul>

    <h2>避けると何が得？</h2>
    <p>当サイトデータでも、1等の賞金額は当選口数で大きく変わります（<a href="prize-structure.html">賞金の仕組み</a>）。人気パターンは当たったときに口数が膨れやすいと言われており、逆に<b>「不規則に見える組合せ」は分割リスクが低め</b>、というのが定説です。当選確率そのものは変わらない点だけ、最後まで忘れないでください。</p>

    <div class="owner-note">僕自身は「偶数だけ」「全部一の位が同じ」は避けています。当たりやすくしたいのではなく、万が一当たった時に独り占めしやすい側に寄せたいからです。ごく小さな差異ですが、ゼロコストでできる節約技です。</div>

    <div class="cta-box"><b>人気リスクを点検する</b><br /><a href="../index.html">技法研究の人気パターン分析</a>で、自分の組合せの分割リスク傾向を確認できます。</div>
'''

BODIES['backtest.html'] = '''
    <p class="lead">バックテストは「ある選び方を過去の抽選に当てはめたら、結果はどうだったか」を確かめる検証方法です。当サイトにも搭載していますが、結果の読み方にはコツがあります。</p>

    <h2>バックテストでわかること・わからないこと</h2>
    <table class="info">
      <tr><th>わかること</th><td>過去データの範囲での当選回数・等級の分布・合計・奇偶などの傾向</td></tr>
      <tr><th>わからないこと</th><td>未来の当選確率。過去と未来の抽選は無関係（独立）なので、成績が良かった方法が今後も有利とは限りません</td></tr>
    </table>

    <h2>ランダム基準線との比較が大切</h2>
    <p>当サイトのバックテストは、同じ条件で<b>完全ランダムに選んだ場合の基準線</b>を併記しています。</p>
    <ol>
      <li>気になる戦略（ホット重視・未出現重視など）で実行する。</li>
      <li>ランダム基準線と当選回数がほぼ同じなら「その戦略の過去成績はランダムと同等」と読みます。</li>
      <li>大きく上振れしていても、試行回数が少ないと偶然の範囲に入ります。</li>
    </ol>

    <h2>過剰適合（オーバーフィッティング）に注意</h2>
    <p>「過去データにピッタリ合う条件」は、その期間の偶然を拾っているだけのことが多く、次の期間では機能しないことが知られています。条件を増やしすぎず、<b>シンプルな条件で別期間でも再試行する</b>のが健全な検証です。</p>

    <div class="notice info">当サイトでは、参考スコアも「統計実験値」として扱い、実際の払戻率や収益を保証しないことを各所に明記しています。</div>

    <div class="cta-box"><b>実際に動かしてみる</b><br /><a href="../index.html">高度/バックテストメニュー</a>で、期間・戦略を選んで今すぐ検証できます。</div>
'''

BODIES['coverage.html'] = '''
    <p class="lead">同じ予算でも、買う組合せの作り方で「数字のカバー範囲」は変わります。海外で「ウィーリング」と呼ばれる考え方を、ミニロト向けにわかりやすく紹介します。</p>

    <h2>カバレッジとは</h2>
    <p>たとえば10個の気になる数字があるとき、5個選びの組合せは全部で252通り。全部買うと50,400円です。カバレッジ設計は、<b>その一部だけ買っても「3個一致以上」などの条件をできるだけ広く満たす</b>ように組合せを選ぶ技術です。</p>

    <h2>メリットと限界</h2>
    <ul>
      <li><b>メリット</b>：少ない枚数で広い数字範囲を押さえられる。小当たりの取りこぼしを減らせる。</li>
      <li><b>限界</b>：1等の理論確率は買う枚数に比例。カバレッジは「当たりやすさの配分を整える」もので、確率そのものを増やす魔法ではありません。</li>
    </ul>

    <h2>当サイトのカバレッジツールの使い方</h2>
    <ol>
      <li>候補数字（例：10〜14個）を入力します。</li>
      <li>「3個組カバー」「4個組カバー」など目標の強さを選びます。</li>
      <li>生成された組合せとカバー率を確認し、予算内のものだけマークシート印刷に追加します。</li>
    </ol>
    <div class="notice warn">カバー率が高い＝当選を保証する、ではありません。理論確率は常に「枚数 ÷ 169,911」で決まります。予算上限は<a href="responsible-play.html">予算管理の記事</a>も参考に。</div>

    <div class="cta-box"><b>試してみる</b><br /><a href="../index.html">カバレッジメニュー</a>で、候補数字から最適な組合せセットを自動設計できます。</div>
'''

BODIES['statistics-guide.html'] = '''
    <p class="lead">「メニューが多くて何から見ればいい？」という声に応えて、当サイトの全10メニューの使い分けを運営自身が順番に案内します。初めての方はこの記事の3ステップで十分です。</p>

    <h2>初めての3ステップ</h2>
    <ol>
      <li><b>データメニュー</b>で最新回が正しいか確認（毎週火曜の抽選後に更新）。</li>
      <li><b>統計/相性メニュー</b>で期間を「直近100回」にして、出現回数と未出現をざっと見る。</li>
      <li><b>数字生成メニュー</b>で「バランス型・10口」を生成し、気に入ったものだけ印刷リストへ。</li>
    </ol>

    <h2>各メニューの使いどころ</h2>
    <table class="info">
      <tr><th>メニュー</th><th>こんなときに</th></tr>
      <tr><td>ダッシュボード</td><td>最新結果・各種指標の全体像をひと目で</td></tr>
      <tr><td>データ</td><td>全履歴の検索・絞込・CSV/JSONの取得</td></tr>
      <tr><td>統計/相性</td><td>出現回数・未出現・相性ペアなど基礎統計</td></tr>
      <tr><td>高度/バックテスト</td><td>戦略の過去検証とランダム比較（<a href="backtest.html">解説</a>）</td></tr>
      <tr><td>専門分析</td><td>賞金分析・条件別相性・バランス点検など深堀り</td></tr>
      <tr><td>技法研究</td><td>予算計算・フィルタ影響・人気リスクなど実験室</td></tr>
      <tr><td>数字生成</td><td>条件つき生成（<a href="quickpick-vs-jisen.html">ランダムも可</a>）</td></tr>
      <tr><td>カバレッジ</td><td>候補数字から効率セットを設計（<a href="coverage.html">入門記事</a>）</td></tr>
      <tr><td>当選確認</td><td>手持ち組合せと任意回の照合・賞金表示</td></tr>
      <tr><td>マークシート</td><td>決めた組合せを印刷して売り場へ（<a href="marksheet-guide.html">書き方</a>）</td></tr>
    </table>

    <h2>週に1回のおすすめルーティン</h2>
    <ol>
      <li>火曜夜または水曜：最新結果を確認（<a href="https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html" target="_blank" rel="noopener noreferrer">公式</a>との照合も忘れずに）。</li>
      <li>先週買った組合せを当選確認でチェック。</li>
      <li>来週分はデータの記録を見てから決める。深追いはしない。</li>
    </ol>

    <div class="cta-box"><b>まずはここから</b><br /><a href="../index.html">トップページ（ダッシュボード）</a>を開くと、今日できることが全部見えます。</div>
'''

BODIES['marksheet-guide.html'] = '''
    <p class="lead">売り場で配布されているマークシート。慣れれば簡単ですが、初めてだと少し戸惑います。基本の書き方と、当サイトの印刷ツールとの併用方法を紹介します。</p>

    <h2>マークシートの基本</h2>
    <ul>
      <li>A〜Eのブロックがあり、<b>1ブロック＝1口</b>（1口200円）。1枚で最大5口申し込めます。</li>
      <li>買いたい数字に縦線でしっかりマーク。鉛筆・濃いめのボールペン推奨。</li>
      <li>機械に選んでほしい部分は「クイックピック」欄にマークします。</li>
      <li>各ブロックは独立しています。別々の買い方を混ぜてOK。</li>
    </ul>

    <h2>失敗しやすいポイント</h2>
    <ul>
      <li><b>訂正はその枠を潰さず別ブロックへ</b>。二重に塗ると意図しない口数になることがあります。</li>
      <li><b>口数の申込はブロック数で決まる</b>。「2口買いたかった」は2ブロック分のマークです。</li>
      <li><b>受け取った宝くじは再確認</b>。発券後の数字が自分の指定どおりか、その場で確認しましょう。</li>
    </ul>

    <h2>当サイトの印刷ツールとの併用</h2>
    <p>当サイトの「マークシート/印刷」メニューは、決めた組合せを一覧にして印刷できるツールです。売り場でその紙を見ながら転記すれば、廊下で迷わず・塗り間違えも減らせます。</p>
    <ol>
      <li>数字生成やカバレッジで決めた組合せを印刷リストに追加。</li>
      <li>「印刷」ボタンで一覧を出力（A4対応）。</li>
      <li>売り場で転記して発券。枚数と金額を最終確認。</li>
    </ol>

    <div class="notice info">購入は20歳以上の方・日本国内に限られます。宝くじの詳細・最新の案内は公式サイトをご確認ください。</div>

    <div class="cta-box"><b>印刷して準備</b><br /><a href="../index.html">マークシート/印刷メニュー</a>で購入予定リストを作れます。</div>
'''

BODIES['responsible-play.html'] = '''
    <p class="lead">当サイトは統計情報サイトですが、根本にあるのは「宝くじは娯楽」という考え方です。無理なく長く楽しむための、シンプルなルールを紹介します。</p>

    <h2>基本のルール</h2>
    <ul>
      <li><b>購入は20歳以上・日本国内の方のみ</b>（法律の定め）。</li>
      <li><b>使うのは余裕資金だけ</b>。生活費・貯蓄・借入からは絶対に購入しません。</li>
      <li><b>月額予算を先に決める</b>。例：「月2,000円まで」など、負けても笑える金額に。</li>
      <li><b>負けを取り戻そうとしない</b>。「次こそ取り返す」は最も危険なサインです。</li>
    </ul>

    <h2>期待値の現実</h2>
    <p>払戻率は法律上50%未満。長く買い続けるほど、平均すると投入額の半分以下が戻る計算です。「当たればラッキーの余興」として、深追いしないのが健全な付き合い方です（数字の現実は<a href="win-reality.html">当選確率の現実</a>に整理しました）。</p>

    <h2>危険サインのセルフチェック</h2>
    <ul>
      <li>予算を決めていない、または決めた予算を超えた</li>
      <li>外れが続いて購入額を増やしたくなった</li>
      <li>家族や友人に購入額を隠したくなった</li>
    </ul>
    <p>1つでも当てはまったら、いったん購入を休むのがおすすめです。心配な場合は、お近くの消費生活センター等の相談窓口にご相談ください。</p>

    <div class="notice ok">当サイトの<a href="../index.html">技法研究メニューの予算計算</a>で、口数と理論確率を数値で確認してから判断できます。</div>
'''

BODIES['cashing.html'] = '''
    <p class="lead">もし当たったら——の前に知っておくと得する、換金の基本の流れです。うっかり期限切れ・忘れ物で困らないために。</p>

    <h2>換金までの流れ</h2>
    <ol>
      <li><b>当選番号を確認する</b>：必ず<a href="https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html" target="_blank" rel="noopener noreferrer">公式発表（みずほ銀行）</a>で照合。当サイトは参考用です。</li>
      <li><b>宝くじ券を保管する</b>：券そのものが換金に必要です。折らず・濡らさず保管を。</li>
      <li><b>金額に応じた場所へ</b>：少額は宝くじ売場、一定額以上はみずほ銀行の本店・支店窓口になります。</li>
      <li><b>高額は本人確認</b>：高額当選金の受取では本人確認書類の提示が必要です。</li>
    </ol>

    <h2>忘れがちな注意点</h2>
    <ul>
      <li><b>支払期限は1年</b>。抽選日の翌日から1年を過ぎると、原則受け取れません（時効）。忘れず換金を。</li>
      <li><b>当選金は非課税</b>とされています。ただし個別の事情は最寄りの税務署・専門家に相談を（当サイトは税務の助言ではありません）。</li>
      <li><b>券の紛失・破損には注意</b>。宝くじは原則、実物が命。大切に扱いましょう。</li>
    </ul>

    <h2>小当たりが続くときは</h2>
    <p>4等の900円級は売場でそのまま受け取れます。「貯まった小当たり」をまとめて換金に行くのも一つの楽しみ。手数料は不要です。</p>

    <div class="owner-note">当選結果の照合を急ぐ方へ：当サイトの<a href="../index.html">当選確認メニュー</a>で事前にざっと調べ、最終確認は公式で——この2段構えが一番安全です。</div>
'''

# ------------------------------------------------------------------ 追記(글자수 보강·실질 내용)
EXTRA = {}
EXTRA['basics.html'] = '''
    <h2>「5等はないの？」とよく聞かれます</h2>
    <p>ミニロトの等級は1等〜4等まで。<b>2個一致はハズレ</b>です。ロト6の5等（3個一致）と混同している方が多いポイントなので注意しましょう。逆に言えば、ミニロトの4等（3個一致・約900円前後）は理論確率1/52と、数字くじのなかでは手の届きやすい等級です。</p>
    <h2>「ボーナスは何のため？」もうひと押し</h2>
    <p>2等専用です。本数字4個＋ボーナスの2等は、本数字4個だけの3等の26倍も当たりにくくなります（125通り→5通り）。ボーナス1個を当てにいくより、本数字を点検する方が堅実です。</p>
'''
EXTRA['combination-formula.html'] = '''
    <h2>ボーナスまで含めると</h2>
    <p>本数字5個を決めたあと、ボーナス数字は残り26個から1個選びます。つまり「本数字＋ボーナス」まで含めた完全なパターン数は <b>169,911 × 26 ＝ 4,417,686通り</b>。全パターンを買い占めるには88億円超が必要で、「全部買えば必ず元が取れる」式の必勝法は現実に存在しません。</p>
    <h2>十の位で考える人へ</h2>
    <p>「1〜10」「11〜20」「21〜31」の3ブロックに分けると、本数字5個は平均的には各ブロックに1〜2個ずつ散る構成が多くなります（純粋な数の分布）。全員1ブロックに集まる組合せは少ないのですが、それもまた「珍しい構成」というだけで確率操作ではありません。</p>
'''
EXTRA['loto-types.html'] = '''
    <h2>賞金の規模感も比較</h2>
    <table class="info">
      <tr><th>種類</th><th>1等の規模感</th><th>性格ひとこと</th></tr>
      <tr><td>ミニロト</td><td>数百万〜4,000万円</td><td>堅実な夢・週1のお楽しみ</td></tr>
      <tr><td>ロト6</td><td>2億円前後（最高6億円）</td><td>バランス型の定番</td></tr>
      <tr><td>ロト7</td><td>キャリーオーバー時10億円</td><td>一発屋専用・最難関</td></tr>
      <tr><td>ナンバーズ3</td><td>約9万円（ストレート）</td><td>身近な小当たり狙い</td></tr>
      <tr><td>ナンバーズ4</td><td>約90万円（ストレート）</td><td>毎日抽選・ペース注意</td></tr>
    </table>
    <p>「当たりやすさ×賞金額」は完全なシーソー関係。当たりやすいほど安く、高いほど当たらない——この図式さえ押さえておけば、怪しい宣伝にまず騙されません。</p>
'''
EXTRA['win-reality.html'] = '''
    <h2>4等は「生活圏の当たり」</h2>
    <p>一方で4等（3個一致）は理論1/52。10口買えば約18%の確率で1枚は含まれます。当サイトデータでも毎週5万口前後が4等当選。<b>「たまに900円前後が戻る」</b>くらいの感覚で長く付き合えるのが実態です。</p>
    <h2>リスクの物差し</h2>
    <p>確率の比較表現は誤解を生みやすいので避けますが、「毎週1口を何十年続けても当たらない人の方が圧倒的に多い」は純粋な算数です。だからこそ「当たったら儲けもの」という起点に立つべきだと、僕は利用者には常々伝えていきたいと考えています。</p>
'''
EXTRA['faq.html'] = '''
    <h2>Q8. 当サイトのデータは正確ですか？</h2>
    <p>公開されている過去データを集約・点検して掲載していますが、誤記・遅延の可能性はゼロではありません。<b>当選の最終確認は必ず公式発表（みずほ銀行）で</b>行ってください。誤りを見つけた場合は<a href="../contact.html">お問い合わせ</a>からご指摘いただけます。</p>
    <h2>Q9. データの更新タイミングは？</h2>
    <p>抽選（毎週火曜）後、公式発表の確認を経て更新します。トップのお知らせに最新回の基準日が表示されます。古い可能性がある場合は警告表示が出ます。</p>
'''
EXTRA['top10-numbers.html'] = '''
    <h2>期間を変えると順位は入れ替わる</h2>
    <p>この表は第1回からの累計ですが、「直近100回だけ」に絞ると順位はがらりと変わります。短期のランキングほど偶然が支配的なので、「直近で出ている数字＝勢いがある」はほぼ後付けの物語です。累計ランキングは「歴史の記録」として楽しむのがちょうどいい距離感です。</p>
    <h2>ボーナス込みなら？</h2>
    <p>ボーナス数字を足した集計も数字ごとの出にくさの参考にはなりますが、本数字だけの集計が基準です。試したい方は当サイトからCSVを取得して、エクセル等で自由に集計してみてください——全部無料公開なのは、こういう「自分で確かめる」遊びをしてほしいからです。</p>
'''
EXTRA['absent-numbers.html'] = '''
    <h2>もっと長期の未出現も普通に起きる</h2>
    <p>全1,397回の履歴を見ても、特定数字が30回近く出なかった区間は実在します。(26/31)の30乗≈0.5%しかない事例ですが、31数字×多くの区間で見れば登場するのは自然です。当サイトダッシュボードの「最長未出現」カードでも現在値をいつでも確認できます。</p>
    <h2>「待ち伏せ」買いは効率が悪い</h2>
    <p>未出現の数字が出るまで毎週買い続ける戦法を考える人がいますが、待っている間の毎回の確率は同じ約16.1%。出現までの平均待ちは約6.2回分で、早くも遅くも確率の範囲内。「記念日過ぎたから中止」といった自分ルールなしで始めると、ズルズル費用だけ増える典型的なパターンなので注意です。</p>
'''
EXTRA['consecutive-numbers.html'] = '''
    <h2>理論値とぴったり一致</h2>
    <p>実は「連番が1組も入らない」組合せの数は、計算で80,730通りとなります。つまり連番入りの組合せは 169,911 − 80,730 ＝ 89,181通りで、理論上の出現割合は<b>約52.5%</b>。実績の52.5%と驚くほど一致しています——抽選が理論どおり公正に行われている証拠とも読める数字です。</p>
    <h2>「絶対連番」も5.9%の世界</h2>
    <p>1-2-3-4-5のような完全な5連番は理論上たった27通り（1-2-3-4-5〜27-28-29-30-31）。当たったら話題になりますが、確率は他の任意の組合せと同じ1/169,911。完全連番は避けて、1組だけの連番は避けない、が数字的にはバランスの良い姿勢だと僕は考えています。</p>
'''
EXTRA['winners-analysis.html'] = '''
    <h2>全部足すといくら戻る？</h2>
    <p>第1397回の賞金総額を単純計算すると約1.7億円（21口×約730万円＋87口×12.6万円＋1,779口×1.06万円＋51,536口×900円の概算）。この「総額」は販売額の一部にすぎず、残りは公営の運営費・収益金として公共事業等の財源に回る仕組みです。「みんなの購入金のうち賞金になるのは半分以下」——この構造を頭に入れておくと、数字への期待値が自然と現実的になります。</p>
    <h2>2等という隠れポジション</h2>
    <p>ボーナス1個で2等と3等が分かれる境目、1等の数十万人に対し2等は週に数十〜数百口。賞金も10万円級が多く、「届きそうで届かない」恰好の夢の対象です。ボーナスの仕組みは<a href="basics.html">基本ルールの記事</a>でも詳しく書いています。</p>
'''
EXTRA['statistics-reading.html'] = '''
    <h2>平均に戻る波のつかまえ方</h2>
    <p>直近で出すぎた数字は、その後の長期では平均に近づいていくことが多いです。これは「必然の調整」ではなく、長く見れば偶然の偏りが薄まる当然の動き。だから「勢いがある数字に全賭け」は、波の頂点で乗り込む行為と同じです。</p>
    <h2>集計方法の透明性</h2>
    <p>当サイトの集計は「第1回からの公式判定分」をベースに機械集計しています。算出結果が気になる方は、ダウンロードできるCSV/JSONで御自身でも検算いただけます。疑ったら検算できる、これがデータ公開の本当の意味です。</p>
'''
EXTRA['independence.html'] = '''
    <h2>「必勝法セールス」の見抜き方</h2>
    <p>独り立ちした試行の商品に「検証済み・実績あり」を掲げても、それは過去の偶然の並べ替えにすぎないことが大半です。チェックは簡単——「ランダムと比べた差は？」「試行回数は？」「次の期間でも再現した？」の3点でほぼ見抜けます。この質問に答えられない情報源は避けましょう。</p>
    <h2>データを見る心構え</h2>
    <p>「効く」を探すのではなく「偏っていないか」を見る。この目的転換ができると、統計は急に実用の道具になります。見慣れないうちは<a href="statistics-guide.html">使い方ガイド</a>の3ステップどおりで十分です。</p>
'''
EXTRA['prize-structure.html'] = '''
    <h2>還元率の法律の枠</h2>
    <p>宝くじの払戻率（還元率）は、法律で「発売額の50%未満」と定められています。競輪・競馬（70〜80%）と比べても控えめな設計で、その差額は収益金として都道府県・政令市の公共事業等に使われます。「買っても半分未満しか戻らない」のは制度そのもの——だからこそ「回収して勝つ発想」は最初から捨てるのが得策です。</p>
    <h2>小当たりの年間感覚</h2>
    <p>毎週4等（900円前後）に1回でも当たれば、理論上は年52回分の900円×当選確率の収支が積み重なります。もっとも確率どおりに当たるとは限らないので、あくまで長い目で見たお楽しみ枠。小当たりの積み重ねが「宝くじの一番身近な楽しみ」という人は多いです。</p>
'''
EXTRA['quickpick-vs-jisen.html'] = '''
    <h2>売り場の機械も「擬似乱数」</h2>
    <p>豆知識として、クイックピックの機械は完全な物理乱数ではなく擬似乱数（計算で作るランダム風の数列）を使っています。ただし利用者がその出方を予測することは実際には不可能（内部状態が見えないため）。だから「QPに裏がある」という心配は不要です。</p>
    <h2>ハイブリッドという現実解</h2>
    <p>実際には「A〜Cブロックは自選、残りはQP」という併用が広く使われています。自分の数字への愛着も捨てがたい、でも変に偏りたくない——この妥協案は数字的にも、満足度的にもかなり良い選択です。迷ったら併用、が運営のおすすめです。</p>
'''
EXTRA['avoid-patterns.html'] = '''
    <h2>当サイトの人気リスク機能の使い方</h2>
    <p>「この組合せ、人とかぶりそう？」を点検するには、技法研究メニューの「人気パターン/賞金分断リスク」を使います。誕生日密度・連続度・ゾロ目等の指標をもとに、<b>分割リスクが高めか低めか</b>を目安表示します（あくまで推測の参考値）。生成した組合せをそのまま転記できるので、印刷前の最終チェックにどうぞ。</p>
    <h2>なら何が正解？</h2>
    <p>「無作為で見栄えの悪い、人に自慢しにくい組合せ」が、皮肉にも分割リスクは低めです。3・14・20・25・31のような、どこにも物語の感じられない並び。当サイトの数字生成「完全ランダム」はまさにこの手の組合せをよく出します。</p>
'''
EXTRA['backtest.html'] = '''
    <h2>実際に動かしたときの画面の見方</h2>
    <p>例として「戦略＝ホット重視・期間＝直近100回」で実行すると、当選回数に加えて「ランダム基準線との差」が表示されます。注目点は<b>差がプラスかどうかより、試行回数に対して小さくないか</b>。100回程度では両方とも非常に近い値になることが大部分で、「まあそうだよね」と笑って終われるのが健全な読み取りです。</p>
    <h2>検証ノートを作ると意外と面白い</h2>
    <p>結果を毎週メモに残すと、自分の思い込みが見えてきます。「ホット重視だと当たる気がした」がデータ上はランダムと互角だった——この気づきの積み重ねが、一番価値のある勉強だったりします。</p>
'''
EXTRA['coverage.html'] = '''
    <h2>候補数と総組合せの予算感</h2>
    <table class="info num-table">
      <tr><th>候補数字</th><th>全部買う組合せ数</th><th>全部買う費用</th></tr>
      <tr><td>10個</td><td>252通り</td><td>50,400円</td></tr>
      <tr><td>12個</td><td>792通り</td><td>158,400円</td></tr>
      <tr><td>14個</td><td>2,002通り</td><td>400,400円</td></tr>
    </table>
    <p>この表を見ると「全部買い」が簡単に破綻するのが一目瞭然。だから一部を選ぶカバレッジが発明されたわけですが、選んだ一部で1等が外れれば素通りです。カバレッジは<b>小当たりの効率化あってこそ</b>の技術、という位置づけを間違えないようにしましょう。</p>
'''
EXTRA['statistics-guide.html'] = '''
    <h2>モバイルでの使い方</h2>
    <p>当サイトはスマホでも全メニューが動きます（表は横スクロール対応）。売り場の待ち時間に数字生成→印刷リスト追加→自宅のパソコンで印刷、という流れも快適にできます。</p>
    <h2>週ごとの「型」があると続く</h2>
      <p>火曜の夜：当選確認 → 水曜：最新データ反映の確認 → 週末：来週分の生成・印刷。この3点のサイクルを作ると、「毎週ぶれない自分ルール」ができあがります。熱くなりすぎず、それでいて記録は続く——運営としては、これが一番続けやすい遊び方だと考えています。</p>
'''
EXTRA['marksheet-guide.html'] = '''
    <h2>発券後の確認はクセに</h2>
    <p>受け取った宝くじ券に印字された数字が、自分のマークどおりか——これを毎回10秒で確認するだけで、悲しい事故はほぼ防げます。抽選日前に「券の写真を撮っておく」人もいます（紛失時の備忘録として）。</p>
    <h2>代理購入について</h2>
    <p>家族に買ってきてもらう等の代理購入は一般的ですが、賞金の受取は原則として当選券を持つ人が手続きします。高額当選の「名義」でもめないよう、家族内でも事前に話しておくと安心です。</p>
'''
EXTRA['responsible-play.html'] = '''
    <h2>宝くじの収益はどこへ行く？</h2>
    <p>販売額から賞金と運営費を除いた収益金は、法律により公共事業（教育・福祉・防災等）の財源として都道府県・政令市に使われます。「夢の代金」の一部が社会貢献になっている面もある——とはいえ、この事実が購入の勧奨にはならないと僕は考えます。<b>楽しむ範囲で、だけが原理です。</b></p>
    <h2>比較として知っておく</h2>
    <p>他の公営競技（競馬・競輪等）は還元率70〜80%前後。宝くじは50%未満で、数字上はかなり厳しい部類。だからギャンブルの「勝負」ではなく、娯楽の「余興」——この区分けができる人は、宝くじと健康に長く付き合えます。</p>
'''
EXTRA['cashing.html'] = '''
    <h2>当日の持ち物チェック</h2>
    <ul>
      <li>当選券そのもの</li>
      <li>本人確認書類（高額の場合・運転免許証等）</li>
      <li>（高額の場合）印鑑を求められることがあります</li>
    </ul>
    <h2>インターネット購入との違い</h2>
    <p>公式のネット購入経由なら当選金は指定口座に自動振込の仕組みです（時効の心配がないのが利点）。当サイトはネット購入の案内は行っていないため、詳細は公式サイトで確認してください。紙で買う派の方は「券の物」と「期限1年」だけは確実に覚えておきましょう。</p>
    <h2>当選発表当日の心得</h2>
    <p>「当たったかも！」と思っても、焦って換金に行く必要はありません。期限は1年あります。公式発表を静かに照合し、券を安全に保管してから、営業時間内の窓口へどうぞ。高額になるほど「慌てない」が最大の守りです。</p>
'''

# ------------------------------------------------------------------ 생성
CAT_LABELS = {'基本': '基礎知識', '実録': 'データ実録', '実践': '実践・検証・ルール'}
TITLE_OF = {a['file']: a['title'] for a in ARTICLES}

def related_block(file: str, cat: str) -> str:
    others = [a['file'] for a in ARTICLES if a['file'] != file and a['cat'] == cat][:3]
    if len(others) < 3:
        others += [a['file'] for a in ARTICLES if a['file'] != file and a['file'] not in others][: 3 - len(others)]
    links = ' ｜ '.join(f'<a href="{f}">{TITLE_OF[f]}</a>' for f in others[:3])
    return f'    <div class="related"><b>関連コラム</b>：{links}</div>\n'

def generate() -> None:
    for a in ARTICLES:
        f = a['file']
        body = BODIES[f]
        extra = EXTRA.get(f, '')
        if extra and '<div class="cta-box"' in body:
            body = body.replace('<div class="cta-box"', extra + '<div class="cta-box"', 1)
        else:
            body = body + extra
        body = body + related_block(f, a['cat'])
        shell(f, a['title'], a['desc'],
              f'<a href="index.html">コラム</a> &gt; {a["title"]}',
              a['title'], a['date'], body)

    # 목록 페이지 (카테고리別)
    groups = []
    for cat in ['基本', '実録', '実践']:
        cards = []
        for a in [x for x in ARTICLES if x['cat'] == cat]:
            cards.append(f'''      <div class="method-card">
        <span class="badge">コラム</span>
        <b>{a['title']}</b>
        <p>{a['desc']}</p>
        <a href="{a['file']}">この記事を読む →</a>
      </div>''')
        groups.append(f'''    <h2>{CAT_LABELS[cat]}</h2>
    <div class="blog-grid">
{chr(10).join(cards)}
    </div>''')
    groups_html = '\n'.join(groups)

    index_body = f'''
    <p class="lead">ミニロトのルール・確率・統計の読み方・検証方法・健全な楽しみ方を、運営が一つずつ文章で解説するコラムです。全{len(ARTICLES)}本。随時追加していきます。</p>
    <style>
      .method-card{{padding:14px;border-radius:14px;background:#fff;border:1px solid var(--line);box-shadow:0 4px 12px rgba(15,23,42,.035)}}
      .method-card b{{display:block;color:var(--navy);font-size:15px;line-height:1.5}}
      .method-card p{{margin:7px 0 10px;color:var(--muted);font-size:12.5px;line-height:1.6}}
      .method-card .badge{{display:inline-flex;margin-bottom:8px;padding:3px 9px;border-radius:999px;background:#fff7ed;border:1px solid #fde68a;color:#92400e;font-size:11px;font-weight:800}}
      .blog-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:8px 0 22px}}
      @media(max-width:640px){{.blog-grid{{grid-template-columns:1fr}}}}
    </style>
{groups_html}
    <div class="cta-box"><b>分析ツールはこちら</b><br />コラムで紹介している統計・バックテスト・カバレッジはすべて<a href="../index.html">トップページのツール</a>で無料公開中です。</div>
'''
    shell('index.html', 'コラム一覧', 'ミニロトのルール・確率・統計の読み方・検証・健全な楽しみ方を解説するコラム一覧。',
          'コラム一覧', 'コラム・読みもの', '2026-08-04', index_body)


if __name__ == '__main__':
    generate()
    print(f'BLOG DONE: {len(ARTICLES)} articles + index → {BLOG}')

