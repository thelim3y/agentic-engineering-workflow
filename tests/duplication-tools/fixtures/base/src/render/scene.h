#pragma once

#include "gfx.h"

#include <cstdint>

namespace render {

struct Material {
  gfx::Texture* albedo;
  gfx::Texture* normal_map;
  gfx::Texture* roughness;
};

struct Mesh {
  gfx::Buffer* vertices;
  gfx::Buffer* indices;
  uint32_t index_count;
  const Material* material;
  float model[16];
};

struct FrameTargets {
  gfx::Texture* color;
  gfx::Texture* depth;
  uint32_t width;
  uint32_t height;
};

}  // namespace render
