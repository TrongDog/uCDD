#!/usr/bin/env bash
# A Claude Code SessionStart hook (startup, resume, compact): what a fresh
# or compacted context must have in front of it before it touches anything.
# Plain stdout from a SessionStart hook is added to Claude's context.
#
# Prints: one line per check (the ledger, the fixes and references indexes, STATE's gate, open
# questions and faults, the lessons pre-read, the library's coverage), then the standing rules
# that compaction loses first.
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

# One line per check, pass or the failing line, never tables (the owner's decision of 9 Nov 2026,
# efficiency: "The session-recall hook prints one line per check (pass or the failing line), not
# tables"). The fixes index, the references index, STATE's sections and the library's coverage are
# read where they are; the hook says whether each is there and sound, and points to it.
METHOD="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== Session recall (hooks/session-recall.sh): one line per check; top folder $top ==="

ledger="$top/ledger/runs.jsonl"
if [ -f "$ledger" ]; then
  echo "ledger: pass, $(wc -l < "$ledger") runs in ledger/runs.jsonl"
else
  echo "ledger: FAIL: EMPTY (no ledger/runs.jsonl); no 'Evidence: emulator' trailer is valid until the runners record"
fi

fixed=""
for f in "$top/context/FIXED.md" "$top/FIXED.md"; do
  [ -f "$f" ] && fixed="$f" && break
done
rows=0
[ -n "$fixed" ] && rows=$(($(grep -cE '^\| ' "$fixed") - 2))
if [ -n "$fixed" ] && [ "$rows" -gt 0 ]; then
  echo "fixes index: pass, ${fixed#$top/}, $rows rows; search it by symptom, file, port or command before any change"
elif [ -n "$fixed" ]; then
  echo "fixes index: FAIL: ${fixed#$top/} holds no rows; run python3 METHOD/tools/fixed.py --out $fixed in a uCDD worktree"
else
  echo "fixes index: FAIL: FIXED.md is missing; run python3 METHOD/tools/fixed.py --out $top/context/FIXED.md in a uCDD worktree"
fi

refsidx="$top/context/REFS.md"
keys=0
[ -f "$refsidx" ] && keys=$(grep -cE '^\| `' "$refsidx")
if [ "$keys" -gt 0 ]; then
  echo "refs index: pass, context/REFS.md, $keys keys; name the key that decides before a test, row or fix"
elif [ -f "$refsidx" ]; then
  echo "refs index: FAIL: context/REFS.md holds no keys; python3 METHOD/tools/refindex.py --out $refsidx"
else
  echo "refs index: FAIL: context/REFS.md is missing; python3 METHOD/tools/refindex.py --out $top/context/REFS.md"
fi

state="$top/context/STATE.md"
if [ -f "$state" ]; then
  # the first IN_PROGRESS gate row of any table (Project A, Tightening): its gate and first unmet line
  gate="$(grep -m1 -E '^\| *[AT][0-9][^|]*\| *IN_PROGRESS' "$state" | awk -F'|' '{g=$2; f=$4; gsub(/^ +| +$/, "", g); gsub(/^ +| +$/, "", f); print g "; first unmet: " (f == "" ? "none written" : f)}')"
  # none in progress: the first gate row that is not PASS (the next to start), else a FAIL
  [ -z "$gate" ] && gate="$(grep -E '^\| *[AT][0-9][^|]*\|' "$state" | grep -vE '^\| *[AT][0-9][^|]*\| *PASS' | head -1 | awk -F'|' '{g=$2; s=$3; gsub(/^ +| +$/, "", g); gsub(/^ +| +$/, "", s); print g "; " s " (none in progress: the first not PASS)"}')"
  if [ -n "$gate" ]; then
    echo "gate: $gate (do it; nothing else)"
  else
    echo "gate: FAIL: no gate row (| A0 or | T0 ... |) in context/STATE.md"
  fi
  # the paragraph that opens "Open, by number", joined, up to its first full stop
  open="$(awk '/^Open, by number/{f=1} f && /^$/{exit} f' "$state" | tr '\n' ' ' | sed -E 's/^Open, by number[^:]*: *//; s/\. .*//; s/\.? *$//')"
  [ -z "$open" ] && open="$(awk '/^## Questions for the owner/{f=1;next} /^## /{f=0} f && /^[0-9]+\. /' "$state" | grep -vc 'Answered') numbered, the format before 9 Nov 2026"
  if grep -qE '^Open, by number|^## Questions for the owner' "$state"; then
    echo "questions open: ${open:-none} (unanswered questions become your assumptions)"
  else
    echo "questions open: FAIL: context/STATE.md has neither an \"Open, by number\" line nor a Questions for the owner section"
  fi
  faults="$(awk '/^## Open faults/{f=1;next} /^## /{f=0} f' "$state" | tr '\n' ' ' | sed -E 's/  +/ /g; s/^ //; s/ $//')"
  [ "${#faults}" -gt 300 ] && faults="${faults:0:300} ... (the rest in context/STATE.md, Open faults)"
  if grep -qE '^## Open faults' "$state"; then
    echo "open faults: ${faults:-none written}"
  else
    echo "open faults: FAIL: context/STATE.md has no Open faults section"
  fi
else
  echo "state: FAIL: context/STATE.md is missing"
fi

lessons="$top/context/LESSONS.md"
if [ -f "$lessons" ] && [ -f "$state" ]; then
  said="$(python3 "$METHOD/tools/lessons_recall.py" check --register "$lessons" --state "$state" 2>&1)"
  if [ $? -eq 0 ]; then
    echo "lessons pre-read: pass (every IN_PROGRESS gate carries its lessons_read line; before a gate or a new tool: python3 METHOD/tools/lessons_recall.py <terms> --line)"
  else
    echo "lessons pre-read: FAIL: $(printf '%s\n' "$said" | tail -1)"
  fi
fi

if [ -d "$METHOD" ]; then
  # the tool's own exit is read, never tail's (L33: the r3.9 package's `| tail -4` hid it)
  coverage="$(python3 "$METHOD/tools/libsearch.py" --coverage 2>&1)"
  if [ $? -eq 0 ]; then
    echo "library: pass, $(printf '%s\n' "$coverage" | tail -1)"
  else
    echo "library: FAIL: $(printf '%s\n' "$coverage" | tail -1); add its extraction before any silent is written"
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
