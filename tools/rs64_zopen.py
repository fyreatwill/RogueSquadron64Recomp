"""s7723: open a retained capture that may be compressed (*.zst via `zstd -dc`, *.gz via gzip) as text, else plain open.
Lets the one-capture scorers read the retained run logs in scratch/ without a 100-180 MB decompressed copy on disk.
zstd is a PURE spawn for tools/s7651_gate_sweep.py, so a gate reading through this stays cacheable."""
import gzip, io, subprocess


def zopen(path, errors='replace'):
    p = str(path)
    if p.endswith('.zst'):
        return io.StringIO(subprocess.run(['zstd', '-dcq', p], capture_output=True, check=True).stdout.decode('utf-8', errors))
    if p.endswith('.gz'):
        return gzip.open(p, 'rt', errors=errors)
    return open(p, errors=errors)
