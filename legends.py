import os
import re

# From /usr/bin/scopebuddy 1.5.0: (group, [(name, default, description)])
SCOPEBUDDY = [
    ("Set in a config", [
        ("SCB_GAMESCOPE_ARGS", "", "Default gamescope args. Ignored if args are given before -- in the launch options, unless SCB_APPENDMODE=1. Use += to add to it."),
        ("SCB_APPENDMODE", "0", "1 = always put SCB_GAMESCOPE_ARGS in front of the launch option args instead of being replaced by them."),
        ("SCB_AUTO_RES", "0", "1 = set -W/-H from the current display resolution."),
        ("SCB_AUTO_HDR", "0", "1 = add --hdr-enabled if HDR is on for the display. Without gamescope on the desktop it also exports PROTON_ENABLE_WAYLAND=1 and PROTON_ENABLE_HDR=1."),
        ("SCB_AUTO_VRR", "0", "1 = add --adaptive-sync if VRR is on for the display."),
        ("SCB_AUTO_REFRESH", "0", "1 = set -r to the display refresh rate."),
        ("SCB_AUTO_FRAME_LIMIT", "0", "1 = set --framerate-limit to the display refresh rate."),
        ("SCB_NOSCOPE", "0", "1 = launch the game without gamescope."),
        ("SCB_NESTEDFIX", "1", "Fix for the Steam overlay and Steam Input in nested gamescope. 0 disables it."),
        ("SCB_DEBUG", "0", "1 = write the launch command to ~/.config/scopebuddy/scopebuddy.log."),
        ("SCB_PRE_COMMAND", "", "Shell command run before gamescope starts (gamescope mode only)."),
        ("SCB_POST_COMMAND", "", "Shell command run when the game exits."),
    ]),
    ("Launch options only", [
        ("SCB_CONF", "scb.conf", "Global config to load. noscope.conf and gamemode.conf are picked automatically."),
        ("SCB_APPID", "", "Override the detected AppID."),
        ("SCB_STEAMARGIGNORE", "1", "Drop the -e/--steam gamescope flags, which currently crash gamescope."),
        ("GAMESCOPE_BIN", "gamescope", "gamescope binary to run."),
        ("KSCREEN_COMMAND", "kscreen-doctor", "KDE display tool used by SCB_AUTO_*."),
        ("GDCTL_COMMAND", "gdctl", "GNOME display tool used by SCB_AUTO_*."),
        ("GNOME_RANDR_COMMAND", "gnome-randr", "GNOME fallback display tool used by SCB_AUTO_*."),
        ("WLR_RANDR_COMMAND", "wlr-randr", "wlroots display tool used by SCB_AUTO_*."),
    ]),
    ("Read-only, for scripting", [
        ("SCB_CONFIGDIR", "", "The ScopeBuddy config folder, e.g. source $SCB_CONFIGDIR/hdr.conf"),
        ("SCB_GAMEMODE", "", "1 when running in Steam Game Mode (SCB_NOSCOPE is then 1 too)."),
        ("SCB_NOSCOPE", "", "1 when running without gamescope."),
        ("SCB_APPID", "", "AppID of the game being launched."),
        ("SCB_CONFIGFILE", "", "Full path of the global config that was loaded."),
        ("SCB_VER", "", "ScopeBuddy version."),
        ("command", "", "The expanded %command%. command+=\" ...\" adds game arguments."),
    ]),
]

