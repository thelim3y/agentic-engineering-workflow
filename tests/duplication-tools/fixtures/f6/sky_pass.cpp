#include "gfx.h"
#include "scene.h"

#include <algorithm>
#include <cstdint>

namespace render {

class SkyPass {
 public:
  explicit SkyPass(gfx::Device& device);
  ~SkyPass();

  void record(gfx::CommandList& commands, const FrameTargets& targets,
              gfx::Texture* environment, const float inverse_view_projection[16]);

 private:
  gfx::Device& device_;
  gfx::Pipeline* pipeline_ = nullptr;
  gfx::Sampler* environment_sampler_ = nullptr;
};

namespace {

struct SkyConstants {
  float inverse_view_projection[16];
  float intensity;
  float padding[3];
};

constexpr float kSkyIntensity = 1.0f;

}  // namespace

SkyPass::SkyPass(gfx::Device& device) : device_(device) {
  gfx::PipelineDesc desc{};
  desc.vertex_shader = device_.load_shader("shaders/fullscreen.vert.spv");
  desc.fragment_shader = device_.load_shader("shaders/sky.frag.spv");
  desc.vertex_layout = {};
  desc.topology = gfx::Topology::TriangleList;
  desc.cull_mode = gfx::CullMode::None;
  desc.depth_test = true;
  desc.depth_write = false;
  desc.depth_compare = gfx::CompareOp::LessOrEqual;
  desc.color_format = gfx::Format::Rgba16Float;
  desc.depth_format = gfx::Format::Depth32Float;
  pipeline_ = device_.create_pipeline(desc);
  environment_sampler_ = device_.create_sampler(/*linear=*/true, /*repeat=*/false);
}

SkyPass::~SkyPass() {
  device_.destroy(environment_sampler_);
  device_.destroy(pipeline_);
}

void SkyPass::record(gfx::CommandList& commands, const FrameTargets& targets,
                     gfx::Texture* environment, const float inverse_view_projection[16]) {
  commands.begin_pass(targets.color, targets.depth, nullptr, 1.0f);
  commands.bind_pipeline(pipeline_);

  gfx::Viewport viewport{};
  viewport.width = static_cast<float>(targets.width);
  viewport.height = static_cast<float>(targets.height);
  viewport.max_depth = 1.0f;
  commands.set_viewport(viewport);

  SkyConstants constants{};
  std::copy_n(inverse_view_projection, 16, constants.inverse_view_projection);
  constants.intensity = kSkyIntensity;

  commands.bind_texture(0, environment, environment_sampler_);
  commands.push_constants(&constants, sizeof(constants));
  commands.draw(3, 0);

  commands.end_pass();
}

}  // namespace render
