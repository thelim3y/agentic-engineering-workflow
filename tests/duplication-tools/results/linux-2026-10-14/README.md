# Linux duplication tool evidence

Run: 2026-10-14. Status: tool-selection spike; the check is not implemented.

Ubuntu 24.04.5 LTS, kernel 7.0.0-31-generic, x86-64. Python 3.12.3 and Node
v22.23.2. The fixtures pass `clang++ -std=c++20 -fsyntax-only -Wall -Wextra`
(Ubuntu clang 19.1.1).

## Tools

| Tool | Version | Source |
|---|---|---|
| PMD CPD | 7.28.0 | `pmd-dist-7.28.0-bin.zip` from the github.com/pmd/pmd releases |
| JDK for PMD | Temurin 21.0.12.1+1 | api.adoptium.net, latest 21 GA, Linux x64 |
| jscpd | 5.3.3 | `npm install --ignore-scripts jscpd@5.3.3` |
| Dolos | 2.9.3 | `npm install --ignore-scripts @dodona/dolos@2.9.3`, then `npm rebuild @dodona/dolos-parsers`; its parsers are native builds |
| lizard | 1.24.0 | `pip install lizard==1.24.0` in a virtual environment |

copydetect 0.5.0 was not run: it has had no release or commit since April 2024.

## Results

| File | Command |
|---|---|
| [cpd.txt](cpd.txt) | `spike.py cpd` |
| [jscpd.txt](jscpd.txt) | `spike.py jscpd` |
| [dolos.txt](dolos.txt) | `spike.py dolos` |
| [lizard.txt](lizard.txt) | `spike.py lizard` |
| [probes.txt](probes.txt) | `spike.py probes` |

The fixtures were hashed before the first tool run; [SHA256SUMS](SHA256SUMS)
matches that record. These files come from the committed script and match the
first run.

CPD's file access was traced separately:

```sh
strace -f -e trace=openat,open,stat,newfstatat,access \
  PMD/bin/pmd cpd --language cpp --minimum-tokens 100 \
  --ignore-identifiers --ignore-literals --format text src
```

It opened only the scanned sources. The JVM probes `.hotspotrc` and
`.hotspot_compiler` in its working directory, so `spike.py` runs CPD from an empty
directory.
