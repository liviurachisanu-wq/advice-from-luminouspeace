"""Generate index.html, the field-guide download page. Stdlib only.

The page is one self-contained file that works offline: no remote fonts,
scripts or requests. Facts (version, dates, footnote, download files and
sizes, the reading ledger, the reflexes) are read from the repository when
the build runs; the page's own wording lives in this module.

JavaScript only enhances static markup. Without it, every download link,
every platform's steps, all four sample replies and the whole reading ledger
remain on the page.
"""
from datetime import date
from urllib.parse import quote
import html
import json
import re


# ---------------------------------------------------------------------------
# Page wording. Everything here is copy written for the page, not data.
# ---------------------------------------------------------------------------

TAGLINE = 'Practical judgment. Human attention. Concrete next steps.'
LEDE = ('A thinking partner for leadership, careers, delivery, change and AI adoption. '
        'It can challenge your premise, offer a next step, or simply listen.')
QUOTE_CITE = 'The standing instruction the guide is built on'
SAMPLE_QUESTION = 'My managers ask me to approve everything. What should I change this week?'

# The four answers. The replies are written for this page; they are not
# output from the instructions (the page says so next to them).
MODES = [
    {'id': 'opinion', 'name': 'Opinion', 'line': 'A perspective to think with.',
     'reply': 'My read: approvals are piling up on you because the decision rights were never '
              'written down. People are not being careless — they are being safe. That is a '
              'design problem before it is a people problem.'},
    {'id': 'recommendation', 'name': 'Recommendation', 'line': 'A course of action, with the tradeoffs.',
     'reply': 'This week, pick the three decision types you approve most often. For each, write '
              'who decides, the limit they decide within, and when you want to hear about it '
              'afterwards. Keep approval only above those limits.'},
    {'id': 'action', 'name': 'Action', 'line': 'Agreed, practical help — done with you.',
     'reply': 'Let’s draft it now. Give me the last ten things you were asked to approve, and I '
              'will sort them into “decide alone”, “decide and tell me”, and “ask me first”, '
              'ready for Monday’s meeting.'},
    {'id': 'listening', 'name': 'Listening or space', 'line': 'Room to talk — no advice unless you ask.',
     'reply': 'That sounds exhausting — being the bottleneck while still being blamed for the '
              'pace. I’m listening. Tell me as much or as little as you want; I won’t turn it '
              'into a plan unless you ask.'},
]

# One line per reflex. Ids, names and sources come from the instructions;
# the instructions have no one-line form, so these lines are page copy.
REFLEX_LINES = {
    'R1': 'Who should own this decision, and who can challenge it?',
    'R2': 'Find the cue and the reward before asking for more willpower.',
    'R3': 'Does the plan protect autonomy and real learning?',
    'R4': 'Separate immediate satisfaction from belonging and purpose.',
    'R5': 'What is enough, and can you live with the downside?',
    'R6': 'A tired, non-urgent choice may deserve a night’s rest.',
    'R7': 'Who bears the risk when leadership creates insecurity?',
}

# Setup steps, condensed from docs/SETUP.md. {ledger} becomes a download link
# to the reading ledger; {version} becomes the release version.
# `text` names the instruction text the copy button copies (None: no button).
PLATFORMS = [
    {'id': 'chatgpt', 'name': 'ChatGPT', 'how': 'Project instructions',
     'file': 'chatgpt-project-instructions.txt', 'action': 'Download instructions', 'text': 'portable',
     'steps': ['Create a new Project called Advice from LuminousPeace.',
               'Paste the instructions into the Project instructions.',
               'Add the {ledger} as a reference file.',
               'Start a fresh chat inside the Project and try a real decision.']},
    {'id': 'claude', 'name': 'Claude', 'how': 'Skill ZIP',
     'file': 'advice-from-luminouspeace-claude-v{version}.zip', 'action': 'Download skill ZIP', 'text': None,
     'steps': ['Download the skill ZIP as a file — not the whole repository.',
               'Open Customize → Skills and upload the ZIP, if your account permits it.',
               'Enable it, then ask for Advice from LuminousPeace in a fresh chat.',
               'Check the reply ends with the v{version} footnote.']},
    {'id': 'gemini', 'name': 'Gemini', 'how': 'Gem instructions',
     'file': 'gemini-gem-instructions.txt', 'action': 'Download Gem instructions', 'text': 'portable',
     'steps': ['Open Gemini on the web → Gems → New Gem.',
               'Name it Advice from LuminousPeace and paste the instructions.',
               'Optionally attach the {ledger} under Knowledge.',
               'Preview, save, and test in a fresh conversation.']},
    {'id': 'copilot', 'name': 'Microsoft 365 Copilot', 'how': 'Agent instructions',
     'file': 'copilot-agent-instructions.txt', 'action': 'Download agent instructions', 'text': 'copilot',
     'steps': ['Microsoft 365 Copilot → New agent → Configure, where your organization allows it.',
               'Name the agent LuminousPeace Advice.',
               'Paste the compact instructions (under 8,000 characters).',
               'Test in the preview; save under your organization’s policies.']},
    {'id': 'portable', 'name': 'Any chat', 'how': 'Portable text',
     'file': 'portable-instructions.txt', 'action': 'Download portable text', 'text': 'portable',
     'steps': ['Open a fresh conversation in any capable assistant.',
               'Paste the portable instructions as your first message.',
               'Then describe your situation in your own words.']},
]

STEP_NAMES = ['Choose', 'Get the file', 'Paste and check']
STEP_TITLES = ['Which assistant do you use?', 'Get the instructions', 'Paste them in and check']
STEP_SUBS = ['Each assistant gets a version written for it.',
             'Download the file, or copy the text straight to your clipboard.',
             'Follow these steps inside {platform}.']

COVERAGE_NAMES = {'partial': 'Partial text read', 'desc': 'Description only', 'unres': 'Unresolved'}
STATUS_LINE = ('Packaging checks pass. Real-account tests in ChatGPT, Claude, Gemini and Copilot '
               'are not yet verified.')
