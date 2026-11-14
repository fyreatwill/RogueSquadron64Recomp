# NEXT (s7359): idiom-class audit - class AJ, unbounded string copies of env/config/file text
HYPOTHESIS-ID: host-unbounded-string-copy
Context: s7358 closed class AI (numeric env parses; census tools/s7358_envparse_census.py, arms tools/s7358_arms.zsh).
Idiom (class AJ): in host C++ we own (src/, lib/N64ModernRuntime/{librecomp,ultramodern}/src, our lib/rt64 '+' lines):
strcpy/strcat/sprintf/vsprintf, sscanf/fscanf "%s"/"%[" without a width, memcpy(dst, src, strlen(src)[+1]) and
snprintf whose return value is used as an offset (it reports the untruncated length), with a fixed-size destination and a
source that is getenv text, a config/mod/save file, a path (std::filesystem / SDL_GetBasePath), or a guest-RAM string.
Hypotheses: H-safe (every such copy is bounded), H-diag (only env-gated diagnostics are unbounded), H-overflow (a default-on or
owner-knob path copies unbounded text into a fixed buffer: fix with a bounded copy + named warning).
Method: tools/s7359_strcopy_census.py: enumerate the calls; classify BOUNDED (snprintf/strncpy/strlcpy with sizeof dst,
"%Ns" width <= dst-1, std::string) / CONST (source is a literal) / G (env-gated diagnostic) / B (default-on or owner-knob,
unbounded) / ?. snprintf-return-as-offset is its own row type. MANUAL table like s7358. Controls: planted strcpy(getenv) (B),
snprintf(sizeof) (BOUNDED), strcpy literal (CONST), env-gated sprintf (G).
Second line: for each B, run with an oversized value (e.g. a 600-char env string / long path) pre-fix vs post-fix; 20 s boot
arms like tools/s7357_arms.zsh (own working folder, save COPY; never touch build/saves) or the s7358 route arms. ASan build in a
separate dir is allowed if the overflow is silent. Then 260 s dd8 smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7359_dd8 ''`.
Exit: PORTING-STATE s7359, CURRENT-TRUTH item 27x -> closed, commit.
