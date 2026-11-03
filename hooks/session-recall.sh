#!/usr/bin/env bash
# A Claude Code SessionStart hook (startup, resume, compact): what a fresh
# or compacted context must have in front of it before it touches anything.
# Plain stdout from a SessionStart hook is added to Claude's context.
#
# Prints: the ledger's state, the fixes index (newest rows), STATE.md's open
# faults and questions, and the standing rules that compaction loses first.
# Finds the top folder by walking up from CLAUDE_PROJECT_DIR (or the cwd)
# to the directory that holds context/LESSONS.md.

set -u
start="${CLAUDE_PROJECT_DIR:-$PWD}"
top=""
d="$start"
while [ -n "$d" ] && [ "$d" != "/" ]; do
  if [ -f "$d/context/LESSONS.md" ]; then top="$d"; break; fi
  d="$(dirname "$d")"
done
[ -z "$top" ] && exit 0

echo "=== Session recall (hooks/session-recall.sh) ==="
echo "Top folder: $top"

ledger="$top/ledger/runs.jsonl"
if [ -f "$ledger" ]; then
  echo "Ledger: $(wc -l < "$ledger") runs recorded in ledger/runs.jsonl."
else
  echo "Ledger: EMPTY (no ledger/runs.jsonl). No 'Evidence: emulator' trailer is valid until the runners record. Rebuild the runner-to-ledger path first."
fi

fixed=""
for f in "$top/context/FIXED.md" "$top/FIXED.md"; do
  [ -f "$f" ] && fixed="$f" && break
done
if [ -n "$fixed" ]; then
  echo "--- Fixes already made ($fixed, newest 25 rows) ---"
  grep -E '^\| ' "$fixed" | sed -n '3,27p'
else
  echo "--- FIXED.md is missing: run python3 METHOD/tools/fixed.py --out $top/context/FIXED.md in a uCDD worktree ---"
fi

refsidx="$top/context/REFS.md"
if [ -f "$refsidx" ]; then
  echo "--- Which document decides what (context/REFS.md, first 20 keys; regenerate with tools/refindex.py) ---"
  grep -E '^\| `' "$refsidx" | head -20
else
  echo "--- context/REFS.md is missing: python3 METHOD/tools/refindex.py --out $top/context/REFS.md ---"
fi

state="$top/context/STATE.md"
if [ -f "$state" ]; then
  echo "--- STATE.md: open faults ---"
  awk '/^## Open faults/{f=1;next} /^## /{f=0} f' "$state" | head -40
  echo "--- STATE.md: questions for Michael (unanswered questions become your assumptions) ---"
  awk '/^## Questions for Michael/{f=1;next} /^## /{f=0} f' "$state" | head -30
  # Gate tables for any directive in force (Tightening r3, Project A, ...): the current gate and
  # its first unmet acceptance line are what a fresh or compacted context acts on first.
  for sec in "Tightening r3" "Project A"; do
    if grep -q "^## $sec" "$state"; then
      echo "--- STATE.md: $sec (do the first gate that is not PASS; nothing else) ---"
      awk -v s="^## $sec" '$0 ~ s {f=1;next} /^## /{f=0} f' "$state" | head -40
    fi
  done
fi
# r3.8 (2 Nov 2026): METHOD, the package this hook is in (the block below names it; set -u)
METHOD="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# r3.8: paste this block into hooks/session-recall.sh after the STATE.md gate tables
# (the "for sec in" loop). It prints the lessons_read check for every IN_PROGRESS gate
# at session start, resume and compaction, so a gate worked on without its pre-read is
# seen before the work resumes, not after the next hit.
lessons="$top/context/LESSONS.md"
if [ -f "$lessons" ] && [ -f "$state" ]; then
  echo "--- Lessons pre-read (r3.8): every IN_PROGRESS gate carries lessons_read = \"terms: ...; lessons: ...; date\" ---"
  python3 "$METHOD/tools/lessons_recall.py" check --register "$lessons" --state "$state" 2>&1 | head -6
  echo "    before a gate or a new tool: python3 METHOD/tools/lessons_recall.py <terms> --line  (paste the line into the gate row)"
  echo "    a hit line ends '| read: yes' if the lesson was in that gate's pre-read list, else '| read: no' (a reading failure)"
fi
# r3.9: paste this block into hooks/session-recall.sh after the r3.8 lessons block.
# It prints the library's search coverage at session start, resume and compaction, so a
# document that joined the library and is not searched (question 54's failure: 32 files
# of Ralf Brown's list unread for a week) is seen before the next "silent" is written.
# Installed with one change (3 Nov 2026): the package tested `libsearch.py --coverage | tail -4`,
# whose status is tail's, so the LIBRARY line could never print (L33); the tool's own exit
# is kept and read here.
if [ -d "$METHOD" ]; then
  echo "--- Library search coverage (r3.9): every document searched, PDFs through their extraction ---"
  coverage="$(python3 "$METHOD/tools/libsearch.py" --coverage 2>&1)"
  coverage_exit=$?
  printf '%s\n' "$coverage" | tail -4
  if [ "$coverage_exit" -ne 0 ]; then
    echo "    LIBRARY: a document is unsearched; add its extraction before any silent is written"
  fi
fi

cat <<'EOF'
--- Standing rules that compaction loses first ---
- Before any edit to src/*.asm, *.inc or scripts/build.py the recall hook shows what the notes already say; read it in full; cite or cherry-pick an existing fix, never rewrite it (a rewrite is a lesson hit).
- No "Evidence: emulator" without a ledger entry the runners wrote; no verdict from a run with the dynamic recompiler on (RIG_DYNAREC=0 for every run that records).
- Rule 1 first: the citation is written in the row before the fix, and it names a key in method.toml [references].
- One ISSUES.md, on the notes branch; rows go there, never into a feature branch's copy.
- "Built, not run" is not done. Say it in every place the change is mentioned.
- Before writing a test case, a row or a fix: name the key that decides its expected result (context/REFS.md), quote its line; no key means `silent` and what decides instead. The recall hook shows the document lines before the edit; read them.
EOF
exit 0
