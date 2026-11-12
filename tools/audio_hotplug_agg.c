// s7199: real audio-output hot-plug for tests. Creates / destroys a public CoreAudio aggregate output device that
// wraps the default output, so a running game sees a genuine device ADDED / REMOVED (not a synthetic SDL event).
//   audio_hotplug_agg create <name>   (prints the aggregate UID; device persists until destroyed)
//   audio_hotplug_agg destroy <name>
//   audio_hotplug_agg list
//   audio_hotplug_agg getdefault            (prints the default output UID)
//   audio_hotplug_agg setuid <uid>          (s7200: make device <uid> the default output; restore with the saved UID)
// Build: cc -O1 -o build/audio_hotplug_agg tools/audio_hotplug_agg.c -framework CoreAudio -framework CoreFoundation
#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <string.h>

static AudioObjectID default_out(void) {
    AudioObjectPropertyAddress a = {kAudioHardwarePropertyDefaultOutputDevice, kAudioObjectPropertyScopeGlobal,
                                    kAudioObjectPropertyElementMain};
    AudioObjectID d = 0; UInt32 sz = sizeof d;
    AudioObjectGetPropertyData(kAudioObjectSystemObject, &a, 0, NULL, &sz, &d);
    return d;
}
static CFStringRef str_prop(AudioObjectID d, AudioObjectPropertySelector s) {
    AudioObjectPropertyAddress a = {s, kAudioObjectPropertyScopeGlobal, kAudioObjectPropertyElementMain};
    CFStringRef r = NULL; UInt32 sz = sizeof r;
    if (AudioObjectGetPropertyData(d, &a, 0, NULL, &sz, &r) != noErr) return NULL;
    return r;
}
static AudioObjectID find_by_uid(CFStringRef uid) {
    AudioObjectPropertyAddress a = {kAudioHardwarePropertyTranslateUIDToDevice, kAudioObjectPropertyScopeGlobal,
                                    kAudioObjectPropertyElementMain};
    AudioObjectID d = 0; UInt32 sz = sizeof d;
    if (AudioObjectGetPropertyData(kAudioObjectSystemObject, &a, sizeof uid, &uid, &sz, &d) != noErr) return 0;
    return d;
}
static int set_default(AudioObjectID d) {
    AudioObjectPropertyAddress a = {kAudioHardwarePropertyDefaultOutputDevice, kAudioObjectPropertyScopeGlobal,
                                    kAudioObjectPropertyElementMain};
    OSStatus st = AudioObjectSetPropertyData(kAudioObjectSystemObject, &a, 0, NULL, sizeof d, &d);
    printf("setdefault id=%u status=%d now=%u\n", (unsigned)d, (int)st, (unsigned)default_out());
    return st == noErr && default_out() == d ? 0 : 1;
}
int main(int argc, char** argv) {
    if (argc >= 2 && !strcmp(argv[1], "getdefault")) {
        CFStringRef u = str_prop(default_out(), kAudioDevicePropertyDeviceUID);
        char b[300] = ""; if (!u || !CFStringGetCString(u, b, sizeof b, kCFStringEncodingUTF8)) return 1;
        printf("%s\n", b); return 0;
    }
    if (argc >= 3 && !strcmp(argv[1], "setuid")) {
        CFStringRef u = CFStringCreateWithCString(NULL, argv[2], kCFStringEncodingUTF8);
        AudioObjectID d = find_by_uid(u);
        if (!d) { fprintf(stderr, "no device uid %s\n", argv[2]); return 1; }
        return set_default(d);
    }
    if (argc >= 2 && !strcmp(argv[1], "list")) {
        AudioObjectPropertyAddress a = {kAudioHardwarePropertyDevices, kAudioObjectPropertyScopeGlobal,
                                        kAudioObjectPropertyElementMain};
        UInt32 sz = 0; AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &a, 0, NULL, &sz);
        AudioObjectID ids[64]; if (sz > sizeof ids) sz = sizeof ids;
        AudioObjectGetPropertyData(kAudioObjectSystemObject, &a, 0, NULL, &sz, ids);
        for (UInt32 i = 0; i < sz / sizeof(AudioObjectID); ++i) {
            char n[256] = "?"; CFStringRef s = str_prop(ids[i], kAudioObjectPropertyName);
            if (s) { CFStringGetCString(s, n, sizeof n, kCFStringEncodingUTF8); CFRelease(s); }
            printf("%u %s\n", (unsigned)ids[i], n);
        }
        return 0;
    }
    if (argc < 3) { fprintf(stderr, "usage: %s create|destroy <name> | list\n", argv[0]); return 2; }
    char uidbuf[300]; snprintf(uidbuf, sizeof uidbuf, "rs64.hotplug.%s", argv[2]);
    CFStringRef uid = CFStringCreateWithCString(NULL, uidbuf, kCFStringEncodingUTF8);
    CFStringRef name = CFStringCreateWithCString(NULL, argv[2], kCFStringEncodingUTF8);
    if (!strcmp(argv[1], "destroy")) {
        AudioObjectID d = find_by_uid(uid);
        if (!d) { fprintf(stderr, "no device %s\n", uidbuf); return 1; }
        OSStatus st = AudioHardwareDestroyAggregateDevice(d);
        printf("destroy id=%u status=%d\n", (unsigned)d, (int)st);
        return st == noErr ? 0 : 1;
    }
    CFStringRef sub = str_prop(default_out(), kAudioDevicePropertyDeviceUID);
    if (!sub) { fprintf(stderr, "no default output UID\n"); return 1; }
    CFMutableDictionaryRef sd = CFDictionaryCreateMutable(NULL, 0, &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    CFDictionarySetValue(sd, CFSTR(kAudioSubDeviceUIDKey), sub);
    CFArrayRef subs = CFArrayCreate(NULL, (const void**)&sd, 1, &kCFTypeArrayCallBacks);
    CFMutableDictionaryRef desc = CFDictionaryCreateMutable(NULL, 0, &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    CFDictionarySetValue(desc, CFSTR(kAudioAggregateDeviceNameKey), name);
    CFDictionarySetValue(desc, CFSTR(kAudioAggregateDeviceUIDKey), uid);
    CFDictionarySetValue(desc, CFSTR(kAudioAggregateDeviceSubDeviceListKey), subs);
    CFDictionarySetValue(desc, CFSTR(kAudioAggregateDeviceMainSubDeviceKey), sub);
    int zero = 0; CFNumberRef priv = CFNumberCreate(NULL, kCFNumberIntType, &zero);
    CFDictionarySetValue(desc, CFSTR(kAudioAggregateDeviceIsPrivateKey), priv);
    AudioObjectID agg = 0;
    OSStatus st = AudioHardwareCreateAggregateDevice(desc, &agg);
    printf("create id=%u status=%d uid=%s\n", (unsigned)agg, (int)st, uidbuf);
    return st == noErr ? 0 : 1;
}
