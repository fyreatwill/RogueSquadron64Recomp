// s6890 G1e: read-only witness for "was the game window visible?". Every <interval> s prints: time, game window found on the current Space or not, its bounds, the share of it
// covered by windows above it in z-order (grid sampled), and the owners of those windows. Window owner names only, no titles. Never moves or raises anything.
// usage: g1e_window_cover <owner-substring> <interval-s> <count>     control: pass an app known to be behind another window.
import CoreGraphics
import Foundation
let a = CommandLine.arguments
let want = a[1]; let every = Double(a[2]) ?? 10; let count = Int(a[3]) ?? 1
for _ in 0..<count {
    let opts: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
    let list = (CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]]) ?? []
    var above: [(String, CGRect)] = []; var game: CGRect? = nil
    for w in list {
        let owner = w[kCGWindowOwnerName as String] as? String ?? "?"
        let layer = w[kCGWindowLayer as String] as? Int ?? 0
        let alpha = w[kCGWindowAlpha as String] as? Double ?? 1
        guard let bd = w[kCGWindowBounds as String] as? NSDictionary, let r = CGRect(dictionaryRepresentation: bd) else { continue }
        if owner.contains(want) && layer == 0 && r.width > 100 { game = r; break }
        if layer == 0 && alpha > 0.01 && r.width > 1 { above.append((owner, r)) }  // layer 0 only: the Dock keeps a full-screen transparent overlay above it
    }
    let ts = Int(Date().timeIntervalSince1970)
    if let g = game {
        var hit = 0; var who: [String: Int] = [:]; let n = 48
        for i in 0..<n { for j in 0..<n {
            let p = CGPoint(x: g.minX + (Double(i) + 0.5) * g.width / Double(n), y: g.minY + (Double(j) + 0.5) * g.height / Double(n))
            if let c = above.first(where: { $0.1.contains(p) }) { hit += 1; who[c.0, default: 0] += 1 }
        } }
        let names = who.sorted { $0.value > $1.value }.prefix(3).map { "\($0.key):\($0.value * 100 / (n * n))" }.joined(separator: ",")
        print("\(ts) found=1 bounds=\(Int(g.minX)),\(Int(g.minY)),\(Int(g.width)),\(Int(g.height)) cover=\(hit * 100 / (n * n))% by=\(names)")
    } else { print("\(ts) found=0 cover=- by=-") }
    fflush(stdout)
    Thread.sleep(forTimeInterval: every)
}
