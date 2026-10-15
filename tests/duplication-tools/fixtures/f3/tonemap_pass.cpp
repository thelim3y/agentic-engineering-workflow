#include "gfx.h"
#include "scene.h"

#include <algorithm>
#include <cmath>
#include <cstdint>

namespace render {

class TonemapPass {
 public:
  explicit TonemapPass(gfx::Device& device);
  ~TonemapPass();

  void record(gfx::CommandList& commands, const FrameTargets& targets,
              gfx::Texture* hdr_color, float average_luminance, float delta_seconds);

 private:
  gfx::Device& device_;
  gfx::Pipeline* pipeline_ = nullptr;
  gfx::Sampler* hdr_sampler_ = nullptr;
  float adapted_luminance_ = 0.18f;
};

namespace {

struct TonemapConstants {
  float exposure;
  float white_point;
  float inverse_gamma;
  float padding;
};

constexpr float kKeyValue = 0.18f;
constexpr float kAdaptationRate = 1.5f;
constexpr float kMinLuminance = 0.0001f;
constexpr float kWhitePoint = 4.0f;
constexpr float kDisplayGamma = 2.2f;

float adapt_luminance(float adapted, float measured, float delta_seconds) {
  const float clamped = std::max(measured, kMinLuminance);
  const float blend = 1.0f - std::exp(-delta_seconds * kAdaptationRate);
  return adapted + (clamped - adapted) * blend;
}

}  // namespace

TonemapPass::TonemapPass(gfx::Device& device) : device_(device) {
  gfx::PipelineDesc desc{};
  desc.vertex_shader = device_.load_shader("shaders/fullscreen.vert.spv");
  desc.fragment_shader = device_.load_shader("shaders/tonemap.frag.spv");
  desc.vertex_layout = {};
  desc.topology = gfx::Topology::TriangleList;
  desc.cull_mode = gfx::CullMode::None;
  desc.depth_test = false;
  desc.depth_write = false;
  desc.depth_compare = gfx::CompareOp::Always;
  desc.color_format = gfx::Format::Rgba8Unorm;
  desc.depth_format = gfx::Format::Depth32Float;
  pipeline_ = device_.create_pipeline(desc);
  hdr_sampler_ = device_.create_sampler(/*linear=*/true, /*repeat=*/false);
}

TonemapPass::~TonemapPass() {
  device_.destroy(hdr_sampler_);
  device_.destroy(pipeline_);
}

void TonemapPass::record(gfx::CommandList& commands, const FrameTargets& targets,
                         gfx::Texture* hdr_color, float average_luminance,
                         float delta_seconds) {
  adapted_luminance_ = adapt_luminance(adapted_luminance_, average_luminance, delta_seconds);

  const float clear_color[4] = {0.0f, 0.0f, 0.0f, 1.0f};
  commands.begin_pass(targets.color, nullptr, clear_color, 1.0f);
  commands.bind_pipeline(pipeline_);

  gfx::Viewport viewport{};
  viewport.width = static_cast<float>(targets.width);
  viewport.height = static_cast<float>(targets.height);
  viewport.max_depth = 1.0f;
  commands.set_viewport(viewport);

  TonemapConstants constants{};
  constants.exposure = kKeyValue / adapted_luminance_;
  constants.white_point = kWhitePoint;
  constants.inverse_gamma = 1.0f / kDisplayGamma;

  commands.bind_texture(0, hdr_color, hdr_sampler_);
  commands.push_constants(&constants, sizeof(constants));
  commands.draw(3, 0);

  commands.end_pass();
}

}  // namespace render
