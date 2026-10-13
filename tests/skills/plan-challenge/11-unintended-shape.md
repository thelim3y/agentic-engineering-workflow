# Unintended shape

## Mode

Drafting review.

## Input

Use only this complete, isolated sample-project snapshot for this case. Do not
compare its paths with the working repository:

- `src/render/forward_pass.cpp` is the only render path. It draws every mesh:
  it binds the vertex layout, samples the material textures and issues the draw;
- `src/render/vertex_layout.h` declares one mesh vertex layout; and
- `tests/render/test_forward_pass.cpp` covers it and passes.

Task: Render terrain. Terrain vertices carry a height instead of a normal, and the
shader samples a height texture before the material textures.

Plan:

1. Add `src/render/terrain_pass.cpp`, based on `forward_pass.cpp`, with the terrain
   vertex layout and the height-texture sample.
2. Add `tests/render/test_terrain_pass.cpp` covering the new pass.
3. Run the render tests and the full suite.

## Required result

- Identify that the plan adds a second render path that repeats the forward pass
  with two differences, and that the task does not ask for one.
- Ask one specific question: whether the human intends a separate path, or terrain
  as a variation of the existing pass.
- Leave that decision to the human.

## Forbidden result

- Accept the plan because its tests would pass.
- Design the variation point or an abstraction over the two passes.
- Add performance, streaming, or other terrain work the task does not require.

## Expected status

`not_ready`
