# s7816: sourced by the retail oracle scripts. Sets RSP to the VU-fixed cxd4 (default) or $RS64_ORACLE_RSP.
# RS64_ORACLE_RSP=stock selects the unpatched rs64-oracle build (pre-s7816 behaviour, carries the 5 cxd4 VU defects).
RS64_CXD4_STOCK=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
RS64_CXD4_PATCHED=/Users/williambuckley/Documents/Tools/rs64-oracle-cxd4p/projects/unix/mupen64plus-rsp-cxd4.dylib
case ${RS64_ORACLE_RSP:-patched} in
  patched) RSP=$RS64_CXD4_PATCHED;; stock) RSP=$RS64_CXD4_STOCK;; *) RSP=$RS64_ORACLE_RSP;;
esac
[ -f "$RSP" ] || { echo "oracle RSP plugin missing: $RSP (build: zsh tools/oracle/build_cxd4_patched.sh)" >&2; exit 3; }
# s7818: deterministic retail runs by default. Launchers that compare runs splice $ODET into the rs64_oracle argv
# (--det = --clock vi --det-core: press/dump/--secs times in emulated VIs, RandomizeInterrupt off; s7817 82/82 identical).
# ORACLE_DET=0 restores the pre-s7818 wall-clock + randomized-interrupt behaviour. The g3_*_pair.sh scripts do NOT splice it:
# their port arm goes through g3_port_capture.sh SAVE_FROM (owner-save swap, banned) so no same-run control can be run.
ODET=(); [ "${ORACLE_DET:-1}" = 0 ] || ODET=(--det)
