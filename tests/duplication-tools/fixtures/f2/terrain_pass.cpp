#include "gfx.h"
#include "scene.h"
#include "vertex_layout.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace render {

class TerrainPass {
 public:
  explicit TerrainPass(gfx::Device& device);
  ~TerrainPass();

  void record(gfx::CommandList& commands, const FrameTargets& targets,
              std::span<const Mesh> meshes, gfx::Texture* height_map,
              const float view_projection[16]);

 private:
  gfx::Device& device_;
  gfx::Pipeline* pipeline_ = nullptr;
  gfx::Sampler* material_sampler_ = nullptr;
};

namespace {

struct TerrainVertex {
  float position[3];
  float height;
  float uv[2];
};

constexpr std::array<gfx::VertexAttribute, 3> kTerrainVertexAttributes{{
    {0, gfx::Format::Rgb32Float, offsetof(TerrainVertex, position)},
    {1, gfx::Format::R32Float, offsetof(TerrainVertex, height)},
    {2, gfx::Format::Rg32Float, offsetof(TerrainVertex, uv)},
}};

gfx::VertexLayout terrain_vertex_layout() {
  return {sizeof(TerrainVertex), kTerrainVertexAttributes};
}

struct DrawConstants {
  float view_projection[16];
  float model[16];
};

void copy_matrix(float destination[16], const float source[16]) {
  for (int i = 0; i < 16; ++i) {
    destination[i] = source[i];
  }
}

}  // namespace

TerrainPass::TerrainPass(gfx::Device& device) : device_(device) {
  gfx::PipelineDesc desc{};
  desc.vertex_shader = device_.load_shader("shaders/terrain.vert.spv");
  desc.fragment_shader = device_.load_shader("shaders/terrain.frag.spv");
  desc.vertex_layout = terrain_vertex_layout();
  desc.topology = gfx::Topology::TriangleList;
  desc.cull_mode = gfx::CullMode::Back;
  desc.depth_test = true;
  desc.depth_write = true;
  desc.depth_compare = gfx::CompareOp::Less;
  desc.color_format = gfx::Format::Rgba16Float;
  desc.depth_format = gfx::Format::Depth32Float;
  pipeline_ = device_.create_pipeline(desc);
  material_sampler_ = device_.create_sampler(/*linear=*/true, /*repeat=*/true);
}

TerrainPass::~TerrainPass() {
  device_.destroy(material_sampler_);
  device_.destroy(pipeline_);
}

void TerrainPass::record(gfx::CommandList& commands, const FrameTargets& targets,
                         std::span<const Mesh> meshes, gfx::Texture* height_map,
                         const float view_projection[16]) {
  const float clear_color[4] = {0.0f, 0.0f, 0.0f, 1.0f};
  commands.begin_pass(targets.color, targets.depth, clear_color, 1.0f);
  commands.bind_pipeline(pipeline_);

  gfx::Viewport viewport{};
  viewport.width = static_cast<float>(targets.width);
  viewport.height = static_cast<float>(targets.height);
  viewport.max_depth = 1.0f;
  commands.set_viewport(viewport);

  DrawConstants constants{};
  copy_matrix(constants.view_projection, view_projection);

  for (const Mesh& mesh : meshes) {
    if (mesh.material == nullptr || mesh.index_count == 0) {
      continue;
    }
    commands.bind_vertex_buffer(0, mesh.vertices, 0);
    commands.bind_index_buffer(mesh.indices, 0);
    commands.bind_texture(0, height_map, material_sampler_);
    commands.bind_texture(1, mesh.material->albedo, material_sampler_);
    commands.bind_texture(2, mesh.material->normal_map, material_sampler_);
    commands.bind_texture(3, mesh.material->roughness, material_sampler_);
    copy_matrix(constants.model, mesh.model);
    commands.push_constants(&constants, sizeof(constants));
    commands.draw_indexed(mesh.index_count, 0, 0);
  }

  commands.end_pass();
}

}  // namespace render