UPDATES_LINE = ('Installed copies do not update themselves. Download a new release and replace your '
                'instructions; the footnote tells you which version is loaded.')
PRIVACY_LINE = ('Private coaching records, assessments and correspondence are not included. '
                'Use hypothetical or redacted examples in public issues.')
LEDGER_NOTE = ('No complete books were read for this release. The creator’s own reading is separate '
               'from AI source coverage and does not imply endorsement.')

# Ledger headings read "Sxx — Title — Author". S14's ledger entry says the role
# of "HN" is itself unresolved, so its heading is shown whole, as written.
TITLE_AS_WRITTEN = {'S14': 'Author unresolved'}

NUMBER_WORDS = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen',
                'Eighteen', 'Nineteen', 'Twenty']

# The open-book logo: a sun rising from the spine of an open book. On the page
# its colours come from CSS classes, so it follows light and dark; the favicon
# carries its own colours and a dark-scheme variant.
MARK_PATHS = ('<circle class="sun" cx="24" cy="23" r="9.5"/>'
              '<path class="rays" d="M24 5.5v3.5M13.5 9.5l2.3 2.6M34.5 9.5l-2.3 2.6"/>'
              '<path class="pages" d="M3 24c8-3.5 15-2.5 21 2.5 6-5 13-6 21-2.5v18c-8-3.5-15-2.5-21 2.5-6-5-13-6-21-2.5z"/>'
              '<path class="cut" d="M24 27v17"/>')
FAVICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><style>'
               '.sun{fill:#b5762a}.rays{stroke:#b5762a;stroke-width:2.6;stroke-linecap:round}'
               '.pages{fill:#1d2b28}.cut{stroke:#f3eee2;stroke-width:2.2}'
               '@media (prefers-color-scheme:dark){.pages{fill:#efe8da}.cut{stroke:#171513}}'
               '</style>' + MARK_PATHS + '</svg>')


# ---------------------------------------------------------------------------
# Facts read from the repository.
# ---------------------------------------------------------------------------

def read_ledger(text):
    """Return the ledger entries and the counts per coverage class."""
    books = []
    for block in re.split(r'(?m)^## ', text)[1:]:
        heading, _, body = block.partition('\n')
        ident, *parts = [part.strip() for part in heading.split(' — ')]
        coverage = re.search(r'(?m)^Coverage: (.+)$', body)
        if not re.fullmatch(r'S\d\d', ident) or not parts or not coverage:
            raise ValueError('Unreadable ledger entry: ' + heading)
        label, _, detail = coverage.group(1).partition(' — ')
        if label.startswith('PARTIAL'):
            kind = 'partial'
        elif label.startswith('UNAVAILABLE BOOK TEXT'):
            kind = 'desc'
        elif label.startswith('UNAVAILABLE /'):
            kind = 'unres'
        else:
            raise ValueError('Unknown coverage label in ledger entry ' + ident)
        if ident in TITLE_AS_WRITTEN:
            title, byline = ' — '.join(parts), TITLE_AS_WRITTEN[ident]
        else:
            title, byline = parts[0], ' — '.join(parts[1:])
        books.append({'id': ident, 'title': title, 'byline': byline, 'cov': kind,
                      'read': detail[:1].upper() + detail[1:]})
    counts = {kind: sum(book['cov'] == kind for book in books) for kind in COVERAGE_NAMES}
    summary = re.search(r'(\d+) complete books; (\d+) partial primary texts; (\d+) descriptions only; '
                        r'(\d+) unresolved', text)
    if not summary or [int(n) for n in summary.groups()] != [0, counts['partial'], counts['desc'], counts['unres']]:
        raise ValueError('Ledger summary line does not match its entries')
    return books, counts


def read_reflexes(prompt):
    """R1–R7 from the instructions: id, name and the ledger entry it draws on."""
    found = re.findall(r'(?m)^(R\d) — (.+?) \(.*?\b(S\d\d)\b', prompt)
    if [r[0] for r in found] != list(REFLEX_LINES):
        raise ValueError('Reflexes in the instructions do not match the page')
    return [{'id': rid, 'name': name, 'source': src, 'line': REFLEX_LINES[rid]} for rid, name, src in found]


def read_prompt_lines(prompt):
    """The standing quote and the support question, as the instructions word them."""
    standing = re.search(r'standing instruction is: “(.+?)”', prompt)
    question = re.search(r'ask naturally: "(.+?)"', prompt)
    if not standing or not question:
        raise ValueError('Standing instruction or support question not found in the instructions')
    return standing.group(1), question.group(1)


def size_label(n):
    return f'{max(1, round(n / 1024))} KB'


# ---------------------------------------------------------------------------
# Markup helpers.
# ---------------------------------------------------------------------------

def esc(value):
    return html.escape(str(value), quote=True)


def mark(size):
    return (f'<svg class="mark" width="{size}" height="{size}" viewBox="0 0 48 48" '
            f'aria-hidden="true" focusable="false">{MARK_PATHS}</svg>')


def step_html(text, version):
    ledger = '<a href="sources/book-source-ledger.md" download>reading ledger</a>'
    return esc(text.replace('{version}', version)).replace('{ledger}', ledger)


def spine_height(i):
    return 190 + (i * 37) % 70


def masthead(edition):
    return f'''<header class="mast">
<span class="edition">{esc(edition)}</span>
<a class="brand" href="#top">{mark(40)}<span><small>Advice from</small> <b>LuminousPeace</b></span></a>
<nav aria-label="Main">
<a href="#top" data-nav="home">Field guide</a>
<a href="#ledger" data-nav="ledger">Reading ledger</a>
<a class="cta" href="#setup">Set it up</a>
</nav>
</header>'''


