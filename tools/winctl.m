// winctl — window discovery, activation and key injection for the capture
// harness, without AppleScript/System Events.
//
// Past sessions lost measurements to `osascript`: it needs Accessibility
// approval, it hangs in some login contexts (session 10 took no captures at
// all because of it), and "raise then screencapture -R" grabs whatever is on
// top if the raise silently failed. CGWindowListCopyWindowInfo gives the
// window id directly, and `screencapture -l<id>` reads that window's own
// backing store, so a capture cannot pick up a different window.
//
// Build: clang -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m
//
//   winctl find <pid>          -> "<windowid> <x> <y> <w> <h>" for the largest
//                                 on-screen window owned by pid (exit 1 if none)
//   winctl activate <pid>      -> bring that app forward
//   winctl key <pid> <keycode> -> post key down/up straight to that process
//                                 (no focus required)
//   winctl trusted             -> "yes"/"no" + exit 0/1: may THIS process post
//                                 synthetic events? (Accessibility permission)
#import <Cocoa/Cocoa.h>
#import <CoreGraphics/CoreGraphics.h>
#import <ApplicationServices/ApplicationServices.h>

static int findWindow(pid_t pid, CGWindowID *outId, CGRect *outRect) {
    CFArrayRef list = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
        kCGNullWindowID);
    if (list == NULL) {
        return 0;
    }

    int found = 0;
    double bestArea = 0.0;
    for (CFIndex i = 0; i < CFArrayGetCount(list); i++) {
        NSDictionary *info = (__bridge NSDictionary *)CFArrayGetValueAtIndex(list, i);
        NSNumber *owner = info[(__bridge NSString *)kCGWindowOwnerPID];
        if (owner == nil || [owner intValue] != (int)pid) {
            continue;
        }

        CGRect rect = CGRectZero;
        CFDictionaryRef boundsDict =
            (__bridge CFDictionaryRef)info[(__bridge NSString *)kCGWindowBounds];
        if (boundsDict == NULL || !CGRectMakeWithDictionaryRepresentation(boundsDict, &rect)) {
            continue;
        }

        // Skip the tiny helper/status windows SDL and Metal create.
        const double area = rect.size.width * rect.size.height;
        if (area < 10000.0 || area <= bestArea) {
            continue;
        }

        bestArea = area;
        *outId = [info[(__bridge NSString *)kCGWindowNumber] unsignedIntValue];
        *outRect = rect;
        found = 1;
    }

    CFRelease(list);
    return found;
}

static void postKey(pid_t pid, CGKeyCode code, useconds_t holdUs) {
    CGEventSourceRef src = CGEventSourceCreate(kCGEventSourceStateHIDSystemState);
    CGEventRef down = CGEventCreateKeyboardEvent(src, code, true);
    CGEventRef up = CGEventCreateKeyboardEvent(src, code, false);
    // Posting to the pid rather than the session means the window does not have
    // to be frontmost, so a failed raise cannot silently swallow the input.
    CGEventPostToPid(pid, down);
    // The game samples SDL_GetKeyboardState once per frame, and the hangar runs
    // at roughly 10 fps, so a short hold can land entirely between two polls and
    // the press is simply never seen. Hold longer than one frame at that rate.
    usleep(holdUs);
    CGEventPostToPid(pid, up);
    if (down) CFRelease(down);
    if (up) CFRelease(up);
    if (src) CFRelease(src);
}

int main(int argc, const char **argv) {
    @autoreleasepool {
        // `trusted` takes no pid, so it is handled before the argc check.
        //
        // This exists because CGEventPostToPid reports success whether or not
        // the caller holds Accessibility permission. Session 24 lost two runs
        // to that: the schedule "fired" with exit 0 and the game never saw a
        // key, so the run silently followed the undriven route and was scored
        // as if it were the driven one. AXIsProcessTrusted answers the question
        // directly and costs nothing, so a run that cannot be driven can be
        // refused up front instead of after 110 seconds.
        if (argc >= 2 && strcmp(argv[1], "trusted") == 0) {
            const BOOL ok = AXIsProcessTrusted();
            printf("%s\n", ok ? "yes" : "no");
            return ok ? 0 : 1;
        }

        if (argc < 3) {
            fprintf(stderr, "usage: winctl find|activate|key <pid> [keycode]\n"
                            "       winctl trusted\n");
            return 2;
        }

        const char *cmd = argv[1];
        const pid_t pid = (pid_t)atoi(argv[2]);

        if (strcmp(cmd, "find") == 0) {
            CGWindowID wid = 0;
            CGRect rect = CGRectZero;
            if (!findWindow(pid, &wid, &rect)) {
                return 1;
            }
            printf("%u %d %d %d %d\n", (unsigned)wid,
                   (int)rect.origin.x, (int)rect.origin.y,
                   (int)rect.size.width, (int)rect.size.height);
            return 0;
        }

        if (strcmp(cmd, "activate") == 0) {
            NSRunningApplication *app =
                [NSRunningApplication runningApplicationWithProcessIdentifier:pid];
            if (app == nil) {
                return 1;
            }
            return [app activateWithOptions:NSApplicationActivateIgnoringOtherApps] ? 0 : 1;
        }

        if (strcmp(cmd, "key") == 0) {
            if (argc < 4) {
                fprintf(stderr, "usage: winctl key <pid> <keycode> [hold-ms]\n");
                return 2;
            }
            const int holdMs = (argc >= 5) ? atoi(argv[4]) : 150;
            postKey(pid, (CGKeyCode)atoi(argv[3]), (useconds_t)(holdMs * 1000));
            return 0;
        }

        fprintf(stderr, "unknown command %s\n", cmd);
        return 2;
    }
}
