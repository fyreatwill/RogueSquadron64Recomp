// s7966 class DI: two game instances share one data root. Two writer processes run the exact pi.cpp
// update_save_file sequence (open_output_file_with_backup -> write -> close -> finalize_output_file_with_backup)
// on ONE save path with distinct whole payloads (A = 0xAA.., B = 0x55..). A reader samples the final file the way
// read_save_file does (open_input_file_with_backup) throughout. Bad sample = not exactly SAVE_SIZE bytes of all A or all B.
// Also counts finalize failures (each one = a "Failed to write to the save file" dialog in the game).
// Usage: harness <dir> <iters_per_writer>. Prints one line; exit 0 = no torn/short sample and 0 finalize failures.
#include FILES_CPP
#include <cstdio>
#include <cstdlib>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>
static constexpr size_t SAVE_SIZE = 512;
static int writer(const std::filesystem::path& p, char fill, unsigned iters) {
    std::vector<char> buf(SAVE_SIZE, fill);
    int fails = 0;
    for (unsigned i = 0; i < iters; i++) {
        std::ofstream f = recomp::open_output_file_with_backup(p, std::ios_base::binary);
        if (!f.good()) { fails++; continue; }
        // two halves, so a concurrent truncate/rename has a window inside the write as in a real 512-byte EEPROM flush
        f.write(buf.data(), SAVE_SIZE / 2); f.flush(); f.write(buf.data() + SAVE_SIZE / 2, SAVE_SIZE / 2);
        f.close();
        if (f.fail()) { fails++; continue; }
        if (!recomp::finalize_output_file_with_backup(p)) fails++;
    }
    return fails > 250 ? 250 : fails;
}
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    std::filesystem::path d = argv[1]; std::filesystem::create_directories(d);
    std::filesystem::path p = d / "rs64.n64.us.1.0.bin";
    unsigned iters = (unsigned)atoi(argv[2]);
    { std::ofstream s(p, std::ios_base::binary); std::vector<char> a(SAVE_SIZE, (char)0xAA); s.write(a.data(), SAVE_SIZE); }
    pid_t w[2];
    for (int k = 0; k < 2; k++) {
        w[k] = fork();
        if (w[k] < 0) { perror("fork"); return 3; }
        if (w[k] == 0) _exit(writer(p, k ? (char)0x55 : (char)0xAA, iters));
    }
    long samples = 0, good = 0, shortf = 0, mixed = 0, missing = 0;
    int alive = 2, wfail = 0;
    while (alive > 0) {
        std::vector<char> buf(SAVE_SIZE + 16, 0);
        std::ifstream f = recomp::open_input_file_with_backup(p, std::ios_base::binary);
        samples++;
        if (!f.good()) missing++;
        else {
            f.read(buf.data(), buf.size()); size_t got = (size_t)f.gcount();
            if (got != SAVE_SIZE) shortf++;
            else { bool a = true, b = true; for (size_t i = 0; i < SAVE_SIZE; i++) { a &= buf[i] == (char)0xAA; b &= buf[i] == (char)0x55; }
                   if (a || b) good++; else mixed++; }
        }
        int st; pid_t r;
        while ((r = waitpid(-1, &st, WNOHANG)) > 0) { alive--; if (WIFEXITED(st)) wfail += WEXITSTATUS(st); }
    }
    // final state after both writers finished
    std::ifstream f = recomp::open_input_file_with_backup(p, std::ios_base::binary);
    std::vector<char> buf(SAVE_SIZE + 16, 0); size_t got = 0; if (f.good()) { f.read(buf.data(), buf.size()); got = (size_t)f.gcount(); }
    bool fa = got == SAVE_SIZE, fb = fa; for (size_t i = 0; i < got && i < SAVE_SIZE; i++) { fa &= buf[i] == (char)0xAA; fb &= buf[i] == (char)0x55; }
    long torn = shortf + mixed + missing;
    printf("samples=%ld good=%ld short=%ld mixed=%ld missing=%ld torn=%ld finalize_fail=%d final=%s\n", samples, good, shortf, mixed,
           missing, torn, wfail, fa ? "A" : fb ? "B" : "BAD");
    return (torn == 0 && wfail == 0 && (fa || fb)) ? 0 : 1;
}
