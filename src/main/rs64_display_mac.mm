// s6930 G1f: share of the primary screen's height above the safe area (the notch band), 0 on a screen without one.
// SDL's desktop fullscreen window stops below that band, so a whole-panel aspect is wrong there.
#import <AppKit/AppKit.h>

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
