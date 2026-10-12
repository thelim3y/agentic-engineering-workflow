#!/bin/sh
# Writes from a child process, a nested subprocess chain, and a detached
# (setsid, double-forked) process.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    python3 -c "import subprocess; subprocess.run(['sh','-c','echo assert True > \"$ISO_PROT/test_protected.py\"'])"; echo "fixture: child rc=$?"
    sh -c "python3 -c \"import subprocess; subprocess.run(['sh','-c','sed -i s/4/5/ $ISO_PROT/test_protected.py'])\""; echo "fixture: nested rc=$?"
    setsid sh -c "sleep 1; echo tampered > '$ISO_PROT/selectors.txt'" >/dev/null 2>&1 </dev/null &
    sleep 2; echo "fixture: detached done"
    ;;
  positive)
    python3 -c "import subprocess; subprocess.run(['sh','-c','echo child > \"$ISO_WS/child.txt\"'])"
    sh -c "python3 -c \"import subprocess; subprocess.run(['sh','-c','echo nested > $ISO_WS/nested.txt'])\""
    echo "fixture: rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) [ -s "$ISO_WS/child.txt" ] && [ -s "$ISO_WS/nested.txt" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
