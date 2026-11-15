#!/usr/bin/env python3
"""s6869: find and cut data decoded as code after a function's real end. make_elf.py sizes every function up to the next
symbol, so audioCompandS16's 0x54-byte body carried 100k lines of decoded table. s6870: tools/regen_front.sh now fixes that
at the source, so on its output this step cuts nothing; it stays for a plain N64Recomp run and to write tools/func_sizes.txt. Mid-function addresses are not in the
lookup table, so a tail can only be entered by goto or fall-through from the body; both are checked before any cut.
Real end: walk the instruction comments from the entry, following branches (never-taken $zero forms skipped) and every
goto of a jump-table switch. Crossing check, on the C itself, not the comments: no goto above the cut names a label
below it, the cut sits at brace depth 1, and the last statement above it cannot fall through.
do_break exits, so the walk stops at a .word that translated to do_break. Only dead code is removed: every path through
the function behaves as before, whether or not the body is real code. A function is cut only if its tail holds a .word
line; a tail of valid-looking words is reported, not touched.
usage: fixup_cut_decoded_tails.py <RecompiledFuncs dir> [--dry] [--md out.md] [--syms toml] [--sizes out.txt]
       fixup_cut_decoded_tails.py <RecompiledFuncs dir> --self-test   (reads the tree, writes nothing)"""
import argparse, glob, os, re, sys

