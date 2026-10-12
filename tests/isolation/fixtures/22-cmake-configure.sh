#!/bin/sh
# Real configure-time execution, paired with an allowed C++ build and run.
. "$(dirname "$0")/lib.sh"
project="$(dirname "$0")/../projects/cmake-configure"
case "$1" in
  attack|positive)
    if ! command -v cmake >/dev/null || ! command -v g++ >/dev/null || ! command -v make >/dev/null; then
      echo 'ISOLATION_UNSUPPORTED: CMake, g++ and make are required'
      exit 64
    fi
    cmake -S "$project" -B "$ISO_WS/build" -G 'Unix Makefiles' \
      -DCMAKE_CXX_COMPILER=/usr/bin/g++ -DPROBE_MODE="$1" || exit "$?"
    if [ "$1" = positive ]; then
      cmake --build "$ISO_WS/build" --parallel 1 && \
        "$ISO_WS/build/allowed" > "$ISO_WS/build-result.txt"
    fi ;;
  judge_attack) iso_judge_prot ;;
  judge_positive)
    if [ -f "$ISO_WS/build-result.txt" ] && [ "$(cat "$ISO_WS/build-result.txt")" = 'CPP_BUILD_OK' ]; then
      iso_verdict_positive ok
    else
      iso_verdict_positive failed
    fi ;;
esac
