// s7958 class FW harness: SIGKILL a writer that alternates two values into one file; after each kill the file must
// hold one complete value. OLD = the pre-fix audio_device.txt writer (fopen "w" in place), NEW = rs64_write_file_atomic.
#include "../src/main/rs64_atomic_write.h"
#include <cerrno>
#include <csignal>
#include <cstring>
#include <sys/stat.h>
#include <cstdlib>
#include <sys/wait.h>
static const std::string A = "MacBook Pro Speakers\n", B = "External Headphones (USB Audio Device Long Name)\n";
static void old_write(const std::string& p, const std::string& v) {
    if (FILE* f = fopen(p.c_str(), "w")) { fprintf(f, "%s", v.c_str()); fclose(f); }
}
int main(int argc, char** argv) {
    const std::string arm = argv[1], path = argv[2]; const int kills = atoi(argv[3]);
    const bool isnew = arm == "new", isdel = arm == "del";  // del = s7965 classifier control: unlink, then atomic write
    if ((isnew || isdel) ? !rs64_write_file_atomic(path, A) : (old_write(path, A), false)) return 3;
    int bad = 0, empty = 0, missing = 0, zero = 0, partial = 0, openerr = 0, lasterr = 0, forkfail = 0, waitfail = 0, first_bad = -1;
    srand(7958);
    for (int k = 0; k < kills; ++k) {
        pid_t c = fork();
        // s7965: a failed fork returned -1 and kill(-1, SIGKILL) would signal every process this user owns.
        if (c < 0) { ++forkfail; usleep(10000); continue; }
        if (c == 0) { for (unsigned i = 0;; ++i) { const std::string& v = (i & 1) ? B : A; if (isdel) { unlink(path.c_str()); rs64_write_file_atomic(path, v); } else if (isnew) rs64_write_file_atomic(path, v); else old_write(path, v); } }
        usleep(200 + rand() % 1800);
        kill(c, SIGKILL);
        int st = 0; pid_t w;
        while ((w = waitpid(c, &st, 0)) < 0 && errno == EINTR) {}
        if (w != c) ++waitfail;  // the writer may still be running: the read below would race it
        // s7965: say WHICH bad state (one s7964 sweep run read 170 "empty" in the new arm, never reproduced standalone):
        // missing = target gone (rename atomicity broken), zero/partial = published bad content, openerr = the READ failed.
        std::string got; bool read_ok = false; int oe = 0;
        for (int t = 0; t < 20 && !read_ok; ++t) {
            FILE* f = fopen(path.c_str(), "rb");
            if (!f) { oe = errno; if (oe == ENOENT) break; usleep(1000); continue; }
            char buf[256]; size_t n; got.clear();
            while ((n = fread(buf, 1, sizeof buf, f)) > 0) got.append(buf, n);
            read_ok = !ferror(f); if (!read_ok) oe = errno; fclose(f);
        }
        if (!read_ok) { if (oe == ENOENT) { ++bad; ++empty; ++missing; } else { ++openerr; lasterr = oe; } continue; }
        if (got != A && got != B) { ++bad; if (got.empty()) { ++empty; ++zero; } else ++partial; if (first_bad < 0) first_bad = k; }
    }
    std::string err; const bool nodir = rs64_write_file_atomic("/nonexistent_s7958/x.txt", A, &err);
    printf("RESULT arm=%s kills=%d bad=%d empty=%d nodir_ok=%d missing=%d zero=%d partial=%d openerr=%d lasterr=%d forkfail=%d waitfail=%d first_bad=%d err='%s'\n",
           arm.c_str(), kills, bad, empty, nodir ? 1 : 0, missing, zero, partial, openerr, lasterr, forkfail, waitfail, first_bad, err.c_str());
    return 0;
}
