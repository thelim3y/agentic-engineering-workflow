#pragma once

#include "gfx.h"

#include <array>
#include <cstddef>

namespace render {

struct MeshVertex {
  float position[3];
  float normal[3];
  float uv[2];
};

inline constexpr std::array<gfx::VertexAttribute, 3> kMeshVertexAttributes{{
    {0, gfx::Format::Rgb32Float, offsetof(MeshVertex, position)},
    {1, gfx::Format::Rgb32Float, offsetof(MeshVertex, normal)},
    {2, gfx::Format::Rg32Float, offsetof(MeshVertex, uv)},
}};

inline gfx::VertexLayout mesh_vertex_layout() {
  return {sizeof(MeshVertex), kMeshVertexAttributes};
}

}  // namespace render
