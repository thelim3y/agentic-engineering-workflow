Recorded before the first tool run on F4-F6, 2026-10-14.

| Case | File | Class | Expected from the check |
|---|---|---|---|
| F4 | outline_pass.cpp | Convention, close: same pipeline, preamble and mesh-binding conventions; selection filter, no textures, no clear. | No finding |
| F5 | water_pass.cpp | Copy: forward pass adapted line by line, with an edit every few statements. | Finding |
| F6 | sky_pass.cpp | Convention, medium: fullscreen pass with depth test, same pipeline and preamble conventions. | No finding |

Question: does a CPD window (detects F1, F2, F5; silent on F3, F4, F6) still exist?
