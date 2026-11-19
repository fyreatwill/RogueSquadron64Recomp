// s7620 G6b step 3: thin bridge from the F6 Controls panel (rs64_controls_panel.cpp, which only sees plume's
// metal-cpp objects as raw pointers) to ImGui's Objective-C Metal backend. Compiled with ARC; metal-cpp objects are
// the same Objective-C objects, so a __bridge cast hands them over without changing ownership.
#import <Metal/Metal.h>
#include "imgui/imgui.h"
#include "imgui/backends/imgui_impl_metal.h"

bool rs64_imgui_metal_init(void* dev) {
    return ImGui_ImplMetal_Init((__bridge id<MTLDevice>)dev);
}

void rs64_imgui_metal_new_frame(void* tex) {
    @autoreleasepool {
        MTLRenderPassDescriptor* d = [MTLRenderPassDescriptor renderPassDescriptor];
        d.colorAttachments[0].texture = (__bridge id<MTLTexture>)tex;
        d.colorAttachments[0].loadAction = MTLLoadActionLoad;
        d.colorAttachments[0].storeAction = MTLStoreActionStore;
        ImGui_ImplMetal_NewFrame(d);  // keys the pipeline on the swap chain's pixel format / sample count
    }
}

void rs64_imgui_metal_render(ImDrawData* dd, void* cmdbuf, void* enc) {
    if (!dd || !cmdbuf || !enc) return;
    @autoreleasepool {
        ImGui_ImplMetal_RenderDrawData(dd, (__bridge id<MTLCommandBuffer>)cmdbuf, (__bridge id<MTLRenderCommandEncoder>)enc);
    }
}

void rs64_imgui_metal_shutdown() { ImGui_ImplMetal_Shutdown(); }
