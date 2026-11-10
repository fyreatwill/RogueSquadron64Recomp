# NEXT: owner reports first; otherwise audit the "format-message" names that drive the menu JPEG decoder
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7072): 0x800C7970..0x800C9B8C is the menu JPEG (JFIF) decoder (renamed, scratch/s7072/renames.tsv). Its callers
rasterizeFormatMessageGlyphs (0x800B3D14) and tickFormatMessageWorker (0x800B3650) call decodeJpegScanToImage, and the
s3608 audit's "glyph buffer" (+0x38 = rs_malloc((w*h*field4)>>1), +0x3C = (w*h)/4) looks like an image/alpha buffer.
Unit: read enqueueFormatMessage / tickFormatMessageWorker / buildFormatMessageGlyphBuffer / processAndDisposeFormatMessage /
rasterizeFormatMessageGlyphs / disposeFormatMsgQueueMember bodies, and the strings passed to enqueueFormatMessage (asset
paths? sprintf of a format string at 0x800A5C40). Hypotheses: H-jpeg-loader (an async JPEG image loader worker: strings
are file names, buffers are RGBA5551 + alpha) vs H-text (it really formats text and JPEG decodes glyph sheets).
Discriminator: the format string at 0x800A5C40 and the enqueued strings (read them from the ELF / one boot log).
If H-jpeg-loader: rename the family the same way (word-boundary sed over live tree, menu_overlay.txt, syms toml,
tools/fixup_preempt_point.py FUNCS has rasterizeFormatMessageGlyphs), control = fixup site count 6/9 unchanged, boot to flight.
