// s7429 class CL: kill-at-offset harness for librecomp's save finalize path.
// Builds against a given files.cpp (FILES_CPP include), forks a child that writes alternating
// complete saves A/B through open_output_file_with_backup + finalize_output_file_with_backup
// (the exact pi.cpp update_save_file sequence), SIGKILLs it at a random offset, then loads the save
// with open_input_file_with_backup exactly as pi.cpp read_save_file does (plus its optional short-file
// .bak fallback when LOADER_FALLBACK=1). A load is GOOD when it returns SAVE_SIZE bytes that are all A or all B.
// Usage: harness <dir> <trials> <max_delay_us>. Prints counts; exit 0 = no bad loads, 1 = bad load(s).
#include FILES_CPP
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

static constexpr size_t SAVE_SIZE = 512;  // EEP4K, the size of build/saves/rs64.n64.us.1.0.bin

static void writer_loop(const std::filesystem::path& p) {
    std::vector<char> a(SAVE_SIZE, (char)0xAA), b(SAVE_SIZE, (char)0x55);
    for (unsigned i = 0;; i++) {
        const auto& buf = (i & 1) ? b : a;
        std::ofstream f = recomp::open_output_file_with_backup(p, std::ios_base::binary);
        if (!f.good()) _exit(9);
        f.write(buf.data(), buf.size());
        f.close();
        if (f.fail()) _exit(8);
        if (!recomp::finalize_output_file_with_backup(p)) _exit(7);
    }
}

enum Verdict { V_A, V_B, V_SHORT, V_MIXED, V_MISSING };

static Verdict load(const std::filesystem::path& p, size_t& got_out) {
    std::vector<char> buf(SAVE_SIZE, 0);
    std::ifstream f = recomp::open_input_file_with_backup(p, std::ios_base::binary);
    if (!f.good()) { got_out = 0; return V_MISSING; }
    f.read(buf.data(), buf.size());
    size_t got = (size_t)f.gcount();
#if LOADER_FALLBACK
    if (got < SAVE_SIZE) {
        std::ifstream bf = recomp::open_input_backup_file(p, std::ios_base::binary);
        if (bf.good()) { bf.read(buf.data(), buf.size()); if ((size_t)bf.gcount() == SAVE_SIZE) got = SAVE_SIZE; }
    }
#endif
    got_out = got;
    if (got < SAVE_SIZE) return V_SHORT;
    bool allA = true, allB = true;
    for (char c : buf) { allA &= (c == (char)0xAA); allB &= (c == (char)0x55); }
    return allA ? V_A : allB ? V_B : V_MIXED;
}

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s dir trials max_delay_us\n", argv[0]); return 2; }
    std::filesystem::path dir = argv[1];
    int trials = atoi(argv[2]);
    int max_us = atoi(argv[3]);
    std::filesystem::create_directories(dir);
    std::filesystem::path p = dir / "rs64.n64.us.1.0.bin";
    std::mt19937 rng(7429);
    int n[5] = {0, 0, 0, 0, 0};
    // Seed one complete save so every kill starts from an existing good file (the owner's case).
    { std::ofstream s(p, std::ios_base::binary); std::vector<char> a(SAVE_SIZE, (char)0xAA); s.write(a.data(), a.size()); }
    for (int t = 0; t < trials; t++) {
        pid_t pid = fork();
        if (pid == 0) writer_loop(p);
        usleep(std::uniform_int_distribution<int>(50, max_us)(rng));
        kill(pid, SIGKILL);
        int st = 0; waitpid(pid, &st, 0);
        if (WIFEXITED(st)) { fprintf(stderr, "writer exited %d (I/O failure)\n", WEXITSTATUS(st)); return 3; }
        size_t got = 0;
        Verdict v = load(p, got);
        n[v]++;
        if (v >= V_SHORT && n[v] <= 3) fprintf(stderr, "trial %d: bad load verdict=%d got=%zu\n", t, (int)v, got);
        if (v >= V_SHORT) {  // repair to a good save so later trials keep measuring the kill window, not the residue
            std::ofstream s(p, std::ios_base::binary); std::vector<char> a(SAVE_SIZE, (char)0xAA); s.write(a.data(), a.size());
        }
    }
    printf("trials=%d A=%d B=%d short=%d mixed=%d missing=%d\n", trials, n[V_A], n[V_B], n[V_SHORT], n[V_MIXED], n[V_MISSING]);
    return (n[V_SHORT] + n[V_MIXED] + n[V_MISSING]) ? 1 : 0;
}