def opening(standing):
    sentences = re.findall(r'[^.]+\.', standing)
    return f'''<section class="opening" id="top">
<span class="label">{esc(TAGLINE)}</span>
<h1>{esc(sentences[0].strip())} <em>{esc(sentences[1].strip())}</em></h1>
<p class="lede">{esc(LEDE)}</p>
<blockquote class="pull"><p>{esc(standing)}</p><cite>{esc(QUOTE_CITE)}</cite></blockquote>
</section>'''


def chapter(number, anchor, title, lede, body):
    return f'''<section class="ch" id="{anchor}" aria-labelledby="{anchor}-h">
<h2 id="{anchor}-h" tabindex="-1"><span>{number}</span>{esc(title)}</h2>
<p>{esc(lede)}</p>
{body}
</section>'''


def conversation(question, footnote):
    picks = ''.join(
        f'<button type="button" class="pick" data-mode="{m["id"]}" aria-pressed="false">'
        f'<span class="label">0{i}</span><b>{esc(m["name"])}</b></button>'
        for i, m in enumerate(MODES, 1))
    replies = ''.join(
        f'<div class="reply" data-reply="{m["id"]}"><span class="label no-js">0{i} · {esc(m["name"])} — '
        f'{esc(m["line"])}</span>{esc(m["reply"])}<em>{esc(footnote)}</em></div>'
        for i, m in enumerate(MODES, 1))
    return f'''<div class="chat">
<div class="head"><span class="label">Sample conversation · written replies, not live output</span>
<button type="button" class="link js-only" data-mode="ask" hidden>Start over</button></div>
<p class="you"><small>You</small>{esc(SAMPLE_QUESTION)}</p>
<div class="bot">{mark(30)}<p>{esc(question)}</p></div>
<div class="picks js-only" role="group" aria-label="Choose the kind of answer">{picks}</div>
<div class="replies" aria-live="polite">{replies}</div>
</div>'''


def reflex_cards(reflexes, titles):
    cards = ''.join(
        f'<article class="idx"><span class="label"><span>{r["id"]}</span><span>{r["source"]}</span></span>'
        f'<h3>{esc(r["name"])}</h3><p>{esc(r["line"])}</p>'
        f'<a href="#book-{r["source"]}">Source: {esc(titles[r["source"]])} →</a></article>'
        for r in reflexes)
    return f'<div class="cards">{cards}</div>'


def shelf_teaser(books):
    bars = ''.join(f'<i class="{b["cov"]}" style="height:{spine_height(i) // 3}px"></i>'
                   for i, b in enumerate(books))
    return f'''<div class="teaser"><div class="mini" aria-hidden="true">{bars}</div>
<a class="go" href="#ledger">Walk the shelf →</a></div>'''


def platform_cards(platforms, version, footnote):
    cards = []
    for p in platforms:
        steps = ''.join(f'<li><span>{s}</span></li>' for s in p['steps'])
        cards.append(f'''<section class="plat" id="get-{p["id"]}" aria-labelledby="get-{p["id"]}-h">
<h3 id="get-{p["id"]}-h">{esc(p["name"])} <small>{esc(p["how"])}</small></h3>
<div class="get"><a class="btn primary" href="downloads/{esc(p["file"])}" download>↓ {esc(p["action"])}</a></div>
<p class="file">{esc(p["file"])} · {esc(p["size"])} · <a href="downloads/SHA256SUMS.txt">SHA-256 checksums</a></p>
<ol class="steps">{steps}</ol>
</section>''')
    cards_html = '\n'.join(cards)
    return f'''<div id="wizard" class="wizard" hidden></div>
<div class="platforms no-js">
{cards_html}
<div class="check"><b>How to know it worked</b> — Ask a real question. The reply should end with:<em>{esc(footnote)}</em></div>
</div>
<p id="copy-status" class="sr-only" role="status"></p>'''


def readable_texts(prompt, compact):
    return f'''<div class="texts">
<details id="text-portable"><summary>Portable instructions — readable text</summary><pre>{esc(prompt)}</pre></details>
<details id="text-copilot"><summary>Copilot instructions — readable text</summary><pre>{esc(compact)}</pre></details>
</div>'''


def ledger_view(books, counts, reflexes):
    informs = {r['source']: r for r in reflexes}
    key = ''.join(f'<span class="{kind}">{esc(COVERAGE_NAMES[kind])} · {counts[kind]}</span>'
                  for kind in COVERAGE_NAMES)
    spines = ''.join(
        f'<a class="spine {b["cov"]}" href="#book-{b["id"]}" style="height:{spine_height(i)}px" '
        f'aria-label="{b["id"]}: {esc(b["title"])} — {esc(COVERAGE_NAMES[b["cov"]])}">'
        f'<small>{b["id"][1:]}</small><span>{esc(b["title"])}</span></a>'
        for i, b in enumerate(books))
    cards = []
    for b in books:
        r = informs.get(b['id'])
        note = (f'<b>Informs reflex {r["id"]}</b> — {esc(r["name"])}' if r
                else 'Supplementary reference; no reflex draws on it.')
        byline = f'<p class="by">{esc(b["byline"])}</p>' if b['byline'] else ''
        cards.append(f'''<article class="bookcard" id="book-{b["id"]}" aria-labelledby="book-{b["id"]}-h">
<span class="label">{b["id"]}</span><h3 id="book-{b["id"]}-h">{esc(b["title"])}</h3>{byline}
<span class="cv {b["cov"]}">{esc(COVERAGE_NAMES[b["cov"]])}</span>
<p class="d">{esc(b["read"])}</p>
<div class="rf">{note}</div>
</article>''')
    cards_html = '\n'.join(cards)
    total = len(books)
    word = NUMBER_WORDS[total] if total < len(NUMBER_WORDS) else str(total)
    return f'''<section class="ledger" id="ledger" data-view="ledger" aria-labelledby="ledger-h">
<header class="lhead"><span class="label">Reading ledger</span>
<h1 id="ledger-h" tabindex="-1">{word} titles, honestly labelled.</h1>
<p>{esc(LEDGER_NOTE)}</p></header>
<div class="key">{key}</div>
<p class="label js-only">Choose a spine to read its card.</p>
<div class="shelfwrap">
<div class="shelf" role="group" aria-label="Bookshelf">{spines}</div>
<div class="books" aria-live="polite">
{cards_html}
</div>
</div>
<p class="lnote">{esc(PRIVACY_LINE)}</p>
<p class="ldl"><a href="sources/book-source-ledger.md" download>Download the full ledger (Markdown)</a>
<a href="sources/reflex-references.md">Reflex references</a></p>
</section>'''


