#
# BoardConfig for TECNO Spark 50 (KN4) - recovery build
# Every value below comes from your own phone data. See docs/evidence.md.
#
DEVICE_PATH := device/tecno/KN4

# ---- Architecture: 64-bit only (sys_mssi_64_64only, abilist arm64-v8a) ----
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := cortex-a75

# ---- Platform ----
TARGET_BOARD_PLATFORM := mt6768
TARGET_BOOTLOADER_BOARD_NAME := TECNO-KN4
TARGET_NO_BOOTLOADER := true
TARGET_OTA_ASSERT_DEVICE := KN4,TECNO-KN4

# ---- Kernel: use the stock one (GKI 6.6.118-android15-8, signed modules) ----
TARGET_FORCE_PREBUILT_KERNEL := true
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
BOARD_KERNEL_IMAGE_NAME := Image.gz

# Modern AOSP / TWRP prebuilt DTB definitions
BOARD_PREBUILT_DTBIMAGE_DIR := $(DEVICE_PATH)/prebuilt
BOARD_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb.img
TARGET_PREBUILT_DTB := $(DEVICE_PATH)/prebuilt/dtb.img
BOARD_INCLUDE_DTB_IN_BOOTIMG := true

# ---- Boot image layout: copied from your stock vendor_boot_a.img header ----
BOARD_BOOT_HEADER_VERSION := 4
BOARD_KERNEL_BASE := 0x40000000
BOARD_KERNEL_OFFSET := 0x00080000
BOARD_RAMDISK_OFFSET := 0x07c80000
BOARD_TAGS_OFFSET := 0x0bc80000
BOARD_DTB_OFFSET := 0x0bc80000
BOARD_KERNEL_PAGESIZE := 4096
BOARD_RAMDISK_USE_LZ4 := true
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2
# Optional while debugging (do not use for normal use):
# BOARD_KERNEL_CMDLINE += androidboot.selinux=permissive
BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOT_HEADER_VERSION)
BOARD_MKBOOTIMG_ARGS += --kernel_offset $(BOARD_KERNEL_OFFSET)
BOARD_MKBOOTIMG_ARGS += --ramdisk_offset $(BOARD_RAMDISK_OFFSET)
BOARD_MKBOOTIMG_ARGS += --tags_offset $(BOARD_TAGS_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb_offset $(BOARD_DTB_OFFSET)
BOARD_MKBOOTIMG_ARGS += --dtb $(TARGET_PREBUILT_DTB)

# ---- Recovery lives inside vendor_boot (there is no recovery partition) ----
# Same pattern as other working header-v4 trees (see docs/evidence.md).
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true
TARGET_NO_RECOVERY := true
BUILD_BROKEN_ELF_PREBUILT_PRODUCT_COPY_FILES := true

# Workaround for "error copying vendor files to recovery ramdisk" that other
# dynamic-partition trees hit. Harmless if you never see that error.
BOARD_PRODUCTIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_SYSTEM_EXTIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDORIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_VENDOR_DLKMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_ODMIMAGE_FILE_SYSTEM_TYPE := ext4
TARGET_COPY_OUT_PRODUCT := product
TARGET_COPY_OUT_SYSTEM_EXT := system_ext
TARGET_COPY_OUT_VENDOR := vendor
TARGET_COPY_OUT_VENDOR_DLKM := vendor_dlkm
TARGET_COPY_OUT_ODM := odm

# ---- Partition sizes (exact bytes from your phone) ----
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608
BOARD_DTBOIMG_PARTITION_SIZE := 8388608
BOARD_FLASH_BLOCK_SIZE := 524288
# 524288 = erase-block-size 0x80000 from your "fastboot getvar all"

# ---- A/B and dynamic partitions (super) ----
AB_OTA_UPDATER := true
AB_OTA_PARTITIONS += boot vendor_boot init_boot dtbo vbmeta vbmeta_system vbmeta_vendor \
    system system_ext vendor product odm vendor_dlkm

BOARD_SUPER_PARTITION_SIZE := 10764070912
BOARD_SUPER_PARTITION_GROUPS := tecno_dynamic_partitions
BOARD_TECNO_DYNAMIC_PARTITIONS_SIZE := 10761973760
# Short list on purpose. A recovery build does not need the full super layout, and the
# 12.1 build system may not know odm_dlkm / system_dlkm / tr_* (other header-v4 trees list only these).
BOARD_TECNO_DYNAMIC_PARTITIONS_PARTITION_LIST := system system_ext vendor product odm vendor_dlkm

# ---- File systems ----
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true
TARGET_USES_MKE2FS := true
BOARD_USES_METADATA_PARTITION := true
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab

# ---- Screen: 720x1576, density 280 ----
TARGET_SCREEN_WIDTH := 720
TARGET_SCREEN_HEIGHT := 1576
TW_THEME := portrait_hdpi
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
# If red and blue look swapped on screen, change the line above to BGRA_8888.
RECOVERY_GRAPHICS_USE_LINELENGTH := true

# ---- Backlight (path found on your phone) ----
TW_BRIGHTNESS_PATH := "/sys/class/leds/lcd-backlight/brightness"
TW_MAX_BRIGHTNESS := 5119
TW_DEFAULT_BRIGHTNESS := 2000
# 5119 is the real maximum, read from your phone (max_brightness).
# 2000 is about 40 percent. Change it if the screen is too dark or too bright.

# ---- TWRP options ----
TW_DEFAULT_LANGUAGE := en
TW_EXTRA_LANGUAGES := true
TW_USE_TOOLBOX := true
TW_INCLUDE_FASTBOOTD := true
RECOVERY_SDCARD_ON_DATA := true
BOARD_HAS_NO_SELECT_BUTTON := true

# ---- Phase 2 (turn on only AFTER the recovery boots and touch works) ----
# See docs/README.md, section "Phase 2: decryption".
# TW_INCLUDE_CRYPTO := true
# TW_INCLUDE_CRYPTO_FBE := true
# TW_INCLUDE_FBE_METADATA_DECRYPT := true
# PLATFORM_VERSION := 16.1.0
# PLATFORM_VERSION_LAST_STABLE := $(PLATFORM_VERSION)
# PLATFORM_SECURITY_PATCH := 2099-12-31
# VENDOR_SECURITY_PATCH := $(PLATFORM_SECURITY_PATCH)
# BOOT_SECURITY_PATCH := $(PLATFORM_SECURITY_PATCH)