DXVK = [
    ("DXVK", [
        ("DXVK_HUD", "", "On-screen HUD, e.g. fps,frametimes,gpuload or full. 1 = fps and device info."),
        ("DXVK_CONFIG", "", "dxvk.conf options inline, separated by ;. e.g. dxgi.maxFrameRate=60. Use += to add to it."),
        ("DXVK_CONFIG_FILE", "", "Path to a dxvk.conf file."),
        ("DXVK_FRAME_RATE", "0", "Frame rate limit. 0 = off."),
        ("DXVK_HDR", "0", "1 = expose HDR color spaces to the game. Needs HDR in gamescope or the Wayland driver."),
        ("DXVK_LOG_LEVEL", "info", "none, error, warn, info or debug."),
        ("DXVK_ASYNC", "0", "gplasync builds only: 1 = compile shaders asynchronously to reduce stutter."),
    ]),
    ("DXVK-NVAPI", [
        ("DXVK_ENABLE_NVAPI", "0", "1 = let DXVK report an NVIDIA GPU so NVAPI (DLSS, Reflex) can load."),
        ("DXVK_NVAPI_ALLOW_OTHER_DRIVERS", "0", "1 = allow NVAPI on non-NVIDIA drivers, e.g. for Reflex through the low latency layer."),
        ("DXVK_NVAPI_DRIVER_VERSION", "", "Driver version to report, e.g. 57270 for 572.70."),
        ("DXVK_NVAPI_GPU_ARCH", "", "GPU architecture to report, e.g. AD100 or GB200."),
    ]),
    ("VKD3D-Proton (D3D12)", [
        ("VKD3D_CONFIG", "", "Comma-separated options, e.g. dxr, no_upload_hvv, descriptor_heap. Use += to add to it."),
        ("VKD3D_FRAME_RATE", "0", "Frame rate limit. 0 = off."),
        ("VKD3D_SWAPCHAIN_LATENCY_FRAMES", "", "Maximum queued frames. Lower can reduce input latency."),
        ("VKD3D_FEATURE_LEVEL", "", "D3D12 feature level to report, e.g. 12_2."),
        ("VKD3D_SHADER_MODEL", "", "Shader model to report, e.g. 6_6."),
        ("VKD3D_DEBUG", "", "Log level: none, err, warn, info, trace."),
    ]),
    ("Low latency / Mesa", [
        ("LOW_LATENCY_LAYER", "0", "1 = enable the Vulkan low latency layer (Anti-Lag 2 / Reflex style frame pacing)."),
        ("LOW_LATENCY_LAYER_REFLEX", "0", "1 = let games that use NVIDIA Reflex drive the low latency layer."),
        ("DXIL_SPIRV_CONFIG", "", "Mesa dxil-spirv options, e.g. wmma_rdna3_workaround for FSR4 on RDNA3."),
        ("RADV_PERFTEST", "", "Comma-separated experimental RADV features, e.g. sam, rt, video_decode."),
        ("MESA_VK_WSI_PRESENT_MODE", "", "Force the present mode: fifo, mailbox, immediate or relaxed."),
    ]),
    ("Wine / tools", [
        ("WINE_CPU_TOPOLOGY", "", "CPUs the game sees, e.g. 8:0,1,2,3,4,5,6,7."),
        ("WINEDLLOVERRIDES", "", "DLL load order, e.g. dxgi=n,b to use a native dxgi.dll first."),
        ("MANGOHUD", "0", "1 = enable the MangoHud overlay."),
        ("MANGOHUD_CONFIG", "", "MangoHud options inline, separated by commas, e.g. full or fps_limit=60."),
    ]),
]

