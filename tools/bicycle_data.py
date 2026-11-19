"""Student-facing data dictionary calculated from the supplied bike.csv rows."""
from collections import Counter
from html import escape


def summary(rows):
    fields = list(rows[0])
    counts = {field: Counter(row[field] for row in rows) for field in fields}
    total = len(rows)
    dates = sorted(value for value in counts['発生年月日（始期）'] if value not in {'', '不明'})
    years = Counter()
    for date, number in counts['発生年月日（始期）'].items():
        years[date[:4] if date not in {'', '不明'} else '不明'] += number
    return dict(total=total, fields=fields, counts=counts, date_min=dates[0], date_max=dates[-1], years=years,
                areas=len(counts['市区町村（発生地）']),
                unlocked_pct=counts['施錠関係']['施錠せず']/total*100,
                young_pct=sum(counts['被害者の年齢'][age] for age in ['10歳代', '20歳代'])/total*100,
                parking_pct=counts['発生場所の詳細']['駐車（輪）場']/total*100)


def guide(data, bi, p, notes_url):
    counts = data['counts']

    def values(field, limit=None, labels=None):
        return '、'.join(f'<code>{escape((labels or {}).get(value, value))}</code> {number:,}'
                        for value, number in counts[field].most_common(limit))

    def top(field, ja, en):
        return (f'{len(counts[field]):,}種類。上位：'+values(field, 5)+ja,
                f'{len(counts[field]):,} distinct values. Leading values: '+values(field, 5)+en)

    def categories(field):
        return (values(field), values(field))

    years = '、'.join(f'{year}年 {number:,}' for year, number in sorted(data['years'].items()) if year != '不明')
    years_en = ', '.join(f'{year}: {number:,}' for year, number in sorted(data['years'].items()) if year != '不明')
    dates = counts['発生年月日（始期）']
    date_count = len([v for v in dates if v not in {'', '不明'}])
    date_values = (f'{data["date_min"]}〜{data["date_max"]}。既知の日付{date_count}種類。不明{dates["不明"]}件。年別：'+years,
                   f'{data["date_min"]} to {data["date_max"]}. {date_count} known dates; {dates["不明"]} unknown. By year: '+years_en)
    hours = counts['発生時（始期）']
    hour_top_pairs = [(hour, number) for hour,number in hours.most_common() if hour != '不明'][:3]
    hour_top = '、'.join(f'{hour}時 {number:,}' for hour,number in hour_top_pairs)
    hour_top_en = ', '.join(f'{hour}:00 {number:,}' for hour,number in hour_top_pairs)
    hour_values = (f'00〜23時と不明{hours["不明"]}件。上位：'+hour_top,
                   f'Hours 00–23, plus {hours["不明"]} unknown. Top three hours (counts): '+hour_top_en)
    # The literal CSV labels stay in Japanese so students can use the exact keys.
    fields = [
        ('罪名', '犯罪の種類', 'Crime category', categories('罪名')),
        ('手口', '事件の種類', 'Type of theft', categories('手口')),
        ('管轄警察署（発生地）', '発生地域を管轄する警察署', 'Responsible police station', top('管轄警察署（発生地）', '', '')),
        ('管轄交番・駐在所（発生地）', '担当する交番・駐在所の名称', 'Responsible police box or local post',
         (f'{len(counts["管轄交番・駐在所（発生地）"])-1}種類の名称、空欄{counts["管轄交番・駐在所（発生地）"][""]}件。上位：'+values('管轄交番・駐在所（発生地）', 5),
          f'{len(counts["管轄交番・駐在所（発生地）"])-1} nonblank labels; {counts["管轄交番・駐在所（発生地）"][""]} blanks. Leading values: '+values('管轄交番・駐在所（発生地）', 5))),
        ('市区町村コード（発生地）', '地域を識別する6桁のコード。計算する数値ではなくID', 'Six-digit area identifier; treat it as an ID', top('市区町村コード（発生地）', '', '')),
        ('都道府県（発生地）', '発生した都道府県', 'Prefecture', categories('都道府県（発生地）')),
        ('市区町村（発生地）', '市町村名、千葉市は区別の名称', 'Municipality or Chiba City ward', top('市区町村（発生地）', '', '')),
        ('町丁目（発生地）', '町丁目名。同名の場所があるため市区町村と組み合わせる', 'Neighborhood label; combine it with the municipality',
         (f'{len(counts["町丁目（発生地）"])-1:,}種類の名称、空欄{counts["町丁目（発生地）"][""]}件。上位：'+values('町丁目（発生地）', 5),
          f'{len(counts["町丁目（発生地）"])-1:,} nonblank labels; {counts["町丁目（発生地）"][""]} blanks. Leading values: '+values('町丁目（発生地）', 5))),
        ('発生年月日（始期）', '発生日。期間に幅があれば、その始まりの日付', 'Recorded date, or start date when an interval is known', date_values),
        ('発生時（始期）', '24時間制の時。時間に幅があれば、その始まり', 'Recorded hour, or start hour of a known interval', hour_values),
        ('発生場所', '住宅・道路など、大きな場所の区分', 'General site category', categories('発生場所')),
        ('発生場所の詳細', 'その場所の駐車・駐輪場か、それ以外か', 'Parking/cycle-parking setting or other setting', categories('発生場所の詳細')),
        ('被害者の年齢', '年齢層。正確な年齢ではない', 'Victim age band, not exact age', categories('被害者の年齢')),
        ('被害者の職業', '学生区分などの身分。「その他」は職業の内訳なし', 'Broad status, mainly student categories; other jobs are not detailed', categories('被害者の職業')),
        ('施錠関係', '被害時に鍵がかかっていたか', 'Lock status at the time of theft', categories('施錠関係')),
    ]
    body = '<section id="data-guide"><h2>'+bi('bike.csvの概要','What is in bike.csv?')+'</h2>'
    body += p(f'{data["total"]:,}件・{len(data["fields"])}列。1行が自転車盗の記録1件で、{data["areas"]}の市区町村・区の名称が含まれます。場所・日時・被害者の年齢層と身分・施錠状況を調べられます。',
              f'{data["total"]:,} records and {len(data["fields"])} fields. Each row is one recorded bicycle theft, across {data["areas"]} municipality/ward labels. Explore location, date/hour, victim age band and status, and lock status.')
    body += p(f'施錠せず {data["unlocked_pct"]:.1f}%、10〜29歳 {data["young_pct"]:.1f}%、詳細が駐車（輪）場 {data["parking_pct"]:.1f}%。すべて配布データ全{data["total"]:,}件に占める割合です。',
              f'Unlocked: {data["unlocked_pct"]:.1f}%; ages 10–29: {data["young_pct"]:.1f}%; detailed setting is parking/cycle parking: {data["parking_pct"]:.1f}%. Each percentage uses all {data["total"]:,} supplied records.')
    body += p('2025年の公開分ですが、発生年月日には過去年と不明も含みます。件数は被害率ではありません。緯度・経度の列はありません。',
              'This is the 2025 release, but occurrence dates include earlier years and unknowns. Counts are not theft rates. There are no latitude/longitude fields.')
    body += '<details id="data-fields" class="data-fields"><summary>'+bi('全15列：内容と値の要約','All 15 fields: meanings and value summaries')+'</summary>'
    body += p('値の後の数字は件数。種類の多い列は上位5件を表示。列名・区分名はCSVの表記です。',
              'Numbers following values are record counts. Columns with many categories show their top five. Column names and category labels match the Japanese CSV.')
    body += '<div class="bike-table data-dictionary"><table><thead><tr>'+''.join('<th>'+bi(ja,en)+'</th>' for ja,en in [('列名','Field'),('内容','Meaning'),('値の要約・件数','Values and counts')])+'</tr></thead><tbody>'
    for field, ja, en, (values_ja, values_en) in fields:
        body += '<tr><th scope="row"><code>'+escape(field)+'</code></th><td>'+bi(ja,en)+'</td><td>'+bi(values_ja,values_en)+'</td></tr>'
    body += '</tbody></table></div>'
    body += p('「発生場所」が共同住宅でも、その敷地内の駐輪場なら「発生場所の詳細」は駐車（輪）場になります。2列は同じ区分ではありません。',
              'A record can describe an apartment building in the general site field and its bicycle parking in the detailed field. These columns describe different aspects of the same location.')
    body += '<p class="source-note">'+bi('項目の定義：','Field definitions: ')+'<a href="'+escape(notes_url,quote=True)+'" target="_blank" rel="noopener">'+bi('千葉県警の注記','Chiba Police data notes')+' ↗</a>'+bi('。件数は配布CSVから計算。','; counts calculated from the class CSV.')+'</p></details></section>'
    return body


