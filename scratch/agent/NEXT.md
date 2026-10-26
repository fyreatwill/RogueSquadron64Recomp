# Next: G3c(b) knife spikes - reopen H-rsp-emu vs H-retail
HYPOTHESIS-ID: g3c-owner-visual
Competing: H-rsp-emu (our LLE RSP F5 clip path differs from hardware: VRCP/VRCPH/VRCPL, VMULF/VMACF rounding, VCH/VCL/VCR flags) vs H-retail (retail also draws wedges).
Discriminator: take a logged wedge (G3b s6081-s6085 logs; grep PORTING-STATE for 'spike') and replay its exact vertex/matrix inputs through an independent RSP vector-op reference (python model of VRCP/VRCPL/VRCPH/VRSQ per ares) and compare to our RSP output; independent check = tools/oracle retail run if reaching that level is feasible. Positive control: a known-good vertex must match.
(a) status: s6299 scorer ambiguous (aspect jump +0.11 vs retail, dd3 ~0); revisit with vertex-level probe only after (b).
