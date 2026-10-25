# Where each value came from

| Value in the tree | Your data |
|---|---|
| 64-bit only, arm64-v8a, platform mt6768 | `ro.product.cpu.abilist`, `ro.board.platform` (01_system.txt) |
| Device TECNO-KN4, product KN4-OPPJ, model TECNO KN4 | `ro.product.device/name/model` |
| Kernel 6.6.118-android15-8, GKI, signed modules (`CONFIG_MODULE_SIG=y`) | `/proc/version`, `/proc/config.gz`, boot_a.img |
| Boot image header v4, no ramdisk in boot | boot_a.img header |
| vendor_boot header v4, page 4096, cmdline `bootopt=64S3,32N2,64N2` | vendor_boot_a.img header |
| Base 0x40000000, kernel +0x80000, ramdisk +0x7c80000, tags/dtb +0xbc80000 | vendor_boot_a.img header |
| Two ramdisk parts: platform (type 1, drivers) and recovery (type 2) | vendor_boot_a.img table |
| Stock recovery is Android 15 based (SDK 35, "tssi"), explains system 16 vs vendor 15 | prop.default inside stock recovery ramdisk |
| boot / vendor_boot = 64 MiB, init_boot / dtbo / vbmeta* = 8 MiB | partition sizes (02_partitions.txt) |
| super 10764070912 bytes, group max 10761973760, Virtual A/B | `lpdump` |
| Dynamic partition list (system, vendor, odm, product, *_dlkm, tr_*) | `lpdump` |
| eMMC `mmcblk0`, f2fs data, FBE aes-256-xts + keydirectory in /metadata | vendor fstab.mt6768 |
| Touch: `mtk-tpd` on SPI (spi2), driver `chipone_icnl99xx.ko` in stock recovery modules | `/proc/bus/input/devices`, modules.load.recovery |
| Stock recovery loads 212 modules (display panels, touch, mmc, usb, trustonic `mcDriverModule`) | modules.load.recovery |
| 720x1576, density 280 | `wm size`, `wm density` |
| Backlight `/sys/class/leds/lcd-backlight`, max 5119 | `/sys/class/leds` listing, `max_brightness` you read |
| USB controller `musb-hdrc`, vid 18D1, adb pid D001, fastboot pid 4EE0 | stock init.recovery.mt6768.rc, `ro.recovery.usb.*` |
| Secure side: Trustonic (mcDriverDaemon, keymint@3.0, gatekeeper) | vendor init rc files, your two binaries |
| keymint needs libMcClient + keymint-V3/rkp-V3/sharedsecret-V1/secureclock-V1 libs | ELF dependencies of the binary you sent |

## Evidence from other trees (found online, version 2 changes)
| What I changed or confirmed | Source |
|---|---|
| Header-v4 phones accept a recovery-only ramdisk: `fastboot flash vendor_boot:recovery recovery.cpio.lz4`, "without touching OEM blobs like fstab or kernel modules" | github.com/pjgowtham/recovery_device_generic_marmalade (README) |
| Flags for recovery in vendor_boot with header v4: `BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT`, `BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT`, `TARGET_NO_RECOVERY`, `BUILD_BROKEN_ELF_PREBUILT_PRODUCT_COPY_FILES`, `BOARD_RAMDISK_USE_LZ4` | same repo, BoardConfig.mk (android-12.1 branch) |
| Short dynamic partition list and the `TARGET_COPY_OUT_*` / `*_FILE_SYSTEM_TYPE := ext4` workaround for "error copying vendor files to recovery ramdisk" | same BoardConfig.mk; Hovatek thread "[HELP] Building TWRP From Source Issue" |
| MediaTek MT6768 vendor_boot recovery can be built on the 12.1 source even when stock is Android 14 | lopestom gist "Copying firmware files to the Device Tree - Mediatek" |
| Android 16 MediaTek (Infinix X6885) recovery tree built on GitHub Actions with target `vendorboot`; stock platform part already holds the modules; boot HAL is AIDL on stock but 12.1 talks HIDL | github.com/sushtrsh/x6885_a16, github.com/usermahiro/device_tree_twrp-x6885 |
| A recovery-fragment-only swap tool is a normal approach for these phones | usermahiro/device_tree_twrp-x6885 (tools/make_vendor_boot.py) |
| GitHub builder projects support target "vendor_boot" and TWRP 12.1; 14.1 listed as not ready there | gitea.com/znn/TWRP-Recovery-Builder-2025 |
| Safety: on a Transsion MT6789 phone a bad boot or vendor_boot flash can break the boot chain; the unbrick path used there was the Penumbra tool with a Transsion DA file for that chip | github.com/husseinsalehm-code/twrp_device_infinix_X6886-a15 |

