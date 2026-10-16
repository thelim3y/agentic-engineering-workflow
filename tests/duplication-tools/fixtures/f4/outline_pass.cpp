#include "gfx.h"
#include "scene.h"
#include "vertex_layout.h"

#include <algorithm>
#include <cstdint>
#include <span>

namespace render {

class OutlinePass {
 public:
  explicit OutlinePass(gfx::Device& device);
  ~OutlinePass();

  void record(gfx::CommandList& commands, const FrameTargets& targets,
              std::span<const Mesh> meshes, std::span<const uint32_t> selected,
              const float view_projection[16], const float outline_color[4]);

 private:
  gfx::Device& device_;
  gfx::Pipeline* pipeline_ = nullptr;
};

namespace {

struct OutlineConstants {
  float view_projection[16];
  float model[16];
  float color[4];
  float width;
  float padding[3];
};

constexpr float kOutlineWidth = 0.02f;

bool is_selected(std::span<const uint32_t> selected, uint32_t index) {
  return std::find(selected.begin(), selected.end(), index) != selected.end();
}

}  // namespace

OutlinePass::OutlinePass(gfx::Device& device) : device_(device) {
  gfx::PipelineDesc desc{};
  desc.vertex_shader = device_.load_shader("shaders/outline.vert.spv");
  desc.fragment_shader = device_.load_shader("shaders/outline.frag.spv");
  desc.vertex_layout = mesh_vertex_layout();
  desc.topology = gfx::Topology::TriangleList;
  desc.cull_mode = gfx::CullMode::None;
  desc.depth_test = true;
  desc.depth_write = false;
  desc.depth_compare = gfx::CompareOp::LessOrEqual;
  desc.color_format = gfx::Format::Rgba16Float;
  desc.depth_format = gfx::Format::Depth32Float;
  pipeline_ = device_.create_pipeline(desc);
}

OutlinePass::~OutlinePass() {
  device_.destroy(pipeline_);
}

void OutlinePass::record(gfx::CommandList& commands, const FrameTargets& targets,
                         std::span<const Mesh> meshes, std::span<const uint32_t> selected,
                         const float view_projection[16], const float outline_color[4]) {
  if (selected.empty()) {
    return;
  }

  commands.begin_pass(targets.color, targets.depth, nullptr, 1.0f);
  commands.bind_pipeline(pipeline_);

  gfx::Viewport viewport{};
  viewport.width = static_cast<float>(targets.width);
  viewport.height = static_cast<float>(targets.height);
  viewport.max_depth = 1.0f;
  commands.set_viewport(viewport);

  OutlineConstants constants{};
  std::copy_n(view_projection, 16, constants.view_projection);
  std::copy_n(outline_color, 4, constants.color);
  constants.width = kOutlineWidth;

  for (uint32_t index = 0; index < meshes.size(); ++index) {
    if (!is_selected(selected, index)) {
      continue;
    }
    const Mesh& mesh = meshes[index];
    commands.bind_vertex_buffer(0, mesh.vertices, 0);
    commands.bind_index_buffer(mesh.indices, 0);
    std::copy_n(mesh.model, 16, constants.model);
    commands.push_constants(&constants, sizeof(constants));
    commands.draw_indexed(mesh.index_count, 0, 0);
  }

  commands.end_pass();
}

}  // namespace render