# Descriptions for the PROTON_* vars found in the proton scripts. (option) is the matching PROTON_ADD_CONFIG name.
PROTON_DOCS = {
    "PROTON_ADD_CONFIG": "Comma-separated compat options to turn on, e.g. fsr4,wayland,hdr.",
    "PROTON_CPU_TOPOLOGY": "Sets WINE_CPU_TOPOLOGY, e.g. 8:0,1,2,3,4,5,6,7 to limit the CPUs the game sees.",
    "PROTON_CRASH_REPORT_DIR": "Folder to write Wine crash reports to.",
    "PROTON_D7VK_DDRAW": "1 = use D7VK (Vulkan) for DirectDraw / Direct3D 7 games. (d7vkddraw)",
    "PROTON_DEBUG_DIR": "Folder for PROTON_DUMP_DEBUG_COMMANDS scripts. Default /tmp.",
    "PROTON_DISABLE_HIDRAW": "1 = disable raw HID access for controllers.",
    "PROTON_DISABLE_NVAPI": "1 = disable NVAPI (DLSS, Reflex). (disablenvapi)",
    "PROTON_DLL_COPY": "Comma-separated builtin DLLs to copy into the prefix instead of linking. * for all.",
    "PROTON_DLSS_INDICATOR": "1 = show the DLSS / DLSS-FG on-screen indicator. (dlsshud)",
    "PROTON_DLSS_UPGRADE": "1 = replace the game's DLSS DLLs with the latest version. (dlss)",
    "PROTON_DUMP_DEBUG_COMMANDS": "1 = write scripts to rerun the game with a debugger to PROTON_DEBUG_DIR.",
    "PROTON_DXVK_D3D8": "1 = use DXVK instead of wined3d for Direct3D 8. (dxvkd3d8)",
    "PROTON_DXVK_GPLASYNC": "1 = use DXVK gplasync, compiles shaders asynchronously. (dxvkgplasync)",
    "PROTON_DXVK_LLASYNC": "1 = use the low latency DXVK build with async shaders. (dxvkllasync)",
    "PROTON_DXVK_LOWLATENCY": "1 = use the low latency DXVK build, async off. (dxvklowlatency)",
    "PROTON_DXVK_SAREK": "1 = use DXVK-Sarek for older GPUs without Vulkan 1.3. Disables NVAPI. (dxvksarek)",
    "PROTON_EMULATE_STEAMINPUT": "1 = keep Steam Input's virtual gamepad visible to the game.",
    "PROTON_ENABLE_AMD_AGS": "1 = enable AMD AGS support. (enableamdags)",
    "PROTON_ENABLE_HDR": "1 = enable HDR output. Needs the Wayland driver or gamescope. (hdr)",
    "PROTON_ENABLE_HIDRAW": "Comma-separated VID/PID list to give raw HID access, e.g. 0x054C/0x0CE6.",
    "PROTON_ENABLE_MEDIACONV": "1 = convert in-game video/audio with the media converter. (mediaconv)",
    "PROTON_ENABLE_NVAPI": "1 = enable NVAPI (older Proton). (enablenvapi)",
    "PROTON_ENABLE_WAYLAND": "1 = use Wine's Wayland driver instead of XWayland. (wayland)",
    "PROTON_FFX3_UPGRADE": "1 = upgrade the game's FidelityFX 3 SDK DLLs. (ffx3)",
    "PROTON_FFX4_UPGRADE": "1 = upgrade the game's FidelityFX SDK DLLs to FSR 4. (ffx4)",
    "PROTON_FORCE_LARGE_ADDRESS_AWARE": "1 = let 32-bit games use 4 GB of memory. (forcelgadd)",
    "PROTON_FORCE_NVAPI": "1 = enable NVAPI for games that don't get it by default. (forcenvapi)",
    "PROTON_FSR3_UPGRADE": "1 = replace the game's FSR 3.1 DLL with the latest FSR 3. (fsr3)",
    "PROTON_FSR4_INDICATOR": "1 = show the FSR watermark to confirm FSR 4 is active. (fsr4hud)",
    "PROTON_FSR4_RDNA3_UPGRADE": "1 = upgrade FSR 3.1 games to FSR 4 using the RDNA3 build. (fsr4rdna3)",
    "PROTON_FSR4_UPGRADE": "1 = upgrade FSR 3.1 games to FSR 4. (fsr4)",
    "PROTON_HEAP_DELAY_FREE": "1 = delay freeing heap memory, works around use-after-free bugs. (heapdelayfree)",
    "PROTON_HEAP_ZERO_MEMORY": "1 = zero new heap memory, for games that read it uninitialized. (heapzeromemory)",
    "PROTON_HIDE_APU": "1 = hide the integrated AMD GPU from the game. (hideapu)",
    "PROTON_HIDE_INTEL_GPU": "1 = hide Intel GPUs from the game. (hideintelgpu)",
    "PROTON_HIDE_NVIDIA_GPU": "1 = report NVIDIA GPUs as AMD. (hidenvgpu)",
    "PROTON_HIDE_VANGOGH_GPU": "1 = hide the Steam Deck GPU ID from the game. (hidevggpu)",
    "PROTON_HUD": "DXVK_HUD preset 1-5, 1 = fps only, 5 = full. Add ,options for more. Ignored if DXVK_HUD is set.",
    "PROTON_LIMIT_ADDRESS_SPACE": "1 = limit the address space, for old games that crash with lots of memory. Auto-set for some games, your value wins.",
    "PROTON_LIMIT_RESOLUTIONS": "N = only report the N largest resolutions to the game. Auto-set for some games, your value wins.",
    "PROTON_LOCAL_SHADER_CACHE": "1 = keep a per-game shader cache, for when Steam shader pre-caching is off. (localshadercache)",
    "PROTON_LOG": "1 = write steam-<appid>.log to PROTON_LOG_DIR. Other values are added to WINEDEBUG.",
    "PROTON_LOG_DIR": "Folder for PROTON_LOG output. Default $HOME.",
    "PROTON_MEDIACONV_NO_VIDEO": "1 = don't convert in-game videos.",
    "PROTON_MEDIA_FORCE_GST": "1 = force GStreamer for media playback. Auto-set for some games, your value wins.",
    "PROTON_MLFG_UPGRADE": "1 = upgrade to AMD ML frame generation. (mlfg)",
    "PROTON_NATIVE_AGS": "1 = use the game's own amd_ags_x64.dll. (nativeags)",
    "PROTON_NATIVE_STEAM": "1 = don't let Proton's steam.exe wrapper replace a real steam.exe.",
    "PROTON_NO_D3D10": "1 = disable Direct3D 10. (nod3d10)",
    "PROTON_NO_D3D11": "1 = disable Direct3D 11, the game falls back to an older API. (nod3d11)",
    "PROTON_NO_ESYNC": "1 = disable esync. (noesync)",
    "PROTON_NO_FSYNC": "1 = disable fsync. (nofsync)",
    "PROTON_NO_NTSYNC": "1 = disable ntsync, falls back to fsync/esync. (nontsync)",
    "PROTON_NO_STEAMINPUT": "1 = hide Steam Input's virtual gamepad so the game sees the real controller.",
    "PROTON_NO_STEAM_FFMPEG": "1 = don't use Steam's FFmpeg for media playback.",
    "PROTON_NO_WM_DECORATION": "1 = remove window decorations. (nowmdecoration)",
    "PROTON_NO_WRITE_WATCH": "1 = disable write watch support, for games that misuse it. (nowritewatch)",
    "PROTON_NO_XIM": "1 = disable the X input method, fixes some keyboard input issues. (noxim)",
    "PROTON_NVIDIA_LIBS": "1 = enable nvcuda, nvenc, nvml and nvoptix together. (nvidialibs)",
    "PROTON_NVIDIA_LIBS_NO_32BIT": "Like PROTON_NVIDIA_LIBS without the 32-bit libs. (nvidialibsno32)",
    "PROTON_NVIDIA_NVCUDA": "1 = enable CUDA (nvcuda.dll). (nvcuda)",
    "PROTON_NVIDIA_NVENC": "1 = enable NVENC video encoding. (nvenc)",
    "PROTON_NVIDIA_NVML": "1 = enable NVML GPU monitoring. (nvml)",
    "PROTON_NVIDIA_NVOPTIX": "1 = enable OptiX ray tracing. (nvoptix)",
    "PROTON_OLD_GL_STRING": "1 = shorten the OpenGL extension string, for old games. (oldglstr)",
    "PROTON_PREFER_SDL": "1 = use SDL for controller input. (sdlinput)",
    "PROTON_REMOTE_DEBUG_CMD": "Command to start a remote debugger (e.g. msvsmon) with the game.",
    "PROTON_SET_GAME_DRIVE": "1 = map the game's folder to drive S:. (gamedrive)",
    "PROTON_SET_STEAM_DRIVE": "1 = map the Steam folder to a drive letter. (steamdrive)",
    "PROTON_SONY_DUALSENSE_AS_DUALSHOCK4": "1 = present a DualSense as a DualShock 4. Forced on for some games, set it to use on others.",
    "PROTON_SONY_DUALSHOCK4_V2_AS_V1": "1 = present a DualShock 4 v2 as a v1. Forced on for some games, set it to use on others.",
    "PROTON_SONY_HIDRAW_XINPUT": "1 = give Sony controllers raw HID and XInput. Forced on for some games, set it to use on others.",
    "PROTON_SPOOF_STEAMINPUT_VIDPID": "1 = report Steam Input controllers with an Xbox VID/PID. Auto-set for some games, your value wins.",
    "PROTON_STEAMINPUT_FALLBACK": "1 = fall back to Steam Input, re-enables hidraw. Forced on for some games, set it to use on others.",
    "PROTON_STEAMINPUT_XINPUT_FALLBACK": "1 = fall back to Steam Input over XInput, re-enables hidraw.",
    "PROTON_USE_ARM64": "ARM64 hosts only: 1 = run with ARM64 Wine.",
    "PROTON_USE_D7VK": "1 = use D7VK (Vulkan) for DirectDraw / Direct3D 7 games.",
    "PROTON_USE_HDR": "Same as PROTON_ENABLE_HDR. (hdr)",
    "PROTON_USE_OPTISCALER": "1 = install OptiScaler into the prefix, for FSR 4 / XeSS in DLSS games. (optiscaler)",
    "PROTON_USE_PIPEWIRE": "1 = use Wine's PipeWire audio driver. (pipewire)",
    "PROTON_USE_SDL": "Same as PROTON_PREFER_SDL. (sdlinput)",
    "PROTON_USE_WAYLAND": "Same as PROTON_ENABLE_WAYLAND. (wayland)",
    "PROTON_USE_WINED3D": "1 = use wined3d (OpenGL) instead of DXVK / VKD3D. (wined3d)",
    "PROTON_USE_WINED3D11": "1 = use wined3d for Direct3D 11 only. (wined3d)",
    "PROTON_USE_WOW64": "1 = run 32-bit games in the new WoW64 mode. (wow64)",
    "PROTON_USE_WRITECOPY": "1 = simulate write-copy memory, for some DRM / anti-cheat. (writecopy)",
    "PROTON_USE_XALIA": "1 = enable Xalia, adds controller navigation to some mouse-only UIs.",
    "PROTON_VKD3D_LOWLATENCY": "1 = use the low latency VKD3D-Proton build. (vkd3dlowlatency)",
    "PROTON_WAYLAND_MONITOR": "Wayland driver: output to treat as primary, e.g. DP-1.",
    "PROTON_WAYLAND_OPENGL_OVERLAY": "1 = show the Steam overlay in OpenGL games on the Wayland driver.",
    "PROTON_WAYLAND_STEAM_OVERLAY": "1 = show the Steam overlay in Vulkan games on the Wayland driver.",
    "PROTON_WAYLAND_VULKAN_LAYER_ORDER": "Vulkan layer order for the Wayland Steam overlay bridge.",
    "PROTON_XESS_UPGRADE": "1 = replace the game's XeSS DLLs with the latest version. (xess)",
}
# Set by Proton itself: internal plumbing, or fixes for one specific game
PROTON_INTERNAL = {
    "PROTON_VERB", "PROTON_BUILD_NAME", "PROTON_PIPEWIRE_ALSA_PLUGIN", "PROTON_DISABLE_LSTEAMCLIENT",
    "PROTON_AUDIO_CONVERT", "PROTON_AUDIO_CONVERT_BIN", "PROTON_VIDEO_CONVERT", "PROTON_DEMUX",
    "PROTON_DEATH_STRANDING_CONTROLLER_EFFECTS", "PROTON_DEATH_STRANDING_FORCE_ENVIRONMENT_EFFECTS",
    "PROTON_ENABLE_MHWILDS_USB_AUDIO",
}