def footer(footnote):
    links = [('docs/SETUP.md', 'Platform setup'), ('docs/VALIDATION.md', 'Validation'),
             ('docs/PRIVACY.md', 'Privacy &amp; safety'), ('CHANGELOG.md', 'Changes'),
             ('#ledger', 'Reading ledger'), ('LICENSE', 'MIT license')]
    nav = ''.join(f'<a href="{href}">{label}</a>' for href, label in links)
    return f'''<footer class="foot">{mark(30)}
<div><em>{esc(footnote)}</em>{esc(STATUS_LINE)} {esc(UPDATES_LINE)}</div>
<nav aria-label="Project">{nav}</nav>
</footer>'''


# ---------------------------------------------------------------------------
# The page.
# ---------------------------------------------------------------------------

def landing(meta, prompt, compact, files, ledger_text):
    """Return index.html as text. `files` is the generated output set so far."""
    version = meta['version']
    released = date.fromisoformat(meta['release_date'])
    footnote = meta['footnote']
    edition = f'Edition {version} · {released.strftime("%B %Y")}'
    if meta['status'] != 'released':
        edition += ' · Preview'
    standing, question = read_prompt_lines(prompt)
    reflexes = read_reflexes(prompt)
    books, counts = read_ledger(ledger_text)
    titles = {b['id']: b['title'] for b in books}
    if '0 complete books' not in ledger_text:
        raise ValueError('The page states that no complete books were read; the ledger must agree')

    platforms = []
    for p in PLATFORMS:
        name = p['file'].replace('{version}', version)
        payload = files.get('downloads/' + name)
        if payload is None:
            raise ValueError('Setup names a download that the build does not produce: ' + name)
        platforms.append({**p, 'file': name, 'size': size_label(len(payload)),
                          'steps': [step_html(s, version) for s in p['steps']]})
    texts = {'portable': files['downloads/portable-instructions.txt'].decode(),
             'copilot': files['downloads/copilot-agent-instructions.txt'].decode()}
    for p in platforms:
        if p['text'] and files['downloads/' + p['file']].decode() != texts[p['text']]:
            raise ValueError('Copy text differs from the download for ' + p['id'])

    data = {'platforms': [{k: p[k] for k in ('id', 'name', 'how', 'file', 'size', 'action', 'text', 'steps')}
                          for p in platforms],
            'texts': texts, 'footnote': footnote,
            'steps': {'names': STEP_NAMES, 'titles': STEP_TITLES, 'subs': STEP_SUBS}}
    data_json = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    favicon = 'data:image/svg+xml,' + quote(FAVICON_SVG, safe='')

    guide = '\n'.join([
        opening(standing),
        chapter('I', 'try', 'The four answers',
                'Before advising, it finds out which kind of help you want. Try it: pick one.',
                conversation(question, footnote)),
        chapter('II', 'reflexes', 'Seven reflexes',
                'Optional lenses drawn from partial readings. The core decides; a reflex is used '
                'only when the core leaves a gap.',
                reflex_cards(reflexes, titles)),
        chapter('III', 'shelf', 'The shelf',
                f'{NUMBER_WORDS[len(books)]} titles, each labelled with exactly how much was read.',
                shelf_teaser(books)),
        chapter('IV', 'setup', 'Take it with you',
                'Three steps, about two minutes. Nothing is installed until you paste or upload it yourself.',
                platform_cards(platforms, version, footnote) + '\n' + readable_texts(prompt, compact)),
    ])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="description" content="{esc(LEDE)}">
