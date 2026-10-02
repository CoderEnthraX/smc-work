# shared HTML pieces for the handbooks and the test report (style of the v8.3 handbook)
import html as _h

CSS = open(__file__.replace("common.py", "fonts_local.css")).read() + """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
* { box-sizing: border-box; }
body { font-family: 'Inter', 'Liberation Sans', Arial, sans-serif; color: #1f2733; font-size: 9.6pt; line-height: 1.45; margin: 0; }
.cover { height: 250mm; position: relative; page-break-after: always; }
.cover .bar { height: 5px; background: #1d5b8c; margin-top: 4mm; }
.cover .kick { margin-top: 26mm; color: #1d5b8c; font-weight: 700; letter-spacing: 2.5px; font-size: 10pt; }
.cover h1 { font-size: 34pt; margin: 3mm 0 3mm 0; font-weight: 800; letter-spacing: -0.5px; }
.cover .sub { font-size: 13pt; color: #4a5566; max-width: 125mm; line-height: 1.45; }
.cover .meta { margin-top: 22mm; display: grid; grid-template-columns: 1fr 1fr; column-gap: 12mm; width: 146mm; }
.cover .meta div { border-top: 1px solid #d8dde4; padding: 2.2mm 0 2.8mm 0; }
.cover .meta b { display: block; font-size: 7.2pt; letter-spacing: 1.2px; color: #6b7686; font-weight: 500; }
.cover .note { position: absolute; bottom: 0; left: 0; right: 0; border-top: 1px solid #d8dde4; padding-top: 3mm; color: #6b7686; font-size: 8.4pt; }
.chap { page-break-before: always; }
.lab { color: #1d5b8c; font-weight: 700; letter-spacing: 2px; font-size: 8.4pt; margin-bottom: 1mm; }
h2 { font-size: 21pt; margin: 0 0 2mm 0; font-weight: 800; letter-spacing: -0.3px; }
.lead { color: #4a5566; font-size: 10.4pt; margin: 0 0 5mm 0; }
h3 { font-size: 12pt; margin: 6mm 0 2mm 0; }
p { margin: 0 0 2.2mm 0; }
.card { border: 1px solid #d8dde4; border-radius: 6px; padding: 3.2mm 4mm 2mm 4mm; margin: 0 0 3.5mm 0; page-break-inside: avoid; }
.card .ch { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2mm; gap: 3mm; }
.card .ct { font-weight: 700; font-size: 10.6pt; }
.pills { white-space: nowrap; }
.pd { border: 1px solid #c9d1db; border-radius: 10px; padding: 0.6mm 2.6mm; font-size: 8pt; color: #4a5566; margin-left: 1.5mm; }
.ps { background: #1d5b8c; color: #fff; border-radius: 10px; padding: 0.7mm 2.8mm; font-size: 8pt; font-weight: 600; margin-left: 1.5mm; }
.ps.warn { background: #9a4b00; } .ps.bad { background: #8b1010; } .ps.good { background: #0b6b3a; }
.row { display: grid; grid-template-columns: 27mm 1fr; column-gap: 3mm; margin-bottom: 1.6mm; }
.row .k { font-size: 7.4pt; letter-spacing: 1.1px; color: #6b7686; padding-top: 0.5mm; }
code, .mono { font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size: 8.2pt; background: #f1f3f6; border-radius: 3px; padding: 0 1mm; }
table { border-collapse: collapse; width: 100%; margin: 1mm 0 4mm 0; font-size: 8.5pt; page-break-inside: avoid; }
th { text-align: left; font-size: 7.3pt; letter-spacing: 0.8px; color: #6b7686; font-weight: 600; border-bottom: 1.5px solid #c9d1db; padding: 1.4mm 1.6mm; }
td { border-bottom: 1px solid #e3e7ec; padding: 1.3mm 1.6mm; vertical-align: top; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.hl td { background: #eef4fa; font-weight: 600; }
.pos { color: #0b6b3a; } .neg { color: #a01515; }
.box { border-left: 4px solid #1d5b8c; background: #f3f7fb; padding: 3mm 4mm; margin: 2mm 0 4mm 0; page-break-inside: avoid; }
.box.warn { border-left-color: #b86200; background: #fdf6ee; }
.box.bad { border-left-color: #a01515; background: #fcf1f1; }
.box b.t { display: block; margin-bottom: 1mm; }
ol, ul { margin: 0 0 2.5mm 0; padding-left: 5.5mm; } li { margin-bottom: 1mm; }
.tag { display: inline-block; font-size: 7.2pt; font-weight: 700; border-radius: 3px; padding: 0.2mm 1.5mm; color: #fff; }
.tag.g { background: #0b6b3a; } .tag.r { background: #a01515; } .tag.y { background: #8a6d00; } .tag.b { background: #1d5b8c; }
.small { font-size: 8.2pt; color: #4a5566; }
.divider { page-break-before: always; height: 240mm; display: flex; flex-direction: column; justify-content: center; }
.divider h2 { font-size: 28pt; }
svg text { font-family: 'Inter', 'Liberation Sans', Arial, sans-serif; }
"""


def esc(s):
    return _h.escape(s, quote=False)


def page(title, body):
    return "<!doctype html><html><head><meta charset='utf-8'><title>%s</title><style>%s</style></head><body>%s</body></html>" % (esc(title), CSS, body)


def cover(kick, title, sub, meta, note):
    m = "".join("<div><b>%s</b>%s</div>" % (a, b) for a, b in meta)
    return "<div class='cover'><div class='bar'></div><div class='kick'>%s</div><h1>%s</h1><div class='sub'>%s</div><div class='meta'>%s</div><div class='note'>%s</div></div>" % (kick, title, sub, m, note)


def chap(lab, title, lead, first=False):
    return "<div class='%s'><div class='lab'>%s</div><h2>%s</h2><p class='lead'>%s</p></div>" % ("" if first else "chap", lab, title, lead)


def card(title, default, setv, rows, kind=""):
    r = "".join("<div class='row'><div class='k'>%s</div><div class='v'>%s</div></div>" % (k, v) for k, v in rows)
    return "<div class='card'><div class='ch'><div class='ct'>%s</div><div class='pills'><span class='pd'>Default: %s</span><span class='ps %s'>Set: %s</span></div></div>%s</div>" % (title, default, kind, setv, r)


def table(head, rows, num=(), hl=()):
    th = "".join("<th class='%s'>%s</th>" % ("n" if i in num else "", h) for i, h in enumerate(head))
    tr = ""
    for j, r in enumerate(rows):
        tr += "<tr class='%s'>" % ("hl" if j in hl else "") + "".join("<td class='%s'>%s</td>" % ("n" if i in num else "", c) for i, c in enumerate(r)) + "</tr>"
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, tr)


def money(x, sign=True):
    s = "{:+,}".format(int(x)) if sign else "{:,}".format(int(x))
    cls = "pos" if x > 0 else "neg" if x < 0 else ""
    return "<span class='%s'>%s</span>" % (cls, s)


def box(title, body, kind=""):
    return "<div class='box %s'><b class='t'>%s</b>%s</div>" % (kind, title, body)
