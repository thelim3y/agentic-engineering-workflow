#pragma once

#include <cstdint>
#include <span>
#include <string_view>

namespace gfx {

enum class Format { R32Float, Rg32Float, Rgb32Float, Rgba32Float, Rgba8Unorm, Rgba16Float, Depth32Float };
enum class Topology { TriangleList, TriangleStrip };
enum class CullMode { None, Back };
enum class CompareOp { Always, Less, LessOrEqual };

struct VertexAttribute {
  uint32_t location;
  Format format;
  uint32_t offset;
};

struct VertexLayout {
  uint32_t stride;
  std::span<const VertexAttribute> attributes;
};

struct Texture;
struct Sampler;
struct Buffer;
struct Pipeline;
struct ShaderModule;

struct PipelineDesc {
  ShaderModule* vertex_shader;
  ShaderModule* fragment_shader;
  VertexLayout vertex_layout;
  Topology topology;
  CullMode cull_mode;
  bool depth_test;
  bool depth_write;
  CompareOp depth_compare;
  Format color_format;
  Format depth_format;
};

struct Viewport {
  float x;
  float y;
  float width;
  float height;
  float min_depth;
  float max_depth;
};

class Device {
 public:
  Pipeline* create_pipeline(const PipelineDesc& desc);
  ShaderModule* load_shader(std::string_view path);
  Sampler* create_sampler(bool linear, bool repeat);
  void destroy(Pipeline* pipeline);
  void destroy(Sampler* sampler);
};

class CommandList {
 public:
  void begin_pass(Texture* color, Texture* depth, const float clear_color[4], float clear_depth);
  void end_pass();
  void bind_pipeline(Pipeline* pipeline);
  void set_viewport(const Viewport& viewport);
  void bind_vertex_buffer(uint32_t slot, Buffer* buffer, uint64_t offset);
  void bind_index_buffer(Buffer* buffer, uint64_t offset);
  void bind_texture(uint32_t slot, Texture* texture, Sampler* sampler);
  void push_constants(const void* data, uint32_t size);
  void draw(uint32_t vertex_count, uint32_t first_vertex);
  void draw_indexed(uint32_t index_count, uint32_t first_index, int32_t vertex_offset);
};

}  // namespace gfx
