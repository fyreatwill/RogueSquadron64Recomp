// s7967 class CS: game folder inside a cloud-synced folder (iCloud Drive). Reads a save through the exact
// read_save_file path (recomp::open_input_file_with_backup + read + gcount) and reports, per file, the
// st_flags before/after (dataless = evicted placeholder), bytes read, payload check, errno and latency.
// Usage: harness read <file> <expect_size> <fill_hex>   -> one line, exit 0 = full payload read
//        harness write <file> <size> <fill_hex> <cycles> -> runs the pi.cpp save sequence <cycles> times
#include FILES_CPP
#include <cerrno>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/stat.h>
#include <vector>
static const char* flags_of(const char* p) {
    struct stat st; if (stat(p, &st) != 0) return "nostat";
    return (st.st_flags & SF_DATALESS) ? "dataless" : "local";
}
int main(int argc, char** argv) {
    if (argc < 5) return 2;
    std::string mode = argv[1]; std::filesystem::path p = argv[2];
    size_t size = strtoul(argv[3], nullptr, 0); char fill = (char)strtoul(argv[4], nullptr, 16);
    if (mode == "write") {
        unsigned cycles = argc > 5 ? (unsigned)atoi(argv[5]) : 1; int fails = 0;
        std::vector<char> buf(size, fill);
        for (unsigned i = 0; i < cycles; i++) {
            std::ofstream f = recomp::open_output_file_with_backup(p, std::ios_base::binary);
            if (!f.good()) { fails++; continue; }
            f.write(buf.data(), size); f.close();
            if (f.fail() || !recomp::finalize_output_file_with_backup(p)) fails++;
        }
        printf("write cycles=%u fails=%d final=%s\n", cycles, fails, flags_of(p.c_str()));
        return fails ? 1 : 0;
    }
    const char* before = flags_of(p.c_str());
    auto t0 = std::chrono::steady_clock::now();
    errno = 0;
    std::ifstream f = recomp::open_input_file_with_backup(p, std::ios_base::binary);
    int open_errno = errno; bool good = f.good();
    std::vector<char> buf(size + 16, 0); size_t got = 0;
    if (good) { f.read(buf.data(), buf.size()); got = (size_t)f.gcount(); }
    double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    bool ok = got == size; for (size_t i = 0; i < got && i < size; i++) ok &= buf[i] == fill;
    printf("read before=%s after=%s opened=%d errno=%d got=%zu payload=%s ms=%.1f\n", before, flags_of(p.c_str()),
           good ? 1 : 0, open_errno, got, ok ? "ok" : "BAD", ms);
    return ok ? 0 : 1;
}
