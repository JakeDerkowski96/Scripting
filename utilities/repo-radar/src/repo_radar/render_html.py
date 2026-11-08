"""Render projects as one self-contained HTML dashboard (no external assets).

The page filters and sorts client-side, so it works from a local file with no
server. Every value from a repo is escaped before it reaches the markup.
"""

from __future__ import annotations

from datetime import datetime
from html import escape

from repo_radar.attention import FLAGS
from repo_radar.models import STAGES, Project, ScanResult
from repo_radar.query import humanize_age, pr_summary, sync_summary

_CSS = """
:root{--bg:#f6f7f9;--surface:#fff;--text:#1b1f24;--muted:#5d6672;--line:#e1e5ea;--accent:#2457d6;
--ok:#1a7f4b;--warn:#a15c00;--bad:#b42318;--chip:#eef1f5;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1318;--surface:#171c23;
--text:#e6e9ee;--muted:#98a2b0;--line:#272e38;--accent:#7aa2ff;--ok:#4cc38a;--warn:#e5a63a;
--bad:#ff7b72;--chip:#222a35;}}
:root[data-theme="dark"]{--bg:#0f1318;--surface:#171c23;--text:#e6e9ee;--muted:#98a2b0;
--line:#272e38;--accent:#7aa2ff;--ok:#4cc38a;--warn:#e5a63a;--bad:#ff7b72;--chip:#222a35;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1280px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:20px;margin:0 0 2px}
.sub{color:var(--muted);margin:0 0 20px;font-size:13px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:18px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.tile b{display:block;font-size:22px;font-variant-numeric:tabular-nums}
.tile span{color:var(--muted);font-size:12px}
.tile.alert b{color:var(--bad)}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px}
input[type=search],select{background:var(--surface);color:var(--text);border:1px solid var(--line);
border-radius:6px;padding:7px 10px;font:inherit}
input[type=search]{min-width:220px;flex:1 1 220px}
label{display:flex;gap:6px;align-items:center;color:var(--muted)}
.wrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;min-width:900px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);cursor:pointer;
white-space:nowrap;user-select:none}
th:hover{color:var(--text)}
tr:last-child td{border-bottom:0}
td.name a,td.name strong{font-weight:600;color:var(--text);text-decoration:none}
td.name a:hover{color:var(--accent);text-decoration:underline}
.desc{display:block;color:var(--muted);font-size:12.5px;max-width:420px}
.stage{display:inline-block;padding:1px 8px;border-radius:999px;background:var(--chip);font-size:12px}
.stage.active{color:var(--ok)}.stage.paused{color:var(--warn)}.stage.unset{color:var(--bad)}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.muted{color:var(--muted)}
.flag{display:inline-block;margin:0 4px 4px 0;padding:1px 7px;border-radius:4px;font-size:12px;
background:var(--chip);color:var(--bad);cursor:help}
.tag{display:inline-block;margin-right:4px;font-size:11.5px;color:var(--muted)}
.empty{padding:24px;text-align:center;color:var(--muted);display:none}
footer{margin-top:14px;color:var(--muted);font-size:12px}
"""

_JS = """
const rows=[...document.querySelectorAll('tbody tr')];
const q=document.getElementById('q'),st=document.getElementById('stage'),
at=document.getElementById('attn'),empty=document.getElementById('empty');
function apply(){
  const t=q.value.toLowerCase();let shown=0;
  rows.forEach(r=>{
    const ok=(!t||r.dataset.text.includes(t))&&(!st.value||r.dataset.stage===st.value)
      &&(!at.checked||r.dataset.flags!=='0');
    r.hidden=!ok;if(ok)shown++;
  });
  empty.style.display=shown?'none':'block';
}
[q,st,at].forEach(e=>e.addEventListener('input',apply));
let dir={};
document.querySelectorAll('th[data-k]').forEach(th=>th.addEventListener('click',()=>{
  const k=th.dataset.k;dir[k]=!dir[k];const m=dir[k]?1:-1;
  const body=document.querySelector('tbody');
  rows.sort((a,b)=>{
    const x=a.dataset[k],y=b.dataset[k],isNum=s=>/^\\d+$/.test(s);
    return (isNum(x)&&isNum(y)?x-y:x.localeCompare(y))*m;
  }).forEach(r=>body.appendChild(r));
}));
"""


def _stage_cell(stage: str) -> str:
    label = stage or "unset"
    return f'<span class="stage {escape(label)}">{escape(label)}</span>'