def project_ideas(bi, p):
    ideas = [
        ('地元の自転車レポート', 'Local bike report', '市名を入力すると、その地域の件数・町丁目ランキング・施錠状況を表示。', 'Enter a municipality to see its count, neighborhood ranking and lock-status chart.'),
        ('学生向け防犯キャンペーン', 'Student prevention campaign', '大学生や高校生の記録を絞り、場所・時間帯を可視化。数字に基づく呼びかけを作る。', 'Filter university or high-school records, visualize their places and hours, then write a message supported by the numbers.'),
        ('データで自転車クイズ', 'Bike-data quiz', '集計から問題を作り、input・if・forで出題と採点。答え合わせで図と件数を見せ、発見と防犯の提案を添える。', 'Use input, if and for to ask and score questions based on your counts. Reveal a chart and exact counts, then explain findings and a prevention recommendation.'),
    ]
    body = '<section id="ideas"><h2>'+bi('こんな作品を作れる','Things your team could build')+'</h2>'
    body += p('この3つはヒントです。自分たちの問い・使う人・見せ方を考えて、オリジナルの作品を作ろう。自由なアイデア、大歓迎！',
              'These three examples are starting points. Choose your own question, audience and way to show the data. Original ideas are encouraged!')
    body += '<dl class="bike-project-ideas">'
    for title_ja,title_en,ja,en in ideas:
        body += '<div><dt>'+bi(title_ja,title_en)+'</dt><dd>'+bi(ja,en)+'</dd></div>'
    body += '</dl>'+p('pandasが使えなくても、csv・for・辞書と文字の棒グラフで取り組めます。',
                     'Without pandas, use csv, for loops, dictionaries and text bars.')+'</section>'
    return body
