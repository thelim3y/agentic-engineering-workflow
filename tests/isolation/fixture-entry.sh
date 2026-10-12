#!/bin/sh
# Runner-owned entry marker distinguishes a started fixture from a failed host.
# This is test-harness evidence, not an attestation for untrusted agent code.
set -eu
printf 'started\n' > "$ISO_WS/.fixture-started"
exec sh "$ISO_FIXTURE" "$1"
