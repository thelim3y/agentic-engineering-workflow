#include "gfx.h"
#include "scene.h"
#include "vertex_layout.h"

#include <cstdint>
#include <span>

namespace render {

class TerrainPass {
 public:
  explicit TerrainPass(gfx::Device& gpu);
  ~TerrainPass();

  void record(gfx::CommandList& cmd, const FrameTargets& frame,
              std::span<const Mesh> chunks, const float view_proj[16]);

 private:
  gfx::Device& gpu_;
  gfx::Pipeline* terrain_pipeline_ = nullptr;
  gfx::Sampler* surface_sampler_ = nullptr;
};

namespace {

struct TerrainConstants {
  float view_proj[16];
  float world[16];
};

void assign_matrix(float out[16], const float in[16]) {
  for (int k = 0; k < 16; ++k) {
    out[k] = in[k];
  }
}

}  // namespace

TerrainPass::TerrainPass(gfx::Device& gpu) : gpu_(gpu) {
  gfx::PipelineDesc info{};
  info.vertex_shader = gpu_.load_shader("shaders/terrain.vert.spv");
  info.fragment_shader = gpu_.load_shader("shaders/terrain.frag.spv");
  info.vertex_layout = mesh_vertex_layout();
  info.topology = gfx::Topology::TriangleList;
  info.cull_mode = gfx::CullMode::Back;
  info.depth_test = true;
  info.depth_write = true;
  info.depth_compare = gfx::CompareOp::Less;
  info.color_format = gfx::Format::Rgba16Float;
  info.depth_format = gfx::Format::Depth32Float;
  terrain_pipeline_ = gpu_.create_pipeline(info);
  surface_sampler_ = gpu_.create_sampler(/*linear=*/true, /*repeat=*/true);
}

TerrainPass::~TerrainPass() {
  gpu_.destroy(surface_sampler_);
  gpu_.destroy(terrain_pipeline_);
}

void TerrainPass::record(gfx::CommandList& cmd, const FrameTargets& frame,
                         std::span<const Mesh> chunks, const float view_proj[16]) {
  const float background[4] = {0.0f, 0.0f, 0.0f, 1.0f};
  cmd.begin_pass(frame.color, frame.depth, background, 1.0f);
  cmd.bind_pipeline(terrain_pipeline_);

  gfx::Viewport vp{};
  vp.width = static_cast<float>(frame.width);
  vp.height = static_cast<float>(frame.height);
  vp.max_depth = 1.0f;
  cmd.set_viewport(vp);

  TerrainConstants push{};
  assign_matrix(push.view_proj, view_proj);

  for (const Mesh& chunk : chunks) {
    if (chunk.material == nullptr || chunk.index_count == 0) {
      continue;
    }
    cmd.bind_vertex_buffer(0, chunk.vertices, 0);
    cmd.bind_index_buffer(chunk.indices, 0);
    cmd.bind_texture(0, chunk.material->albedo, surface_sampler_);
    cmd.bind_texture(1, chunk.material->normal_map, surface_sampler_);
    cmd.bind_texture(2, chunk.material->roughness, surface_sampler_);
    assign_matrix(push.world, chunk.model);
    cmd.push_constants(&push, sizeof(push));
    cmd.draw_indexed(chunk.index_count, 0, 0);
  }

  cmd.end_pass();
}

}  // namespace render