<title>Advice from LuminousPeace</title>
<link rel="icon" href="{favicon}">
<script>document.documentElement.classList.add('js');</script>
<style>
{CSS.strip()}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
{masthead(edition)}
<main id="main">
<div class="guide" data-view="home">
{guide}
</div>
{ledger_view(books, counts, reflexes)}
</main>
{footer(footnote)}
</div>
<script>
const PAGE = {data_json};
{JS.strip()}
</script>
<script>
/* If the script above failed to run at all, show the static page. */
if (!document.documentElement.hasAttribute('data-enhanced')) document.documentElement.classList.remove('js');
</script>
</body>
</html>
'''


CSS = r'''
:root {
  color-scheme: light dark;
  --serif: "Iowan Old Style", Charter, "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Noto Serif", serif;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --mono: ui-monospace, Menlo, Consolas, monospace;
  --paper: #f3eee2; --surface: #fbf8f0; --ink: #1d2b28; --ink-2: #3c4a46; --muted: #5d6a65;
  --line: #d9d0bd; --rule: #1d2b28; --accent: #b5762a; --accent-ink: #8a5514; --teal: #163b37;
  --focus: #b57b24; --logo-cut: #f3eee2; --ok: #2a5f55;
  --c-partial: #2a5f55; --c-desc: #b5762a; --c-unres: #a39d8e;
  --spine-partial: #2a5f55; --spine-desc: #94591a; --spine-unres: #a39d8e; --spine-unres-ink: #1d2b28;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #171513; --surface: #1f1c19; --ink: #efe8da; --ink-2: #d2cab9; --muted: #a59d8d;
    --line: #3a342d; --rule: #efe8da; --accent: #dda15a; --accent-ink: #e9b878; --teal: #8fc9bb;
    --focus: #dda15a; --logo-cut: #171513; --ok: #2f6b5e;
    --c-partial: #3f8576; --c-desc: #b5762a; --c-unres: #6d675d;
    --spine-partial: #33705f; --spine-desc: #94591a; --spine-unres: #5f5a51; --spine-unres-ink: #fff;
  }
}
*, *::before, *::after { box-sizing: border-box; }
[hidden] { display: none !important; }
html:not(.js) .js-only, .js .no-js { display: none !important; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 18px/1.65 var(--serif); }
button { font: inherit; color: inherit; cursor: pointer; }
a { color: inherit; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; }
[tabindex="-1"]:focus { outline: none; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.skip { position: absolute; left: 16px; top: -60px; z-index: 2; background: var(--ink); color: var(--paper); padding: 10px 14px; font: 600 15px var(--sans); }
.skip:focus { top: 12px; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 0 32px; }
.label { font: 700 11.5px/1.3 var(--sans); letter-spacing: .16em; text-transform: uppercase; color: var(--muted); }

/* Logo mark */
.mark { flex: none; display: block; }
.mark .sun { fill: var(--accent); }
.mark .rays { fill: none; stroke: var(--accent); stroke-width: 2.6; stroke-linecap: round; }
.mark .pages { fill: currentColor; }
.mark .cut { stroke: var(--logo-cut); stroke-width: 2.2; }

/* Masthead */
.mast { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 16px; padding: 22px 0 16px; border-bottom: 3px double var(--rule); }
.mast .edition { font: 500 13px var(--sans); color: var(--muted); }
.mast .brand { display: flex; flex-direction: column; align-items: center; gap: 4px; text-decoration: none; color: var(--ink); text-align: center; }
.mast .brand small { display: block; font: italic 400 15px var(--serif); color: var(--muted); }
.mast .brand b { display: block; font: 600 26px/1.05 var(--serif); letter-spacing: -.01em; }
.mast nav { justify-self: end; display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 18px; font: 600 14px var(--sans); }
.mast nav a { text-decoration: none; padding: 4px 0; border-bottom: 2px solid transparent; }
.mast nav a[aria-current="page"] { border-bottom-color: var(--accent); }
.mast nav .cta { border: 1px solid var(--rule); padding: 4px 12px; }

/* The guide */
.guide { max-width: 880px; margin: 0 auto; padding-top: 40px; }
.ledger { padding-top: 40px; }
.opening h1 { font-weight: 600; font-size: clamp(38px, 5.6vw, 68px); line-height: 1.02; letter-spacing: -.025em; margin: 12px 0 20px; text-wrap: balance; }
.opening h1 em { font-weight: 400; color: var(--accent-ink); }
.opening .label { display: block; line-height: 1.5; }
.opening .lede { font-size: 21px; color: var(--ink-2); max-width: 36em; margin: 0; }
.pull { margin: 36px 0 0; padding: 26px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); display: grid; grid-template-columns: 60px 1fr; column-gap: 18px; }
.pull::before { content: "“"; grid-row: span 2; font: 600 84px/0.8 var(--serif); color: var(--accent); }
.pull p { margin: 0; font-size: 27px; line-height: 1.3; font-style: italic; letter-spacing: -.01em; }
.pull cite { display: block; margin-top: 10px; font: 500 13.5px var(--sans); font-style: normal; color: var(--muted); }
.ch { padding-top: 52px; }
.ch h2 { display: flex; gap: 16px; align-items: baseline; font-weight: 600; font-size: 32px; line-height: 1.15; letter-spacing: -.015em; margin: 0 0 6px; }
.ch h2 span { font: italic 400 22px var(--serif); color: var(--accent-ink); min-width: 32px; }
.ch > p { color: var(--ink-2); margin: 0 0 22px; max-width: 38em; }

/* I · Sample conversation */
.chat { background: var(--surface); border: 1px solid var(--line); border-top: 3px solid var(--rule); padding: 20px 22px 22px; display: grid; gap: 16px; }
.chat .head { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
.link { background: none; border: 0; padding: 0; font: 600 12.5px var(--sans); color: var(--teal); text-decoration: underline; text-underline-offset: 3px; }
.you { margin: 0; font-size: 21px; line-height: 1.4; font-style: italic; padding-left: 18px; border-left: 2px solid var(--line); }
.you small { display: block; font: 700 11px var(--sans); letter-spacing: .14em; text-transform: uppercase; font-style: normal; color: var(--muted); margin-bottom: 4px; }
.bot { display: grid; grid-template-columns: 34px 1fr; gap: 12px; align-items: start; }
.bot p { margin: 0; font-size: 18px; }
.picks { display: grid; grid-template-columns: repeat(4, minmax(min-content, auto)); border-top: 1px solid var(--rule); }
.pick { text-align: left; background: none; border: 0; border-bottom: 1px solid var(--line); border-right: 1px solid var(--line); padding: 10px 12px 12px; display: grid; gap: 2px; }
.pick:last-child { border-right: 0; }
.pick .label { color: var(--accent-ink); }
.pick b { font-weight: 600; font-size: 16.5px; line-height: 1.2; }
.pick[aria-pressed="true"] { background: color-mix(in oklab, var(--accent) 16%, var(--surface)); box-shadow: inset 0 -3px 0 var(--accent); }
.replies { display: grid; gap: 16px; }
.reply { border-left: 3px solid var(--accent); padding: 4px 0 4px 18px; font-size: 18px; animation: rise .35s ease both; }
.reply .label { display: block; margin-bottom: 6px; color: var(--accent-ink); }
.reply em { display: block; margin-top: 10px; font: italic 14px var(--serif); color: var(--muted); }
.js .reply:not(.on) { display: none; }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } }

/* II · Reflexes */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.idx { background: var(--surface); border: 1px solid var(--line); padding: 16px 18px 18px; background-image: linear-gradient(transparent 33px, color-mix(in oklab, var(--accent) 35%, transparent) 33px, transparent 34px); }
.idx .label { display: flex; justify-content: space-between; }
.idx h3 { font-weight: 600; font-size: 18px; margin: 16px 0 0; line-height: 1.25; }
.idx p { margin: 6px 0 10px; font-size: 15.5px; color: var(--ink-2); font-style: italic; }
.idx a { font: 600 12.5px var(--sans); color: var(--teal); text-underline-offset: 3px; }

