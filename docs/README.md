# TWRP device tree: TECNO Spark 50 (KN4) - version 2 (GitHub build)

Built from your own phone data, then checked against other working trees online
(see `evidence.md`). **Not compiled yet.** Your first GitHub run is the real test.
Send me the error text or the `build.log` and I will fix it.

## 0. Two workflows are included
- `build-orangefox.yml` -> OrangeFox 14.1 (your chosen path)
- `build-twrp.yml` -> TWRP 12.1 (backup path)
Both use the same device tree and give you `recovery.cpio.lz4`. The rest of this file applies to both.
**Do not `fastboot boot` the recovery.** Other vendor_boot-recovery releases warn that it can brick the phone,
and a vendor_boot recovery cannot be tested that way anyway.

## 1. Build on GitHub
1. Create a new GitHub repo. Put the **contents** of this folder at its top level
   (`BoardConfig.mk` must be in the root, and `.github/workflows/build.yml` must keep its path).
2. Open **Actions > Build KN4 recovery > Run workflow**. Keep `twrp-12.1` and `vendorbootimage`.
3. When it finishes, download the artifact **KN4-recovery**. Inside:
   - `recovery.cpio.lz4`  <- this is what you flash
   - `vendor_boot_built.img` (do NOT flash this whole file, see below)
   - `build.log`, `out-listing.txt`, `extract.log`

If the build fails, download the artifact anyway and send me `build.log`.

## 2. Why we flash only the recovery part
Your stock `vendor_boot` has two parts: the **platform** part (signed driver modules for touch,
display, storage) and the **recovery** part. A build alone does not have your drivers.
Header-v4 phones let you replace only the recovery part, so the stock drivers stay untouched.

## 3. Flash (bootloader unlocked)
Check the active slot first:

    fastboot getvar current-slot

Turn off verification (use your own stock vbmeta images, same slot):

    fastboot --disable-verity --disable-verification flash vbmeta_a        vbmeta_a.img
    fastboot --disable-verity --disable-verification flash vbmeta_system_a vbmeta_system_a.img
    fastboot --disable-verity --disable-verification flash vbmeta_vendor_a vbmeta_vendor_a.img

**Method A (preferred): flash only the recovery part.**

    fastboot flash vendor_boot:recovery recovery.cpio.lz4

This is the method the generic header-v4 tree documents. It needs your bootloader to support reading
the partition back. **Your `getvar all` does not list `max-fetch-size`, so this probably will not work
on your phone.** Try it once. If it prints an error, it should not have written anything. Then use method B,
which is the one I expect you to need.

**Method B (fallback): rebuild the full image with my tool.**

    sudo apt install lz4
    python3 tools/repack_vendor_boot.py vendor_boot_a.img recovery.cpio.lz4 -o vendor_boot_new.img
    fastboot flash vendor_boot_a vendor_boot_new.img

Then: `fastboot reboot recovery`.
**Slot b is NOT a safety net on your phone.** Your `getvar all` shows slot b as unbootable
(`slot-unbootable:b: yes`, retry count 0, never successful). So do not use `set_active b` to escape.
Your way back is: boot to fastboot and flash your stock `vendor_boot_a.img` again.
Keep that file on your PC, and keep stock `boot_a.img` and the three stock vbmeta images too.

## 4. What I already know can still go wrong
- Slot switching inside recovery: another Android 16 MediaTek tree reports the stock phone uses an
  AIDL boot HAL while the 12.1 recovery speaks HIDL. Expect no slot switching at first.
- Decryption (Phase 2) is not enabled. Your data is encrypted and the secure side is Trustonic.
- Touch is expected to work because your touch module is already in the stock recovery module list,
  but this is not proven until you boot it.
- Disk space or time on the GitHub runner. Tell me if it fails with "No space left".

## 5. Phase 2 (later): decryption files from the phone
    adb shell su -c "mkdir -p /sdcard/p2 && cd /vendor && cp bin/mcDriverDaemon bin/hw/vendor.trustonic.tee-service bin/kmsetkey_ca.trustonic /sdcard/p2/"
    adb shell su -c "cd /vendor/lib64 && cp libMcClient.so libMcRegistry.so android.hardware.security.keymint-V3-ndk.so android.hardware.security.rkp-V3-ndk.so android.hardware.security.sharedsecret-V1-ndk.so android.hardware.security.secureclock-V1-ndk.so android.hardware.gatekeeper-V1-ndk.so /sdcard/p2/"
    adb pull /sdcard/p2
Some names may not exist. Tell me which fail.
