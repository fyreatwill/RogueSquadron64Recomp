"""s7723: open a retained capture that may be compressed (*.zst via `zstd -dc`, *.gz via gzip) as text, else plain open.
Lets the one-capture scorers read the retained run logs in scratch/ without a 100-180 MB decompressed copy on disk.
zstd is a PURE spawn for tools/s7651_gate_sweep.py, so a gate reading through this stays cacheable."""
import gzip, io, subprocess


def zopen(path, errors='replace'):
    p = str(path)
    p = resolve(p) or p  # s7805: a raw path whose capture survives only as .zst (retention) reads the .zst
    if p.endswith('.zst'):
        return io.StringIO(subprocess.run(['zstd', '-dcq', p], capture_output=True, check=True).stdout.decode('utf-8', errors))
    if p.endswith('.gz'):
        return gzip.open(p, 'rt', errors=errors)
    return open(p, errors=errors)


def resolve(path):
    """s7802: the retained file as stored: `path` itself, else `path`.zst, else None. Gates test existence with this, so a
    capture compressed after the gate was written (s7754/s7751 snaps, 2026-11-21 14:24) is not read as absent (NEEDS-INPUT)."""
    p = str(path)
    if __import__('os').path.exists(p):
        return p
    if __import__('os').path.exists(p + '.zst'):
        return p + '.zst'
    return None


def materialize(path, tmpdir):
    """s7802: a raw on-disk copy for tools that open the file themselves (native harness, a sibling-file lookup like
    <snap>_end.bin). Plain files are returned as is; a .zst is decompressed into tmpdir under its uncompressed basename."""
    import os
    src = resolve(path)
    if src is None:
        raise FileNotFoundError(path)
    if not src.endswith('.zst'):
        return src
    out = os.path.join(tmpdir, os.path.basename(src)[:-4])
    with open(out, 'wb') as f:
        subprocess.run(['zstd', '-dcq', src], stdout=f, check=True)
    return out


def zbytes(path):
    """s7805: whole file as bytes, transparently from <path>.zst when only the compressed copy is retained."""
    p = resolve(str(path)) or str(path)
    if p.endswith('.zst'):
        return subprocess.run(['zstd', '-dcq', p], capture_output=True, check=True).stdout
    if p.endswith('.gz'):
        return gzip.open(p, 'rb').read()
    return open(p, 'rb').read()
