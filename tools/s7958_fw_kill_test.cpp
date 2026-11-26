// s7958 class FW harness: SIGKILL a writer that alternates two values into one file; after each kill the file must
// hold one complete value. OLD = the pre-fix audio_device.txt writer (fopen "w" in place), NEW = rs64_write_file_atomic.
#include "../src/main/rs64_atomic_write.h"
#include <csignal>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <sys/wait.h>
static const std::string A = "MacBook Pro Speakers\n", B = "External Headphones (USB Audio Device Long Name)\n";
static void old_write(const std::string& p, const std::string& v) {
    if (FILE* f = fopen(p.c_str(), "w")) { fprintf(f, "%s", v.c_str()); fclose(f); }
}
int main(int argc, char** argv) {
    const std::string arm = argv[1], path = argv[2]; const int kills = atoi(argv[3]);
    const bool isnew = arm == "new";
    if (isnew ? !rs64_write_file_atomic(path, A) : (old_write(path, A), false)) return 3;
    int bad = 0, empty = 0;
    srand(7958);
    for (int k = 0; k < kills; ++k) {
        pid_t c = fork();
        if (c == 0) { for (unsigned i = 0;; ++i) { const std::string& v = (i & 1) ? B : A; if (isnew) rs64_write_file_atomic(path, v); else old_write(path, v); } }
        usleep(200 + rand() % 1800);
        kill(c, SIGKILL); waitpid(c, nullptr, 0);
        std::ifstream in(path, std::ios::binary); std::stringstream ss; ss << in.rdbuf(); const std::string got = ss.str();
        if (got != A && got != B) { ++bad; if (got.empty()) ++empty; }
    }
    std::string err; const bool nodir = rs64_write_file_atomic("/nonexistent_s7958/x.txt", A, &err);
    printf("RESULT arm=%s kills=%d bad=%d empty=%d nodir_ok=%d err='%s'\n", arm.c_str(), kills, bad, empty, nodir ? 1 : 0, err.c_str());
    return 0;
}
