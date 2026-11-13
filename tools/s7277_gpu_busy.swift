// s7277 G5c GPU load generator: back-to-back Metal compute dispatches of an ALU-heavy kernel until killed.
// Each command buffer runs ~ITER inner iterations per thread over N threads; the next one is committed when the
// previous completes, so the GPU stays saturated (a second process competing with the game's Metal queue).
// build: DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun swiftc -O tools/s7277_gpu_busy.swift -o scratch/s7277/gpu_busy
// usage: gpu_busy [iter=20000] [threads=1048576]   prints cmdbuf/s and ms per buffer every 5 s to stderr.
import Metal
import Foundation
let a = CommandLine.arguments
let iter = UInt32(a.count > 1 ? Int(a[1])! : 20000), n = a.count > 2 ? Int(a[2])! : 1 << 20
let src = """
#include <metal_stdlib>
using namespace metal;
kernel void spin(device float *o [[buffer(0)]], constant uint &it [[buffer(1)]], uint i [[thread_position_in_grid]]) {
  float x = float(i) * 1e-6f, y = 1.0001f;
  for (uint k = 0; k < it; k++) { x = fma(x, y, 0.5f); y = fma(y, 0.99999f, x * 1e-9f); }
  o[i] = x + y;
}
"""
let dev = MTLCreateSystemDefaultDevice()!
let lib = try! dev.makeLibrary(source: src, options: nil)
let pso = try! dev.makeComputePipelineState(function: lib.makeFunction(name: "spin")!)
let q = dev.makeCommandQueue()!
let buf = dev.makeBuffer(length: n * 4, options: .storageModePrivate)!
var it = iter
var cnt = 0, tsum = 0.0, last = Date()
while true {
    let cb = q.makeCommandBuffer()!
    let e = cb.makeComputeCommandEncoder()!
    e.setComputePipelineState(pso); e.setBuffer(buf, offset: 0, index: 0); e.setBytes(&it, length: 4, index: 1)
    e.dispatchThreads(MTLSize(width: n, height: 1, depth: 1), threadsPerThreadgroup: MTLSize(width: pso.maxTotalThreadsPerThreadgroup, height: 1, depth: 1))
    e.endEncoding(); cb.commit(); cb.waitUntilCompleted()
    cnt += 1; tsum += cb.gpuEndTime - cb.gpuStartTime
    if Date().timeIntervalSince(last) >= 5 {
        FileHandle.standardError.write(String(format: "gpu_busy %.1f cb/s %.1f ms/cb\n", Double(cnt) / 5, tsum / Double(cnt) * 1000).data(using: .utf8)!)
        cnt = 0; tsum = 0; last = Date()
    }
}
