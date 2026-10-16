#include "gfx.h"
#include "scene.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace render {

class WaterPass {
 public:
  explicit WaterPass(gfx::Device& device);
  ~WaterPass();

  void record(gfx::CommandList& commands, const FrameTargets& targets,
              std::span<const Mesh> meshes, const float view_projection[16],
              gfx::Texture* ripple_map, float time_seconds);

 private:
  gfx::Device& device_;
  gfx::Pipeline* pipeline_ = nullptr;
  gfx::Sampler* surface_sampler_ = nullptr;
  gfx::Sampler* ripple_sampler_ = nullptr;
};

namespace {

struct WaterConstants {
  float view_projection[16];
  float model[16];
  float time;
  float padding[3];
};

void copy_matrix(float destination[16], const float source[16]) {
  for (int i = 0; i < 16; ++i) {
    destination[i] = source[i];
  }
}

struct WaterVertex {
  float position[3];
  float uv[2];
};

constexpr std::array<gfx::VertexAttribute, 2> kWaterVertexAttributes{{
    {0, gfx::Format::Rgb32Float, offsetof(WaterVertex, position)},
    {1, gfx::Format::Rg32Float, offsetof(WaterVertex, uv)},
}};

}  // namespace

WaterPass::WaterPass(gfx::Device& device) : device_(device) {
  gfx::PipelineDesc desc{};
  desc.vertex_shader = device_.load_shader("shaders/water.vert.spv");
  desc.fragment_shader = device_.load_shader("shaders/water.frag.spv");
  desc.vertex_layout = {sizeof(WaterVertex), kWaterVertexAttributes};
  desc.topology = gfx::Topology::TriangleList;
  desc.cull_mode = gfx::CullMode::None;
  desc.depth_test = true;
  desc.depth_write = false;
  desc.depth_compare = gfx::CompareOp::Less;
  desc.color_format = gfx::Format::Rgba16Float;
  desc.depth_format = gfx::Format::Depth32Float;
  pipeline_ = device_.create_pipeline(desc);
  surface_sampler_ = device_.create_sampler(/*linear=*/true, /*repeat=*/true);
  ripple_sampler_ = device_.create_sampler(/*linear=*/true, /*repeat=*/true);
}

WaterPass::~WaterPass() {
  device_.destroy(ripple_sampler_);
  device_.destroy(surface_sampler_);
  device_.destroy(pipeline_);
}

void WaterPass::record(gfx::CommandList& commands, const FrameTargets& targets,
                       std::span<const Mesh> meshes, const float view_projection[16],
                       gfx::Texture* ripple_map, float time_seconds) {
  commands.begin_pass(targets.color, targets.depth, nullptr, 1.0f);
  commands.bind_pipeline(pipeline_);

  gfx::Viewport viewport{};
  viewport.width = static_cast<float>(targets.width);
  viewport.height = static_cast<float>(targets.height);
  viewport.max_depth = 1.0f;
  commands.set_viewport(viewport);

  WaterConstants constants{};
  copy_matrix(constants.view_projection, view_projection);
  constants.time = time_seconds;

  for (const Mesh& mesh : meshes) {
    if (mesh.index_count == 0) {
      continue;
    }
    commands.bind_vertex_buffer(0, mesh.vertices, 0);
    commands.bind_index_buffer(mesh.indices, 0);
    commands.bind_texture(0, mesh.material->albedo, surface_sampler_);
    commands.bind_texture(1, ripple_map, ripple_sampler_);
    commands.bind_texture(2, mesh.material->roughness, surface_sampler_);
    copy_matrix(constants.model, mesh.model);
    commands.push_constants(&constants, sizeof(constants));
    commands.draw_indexed(mesh.index_count, 0, 0);
  }

  commands.end_pass();
}

}  // namespace render
