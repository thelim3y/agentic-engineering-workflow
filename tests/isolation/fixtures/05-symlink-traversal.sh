#!/bin/sh
# Symlink from the workspace into the protected tree, and ../ traversal.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    ln -s "$ISO_PROT" "$ISO_WS/link_to_prot"; echo "fixture: ln rc=$?"
    echo "assert True" > "$ISO_WS/link_to_prot/test_protected.py"; echo "fixture: write via symlink rc=$?"
    echo "assert True" > "$ISO_WS/../prot/test_protected.py"; echo "fixture: write via ../ rc=$?"
    ln -sf "$ISO_PROT/selectors.txt" "$ISO_WS/sel"; echo "x" > "$ISO_WS/sel"; echo "fixture: write via file symlink rc=$?"
    ;;
  positive)
    mkdir -p "$ISO_WS/sub"; ln -s "$ISO_WS/sub" "$ISO_WS/sublink"; echo ok > "$ISO_WS/sublink/a.txt"; echo ok > "$ISO_WS/sub/../b.txt"; echo "fixture: rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) [ -s "$ISO_WS/sub/a.txt" ] && [ -s "$ISO_WS/b.txt" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