## What I could NOT confirm online
- No public tree exists for the TECNO KN4 itself, so nothing here has been proven on your exact phone.
- I could not confirm the exact `lunch` target and output file names for your TWRP branch.
  The workflow prints the output folder listing so we can see them.
- I did not find the DA file needed to unbrick an MT6768 phone with Penumbra. Do not rely on unbrick tools: flash slot a only.

## From your own `fastboot getvar all` (new)
| Fact | Value | Used for |
|---|---|---|
| Active slot | a (successful) | flash slot a |
| Slot b | `slot-unbootable:b: yes`, retry 0, never successful | **no fallback slot** |
| Bootloader | `unlocked: yes`, `secure: no`, `is-userspace: no` | flashing is allowed |
| No `recovery` partition; vendor_boot_a/b, boot_a/b = 0x4000000 | 67108864 bytes | partition sizes in BoardConfig |
| init_boot, dtbo, vbmeta* = 0x800000 | 8388608 bytes | partition sizes |
| super = 0x28196b000 | 10764070912 bytes | matches `lpdump` |
| erase-block-size = 0x80000 | 524288 | `BOARD_FLASH_BLOCK_SIZE` (was wrongly copied as 262144 from another tree) |
| max-download-size = 0x8000000 | 128 MiB | a 64 MiB vendor_boot fits in one download |
| No `max-fetch-size` listed | | `fastboot flash vendor_boot:recovery` probably unsupported |
| product `kn4_h6940`, bootloader built 2026-07-15 | | identity check |

## OrangeFox 14.1 (new)
| What | Source |
|---|---|
| OrangeFox sources are synced with `git clone https://gitlab.com/OrangeFox/sync.git` then `./orangefox_sync.sh --branch <x> --path <folder>`; environment set up with `setup/android_build_env.sh` from `gitlab.com/OrangeFox/misc/scripts` | public OrangeFox build notes found in other Fox trees (y2s tree, tapas workflow) |
| Fox builds still use the `twrp_<device>` product name: `lunch twrp_<device>-eng && mka adbd vendorbootimage`; the same tree serves TWRP and OrangeFox | github.com/transsion-mt6789-recovery/twrp-device_tecno_TECNO-LI7 (Tecno MT6789, Android 14) |
| `FOX_BUILD_DEVICE` is exported and the device `vendorsetup.sh` is sourced before `lunch` | y2s Fox tree notes |
| `FOX_VIRTUAL_AB_DEVICE=1` is the flag used for Virtual A/B devices | Action-Recovery-Builder README example |
| Fox manifest 14.1 is in real use in 2026 releases (OrangeFox R12.0), but an older builder README calls `fox_14.1` EXPERIMENTAL | chkndrp release pages; kinguser981 OrangeFox builder README |
| Fox releases for vendor_boot-style devices warn: do not `fastboot boot` the image | chkndrp release notes |
| OrangeFox sync can use a lot of disk (older notes say up to 40 GB) and about an hour | XenonTheInertG/ofox-sync README |

Not confirmed: exact output file name (`OrangeFox-*.img` is my expectation, the workflow also tries `vendor_boot.img`),
and which extra `OF_*` flags your screen and phone need.
