# TWRP product file for TECNO Spark 50 (KN4)
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)

# TWRP common config
$(call inherit-product, vendor/twrp/config/common.mk)

# Device config
$(call inherit-product, device/tecno/KN4/device.mk)

PRODUCT_DEVICE       := KN4
PRODUCT_NAME         := twrp_KN4
PRODUCT_BRAND        := TECNO
PRODUCT_MODEL        := TECNO KN4
PRODUCT_MANUFACTURER := TECNO