FN = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(')  # s7420: weak-aware (runs after weaken_patched_funcs)
CMT = re.compile(r'^    // 0x([0-9A-Fa-f]{8}): (\S+)\s*(.*)$')
LBL = re.compile(r'^\s*(\w+):\s*$')   # L_<addr> and the generator's after_N / skip_N
GOTO = re.compile(r'\bgoto (\w+);')
TARGET = re.compile(r'(?:L_|0x)([0-9A-Fa-f]{8})\s*$')
COND = {'beq', 'bne', 'beql', 'bnel', 'blez', 'blezl', 'bgtz', 'bgtzl', 'bltz', 'bltzl', 'bgez', 'bgezl',
        'bc1t', 'bc1f', 'bc1tl', 'bc1fl', 'beqz', 'bnez', 'beqzl', 'bnezl'}
NEVER = {'bltz', 'bltzl', 'bgtz', 'bgtzl'}   # with $zero as the operand
ALWAYS = {'blez', 'blezl', 'bgez', 'bgezl'}


def functions(lines):
    """(name, first line, line of the closing brace) per function."""
    out, start, name = [], None, None
    for i, line in enumerate(lines):
        m = FN.match(line)
        if m:
            start, name = i, m.group(1)
        elif line.startswith((';}', '}')) and start is not None:
            out.append((name, start, i))
            start = None
    return out


def parse(lines, start, end):
    ins, order = {}, []
    for i in range(start, end):
        m = CMT.match(lines[i])
        if m:
            pc = int(m.group(1), 16)
            if pc not in ins:
                ins[pc] = (m.group(2), m.group(3).split('#')[0].strip(), i)
                order.append(pc)
    return ins, order


def switch_targets(lines, line, end):
    """Every goto of the first switch after a register jump."""
    out, depth, seen = set(), 0, False
    if not any(re.search(r'\bswitch\b', l) for l in lines[line:min(line + 8, end)]):
        return out
    for i in range(line, end):
        text = lines[i]
        if not seen and re.search(r'\bswitch\b', text):
            seen = True
        if seen:
            out.update(int(t[2:], 16) for t in GOTO.findall(text) if t.startswith('L_'))
            depth += text.count('{') - text.count('}')
            if depth <= 0 and '}' in text:
                break
    return out


def walk(lines, ins, entry, end):
    """pcs reached from the entry, plus anything the walker could not follow."""
    seen, reached_word, unknown, work = set(), [], [], [entry]
    while work:
        pc = work.pop()
        while pc in ins and pc not in seen:
            seen.add(pc)
            op, args, line = ins[pc]
            m = TARGET.search(args)
            target = int(m.group(1), 16) if m else None
            zero = args.startswith('$zero,')
            # .word only marks what the disassembler disliked: most still translate to code and run on.
            if op == '.word' and any('do_break(' in l for l in lines[line + 1:line + 3]):
                reached_word.append(pc)
                break
            if op == 'jr':
                seen.add(pc + 4)
                if not args.startswith('$ra'):
                    work.extend(switch_targets(lines, line, end))
                break
            if op in ('j', 'b') or (op == 'beq' and args.startswith('$zero, $zero')) or (op in ALWAYS and zero):
                seen.add(pc + 4)
                if target is not None:
                    work.append(target)
                break
            if op in COND:
                if (op in NEVER and zero) or (op in ('bne', 'bnel') and args.startswith('$zero, $zero')):
                    pc += 4
                    continue
                seen.add(pc + 4)
                if target is not None:
                    work.append(target)
                pc += 8
                continue
            pc += 4
    return seen, reached_word, unknown


def statement_before(lines, cut, start):
    for i in range(cut - 1, start, -1):
        text = lines[i].strip()
        if text and not text.startswith('//') and not LBL.match(lines[i]):
            return text
    return ''


def analyse(lines, name, start, end):
    ins, order = parse(lines, start, end)
    if not order:
        return None
    entry = order[0]
    seen, reached_word, unknown = walk(lines, ins, entry, end)
    tail = [pc for pc in order if pc not in seen and pc > max(seen & set(order))]
    row = dict(name=name, entry=entry, last=order[-1], lines=end - start, reached_word=reached_word, unknown=unknown,
               holes=[pc for pc in order if pc not in seen and pc < max(seen & set(order))],
               words=[pc for pc in order if ins[pc][0] == '.word'], tail=len(tail), crossing=[], why=[])
    row['real_end'] = max(seen & set(order)) + 4
    if not tail:
        return row
    row['tail_nop'] = all(ins[pc][0] == 'nop' for pc in tail)
    row['tail_words'] = sum(ins[pc][0] == '.word' for pc in tail)
    cut = ins[tail[0]][2]
    while LBL.match(lines[cut - 1]) or not lines[cut - 1].strip():
        cut -= 1
    # The generator repeats a delay slot after the jump it belongs to; that copy is dead and goes with the tail.
    if ins.get(row['real_end'] - 8, ('',))[0] in ('jr', 'j', 'b'):
        for i in range(cut - 1, max(cut - 12, start), -1):
            if lines[i].strip() == 'return;' or lines[i].strip().startswith('goto '):
                cut = i + 1
                break
    row['cut'] = cut
    below = {m.group(1) for m in map(LBL.match, lines[cut:end]) if m}
    for i in range(start, cut):
        row['crossing'] += [(i, t) for t in GOTO.findall(lines[i]) if t in below]
    depth = sum(l.count('{') - l.count('}') for l in lines[start:cut] if not l.lstrip().startswith('//'))
    last = row['last_stmt'] = statement_before(lines, cut, start)
    if depth != 1:
        row['why'].append(f'depth {depth}')
    if not (last == 'return;' or last.startswith(('goto ', 'do_break(', '__builtin_trap('))):
        row['why'].append(f'falls through: {last[:50]}')
    tail_text = ''.join(lines[cut:end])
    row['hooks'] = sorted(set(re.findall(r'\b(rs64_\w+|rs\d{4}\w*|s\d{4}_\w+|getenv)\b', tail_text)))
    return row


def blocked(row):
    return row['crossing'] or row['why']


def scan(tree):
    for path in sorted(glob.glob(os.path.join(tree, 'funcs_*.c'))):
        lines = open(path, errors='replace').read().split('\n')
        lines = [l + '\n' for l in lines]
        yield path, lines, [r for r in (analyse(lines, *f) for f in functions(lines)) if r]


def self_test(tree):
    """Each injected defect must be caught on a real function; the unmodified copy must not be."""
    for path, lines, rows in scan(tree):
        row = next((r for r in rows if r.get('tail_words') and not blocked(r) and r['last_stmt'] == 'return;'), None)
        if not row:
            continue
        fns = {n: (s, e) for n, s, e in functions(lines)}
        s, e = fns[row['name']]
        label = next(m.group(1) for m in map(LBL.match, lines[row['cut']:e]) if m)
        line = next(i for i in range(s, row['cut']) if CMT.match(lines[i]))
        goto = lines[:line] + [f'    if (ctx->r4) goto {label};\n'] + lines[line:]
        a = analyse(goto, row['name'], s, e + 1)
        ret = max(i for i in range(s, row['cut']) if lines[i].strip() == 'return;')
        fall = lines[:ret] + ['    ctx->r2 = 0;\n'] + lines[ret + 1:]
        b = analyse(fall, row['name'], s, e)
        ok = bool(a['crossing']) and bool(b['why'])
        print(f"self-test {row['name']}: clean blocked={bool(blocked(row))} injected goto flagged={bool(a['crossing'])} "
              f"removed return flagged={bool(b['why'])} -> {'ok' if ok else 'FAILED'}")
        return 0 if ok else 1
    print('self-test: no function with a data tail in this tree (already cut?)')
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--md')
    ap.add_argument('--sizes', help='write "name size" for every cuttable function, for tools/regen_front.sh')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        return self_test(args.tree)
    table, cuts, cut_lines, refused, sized = [], 0, 0, 0, []
    for path, lines, rows in scan(args.tree):
        edits = []
        for r in rows:
            data = r.get('tail_words', 0)
            if r['words'] or r['reached_word']:
                table.append((os.path.basename(path), r))
            if not data:
                continue
            if blocked(r):
                refused += 1
                continue
            edits.append(r)
        if edits and not args.dry:
            ends = {n: e for n, _, e in functions(lines)}
            for r in sorted(edits, key=lambda r: -r['cut']):
                lines[r['cut']:ends[r['name']]] = [f"    // s6869: {r['tail']} decoded data words cut from 0x{r['real_end']:08X}\n"]
            open(path, 'w').write(''.join(lines)[:-1])
        cuts += len(edits)
        sized += edits
        cut_lines += sum(r['lines'] for r in edits)
    out = ['| File | Function | Entry | Real end | Lines | Tail words | .word in tail | do_break stops | Crossing | Fall-through | Hooks in tail |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for f, r in table:
        out.append(f"| {f} | {r['name']} | {r['entry']:08X} | {r['real_end']:08X} | {r['lines']} | {r['tail']} | {r.get('tail_words', 0)} | "
                   f"{len(r['reached_word'])} | {len(r['crossing'])} | {'; '.join(r['why']) or '-'} | {' '.join(r.get('hooks', [])) or '-'} |")
    text = '\n'.join(out) + '\n'
    if args.md:
        open(args.md, 'w').write(text)
    if args.sizes:
        open(args.sizes, 'w').writelines(f"{r['name']} 0x{r['real_end'] - r['entry']:X}\n" for r in sorted(sized, key=lambda r: r['entry'])
                                      if not r['name'].startswith('static_'))   # no ELF symbol: N64Recomp sizes those itself
    print(f'decoded tails: {cuts} {"cuttable" if args.dry else "cut"}, {refused} refused, {cut_lines} function lines before the cut')
    return 0


if __name__ == '__main__':
    sys.exit(main())
