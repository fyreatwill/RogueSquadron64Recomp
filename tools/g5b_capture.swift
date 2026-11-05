// s6894 G5b: presented-frame recorder that is not our runtime. ScreenCaptureKit records the game window as the
// compositor shows it (everything RT64 presented and macOS displayed), scaled to w x h RGB, into one raw file.
// Record per complete frame: u64 displayTime (mach ticks), u32 w, u32 h, then w*h*3 bytes. Idle (unchanged) frames are
// not delivered, so a gap in displayTime is a repeated frame. Control: tools/g5b_capture.swift against a known movie.
// usage: g5b_capture <owner-substring> <out.raw> <w> <h> <delay-s> <duration-s>
import Foundation
import ScreenCaptureKit
import CoreMedia
import CoreVideo
import AppKit

_ = NSApplication.shared  // CGS must be initialised or SCStream asserts in a CLI
let a = CommandLine.arguments
guard a.count >= 7 else { print("usage: owner out w h delay dur"); exit(2) }
let want = a[1], outPath = a[2]
let W = Int(a[3])!, H = Int(a[4])!, delayS = Double(a[5])!, durS = Double(a[6])!

final class Sink: NSObject, SCStreamOutput, SCStreamDelegate {
    let f: UnsafeMutablePointer<FILE>
    var n = 0, idle = 0, other = 0
    var buf: [UInt8]
    let io = DispatchQueue(label: "io")
    init(_ path: String) {
        f = fopen(path, "wb")!
        setvbuf(f, nil, _IOFBF, 1 << 24)
        buf = [UInt8](repeating: 0, count: 16 + W * H * 3)
    }
    func stream(_ s: SCStream, didOutputSampleBuffer sb: CMSampleBuffer, of t: SCStreamOutputType) {
        guard t == .screen, let arr = CMSampleBufferGetSampleAttachmentsArray(sb, createIfNecessary: false) as? [[SCStreamFrameInfo: Any]],
              let att = arr.first, let raw = att[.status] as? Int, let st = SCFrameStatus(rawValue: raw) else { return }
        if st == .idle { idle += 1; return }
        guard st == .complete, let px = CMSampleBufferGetImageBuffer(sb) else { other += 1; return }
        let dt = (att[.displayTime] as? UInt64) ?? 0
        CVPixelBufferLockBaseAddress(px, .readOnly)
        let base = CVPixelBufferGetBaseAddress(px)!.assumingMemoryBound(to: UInt8.self)
        let bpr = CVPixelBufferGetBytesPerRow(px)
        let w = min(W, CVPixelBufferGetWidth(px)), h = min(H, CVPixelBufferGetHeight(px))
        buf.withUnsafeMutableBytes { d in
            d.storeBytes(of: dt, toByteOffset: 0, as: UInt64.self)
            d.storeBytes(of: UInt32(W), toByteOffset: 8, as: UInt32.self)
            d.storeBytes(of: UInt32(H), toByteOffset: 12, as: UInt32.self)
            let o = d.baseAddress!.assumingMemoryBound(to: UInt8.self) + 16
            for y in 0..<h {
                let r = base + y * bpr; let q = o + y * W * 3
                for x in 0..<w { q[x*3] = r[x*4+2]; q[x*3+1] = r[x*4+1]; q[x*3+2] = r[x*4] }  // BGRA -> RGB
            }
        }
        CVPixelBufferUnlockBaseAddress(px, .readOnly)
        fwrite(buf, 1, buf.count, f)
        n += 1
    }
    func stream(_ s: SCStream, didStopWithError e: Error) { print("stopped: \(e)"); fflush(stdout) }
}

func findWindow() async -> SCWindow? {
    guard let c = try? await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: true) else { return nil }
    return c.windows.first { ($0.owningApplication?.applicationName ?? "").contains(want) && $0.frame.width > 100 }
}

Task {
    var win: SCWindow? = nil
    for _ in 0..<600 { win = await findWindow(); if win != nil { break }; try? await Task.sleep(nanoseconds: 500_000_000) }
    guard let w = win else { print("no window"); exit(3) }
    try? await Task.sleep(nanoseconds: UInt64(delayS * 1e9))
    win = await findWindow() ?? w   // the window can be recreated during boot
    print("window \(win!.frame)"); fflush(stdout)
    let cfg = SCStreamConfiguration()
    cfg.width = W; cfg.height = H; cfg.pixelFormat = kCVPixelFormatType_32BGRA
    cfg.minimumFrameInterval = CMTime(value: 1, timescale: 120); cfg.queueDepth = 8; cfg.showsCursor = false
    let sink = Sink(outPath)
    let st = SCStream(filter: SCContentFilter(desktopIndependentWindow: win!), configuration: cfg, delegate: sink)
    do {
        try st.addStreamOutput(sink, type: .screen, sampleHandlerQueue: DispatchQueue(label: "cap", qos: .userInitiated))
        try await st.startCapture()
    } catch { print("start failed: \(error)"); exit(4) }
    try? await Task.sleep(nanoseconds: UInt64(durS * 1e9))
    try? await st.stopCapture()
    fflush(sink.f); fclose(sink.f)
    print("frames \(sink.n) idle \(sink.idle) other \(sink.other)"); fflush(stdout)
    exit(0)
}
RunLoop.main.run()