# (tab label, prefixes of the build name in its version file)
PROTON_FAMILIES = [
    ("Proton", ("proton-", "experimental-")),
    ("GE-Proton", ("GE-Proton",)),
    ("Proton-CachyOS", ("cachyos-",)),
    ("Proton-EM", ("EM-",)),
]


def steam_roots():
    home = os.path.expanduser("~")
    return [os.path.join(home, ".local/share/Steam"), os.path.join(home, ".steam/root"),
            os.path.join(home, ".var/app/com.valvesoftware.Steam/.local/share/Steam")]


def proton_dirs():
    dirs = [os.path.join(root, "compatibilitytools.d", d) for root in steam_roots() + ["/usr/share/steam"]
            if os.path.isdir(os.path.join(root, "compatibilitytools.d"))
            for d in os.listdir(os.path.join(root, "compatibilitytools.d"))]
    libraries = set(steam_roots())
    for root in steam_roots():
        try:
            with open(os.path.join(root, "steamapps/libraryfolders.vdf")) as f:
                libraries.update(re.findall(r'"path"\s+"([^"]+)"', f.read()))
        except OSError:
            pass
    for library in libraries:
        common = os.path.join(library, "steamapps/common")
        if os.path.isdir(common):
            dirs += [os.path.join(common, d) for d in os.listdir(common) if d.startswith("Proton")]
    return dirs


def find_proton_builds():
    """Returns {family: (build name, dir)} for the newest installed build of each family."""
    newest = {}
    for path in {os.path.realpath(d) for d in proton_dirs()}:
        try:
            with open(os.path.join(path, "version")) as f:
                stamp, name = f.read().split(maxsplit=1)
        except (OSError, ValueError):
            continue
        if not os.path.isfile(os.path.join(path, "proton")):
            continue
        name = name.strip()
        for family, prefixes in PROTON_FAMILIES:
            if name.startswith(prefixes) and (family not in newest or int(stamp) > newest[family][0]):
                newest[family] = (int(stamp), name, path)
    return {family: (name, path) for family, (_, name, path) in newest.items()}


def proton_legend(builds, family):
    if family not in builds:
        return [("Not installed", [])]
    name, path = builds[family]
    with open(os.path.join(path, "proton")) as f:
        found = set(re.findall(r'"(PROTON_[A-Z0-9_]+)"', f.read())) - PROTON_INTERNAL
    return [(f"{name} ({os.path.basename(path)})",
             [(var, "", PROTON_DOCS.get(var, "No description yet.")) for var in sorted(found)])]
