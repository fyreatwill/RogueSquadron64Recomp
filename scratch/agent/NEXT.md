# NEXT work unit (s2230) — compare common key-on tuple sets with retail

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Use the existing s2223 retail oracle log and the s2229 8192-detail port log to
compare normalized `($v0,$s1,$a0,$a2)` tuple-set membership for the common
retail and port buckets `0x00696100:640` and `0x006AB400:512`, at all eight
transfer PCs. Include the positive-control and phase-hit checks in the same
result table. Do not compare the port-only title bucket or infer the missing
second 640 origin from this run. Do not change generated game behavior,
key-on returns, guards, defaults, task fields, audio dispatch, or oracle code.

Competing hypotheses and the single discriminator:

- H-ParityMatch: the port tuple sets equal retail in both common buckets, per
  transfer PC; the remaining issue is route/phase coverage.
- H-PortOperandMismatch: one or more port-only tuples remain after
  normalization in a common bucket, identifying an operand-contract split.
- H-RetailOperandMismatch: one or more retail-only tuples remain while the
  port rows are internally complete, identifying a port-side missing branch or
  source value rather than a census-cap artifact.
- H-JoinOrCoverageMismatch: differences disappear when rows are keyed by the
  exact `(origin,width,PC)` bucket, or one side lacks a positive phase row; the
  tuple comparison is not valid and must not drive a runtime change.

The discriminator is one 2-bucket × 8-PC table containing, for each exact
bucket and transfer PC: retail hit count, port transfer count, retail unique
tuple count, port unique tuple count, set intersection, retail-only count, and
port-only count. The retail log is valid only if its whole-RDRAM control is
10,000 writes and both common phase rows are present; the port log is valid
only if its driver reports nonzero LLE/audio controls and its table rows show
zero overflow. Equal sets select H-ParityMatch; port-only values select
H-PortOperandMismatch; retail-only values select H-RetailOperandMismatch; a
missing control or bucket selects H-JoinOrCoverageMismatch. No null without
the controls is usable.

## Exact commands

Verify the independent retail control and the selected port result:

~~~sh
rg -n '\[oracle\] watch write.*10000|\[oracle\] done:|width=640 origin=0x00696100|width=512 origin=0x006ab400' scratch/agent/s2223_retail_keyon_guard_table.log | tail -20
tail -45 scratch/agent/s2229_8192_detail_driver.log
rg -n '\[m5-keyon-table\].*(width=640|width=512)' scratch/s73_post_a_scene/s2229_8192_detail/run.log | tail -12
~~~

Normalize and compare the two common buckets without reading whole logs:

~~~sh
tmpdir=$(mktemp -d /tmp/rs64-keyon-tuples.XXXXXX)
awk '
  /\[hit\]/ {
    pc=""; origin=""; width=""; v0=""; s1=""; a0=""; a2=""
    for (i=1;i<=NF;i++) {
      if ($i ~ /^pc=/) pc=tolower(substr($i,4))
      if ($i ~ /^origin=/) origin=tolower(substr($i,8))
      if ($i ~ /^width=/) width=substr($i,7)
      if ($i ~ /^v0=/) v0=tolower(substr($i,4))
      if ($i ~ /^s1=/) s1=tolower(substr($i,4))
      if ($i ~ /^a0=/) a0=tolower(substr($i,4))
      if ($i ~ /^a2=/) a2=tolower(substr($i,4))
    }
    if (origin=="0x00696100" && width==640) b="first640"
    else if (origin=="0x006ab400" && width==512) b="hangar512"
    else next
    if (pc ~ /^0x80090(cf0|d08|d34|d4c|d78|d90|dbc|dd4)$/)
      print b "|" pc "|" v0 "|" s1 "|" a0 "|" a2
  }
' scratch/agent/s2223_retail_keyon_guard_table.log | sort -u > "$tmpdir/retail.set"
awk '
  /\[m5-keyon-transfer\]/ {
    site=""; origin=""; width=""; v0=""; s1=""; a0=""; a2=""
    for (i=1;i<=NF;i++) {
      if ($i ~ /^site=/) site=tolower(substr($i,6))
      if ($i ~ /^origin=/) origin=tolower(substr($i,8))
      if ($i ~ /^width=/) width=substr($i,7)
      if ($i ~ /^v0=/) v0=tolower(substr($i,4))
      if ($i ~ /^s1=/) s1=tolower(substr($i,4))
      if ($i ~ /^a0=/) a0=tolower(substr($i,4))
      if ($i ~ /^a2=/) a2=tolower(substr($i,4))
    }
    if (origin=="0x696100" && width==640) b="first640"
    else if (origin=="0x6ab400" && width==512) b="hangar512"
    else next
    print b "|" site "|" v0 "|" s1 "|" a0 "|" a2
  }
' scratch/s73_post_a_scene/s2229_8192_detail/run.log | sort -u > "$tmpdir/port.set"
for b in first640 hangar512; do
  for pc in 0x80090cf0 0x80090d08 0x80090d34 0x80090d4c 0x80090d78 0x80090d90 0x80090dbc 0x80090dd4; do
    r="$tmpdir/r.$b.$pc"; p="$tmpdir/p.$b.$pc"
    rg "^$b\\|$pc\\|" "$tmpdir/retail.set" | sort -u > "$r"
    rg "^$b\\|$pc\\|" "$tmpdir/port.set" | sort -u > "$p"
    printf '%s %s retail=%s port=%s both=%s retail_only=%s port_only=%s\n' "$b" "$pc" "$(wc -l < "$r")" "$(wc -l < "$p")" "$(comm -12 "$r" "$p" | wc -l)" "$(comm -23 "$r" "$p" | wc -l)" "$(comm -13 "$r" "$p" | wc -l)"
  done
done
~~~

Keep any rerun phase-gated and use SIGKILL if a recipe needs stopping. A
missing control or a port-only title/retail-only second-origin row is a
coverage result, not permission to alter the key-on path.