/* III · Shelf teaser */
.teaser { display: grid; grid-template-columns: 1fr auto; gap: 28px; align-items: end; padding: 26px 0 0; border-top: 1px solid var(--rule); }
.mini { display: flex; align-items: flex-end; gap: 3px; height: 92px; }
.mini i { width: 12px; border-radius: 2px 2px 0 0; }
.go { display: inline-flex; gap: 8px; align-items: center; background: var(--ink); color: var(--paper); padding: 12px 18px; font: 650 15px var(--sans); text-decoration: none; }
.partial { --c: var(--c-partial); } .desc { --c: var(--c-desc); } .unres { --c: var(--c-unres); }
.mini i { background: var(--c); }

/* IV · Setup */
.stepper { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin: 0 0 16px; padding: 0; list-style: none; }
.stepper button { width: 100%; text-align: left; background: none; border: 0; border-top: 3px solid var(--line); padding: 10px 0 0; color: var(--muted); display: grid; gap: 2px; }
.stepper button span { font: italic 400 20px var(--serif); color: var(--accent-ink); }
.stepper button b { font: 600 15px var(--sans); }
.stepper .done { border-top-color: var(--c-partial); color: var(--ink-2); }
.stepper [aria-current="step"] { border-top-color: var(--rule); color: var(--ink); }
.step, .plat { background: var(--surface); border: 1px solid var(--line); padding: 24px; }
.step h3, .plat h3 { font-weight: 600; font-size: 25px; margin: 0 0 2px; line-height: 1.2; }
.plat h3 small { font: 13px var(--sans); color: var(--muted); margin-left: 6px; }
.step .sub { margin: 0 0 18px; color: var(--ink-2); font-size: 16.5px; }
.choose { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }
.opt { text-align: left; background: var(--paper); border: 1px solid var(--line); padding: 14px; min-height: 92px; display: grid; align-content: space-between; gap: 8px; }
.opt b { font-weight: 600; font-size: 18px; line-height: 1.15; }
.opt small { font: 13px var(--sans); color: var(--muted); }
.opt[aria-pressed="true"] { border-color: var(--rule); box-shadow: inset 0 0 0 2px var(--rule); background: var(--surface); }
.get { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 620px; margin-top: 14px; }
.plat .get { grid-template-columns: minmax(0, 320px); }
.btn { display: flex; align-items: center; justify-content: center; min-height: 48px; padding: 10px 16px; border: 1px solid var(--rule); background: transparent; font: 650 15px var(--sans); text-decoration: none; text-align: center; color: var(--ink); }
.btn.primary { background: var(--ink); color: var(--paper); }
.btn.ok { background: var(--ok); color: #fff; border-color: var(--ok); }
.file { font: 12.5px/1.5 var(--mono); color: var(--muted); overflow-wrap: anywhere; margin: 10px 0 0; }
.warn { margin: 10px 0 0; font: 600 14px var(--sans); color: var(--accent-ink); }
.steps { margin: 0; padding: 0; list-style: none; counter-reset: s; display: grid; gap: 12px; }
.plat .steps { margin-top: 18px; }
.steps li { counter-increment: s; display: grid; grid-template-columns: 32px 1fr; gap: 10px; font-size: 17px; }
.steps li::before { content: counter(s, lower-roman) "."; font-style: italic; color: var(--accent-ink); text-align: right; }
.check { margin-top: 18px; padding: 14px 16px; background: color-mix(in oklab, var(--accent) 12%, var(--surface)); font: 14.5px/1.5 var(--sans); }
.check em { display: block; margin-top: 4px; font: italic 15px var(--serif); color: var(--ink-2); }
.nav { display: flex; justify-content: space-between; gap: 12px; margin-top: 22px; }
.nav .btn { white-space: nowrap; }
.nav .btn.primary { white-space: normal; }
.platforms { display: grid; gap: 14px; }
.texts { margin-top: 28px; border-top: 1px solid var(--line); }
details { border-bottom: 1px solid var(--line); padding: 14px 0; }
summary { cursor: pointer; font: 600 15px var(--sans); }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: var(--surface); border: 1px solid var(--line); padding: 20px; margin: 14px 0 0; font: 13px/1.6 var(--mono); max-height: 70vh; overflow: auto; }

/* Reading ledger */
.lhead { padding: 4px 0 10px; max-width: 760px; }
.lhead h1 { font-weight: 600; font-size: clamp(34px, 4.6vw, 54px); line-height: 1.05; letter-spacing: -.02em; margin: 10px 0 14px; }
.lhead p { color: var(--ink-2); margin: 0; }
.key { display: flex; flex-wrap: wrap; gap: 8px 22px; font: 13.5px var(--sans); color: var(--muted); margin: 18px 0 26px; }
.key span::before { content: ""; display: inline-block; width: 10px; height: 14px; margin-right: 7px; background: var(--c); vertical-align: -2px; }
.shelfwrap { display: grid; gap: 36px; }
.js .shelfwrap { grid-template-columns: minmax(0, 1fr) 300px; gap: 32px; align-items: end; }
.shelf { position: relative; display: flex; align-items: flex-end; gap: 4px; padding: 16px 10px 0; border-bottom: 10px solid color-mix(in oklab, var(--ink) 75%, var(--accent)); min-height: 300px; overflow-x: auto; }
.spine { flex: none; width: 36px; padding: 12px 0; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: space-between; border-radius: 3px 3px 0 0; text-decoration: none; transition: transform .2s ease; box-shadow: inset -4px 0 0 rgb(0 0 0 / .12); }
.spine.partial { background: var(--spine-partial); }
.spine.desc { background: var(--spine-desc); }
.spine.unres { background: var(--spine-unres); color: var(--spine-unres-ink); }
.spine span { writing-mode: vertical-rl; text-orientation: sideways; transform: rotate(180deg); font: 600 13px/1.1 var(--serif); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-height: 240px; }
.spine small { font: 700 10px var(--sans); }
.spine[aria-current="true"] { transform: translateY(-14px); box-shadow: inset -4px 0 0 rgb(0 0 0 / .12), 0 0 0 3px var(--paper), 0 0 0 5px var(--accent); }
.books { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.js .books { display: block; }
.bookcard { background: var(--surface); border: 1px solid var(--line); padding: 22px; }
.bookcard h3 { font-weight: 600; font-size: 24px; line-height: 1.15; margin: 8px 0 2px; }
.bookcard .by { color: var(--muted); font-style: italic; margin: 0 0 14px; }
.bookcard .cv { font: 600 13px var(--sans); display: inline-flex; gap: 8px; align-items: center; }
.bookcard .cv::before { content: ""; width: 10px; height: 10px; background: var(--c); }
.bookcard .d { font-size: 16px; color: var(--ink-2); margin: 10px 0 0; }
.bookcard .rf { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--line); font-size: 15.5px; }
.lnote { margin-top: 26px; font-style: italic; color: var(--ink-2); max-width: 46em; }
.ldl { display: flex; flex-wrap: wrap; gap: 6px 22px; font: 600 14px var(--sans); }

