#!/bin/bash
# Builds mips64-elf binutils 2.40 + gcc 14.2.0 into ~/toolchains/mips64-elf (gcc 12.2 does not build on current macOS SDK)
# Needs: brew install gmp mpfr libmpc gnu-sed. Afterwards add $P/bin (default ~/toolchains/mips64-elf/bin) to PATH.
set -euo pipefail
export MAKEINFO=true
# libgcc t-hardfp needs GNU sed (BSD sed lacks alternation in its regex)
export PATH="$(brew --prefix gnu-sed)/libexec/gnubin:$PATH"
P=${MIPS_PREFIX:-$HOME/toolchains/mips64-elf}; S=${MIPS_SRC:-$HOME/toolchains/src}; J=${JOBS:-$(sysctl -n hw.ncpu)}
B=$(brew --prefix)
export PATH="$P/bin:$PATH"
mkdir -p "$S"; cd "$S"
[ -f binutils-2.40.tar.xz ] || curl -fLO https://ftp.gnu.org/gnu/binutils/binutils-2.40.tar.xz
[ -f gcc-14.2.0.tar.xz ]    || curl -fLO https://ftp.gnu.org/gnu/gcc/gcc-14.2.0/gcc-14.2.0.tar.xz
[ -d binutils-2.40 ] || tar xf binutils-2.40.tar.xz
[ -d gcc-14.2.0 ]    || tar xf gcc-14.2.0.tar.xz
if [ ! -x "$P/bin/mips64-elf-ld" ]; then
  rm -rf build-binutils; mkdir build-binutils; cd build-binutils
  ../binutils-2.40/configure --target=mips64-elf --prefix="$P" --disable-nls --disable-werror --with-system-zlib
  make -j$J MAKEINFO=true; make install MAKEINFO=true; cd "$S"
fi
rm -rf build-gcc; mkdir build-gcc; cd build-gcc
../gcc-14.2.0/configure --target=mips64-elf --prefix="$P" --with-gnu-as --with-gnu-ld \
  --enable-languages=c --without-headers --disable-libssp --disable-multilib --disable-shared \
  --disable-threads --disable-nls --disable-werror --disable-libgomp --disable-libquadmath \
  --disable-libatomic --with-newlib --with-arch=vr4300 --with-tune=vr4300 \
  --with-gmp="$B" --with-mpfr="$B" --with-mpc="$B" --with-system-zlib
make -j$J MAKEINFO=true all-gcc all-target-libgcc
make MAKEINFO=true install-gcc install-target-libgcc
echo BUILD_OK
