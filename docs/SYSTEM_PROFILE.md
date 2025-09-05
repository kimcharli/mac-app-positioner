# System Profile Documentation

This document provides system configuration information for the Mac App Positioner.

## Current Monitor Configuration

**Generated on:** 2025-09-05  
**Command:** `system_profiler SPDisplaysDataType`

### Hardware Overview
- **GPU:** Apple M2 Pro (19 cores)
- **Metal Support:** Metal 3
- **Total Displays:** 3 (1 built-in + 2 external)

### Display Configuration

#### 1. Built-in Display (Main)
- **Model:** Apple Liquid Retina XDR Display
- **Type:** Built-in Color LCD
- **Resolution:** 3456 x 2234 Retina
- **Status:** Main Display, Online
- **Features:** Auto-brightness adjustment
- **Connection:** Internal

#### 2. External Monitor 1
- **Model:** LEN P24h-20 (Lenovo)
- **Resolution:** 2560 x 1440 (QHD/WQHD)
- **Refresh Rate:** 75Hz
- **Status:** Online, Not mirrored
- **Features:** Rotation supported

#### 3. External Monitor 2  
- **Model:** T34w-30 (Ultra-wide)
- **Resolution:** 3440 x 1440 (UWQHD)
- **Refresh Rate:** 60Hz
- **Status:** Online, Not mirrored
- **Features:** Rotation supported

### Monitor Layout Notes

All displays are configured in extended desktop mode (no mirroring). This triple-monitor setup provides:
- **Total pixel width:** ~9,456 pixels (3456 + 2560 + 3440)
- **Mixed DPI:** Retina built-in + standard external displays
- **Aspect ratios:** 16:10 (built-in), 16:9 (LEN), 21:9 (ultra-wide)

### Usage with Mac App Positioner

This configuration should be defined in `config.yaml` to enable automatic application positioning across all three displays.