def _row(p: Project, now: datetime) -> str:
    name = escape(p.name)
    if p.github and p.github.slug:
        name_html = f'<a href="https://github.com/{escape(p.github.slug)}">{name}</a>'
    else:
        name_html = f"<strong>{name}</strong>"

    desc = escape(p.meta.summary) if p.meta.summary else '<span class="muted">no summary</span>'
    tags = "".join(f'<span class="tag">#{escape(t)}</span>' for t in p.meta.tags)

    sync = sync_summary(p)
    sync_cls = "ok" if sync == "✓" else "warn"
    prs = pr_summary(p)
    ci = p.github.ci_status if p.github else ""
    ci_html = {
        "success": '<span class="ok">pass</span>',
        "failure": '<span class="bad">fail</span>',
        "running": '<span class="warn">running</span>',
    }.get(ci, '<span class="muted">—</span>')

    flags = (
        "".join(
            f'<span class="flag" title="{escape(FLAGS.get(f, f))}">{escape(f)}</span>'
            for f in p.flags
        )
        or '<span class="ok">ok</span>'
    )

    nxt = escape(p.meta.next_step) if p.meta.next_step else '<span class="muted">—</span>'
    blockers = (
        f'<span class="desc bad">blocked: {escape("; ".join(p.meta.blockers))}</span>'
        if p.meta.blockers
        else ""
    )
    search_text = " ".join([p.name, p.meta.summary, *p.meta.tags]).lower()

    return (
        f'<tr data-text="{escape(search_text)}" data-stage="{escape(p.meta.stage)}" '
        f'data-flags="{len(p.flags)}" data-name="{name}" '
        f'data-last="{escape(p.git.last_commit)}" data-prs="{escape(prs)}">'
        f'<td class="name">{name_html}<span class="desc">{desc}</span>{tags}</td>'
        f"<td>{_stage_cell(p.meta.stage)}</td>"
        f'<td class="num">{escape(p.git.branch or "—")}</td>'
        f'<td class="num {sync_cls}">{escape(sync)}</td>'
        f'<td class="num">{escape(prs)}</td>'
        f"<td>{ci_html}</td>"
        f'<td class="num">{escape(humanize_age(p.git.last_commit, now))}</td>'
        f"<td>{nxt}{blockers}</td>"
        f"<td>{flags}</td></tr>"
    )


def render_html(result: ScanResult, projects: list[Project], *, now: datetime) -> str:
    """Return the full HTML document.

    Args:
        result: The scan the projects came from (for root and timestamp).
        projects: Rows to show, already filtered and sorted.
        now: Reference time for the age column.
    """
    total = len(projects)
    attention = sum(1 for p in projects if p.flags)
    dirty = sum(1 for p in projects if p.git.dirty)
    unpushed = sum(1 for p in projects if p.git.ahead)
    open_prs = sum((p.github.open_prs or 0) for p in projects if p.github)
    unset = sum(1 for p in projects if not p.meta.stage)

    tiles = [
        ("Projects", total, ""),
        ("Need attention", attention, "alert" if attention else ""),
        ("Uncommitted", dirty, "alert" if dirty else ""),
        ("Unpushed", unpushed, "alert" if unpushed else ""),
        ("Open PRs", open_prs, ""),
        ("No stage set", unset, "alert" if unset else ""),
    ]
    tiles_html = "".join(
        f'<div class="tile {cls}"><b>{n}</b><span>{escape(label)}</span></div>'
        for label, n, cls in tiles
    )
    options = "".join(f'<option value="{s}">{s}</option>' for s in STAGES)
    rows_html = "\n".join(_row(p, now) for p in projects)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Repo Radar</title>
<style>{_CSS}</style>
</head>
<body>
<main>
<h1>Repo Radar</h1>
<p class="sub">{escape(result.root)} · scanned {escape(result.scanned_at)}</p>
<div class="tiles">{tiles_html}</div>
<div class="controls">
<input type="search" id="q" placeholder="Filter by name, summary, tag">
<select id="stage"><option value="">All stages</option>{options}</select>
<label><input type="checkbox" id="attn"> Needs attention only</label>
</div>
<div class="wrap">
<table>
<thead><tr>
<th data-k="name">Project</th><th data-k="stage">Stage</th><th>Branch</th><th>Sync</th>
<th data-k="prs">PRs</th><th>CI</th><th data-k="last">Last commit</th><th>Next</th>
<th data-k="flags">Flags</th>
</tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
<div class="empty" id="empty">No projects match.</div>
</div>
<footer>Sync: ↑ unpushed commits · ↓ unpulled commits · * changed files. Click a header to sort.</footer>
</main>
<script>{_JS}</script>
</body>
</html>
"""
