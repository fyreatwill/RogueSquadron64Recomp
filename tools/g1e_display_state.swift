// s6891 G1e: read-only state of every online display. A line count change under a run set means the display set moved. usage: g1e_display_state
import CoreGraphics
import Foundation
var n:UInt32=0; var ids=[CGDirectDisplayID](repeating:0,count:8); CGGetOnlineDisplayList(8,&ids,&n)
for i in 0..<Int(n){ let d=ids[i]; print(d,"active",CGDisplayIsActive(d),"asleep",CGDisplayIsAsleep(d),"online",CGDisplayIsOnline(d),"main",CGDisplayIsMain(d),"mirror",CGDisplayIsInMirrorSet(d),"bounds",CGDisplayBounds(d)) }
