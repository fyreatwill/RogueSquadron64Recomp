// s7966 class DI header unit: (1) two processes x N rs64_write_file_atomic on one path with distinct texts while the parent
// samples the file: bad = not exactly text A or text B; fails = writer returned false. (2) rs64_instance_lock: parent holds,
// a child must see 0 (busy); after the parent releases (child of a child holding then exiting), a fresh child must see 1.
// Usage: hdr_test <dir> <iters>. Prints ATOMIC/LOCK lines.
#include "../../src/main/rs64_atomic_write.h"
#include "../../src/main/rs64_instance_lock.h"
#include <csignal>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <sys/wait.h>
int main(int argc, char** argv) {
    std::string d = argv[1]; unsigned n = atoi(argv[2]); std::filesystem::create_directories(d);
    std::string p = d + "/audio_device.txt", A(300, 'a'), B(300, 'b'); A += "\n"; B += "\n";
    rs64_write_file_atomic(p, A);
    pid_t w[2];
    for (int k = 0; k < 2; k++) { w[k] = fork(); if (w[k] < 0) return 3;
        if (w[k] == 0) { int f = 0; for (unsigned i = 0; i < n; i++) f += !rs64_write_file_atomic(p, k ? B : A); _exit(f > 250 ? 250 : f); } }
    long samples = 0, bad = 0; int alive = 2, fails = 0;
    while (alive > 0) { std::ifstream f(p); std::stringstream ss; ss << f.rdbuf(); std::string s = ss.str(); samples++;
        if (s != A && s != B) bad++;
        int st; pid_t r; while ((r = waitpid(-1, &st, WNOHANG)) > 0) { alive--; if (WIFEXITED(st)) fails += WEXITSTATUS(st); } }
    int left = 0; for (auto& e : std::filesystem::directory_iterator(d)) left += e.path().filename() != "audio_device.txt";
    printf("ATOMIC samples=%ld bad=%ld fails=%d leftover=%d\n", samples, bad, fails, left);
    std::string ld = d + "/saves", why; int mine = rs64_instance_lock(ld, &why);
    pid_t c = fork(); if (c == 0) { std::string y; _exit(rs64_instance_lock(ld, &y) + 10); }
    int st; waitpid(c, &st, 0); int child_busy = WEXITSTATUS(st) - 10;
    // release: the lock lives as long as the fd; a holder that dies (SIGKILL) releases it. Simulate with a killed holder.
    pid_t h = fork(); if (h == 0) { std::string y; std::string d2 = d + "/saves2"; rs64_instance_lock(d2, &y); pause(); _exit(0); }
    usleep(200000); pid_t c2 = fork(); if (c2 == 0) { std::string y; _exit(rs64_instance_lock(d + "/saves2", &y) + 10); }
    waitpid(c2, &st, 0); int busy2 = WEXITSTATUS(st) - 10; kill(h, SIGKILL); waitpid(h, &st, 0);
    pid_t c3 = fork(); if (c3 == 0) { std::string y; _exit(rs64_instance_lock(d + "/saves2", &y) + 10); }
    waitpid(c3, &st, 0); int after_kill = WEXITSTATUS(st) - 10;
    printf("LOCK first=%d second=%d other_holder=%d after_holder_sigkill=%d\n", mine, child_busy, busy2, after_kill);
    return 0;
}
