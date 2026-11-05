// s6891 G1e: read-only map of which parts of each display no layer-0 window covers, to pick ROGUESQ_WINDOW_POS. Owner names only. usage: g1e_display_free
import CoreGraphics
import Foundation
var n:UInt32=0; var ids=[CGDirectDisplayID](repeating:0,count:8); CGGetActiveDisplayList(8,&ids,&n)
let list=(CGWindowListCopyWindowInfo([.optionOnScreenOnly,.excludeDesktopElements],kCGNullWindowID) as? [[String:Any]]) ?? []
var ws:[(String,CGRect)]=[]
for w in list { let l=w[kCGWindowLayer as String] as? Int ?? 0; let a=w[kCGWindowAlpha as String] as? Double ?? 1
 guard l==0,a>0.01,let bd=w[kCGWindowBounds as String] as? NSDictionary,let r=CGRect(dictionaryRepresentation:bd),r.width>1 else {continue}
 ws.append((w[kCGWindowOwnerName as String] as? String ?? "?",r)) }
for i in 0..<Int(n){ let b=CGDisplayBounds(ids[i]); let hz=CGDisplayCopyDisplayMode(ids[i])?.refreshRate ?? 0
 print("display \(i) id=\(ids[i]) bounds=\(b) hz=\(hz)")
 let C=48,R=24; var rows=""
 for y in 0..<R { var s=""; for x in 0..<C { let p=CGPoint(x:b.minX+(Double(x)+0.5)*b.width/Double(C),y:b.minY+(Double(y)+0.5)*b.height/Double(R)); s+=ws.contains{$0.1.contains(p)} ? "#":"." }; rows+=s+"\n" }
 print(rows)
 print(Set(ws.filter{$0.1.intersects(b)}.map{$0.0}).sorted().joined(separator:",")) }
