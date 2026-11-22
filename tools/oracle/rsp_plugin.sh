# s7816: sourced by the retail oracle scripts. Sets RSP to the VU-fixed cxd4 (default) or $RS64_ORACLE_RSP.
# RS64_ORACLE_RSP=stock selects the unpatched rs64-oracle build (pre-s7816 behaviour, carries the 5 cxd4 VU defects).
RS64_CXD4_STOCK=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
RS64_CXD4_PATCHED=/Users/williambuckley/Documents/Tools/rs64-oracle-cxd4p/projects/unix/mupen64plus-rsp-cxd4.dylib
case ${RS64_ORACLE_RSP:-patched} in
  patched) RSP=$RS64_CXD4_PATCHED;; stock) RSP=$RS64_CXD4_STOCK;; *) RSP=$RS64_ORACLE_RSP;;
esac
[ -f "$RSP" ] || { echo "oracle RSP plugin missing: $RSP (build: zsh tools/oracle/build_cxd4_patched.sh)" >&2; exit 3; }
