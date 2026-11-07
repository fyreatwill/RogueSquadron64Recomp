// s6931 G1e: list the main display's modes, or hold one refresh rate for this process's lifetime only. kCGConfigureForAppOnly reverts when the process exits or is killed, so nothing persists.
// usage: g1e_display_hz            list modes at the current point size
//        g1e_display_hz <hz> [s]   switch, hold for s seconds (default 3600) or until killed, print the mode before and after
import CoreGraphics
import Foundation
let d=CGMainDisplayID()
let opt=[kCGDisplayShowDuplicateLowResolutionModes as String:true] as CFDictionary
guard let cur=CGDisplayCopyDisplayMode(d) else { print("no mode"); exit(1) }
let all=(CGDisplayCopyAllDisplayModes(d,opt) as? [CGDisplayMode]) ?? []
let same=all.filter{$0.width==cur.width&&$0.height==cur.height&&$0.pixelWidth==cur.pixelWidth&&$0.pixelHeight==cur.pixelHeight}
print("current \(cur.width)x\(cur.height) px \(cur.pixelWidth)x\(cur.pixelHeight) hz=\(cur.refreshRate)")
if CommandLine.arguments.count<2 { for m in same { print("mode hz=\(m.refreshRate) flags=\(m.ioFlags) usable=\(m.isUsableForDesktopGUI())") }; exit(0) }
let hz=Double(CommandLine.arguments[1])!; let hold=CommandLine.arguments.count>2 ? Double(CommandLine.arguments[2])! : 3600
guard let m=same.filter({abs($0.refreshRate-hz)<0.5}).first else { print("no mode at \(hz)"); exit(2) }
var c:CGDisplayConfigRef?; CGBeginDisplayConfiguration(&c); CGConfigureDisplayWithDisplayMode(c,d,m,nil)
let e=CGCompleteDisplayConfiguration(c,.forAppOnly)
print("set rc=\(e.rawValue) now hz=\(CGDisplayCopyDisplayMode(d)?.refreshRate ?? 0)"); fflush(stdout)
RunLoop.main.run(until:Date().addingTimeInterval(hold))
