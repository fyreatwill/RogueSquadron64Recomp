// s7202: create a real (virtual) macOS display for display hot-plug tests, hold it, then destroy it.
// Uses the private CoreGraphics CGVirtualDisplay classes (same API as DeskPad / Chromium's
// virtual_display_mac_util). Build: clang -fobjc-arc -framework Foundation -framework CoreGraphics
//   tools/virtual_display.m -o build/virtual_display
// Usage: virtual_display <w> <h> <hold_s>   prints "[vd] created id=N bounds=x,y,w,h ndisp=K",
// then after hold_s releases the display and prints "[vd] destroyed ndisp=K".
#import <Foundation/Foundation.h>
#import <CoreGraphics/CoreGraphics.h>

@interface CGVirtualDisplayDescriptor : NSObject
@property(retain, nonatomic) dispatch_queue_t queue;
@property(retain, nonatomic) NSString *name;
@property(nonatomic) unsigned int maxPixelsHigh;
@property(nonatomic) unsigned int maxPixelsWide;
@property(nonatomic) CGSize sizeInMillimeters;
@property(nonatomic) unsigned int serialNum;
@property(nonatomic) unsigned int productID;
@property(nonatomic) unsigned int vendorID;
@property(copy, nonatomic) void (^terminationHandler)(id, id);
@end
@interface CGVirtualDisplayMode : NSObject
- (instancetype)initWithWidth:(unsigned int)w height:(unsigned int)h refreshRate:(double)r;
@end
@interface CGVirtualDisplaySettings : NSObject
@property(retain, nonatomic) NSArray *modes;
@property(nonatomic) unsigned int hiDPI;
@end
@interface CGVirtualDisplay : NSObject
- (instancetype)initWithDescriptor:(CGVirtualDisplayDescriptor *)d;
- (BOOL)applySettings:(CGVirtualDisplaySettings *)s;
@property(readonly, nonatomic) unsigned int displayID;
@end

static uint32_t ndisp(void) { uint32_t n = 0; CGGetActiveDisplayList(0, NULL, &n); return n; }

int main(int argc, char **argv) {
    @autoreleasepool {
        unsigned w = argc > 1 ? (unsigned)atoi(argv[1]) : 1920, h = argc > 2 ? (unsigned)atoi(argv[2]) : 1080;
        double hold = argc > 3 ? atof(argv[3]) : 20.0;
        uint32_t n0 = ndisp();
        CGVirtualDisplayDescriptor *d = [CGVirtualDisplayDescriptor new];
        d.queue = dispatch_get_main_queue();
        d.name = @"RS64 hotplug test";
        d.maxPixelsWide = w; d.maxPixelsHigh = h;
        d.sizeInMillimeters = CGSizeMake(w * 0.25, h * 0.25);
        d.serialNum = 7202; d.productID = 0x7202; d.vendorID = 0x7202;
        d.terminationHandler = ^(id a, id b) { fprintf(stderr, "[vd] terminated\n"); };
        CGVirtualDisplay *vd = [[CGVirtualDisplay alloc] initWithDescriptor:d];
        if (!vd) { printf("[vd] FAIL create\n"); return 2; }
        CGVirtualDisplaySettings *s = [CGVirtualDisplaySettings new];
        s.hiDPI = 0;
        s.modes = @[[[CGVirtualDisplayMode alloc] initWithWidth:w height:h refreshRate:60]];
        if (![vd applySettings:s]) { printf("[vd] FAIL applySettings\n"); return 3; }
        // let WindowServer publish it
        for (int i = 0; i < 40 && ndisp() == n0; i++) CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.05, false);
        CGRect b = CGDisplayBounds(vd.displayID);
        printf("[vd] created id=%u bounds=%d,%d,%d,%d ndisp=%u->%u\n", vd.displayID, (int)b.origin.x, (int)b.origin.y,
               (int)b.size.width, (int)b.size.height, n0, ndisp());
        fflush(stdout);
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, hold, false);
        vd = nil;
        for (int i = 0; i < 40 && ndisp() != n0; i++) CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.05, false);
        printf("[vd] destroyed ndisp=%u\n", ndisp());
        fflush(stdout);
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 1.0, false);
    }
    return 0;
}
