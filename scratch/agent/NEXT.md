# NEXT work unit — M5 contract-edge selection after source-buffer boundary

HYPOTHESIS-ID: m5-image-task-retail-source-writer

Session 3584 ran the qualified source-buffer watch with all controls. It found
no stable earlier constructor or distinct DMA/copy PC. Do not repeat this
capture or the saturated field table. The earlier-constructor boundary is
unavailable to the current oracle; exact DMA order remains open.

Competing hypotheses and the discriminating result:

- H-RetailSourceWriter: REFUTED at this oracle scope; no stable distinct
  constructor appeared.
- H-RetailCopyOrDma: REFUTED at this oracle scope; no stable distinct DMA/copy
  PC appeared.
- H-RetailNoStableSourceWriter: SELECTED; phase histogram was mixed, with 176
  `0x800078EC` hits and only low-frequency other PCs.
- H-CaptureInvalid: REFUTED; whole-RDRAM, image-span, source-buffer, and target
  phase controls all fired.

The bounded capability check requested for this iteration found existing
port-side event IDs in `rsp.cpp` and `main.cpp` (`audtask-dma-*` and
`m5-source-*`), but the retail oracle exposes no corresponding DMA event
identifier. Therefore the next work unit is not authorized until a new
independent retail/order discriminator is available. Do not build or add
another source-buffer counter.

The exact check that established this was:

    rg -n -i 'dma.*(event|trace|id)|event.*dma|audtask-dma' tools src lib/N64ModernRuntime | head -80

It selected the second outcome: port event IDs alone cannot establish retail
DMA ordering. The next human/oracle capability decision is whether to expose
an event ID in the retail capture; otherwise move to the first systematic M3
idiom-class audit after recording M5's DMA-order boundary as unresolved.
