// s6930 G1f: share of the primary screen's height above the safe area (the notch band), 0 on a screen without one.
// SDL's desktop fullscreen window stops below that band, so a whole-panel aspect is wrong there.
#import <AppKit/AppKit.h>
#import <QuartzCore/CAMetalLayer.h>

// s7226: same for the screen whose frame matches SDL display bounds (x, w, h in points); screens[0] if none matches.
extern "C" double rs64_display_top_inset_frac(void);
extern "C" double rs64_display_top_inset_frac_at(int x, int w, int h) {
    @autoreleasepool {
        for (NSScreen* s in [NSScreen screens]) {
            const NSRect f = s.frame;
            if ((int)f.origin.x == x && (int)f.size.width == w && (int)f.size.height == h) {
                if (f.size.height <= 0.0) return 0.0;
                if (@available(macOS 12.0, *)) return s.safeAreaInsets.top / f.size.height;
                return 0.0;
            }
        }
    }
    return rs64_display_top_inset_frac();
}
extern "C" double rs64_display_top_inset_frac(void) {
    @autoreleasepool {
        NSArray<NSScreen*>* screens = [NSScreen screens];
        if (screens.count == 0) return 0.0;
        NSScreen* s = screens[0];
        const double h = s.frame.size.height;
        if (h <= 0.0) return 0.0;
        if (@available(macOS 12.0, *)) return s.safeAreaInsets.top / h;
        return 0.0;
    }
}

// s7202 display hot-plug witness: where the game window is after a display change (frame, screen, active Space,
// occlusion, fullscreen style, layer drawable/scale). Main thread only (called from update_gfx).
extern "C" void rs64_window_state_log(void* nswindow, void* metal_layer, const char* tag) {
    @autoreleasepool {
        NSWindow* w = (__bridge NSWindow*)nswindow;
        if (!w) return;
        const NSRect f = w.frame;
        NSScreen* s = w.screen;
        const NSRect sf = s ? s.frame : NSZeroRect;
        CAMetalLayer* l = (__bridge CAMetalLayer*)metal_layer;
        const CGSize ds = l ? l.drawableSize : CGSizeZero;
        fprintf(stderr, "[g1f-win] %s frame=%.0f,%.0f,%.0fx%.0f screen=%.0f,%.0f,%.0fx%.0f scale=%.1f active_space=%d visible=%d "
                "occl_visible=%d fs_style=%d key=%d layer=%.0fx%.0f@%.1f nscreens=%lu\n", tag,
                f.origin.x, f.origin.y, f.size.width, f.size.height, sf.origin.x, sf.origin.y, sf.size.width, sf.size.height,
                w.backingScaleFactor, (int)w.isOnActiveSpace, (int)w.isVisible,
                (int)((w.occlusionState & NSWindowOcclusionStateVisible) != 0),
                (int)((w.styleMask & NSWindowStyleMaskFullScreen) != 0), (int)w.isKeyWindow, ds.width, ds.height,
                l ? l.contentsScale : 0.0, (unsigned long)[NSScreen screens].count);
    }
}