/* Footer */
.foot { margin-top: 72px; padding: 22px 0 44px; border-top: 3px double var(--rule); display: grid; grid-template-columns: auto 1fr auto; gap: 18px; align-items: start; font: 14px/1.55 var(--sans); color: var(--muted); }
.foot em { font: italic 15px var(--serif); color: var(--ink-2); display: block; }
.foot nav { display: flex; flex-direction: column; gap: 4px; text-align: right; }

@media (max-width: 980px) {
  .js .shelfwrap { grid-template-columns: 1fr; }
  .choose { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 860px) {
  .mast { grid-template-columns: auto 1fr; }
  .mast .edition { display: none; }
  .mast .brand { flex-direction: row; align-items: center; gap: 10px; text-align: left; }
  .mast .brand small { display: none; }
  .mast .brand b { font-size: 21px; }
}
@media (max-width: 760px) {
  body { font-size: 17px; }
  .wrap { padding: 0 16px; }
  .mast { grid-template-columns: 1fr; gap: 10px; }
  .mast .brand b { font-size: 19px; }
  .mast nav { justify-self: start; justify-content: flex-start; gap: 10px 16px; font-size: 13px; }
  .guide, .ledger { padding-top: 28px; }
  .pull { grid-template-columns: 1fr; } .pull::before { grid-row: auto; height: 36px; } .pull p { font-size: 22px; }
  .chat { padding: 16px; } .you { font-size: 18px; } .bot p, .reply { font-size: 16.5px; }
  .picks { grid-template-columns: repeat(2, minmax(0, 1fr)); } .pick:nth-child(2) { border-right: 0; }
  .teaser { grid-template-columns: 1fr; }
  .step, .plat { padding: 18px; }
  .choose { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .get { grid-template-columns: 1fr; }
  .foot { grid-template-columns: 1fr; } .foot nav { text-align: left; }
}
@media (prefers-reduced-motion: reduce) {
  .reply { animation: none; }
  .spine { transition: none; }
}
'''


JS = r'''
/* Enhances the static page: the sample conversation, the three-step setup,
   copy buttons and the reading ledger as a #ledger view. Every part also
   works without this script. */
(function () {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const esc = (text) => String(text).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const NUMERALS = ['I', 'II', 'III'];

  /* ---- I · Sample conversation ---------------------------------------- */
  function showReply(mode) {
    $$('.pick').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === mode)));
    $$('.reply').forEach((r) => r.classList.toggle('on', r.dataset.reply === mode));
    $('.chat [data-mode="ask"]').hidden = mode === 'ask';
  }

  /* ---- IV · Setup, one step at a time --------------------------------- */
  const setup = { step: 0, platform: PAGE.platforms[0].id, copy: 'idle' };
  const wizard = $('#wizard');

  function platform() {
    return PAGE.platforms.find((p) => p.id === setup.platform);
  }

  function chooseStep() {
    return '<div class="choose" role="group" aria-label="Assistants">' + PAGE.platforms.map((p) =>
      `<button type="button" class="opt" data-platform="${p.id}" aria-pressed="${p.id === setup.platform}">` +
      `<b>${esc(p.name)}</b><small>${esc(p.how)}</small></button>`).join('') + '</div>';
  }

  function getStep(p) {
    let copy = '';
    if (p.text) {
      const copied = setup.copy === 'copied';
      copy = `<button type="button" class="btn${copied ? ' ok' : ''}" data-copy="${p.text}">` +
        (copied ? '✓ Copied — paste it into your assistant' : 'Copy instructions') + '</button>';
    }
    const blocked = setup.copy === 'failed' && p.text
      ? `<p class="warn">Copying is blocked here. Download the file instead, or <a href="#text-${p.text}" data-open>select the text below</a>.</p>`
      : '';
    return `<div class="get"><a class="btn primary" href="downloads/${esc(p.file)}" download>↓ ${esc(p.action)}</a>${copy}</div>` +
      `<p class="file">${esc(p.file)} · ${esc(p.size)} · <a href="downloads/SHA256SUMS.txt">SHA-256 checksums</a></p>${blocked}`;
  }

  function pasteStep(p) {
    return '<ol class="steps">' + p.steps.map((s) => `<li><span>${s}</span></li>`).join('') + '</ol>' +
      `<div class="check"><b>How to know it worked</b> — Ask a real question. The reply should end with:<em>${esc(PAGE.footnote)}</em></div>`;
  }

  function renderSetup(focus) {
    const p = platform(), i = setup.step, s = PAGE.steps;
    const body = [chooseStep, getStep, pasteStep][i](p);
    const back = i > 0 ? `<button type="button" class="btn" data-step="${i - 1}">← Back</button>` : '<span></span>';
    const next = i < 2
      ? `<button type="button" class="btn primary" data-step="${i + 1}">Next →</button>`
      : '<button type="button" class="btn primary" data-done>Done — now try a real decision</button>';
    wizard.innerHTML =
      '<ol class="stepper">' + s.names.map((name, k) =>
        `<li><button type="button" data-step="${k}"${k === i ? ' aria-current="step"' : ''}${k < i ? ' class="done"' : ''}>` +
        `<span>${NUMERALS[k]}</span><b>${esc(name)}</b></button></li>`).join('') + '</ol>' +
      `<section class="step" aria-labelledby="step-h"><h3 id="step-h" tabindex="-1">${esc(s.titles[i])}${i > 0 ? ' · ' + esc(p.name) : ''}</h3>` +
      `<p class="sub">${esc(s.subs[i]).replace('{platform}', esc(p.name))}</p>${body}` +
      `<div class="nav">${back}${next}</div></section>`;
    const target = focus && $(focus, wizard);
    if (target) target.focus();
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); return true; } catch (error) { /* fall through */ }
    }
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.appendChild(area);
    area.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch (error) { ok = false; }
    area.remove();
    return ok;
  }

  /* ---- Views: the guide, or the reading ledger at #ledger -------------- */
  let view = null;
  let guideScroll = 0;  /* where the reader was in the guide before the ledger */

  function viewFor(hash) {
    if (!hash) return 'home';
    if (hash === 'ledger' || /^book-S\d\d$/.test(hash)) return 'ledger';
    const target = document.getElementById(hash);
    const owner = target && target.closest('[data-view]');
    return owner ? owner.dataset.view : view || 'home';
  }

  function selectBook(id) {
    const card = document.getElementById('book-' + id) || $('.bookcard');
    $$('.bookcard').forEach((c) => { c.hidden = c !== card; });
    const shelf = $('.shelf');
    $$('.spine').forEach((s) => {
      if (s.getAttribute('href') !== '#' + card.id) { s.removeAttribute('aria-current'); return; }
      s.setAttribute('aria-current', 'true');
      /* Keep the chosen spine in sight when the shelf scrolls sideways. */
      if (s.offsetLeft < shelf.scrollLeft || s.offsetLeft + s.offsetWidth > shelf.scrollLeft + shelf.clientWidth) {
        shelf.scrollLeft = s.offsetLeft - (shelf.clientWidth - s.offsetWidth) / 2;
      }
    });
    return card;
  }

  function route() {
    const hash = decodeURIComponent(location.hash.slice(1));
    const next = viewFor(hash);
    const book = /^book-(S\d\d)$/.exec(hash);
    const pickBook = () => selectBook(book ? book[1] : ($('.spine[aria-current]') || $('.spine')).getAttribute('href').slice(6));
    if (next === view) {
      if (view === 'ledger') pickBook();
      return;
    }
    const first = view === null;
    if (view === 'home') guideScroll = window.scrollY;
    view = next;
    $$('[data-view]').forEach((v) => { v.hidden = v.dataset.view !== view; });
    if (view === 'ledger') pickBook();
    $$('.mast [data-nav]').forEach((a) => {
      if (a.dataset.nav === view) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    document.title = (view === 'ledger' ? 'Reading ledger — ' : '') + 'Advice from LuminousPeace';
    if (first && !hash) return;
    const target = hash && document.getElementById(hash);
    if (view === 'ledger') {
      window.scrollTo(0, 0);
      if (!first) $('#ledger-h').focus({ preventScroll: true });
    } else if (target) {
      target.scrollIntoView();
    } else {
      window.scrollTo(0, guideScroll);  /* e.g. Back from the ledger */
    }
  }

  /* ---- Wiring ----------------------------------------------------------- */
  function onClick(event) {
    const t = event.target.closest('[data-mode],[data-platform],[data-step],[data-done],[data-copy],[data-open],.spine');
    if (!t) return;
    if (t.dataset.mode) {
      showReply(t.dataset.mode);
      if (t.dataset.mode === 'ask') $('.pick').focus();
    } else if (t.dataset.platform) {
      setup.platform = t.dataset.platform; setup.copy = 'idle';
      renderSetup(`[data-platform="${t.dataset.platform}"]`);
    } else if (t.dataset.step) {
      setup.step = Number(t.dataset.step); setup.copy = 'idle';
      renderSetup('#step-h');
    } else if ('done' in t.dataset) {
      setup.step = 0; setup.copy = 'idle';
      renderSetup();
      showReply('ask');
      $('#try').scrollIntoView();
      $('#try-h').focus({ preventScroll: true });
    } else if (t.dataset.copy) {
      const key = t.dataset.copy;
      copyText(PAGE.texts[key]).then((ok) => {
        setup.copy = ok ? 'copied' : 'failed';
        renderSetup(`[data-copy="${key}"]`);
        $('#copy-status').textContent = ok ? 'Instructions copied.' : 'Copying is blocked here. Download the file instead, or select the text below.';
      });
    } else if ('open' in t.dataset) {
      const details = document.getElementById(t.getAttribute('href').slice(1));
      if (details) details.open = true;
    } else if (t.classList.contains('spine')) {
      event.preventDefault();
      history.replaceState(null, '', t.getAttribute('href'));
      selectBook(t.getAttribute('href').slice(6)).scrollIntoView({ block: 'nearest' });
    }
  }

  try {
    showReply('ask');
    renderSetup();
    wizard.hidden = false;
    document.addEventListener('click', onClick);
    window.addEventListener('hashchange', route);
    route();
    document.documentElement.setAttribute('data-enhanced', '');
  } catch (error) {
    /* Fall back to the static page rather than leave parts hidden. */
    document.documentElement.classList.remove('js');
    $$('[data-view]').forEach((v) => { v.hidden = false; });
    if (wizard) wizard.hidden = true;
    throw error;
  }
})();
'''
