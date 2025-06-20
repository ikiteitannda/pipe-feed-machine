#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-
#

GAMMA_MIN = 0.1
GAMMA_MAX = 10.0
CONTRAST_MIN = -50
CONTRAST_MAX = 100
UNSIGNED_INT_MAX = 0xFFFFFFFF
UNSIGNED_LONG_LONG_MAX = 0xFFFFFFFFFFFFFFFF

PIXEL_COLOR_MASK = 0xff000000
PIXEL_COLOR = 0x2000000
PIXEL_MONO = 0x1000000
PIXEL_ID_MASK = 0x0000ffff
PIXEL_BIT_MASK = 0x00ff0000

#Log type code
class GxLogTypeList:
    GX_LOG_TYPE_OFF = 0x00000000      #All types are sent \ Not sent
    GX_LOG_TYPE_FATAL = 0x00000001    #log type: fatal
    GX_LOG_TYPE_ERROR = 0x00000010    #log type: error
    GX_LOG_TYPE_WARN = 0x00000100     #log type: warn
    GX_LOG_TYPE_INFO = 0x00001000     #log type: info
    GX_LOG_TYPE_DEBUG = 0x00010000    #log type: debug
    GX_LOG_TYPE_TRACE = 0x00100000    #log type: trace

    def __int__(self):
        pass


# frame state code
class GxFrameStatusList:
    SUCCESS = 0                 # Normal frame
    INCOMPLETE = -1             # Incomplete frame
    INVALID_IMAGE_INFO = -2     # invalid image info

    def __init__(self):
        pass

#Interface type code
class GxTLClassList:
    TL_TYPE_UNKNOWN = 0         # Unknown TL type
    TL_TYPE_USB = 1             # USB TL type
    TL_TYPE_GEV = 2             # GEV TL type
    TL_TYPE_U3V = 4             # U3V TL type
    TL_TYPE_CXP = 8             # CXP TL type

    def __int__(self):
        pass

# Device type code
class GxDeviceClassList:
    UNKNOWN = 0                 # Unknown device type
    USB2 = 1                    # USB2.0 vision device
    GEV = 2                     # Gige vision device
    U3V = 3                     # USB3.0 vision device
    SMART = 4                   # Smart device
    CXP = 5						# CXP device

    def __init__(self):
        pass


class GxAccessMode:
    READONLY = 2                # Open the device in read-only mode
    CONTROL = 3                 # Open the device in controlled mode
    EXCLUSIVE = 4               # Open the device in exclusive mode

    def __init__(self):
        pass


class GxAccessStatus:
    UNKNOWN = 0                # The device's current status is unknown
    READWRITE = 1              # The device currently supports reading and writing
    READONLY = 2               # The device currently only supports reading
    NOACCESS = 3               # The device currently does neither support reading nor support writing

    def __init__(self):
        pass


class GxIPConfigureModeList:
    DHCP = 0x6                 # Enable the DHCP mode to allocate the IP address by the DHCP server
    LLA = 0x4                  # Enable the LLA mode to allocate the IP addresses
    STATIC_IP = 0x5            # Enable the static IP mode to configure the IP address
    DEFAULT = 0x7              # Enable the default mode to configure the IP address

    def __init__(self):
        pass


class GxDeviceTemperatureSelectorEntry:
    SENSOR = 1
    MAINBOARD = 2

    def __init__(self):
        pass


class GxPixelSizeEntry:
    BPP8 = 8
    BPP10 = 10
    BPP12 = 12
    BPP14 = 14
    BPP16 = 16
    BPP24 = 24
    BPP30 = 30
    BPP32 = 32
    BPP36 = 36
    BPP48 = 48
    BPP64 = 64

    def __init__(self):
        pass


class GxPixelColorFilterEntry:
    NONE = 0
    BAYER_RG = 1
    BAYER_GB = 2
    BAYER_GR = 3
    BAYER_BG = 4

    def __init__(self):
        pass


GX_PIXEL_MONO = 0x01000000
GX_PIXEL_COLOR = 0x02000000
GX_PIXEL_8BIT = 0x00080000
GX_PIXEL_10BIT = 0x000A0000
GX_PIXEL_12BIT = 0x000C0000
GX_PIXEL_14BIT = 0x000E0000
GX_PIXEL_16BIT = 0x00100000
GX_PIXEL_24BIT = 0x00180000
GX_PIXEL_30BIT = 0x001E0000
GX_PIXEL_32BIT = 0x00200000
GX_PIXEL_36BIT = 0x00240000
GX_PIXEL_48BIT = 0x00300000
GX_PIXEL_64BIT = 0x00400000
GX_PIXEL_96BIT = 0x00600000

class GxPixelFormatEntry:
    UNDEFINED = 0
    MONO8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x0001)  # 0x1080001
    MONO8_SIGNED = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x0002)  # 0x1080002
    MONO10 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0003)  # 0x1100003
    MONO10_P = (GX_PIXEL_MONO  | GX_PIXEL_10BIT | 0x0046)  # 0x010A0046
    MONO12 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0005)  # 0x1100005
    MONO12_P = (GX_PIXEL_MONO  | GX_PIXEL_12BIT | 0x0047)  # 0x010C0047
    MONO14 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0025)  # 0x1100025
    MONO14_P = (GX_PIXEL_MONO  | GX_PIXEL_14BIT | 0x0104)  # 0x010E0104
    MONO16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0007)  # 0x1100007
    BAYER_GR8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x0008)  # 0x1080008
    BAYER_RG8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x0009)  # 0x1080009
    BAYER_GB8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x000A)  # 0x108000A
    BAYER_BG8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x000B)  # 0x108000B
    BAYER_GR10 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x000C)  # 0x110000C
    BAYER_GR10_P = (GX_PIXEL_MONO  | GX_PIXEL_10BIT | 0x0056)  # 0x010A0056
    BAYER_RG10 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x000D)  # 0x110000D
    BAYER_RG10_P = (GX_PIXEL_MONO  | GX_PIXEL_10BIT | 0x0058) # 0x010A0058
    BAYER_GB10 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x000E)  # 0x110000E
    BAYER_GB10_P = (GX_PIXEL_MONO  | GX_PIXEL_10BIT | 0x0054)  # 0x010A0054
    BAYER_BG10 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x000F)  # 0x110000F
    BAYER_BG10_P = (GX_PIXEL_MONO  | GX_PIXEL_10BIT | 0x0052)  # 0x010A0052
    BAYER_GR12 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0010)  # 0x1100010
    BAYER_GR12_P = (GX_PIXEL_MONO  | GX_PIXEL_12BIT | 0x0057)  # 0x010C0057
    BAYER_RG12 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0011)  # 0x1100011
    BAYER_RG12_P = (GX_PIXEL_MONO  | GX_PIXEL_12BIT | 0x0059)  # 0x010C0059
    BAYER_GB12 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0012)  # 0x1100012
    BAYER_GB12_P = (GX_PIXEL_MONO  | GX_PIXEL_12BIT | 0x0055)  # 0x010C0055
    BAYER_BG12 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0013)  # 0x1100013
    BAYER_BG12_P = (GX_PIXEL_MONO  | GX_PIXEL_12BIT | 0x0053)  # 0x010C0053
    BAYER_GR14 = (GX_PIXEL_MONO  | GX_PIXEL_16BIT | 0x0109)  # 0x01100109 
    BAYER_GR14_P = (GX_PIXEL_MONO  | GX_PIXEL_14BIT | 0x0105)  # 0x010E0105
    BAYER_RG14 = (GX_PIXEL_MONO  | GX_PIXEL_16BIT | 0x010A)  # 0x0110010A
    BAYER_RG14_P = (GX_PIXEL_MONO  | GX_PIXEL_14BIT | 0x0106)  # 0x010E0106
    BAYER_GB14 = (GX_PIXEL_MONO  | GX_PIXEL_16BIT | 0x010B)  # 0x0110010B
    BAYER_GB14_P = (GX_PIXEL_MONO  | GX_PIXEL_14BIT | 0x0107)  # 0x010E0107
    BAYER_BG14 = (GX_PIXEL_MONO  | GX_PIXEL_16BIT | 0x010C)  # 0x0110010C
    BAYER_BG14_P = (GX_PIXEL_MONO  | GX_PIXEL_14BIT | 0x0108)  # 0x010E0108
    BAYER_GR16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x002E)  # 0x110002E
    BAYER_RG16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x002F)  # 0x110002F
    BAYER_GB16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0030)  # 0x1100030
    BAYER_BG16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x0031)  # 0x1100031
    RGB8_PLANAR = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x0021)  # 0x2180021
    RGB10_PLANAR = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x0022)  # 0x2300022
    RGB12_PLANAR = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x0023)  # 0x2300023
    RGB16_PLANAR = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x0024)  # 0x2300024
    RGB8 = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x0014)  # 0x2180014
    RGB10 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x0018)  # 0x2300018
    RGB12 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x001A)  # 0x230001A 
    RGB14 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x005E)  # 0x230005E
    RGB16 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x0033)  # 0x2300033
    BGR8 = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x0015)  # 0x2180015
    BGR10 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x0019)  # 0x2300019
    BGR12 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x001B)  # 0x230001B
    BGR14 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x004A)  # 0x230004A
    BGR16 = (GX_PIXEL_COLOR | GX_PIXEL_48BIT | 0x004B)  # 0x230004B   
    RGBA8 = (GX_PIXEL_COLOR | GX_PIXEL_32BIT | 0x0016)  # 0x2200016  
    BGRA8 = (GX_PIXEL_COLOR | GX_PIXEL_32BIT | 0x0017)  # 0x2200017
    ARGB8 = (GX_PIXEL_COLOR | GX_PIXEL_32BIT | 0x0018)  # 0x2200018
    ABGR8 = (GX_PIXEL_COLOR | GX_PIXEL_32BIT | 0x0019)  # 0x2200019
    R8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x00C9)  # 0x010800C9
    G8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x00CD)  # 0x010800CD
    B8 = (GX_PIXEL_MONO | GX_PIXEL_8BIT | 0x00D1)  # 0x010800D1
    COORD3D_ABC32F = (GX_PIXEL_COLOR | GX_PIXEL_96BIT | 0X00C0)  # 0x021800C0
    COORD3D_ABC32F_PLANAR = (GX_PIXEL_COLOR | GX_PIXEL_96BIT | 0X00C1)  # 0x021800C1
    COORD3D_C16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0x00B8)  # 0x011000B8
    COORD3D_C16I16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0xFF02)  # 0x0110FF02 custom 3d pixel foramt
    COORD3D_C16S16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0xFF03)  # 0x0110FF03 custom 3d pixel foramt
    COORD3D_C16I16S16 = (GX_PIXEL_MONO | GX_PIXEL_16BIT | 0xFF04)  # 0x0110FF04 custom 3d pixel foramt
    YUV444_8 = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x0020)  # 0x2180020
    YUV422_8 = (GX_PIXEL_COLOR | GX_PIXEL_16BIT | 0x0032)  # 0x2100032
    YUV422_8_UYVY = (GX_PIXEL_COLOR | GX_PIXEL_16BIT | 0x001F)  # 0x210001F
    YUV411_8 = (GX_PIXEL_COLOR | GX_PIXEL_12BIT | 0x001E)  # 0x20C001E
    YUV420_8_PLANAR = (GX_PIXEL_COLOR | GX_PIXEL_12BIT | 0x0040)  # 0x20C0040
    YCBCR444_8 = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x005B)  # 0x218005B
    YCBCR422_8 = (GX_PIXEL_COLOR | GX_PIXEL_16BIT | 0x003B)  # 0x210003B
    YCBCR411_8 = (GX_PIXEL_COLOR | GX_PIXEL_12BIT | 0x005A)  # 0x20C005A
    YCBCR601_444_8 = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x003D)  # 0x218003D
    YCBCR601_422_8 = (GX_PIXEL_COLOR | GX_PIXEL_16BIT | 0x003E)  # 0x210003E
    YCBCR601_411_8 = (GX_PIXEL_COLOR | GX_PIXEL_12BIT | 0x003F)  # 0x20C003F
    YCBCR709_444_8 = (GX_PIXEL_COLOR | GX_PIXEL_24BIT | 0x0040)  # 0x2180040
    YCBCR709_422_8 = (GX_PIXEL_COLOR | GX_PIXEL_16BIT | 0x0041)  # 0x2100041
    YCBCR709_411_8 = (GX_PIXEL_COLOR | GX_PIXEL_12BIT | 0x0042)  # 0x20C0042
    MONO10_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x0004)  # 0x010C0004
    MONO12_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x0006)  # 0x010C0006
    BAYER_BG10_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x0029)  # 0x010C0029
    BAYER_BG12_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x002D)  # 0x010C002D
    BAYER_GB10_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x0028)  # 0x010C0028
    BAYER_GB12_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x002C)  # 0x010C002C
    BAYER_GR10_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x0026)  # 0x010C0026
    BAYER_GR12_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x002A)  # 0x010C002A
    BAYER_RG10_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x0027)  # 0x010C0027
    BAYER_RG12_PACKED = (GX_PIXEL_MONO | GX_PIXEL_12BIT | 0x002B)  # 0x010C002B  
    def __init__(self):
        pass


class GxTestPatternEntry:
    OFF = 0
    GRAY_FRAME_RAMP_MOVING = 1
    SLANT_LINE_MOVING = 2
    VERTICAL_LINE_MOVING = 3
    HORIZONTAL_LINE_MOVING = 4
    GREY_VERTICAL_RAMP = 5
    SLANT_LINE = 6

    def __init__(self):
        pass


class GxTestPatternGeneratorSelectorEntry:
    SENSOR = 0          # Sensor test pattern
    REGION0 = 1         # FPGA test pattern

    def __init__(self):
        pass


class GxRegionSendModeEntry:
    SINGLE_ROI = 0
    MULTI_ROI = 1

    def __init__(self):
        pass


class GxRegionSelectorEntry:
    REGION0 = 0
    REGION1 = 1
    REGION2 = 2
    REGION3 = 3
    REGION4 = 4
    REGION5 = 5
    REGION6 = 6
    REGION7 = 7

    def __init__(self):
        pass


class GxBinningHorizontalModeEntry:
    SUM = 0
    AVERAGE = 1

    def __init__(self):
        pass


class GxBinningVerticalModeEntry:
    SUM = 0
    AVERAGE = 1

    def __init__(self):
        pass


class GxSensorShutterModeEntry:
    GLOBAL = 0              # All pixels are exposed simultaneously with same exposure time
    ROLLING = 1             # All pixels have the same exposure time, but exposure start at different time
    GLOBALRESET = 2         # All pixels start exposure at same time, but exposure time are different

    def __init__(self):
        pass


class GxAcquisitionModeEntry:
    SINGLE_FRAME = 0
    MULITI_FRAME = 1
    CONTINUOUS = 2

    def __init__(self):
        pass


class GxTriggerActivationEntry:
    FALLINGEDGE = 0
    RISINGEDGE = 1
    ANYEDGE = 2
    LEVELHIGH = 3
    LEVELLOW = 4

    def __init__(self):
        pass


class GxTriggerSourceEntry:
    SOFTWARE = 0
    LINE0 = 1
    LINE1 = 2
    LINE2 = 3
    LINE3 = 4
    COUNTER2END = 5
    TRIGGER = 6
    MULTISOURCE = 7
    CXPTRIGGER0 = 8
    CXPTRIGGER1 = 9

    def __init__(self):
        pass


class GxExposureModeEntry:
    TIMED = 1
    TRIGGER_WIDTH = 2

    def __init__(self):
        pass


class GxTriggerSelectorEntry:
    FRAME_START = 1
    FRAME_BURST_START = 2

    def __init__(self):
        pass


class GxTransferControlModeEntry:
    BASIC = 0
    USER_CONTROLED = 1

    def __init__(self):
        pass


class GxTransferOperationModeEntry:
    MULTI_BLOCK = 0

    def __init__(self):
        pass


class GxAcquisitionStatusSelectorEntry:
    ACQUISITION_TRIGGER_WAIT = 0
    FRAME_TRIGGER_WAIT = 1

    def __init__(self):
        pass


class GxExposureTimeModeEntry:
    ULTRASHORT = 0
    STANDARD = 1

    def __init__(self):
        pass


class GxUserOutputSelectorEntry:
    OUTPUT0 = 1
    OUTPUT1 = 2
    OUTPUT2 = 4
    OUTPUT3 = 5
    OUTPUT4 = 6
    OUTPUT5 = 7
    OUTPUT6 = 8

    def __init__(self):
        pass


class GxUserOutputModeEntry:
    STROBE = 0
    USER_DEFINED = 1

    def __init__(self):
        pass


class GxLineSelectorEntry:
    LINE0 = 0
    LINE1 = 1
    LINE2 = 2
    LINE3 = 3
    LINE4 = 4
    LINE5 = 5
    LINE6 = 6
    LINE7 = 7
    LINE8 = 8
    LINE9 = 9
    LINE10 = 10
    LINE_STROBE = 11
    LINE11 = 12
    LINE12 = 13
    LINE13 = 14
    LINE14 = 15
    TRIGGER = 16
    IO1 = 17
    IO2 = 18
    FLASH_P = 19
    FLASH_W = 20

    def __init__(self):
        pass
class GxDeviceSerialPortBaudRateEntry:
    Baud9600 = 5
    Baud19200 = 6
    Baud38400 = 7
    Baud76800 = 8
    Baud115200 = 9

    def __init__(self):
        pass

class GxSerialPortStopBitsEntry:
    Bits1 = 0
    Bits1AndAHalf = 1
    Bits2 = 2

    def __init__(self):
        pass


class GxLineModeEntry:
    INPUT = 0
    OUTPUT = 1

    def __init__(self):
        pass


class GxLineSourceEntry:
    OFF = 0
    STROBE = 1
    USER_OUTPUT0 = 2
    USER_OUTPUT1 = 3
    USER_OUTPUT2 = 4
    EXPOSURE_ACTIVE = 5
    FRAME_TRIGGER_WAIT = 6
    ACQUISITION_TRIGGER_WAIT = 7
    TIMER1_ACTIVE = 8
    USER_OUTPUT3 = 9
    USER_OUTPUT4 = 10
    USER_OUTPUT5 = 11
    USER_OUTPUT6 = 12
    TIMER2_ACTIVE = 13
    TIMER3_ACTIVE = 14
    FRAME_TRIGGER = 15
    Flash_W = 16
    Flash_P = 17
    SERIAL_PORT_0 = 18

    def __init__(self):
        pass


class GxGainSelectorEntry:
    ALL = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    DIGITAL_ALL = 4

    def __init__(self):
        pass


class GxBlackLevelSelectEntry:
    ALL = 0
    RED = 1
    GREEN = 2
    BLUE = 3

    def __init__(self):
        pass


class GxBalanceRatioSelectorEntry:
    RED = 0
    GREEN = 1
    BLUE = 2

    def __init__(self):
        pass


class GxGammaModeEntry:
    SRGB = 0
    USER = 1

    def __init__(self):
        pass


class GxLightSourcePresetEntry:
    OFF = 0
    CUSTOM = 1
    DAYLIGHT_6500K = 2
    DAYLIGHT_5000K = 3
    COOL_WHITE_FLUORESCENCE = 4
    INCA = 5

    def __init__(self):
        pass


class GxAALightEnvironmentEntry:
    NATURE_LIGHT = 0
    AC50HZ = 1
    AC60HZ = 2

    def __init__(self):
        pass


class GxAWBLampHouseEntry:
    ADAPTIVE = 0
    D65 = 1
    FLUORESCENCE = 2
    INCANDESCENT = 3
    D75 = 4
    D50 = 5
    U30 = 6

    def __init__(self):
        pass


class GxUserDataFieldSelectorEntry:
    FIELD_0 = 0
    FIELD_1 = 1
    FIELD_2 = 2
    FIELD_3 = 3

    def __init__(self):
        pass


class GxUserSetEntry:
    DEFAULT = 0
    USER_SET0 = 1
    USER_SET1 = 2

    def __init__(self):
        pass


class GxEventSelectorEntry:
    EXPOSURE_END = 0x0004
    BLOCK_DISCARD = 0x9000
    EVENT_OVERRUN = 0x9001
    FRAME_START_OVER_TRIGGER = 0x9002
    BLOCK_NOT_EMPTY = 0x9003
    INTERNAL_ERROR = 0x9004
    FRAME_BURST_START_OVERTRIGGER = 0x9005
    FRAME_START_WAIT = 0x9006
    FRAME_BURST_START_WAIT = 0x9007

    def __init__(self):
        pass


class GxLutSelectorEntry:
    LUMINANCE = 0

    def __init__(self):
        pass


class GxChunkSelectorEntry:
    FRAME_ID = 1
    TIME_STAMP = 2
    COUNTER_VALUE = 3

    def __init__(self):
        pass


class GxColorTransformationModeEntry:
    RGB_TO_RGB = 0
    USER = 1

    def __init__(self):
        pass


class GxColorTransformationValueSelectorEntry:
    GAIN00 = 0
    GAIN01 = 1
    GAIN02 = 2
    GAIN10 = 3
    GAIN11 = 4
    GAIN12 = 5
    GAIN20 = 6
    GAIN21 = 7
    GAIN22 = 8

    def __init__(self):
        pass


class GxResetDeviceModeEntry:
    RECONNECT = 1
    RESET = 2

    def __init__(self):
        pass


class GxTimerSelectorEntry:
    TIMER1 = 1         

    def __init__(self):
        pass


class GxTimerTriggerSourceEntry:
    EXPOSURE_START = 1
    LINE10 = 10
    LINE14 = 14
    STROBE = 16

    def __init__(self):
        pass


class GxCounterSelectorEntry:
    COUNTER1 = 1
    COUNTER2 = 2

    def __init__(self):
        pass


class GxCounterEventSourceEntry:
    FRAME_START = 1
    FRAME_TRIGGER = 2
    ACQUISITION_TRIGGER = 3
    OFF = 4
    SOFTWARE = 5
    LINE0 = 6
    LINE1 = 7
    LINE2 = 8
    LINE3 = 9

    def __init__(self):
        pass


class GxCounterResetSourceEntry:
    OFF = 0
    SOFTWARE = 1
    LINE0 = 2
    LINE1 = 3
    LINE2 = 4
    LINE3 = 5
    COUNTER2END = 6
    CXPTRIGGER0 = 8
    CXPTRIGGER1 = 9


    def __init__(self):
        pass


class GxCounterResetActivationEntry:
    RISINGEDGE = 1

    def __init__(self):
        pass


class GxCounterTriggerSourceEntry:
    OFF = 0
    SOFTWARE = 1
    LINE0 = 2
    LINE1 = 3
    LINE2 = 4
    LINE3 = 5

    def __init__(self):
        pass


class GxTimerTriggerActivationEntry:
    RISINGEDGE = 0

    def __init__(self):
        pass


class GxStopAcquisitionModeEntry:
    GENERAL = 0
    LIGHT = 1

    def __init__(self):
        pass


class GxDSStreamBufferHandlingModeEntry:
    OLDEST_FIRST = 1
    OLDEST_FIRST_OVERWRITE = 2
    NEWEST_ONLY = 3

    def __init__(self):
        pass


class GxAutoEntry:
    OFF = 0
    CONTINUOUS = 1
    ONCE = 2

    def __init__(self):
        pass


class GxSwitchEntry:
    OFF = 0
    ON = 1

    def __init__(self):
        pass

class GxSensorBitDepthEntry:
    BPP8 = 8
    BPP10 = 10
    BPP12 = 12

    def __init__(self):
        pass

class GxMultisourceSelectorEntry:
    Software = 0
    LINE0 = 1
    LINE2 = 3
    LINE3 = 4

    def __init__(self):
        pass

class GxDeviceTapGeometryEntry:
    GEOMETRY_1X_1Y = 0
    GEOMETRY1_X1_Y2 = 19
    GEOMETRY1_X2_YE = 10

    def __init__(self):
        pass

class GxEncoderSelectorEntry:
    ENCODER0 = 0
    ENCODER1 = 1
    ENCODER2 = 1

    def __init__(self):
        pass

class GxEncoderSourceAEntry:
    OFF = 0
    LINE0 = 1
    LINE1 = 2
    LINE2 = 3
    LINE3 = 4
    LINE4 = 5
    LINE5 = 6

    def __init__(self):
        pass

class GxEncoderSourceBEntry:
    OFF = 0
    LINE0 = 1
    LINE1 = 2
    LINE2 = 3
    LINE3 = 4
    LINE4 = 5
    LINE5 = 6

    def __init__(self):
        pass

class GxEncoderModeEntry:
    HIGH_RESOLUTION = 0

    def __init__(self):
        pass

class GxEncoderDirectionEntry:
    FORWARD = 0
    BACKWARD = 1

    def __init__(self):
        pass

class GxShadingCorrectionModeEntry:
    FLAT_FIELD_CORRECTION = 0
    PARALLAX_CORRECTION = 1
    TAILOR_FLAT_FIELD_CORRECTION = 2
    DEVICE_FLAT_FIELD_CORRECTION = 3

    def __init__(self):
        pass

class GxFFCGenerateStatusEntry:
    IDLE = 0
    WAITING_IMAGE = 1
    FINISH = 2

    def __init__(self):
        pass

class GxFFCCoefficientEntry:
    SET0 = 0
    SET1 = 1
    SET2 = 2
    SET3 = 3
    SET4 = 4
    SET5 = 5
    SET6 = 6
    SET7 = 7
    SET8 = 8
    SET9 = 9
    SET10 = 10
    SET11 = 11
    SET12 = 12
    SET13 = 13
    SET14 = 14
    SET15 = 15

    def __init__(self):
        pass

class GxDSNUSelectorEntry:
    DEFAULT = 0
    SET0 = 1
    SET1 = 2
    SET2 = 3
    SET3 = 4
    SET4 = 5
    SET5 = 6
    SET6 = 7
    SET7 = 8
    SET8 = 9
    SET9 = 10
    SET10 = 11
    SET11 = 12
    SET12 = 13
    SET13 = 14
    SET14 = 15
    SET15 = 16

    def __init__(self):
        pass

class GxDSNUGenerateStatusEntry:
    IDLE = 0
    WAITING_IMAGE = 1
    FINISH = 2

    def __init__(self):
        pass

class GxPRNUSelectorEntry:
    DEFAULT = 0
    SET0 = 1
    SET1 = 2
    SET2 = 3
    SET3 = 4
    SET4 = 5
    SET5 = 6
    SET6 = 7
    SET7 = 8
    SET8 = 9
    SET9 = 10
    SET10 = 11
    SET11 = 12
    SET12 = 13
    SET13 = 14
    SET14 = 15
    SET15 = 16

    def __init__(self):
        pass

class GxPRNUGenerateStatusEntry:
    IDLE = 0
    WAITING_IMAGE = 1
    FINISH = 2

    def __init__(self):
        pass

class GxCXPLinkConfigurationEntry:
    CXP6_X1 = 0x00010048
    CXP12_X1 = 0x00010058
    CXP6_X2 = 0x00020048
    CXP12_X2 = 0x00020058
    CXP6_X4 = 0x00040048
    CXP12_X4 = 0x00040058
    CXP3_X1 = 0x00010038
    CXP3_X2 = 0x00020038
    CXP3_X4 = 0x00040038

    def __init__(self):
        pass

class GxCXPLinkConfigurationPreferredEntry:
    CXP12_X4 = 0x00040058

    def __init__(self):
        pass

class GxCXPLinkConfigurationStatusEntry:
    CXP6_X1 = 0x00010048
    CXP12_X1 = 0x00010058
    CXP6_X2 = 0x00020048
    CXP12_X2 = 0x00020058
    CXP6_X4 = 0x00040048
    CXP12_X4 = 0x00040058
    CXP3_X1 = 0x00010038
    CXP3_X2 = 0x00020038
    CXP3_X4 = 0x00040038

    def __init__(self):
        pass

class GxCXPConectionSelectorEntry:
    SELECTOR0 = 0
    SELECTOR1 = 1
    SELECTOR2 = 2
    SELECTOR3 = 3

    def __init__(self):
        pass

class GxCXPConectionTestModeEntry:
    OFF = 0
    MODE1 = 1

    def __init__(self):
        pass

class GxSequencerFratureSelectorEntry:
    FLAT_FIELD_CORRECTION = 0

    def __init__(self):
        pass

class GxSequencerTriggerSourceEntry:
    FRAME_START = 7

    def __init__(self):
        pass

class GxTimerSelectorEntry:
    TIMER1 = 1
    TIMER2 = 2
    TIMER3 = 3

    def __init__(self):
        pass

class GxTimerTriggerSourceEntry:
    EXPOSURE_START = 1
    LINE10 = 10
    LINE14 = 14
    STROBE = 16

    def __init__(self):
        pass

class GxDeviceTemperatureSelectorEntry:
    SENSOR = 1
    MAINBOARD = 2

    def __init__(self):
        pass

class GxNoiseReductionModeEntry:
    OFF = 0
    LOW = 1
    MIDDLE = 2
    HIGH = 3

    def __init__(self):
        pass

class GxHDRModeEntry:
    OFF = 0
    CONTINUOUS = 1

    def __init__(self):
        pass

class GxMGCModeEntry:
    OFF = 0
    TWO_FRAME = 1
    FOUR_FRAME = 2

    def __init__(self):
        pass

class GxAcquisitionBurstModeEntry:
    STANDARD = 0
    HIGH_SPEED  = 1

    def __init__(self):
        pass

class GxSensorSelectorEntry:
    CMOS1 = 0
    CCD1 = 1

    def __init__(self):
        pass

class GxIMUConfigAccRangeEntry:
    ACC_16G = 2
    ACC_8G = 3
    ACC_4G = 4
    ACC_2G = 5

    def __init__(self):
        pass

class GxIMUConfigAccOdrEntry:
    ODR_1000HZ = 0
    ODR_500HZ = 1
    ODR_250HZ = 2
    ODR_125HZ = 3
    ODR_63HZ = 4
    ODR_31HZ = 5
    ODR_16HZ = 6
    ODR_2000HZ = 8
    ODR_4000HZ = 9
    ODR_8000HZ = 10

    def __init__(self):
        pass

class GxIMUConfigAccOdrLowPassFilterFrequencyEntry:
    ODR040 = 0
    ODR025 = 1
    ODR011 = 2
    ODR004 = 3
    ODR002 = 4

    def __init__(self):
        pass

class GxIMUConfigGyroRangeEntry:
    RANGE_125DPS = 2
    RANGE_250DPS = 3
    RANGE_500DPS = 4
    RANGE_1000DPS = 5
    RANGE_2000DPS = 6

    def __init__(self):
        pass

class GxIMUConfigGyroOdrEntry:
    ODR_1000HZ = 0
    ODR_500HZ = 1
    ODR_250HZ = 2
    ODR_125HZ = 3
    ODR_63HZ = 4
    ODR_31HZ = 5
    ODR_4KHZ = 9
    ODR_8KHZ = 10
    ODR_16KHZ = 11
    ODR_32KHZ = 12

    def __init__(self):
        pass

class GxIMUConfigGyroOdrLowPassFilterFrequencyEntry:
    GYROLPF2000HZ = 2000
    GYROLPF1600HZ = 1600
    GYROLPF1525HZ = 1525
    GYROLPF1313HZ = 1313
    GYROLPF1138HZ = 1138
    GYROLPF1000HZ = 1000
    GYROLPF863HZ = 863
    GYROLPF638HZ = 638
    GYROLPF438HZ = 438
    GYROLPF313HZ = 313
    GYROLPF213HZ = 213
    GYROLPF219HZ = 219
    GYROLPF363HZ = 363
    GYROLPF320HZ = 320
    GYROLPF250HZ = 250
    GYROLPF200HZ = 200
    GYROLPF181HZ = 181
    GYROLPF160HZ = 160
    GYROLPF125HZ = 125
    GYROLPF100HZ = 100
    GYROLPF90HZ = 90
    GYROLPF80HZ = 80
    GYROLPF63HZ = 63
    GYROLPF50HZ = 50
    GYROLPF45HZ = 45
    GYROLPF40HZ = 40
    GYROLPF31HZ = 31
    GYROLPF25HZ = 25
    GYROLPF23HZ = 23
    GYROLPF20HZ = 20
    GYROLPF15HZ = 15
    GYROLPF13HZ = 13
    GYROLPF11HZ = 11
    GYROLPF10HZ = 10
    GYROLPF8HZ = 8
    GYROLPF6HZ = 6

    def __init__(self):
        pass

class GxIMUTemperatureOdrEntry:
    ODR_500HZ = 0
    ODR_250HZ = 1
    ODR_125HZ = 2
    ODR_63HZ = 3

    def __init__(self):
        pass

class GxSerialportSelectorEntry:
    SERIALPOR0 = 0

    def __init__(self):
        pass

class GxSerialportSourceEntry:
    OFF = 0
    LINE0 = 1
    LINE1 = 2
    LINE2 = 3
    LINE3 = 4

    def __init__(self):
        pass

class GxSerialportBaundrateEntry:
    BAUNDRATE_9600 = 5
    BAUNDRATE_19200 = 6
    BAUNDRATE_38400 = 7
    BAUNDRATE_76800 = 8
    BAUNDRATE_115200 = 9

    def __init__(self):
        pass

class GxSerialporeStopBitsEntry:
    ONE = 0
    ONEANDHALF = 1
    TWO = 2

    def __init__(self):
        pass

class GxSerialportParityEntry:
    NONE = 0
    ODD = 1
    EVEN = 2
    MARK = 3
    SPACE = 4

    def __init__(self):
        pass

# image interpolation method
class DxBayerConvertType:
    NEIGHBOUR = 0                           # Neighborhood average interpolation algorithm
    ADAPTIVE = 1                            # Edge adaptive interpolation algorithm
    NEIGHBOUR3 = 2                          # The neighborhood average interpolation algorithm for a larger region

    def __init__(self):
        pass


# image valid bit
class DxValidBit:
    BIT0_7 = 0              # bit 0~7
    BIT1_8 = 1              # bit 1~8
    BIT2_9 = 2              # bit 2~9
    BIT3_10 = 3             # bit 3~10
    BIT4_11 = 4             # bit 4~11
    BIT5_12 = 5            # bit 5~12
    BIT6_13 = 6            # bit 6~13
    BIT7_14 = 7            # bit 7~14
    BIT8_15 = 8            # bit 8~15

    def __init__(self):
        pass

class GxNodeNameSpaceList:
    NAMESPACE_CUSTOM                                            = 0             # name resides in custom namespace
    NAMESPACE_STANDARD                                        = 1             # name resides in one of the standard namespaces
    NAMESPACE_UNDEFINEDNAMESPACE                = 2             # Object is not yet initialized

    def __init__(self):
        pass

class GxNodeVisibilityList:
    VISIBILITY_BEGINNER                                                  = 0            # Always visible
    VISIBILITY_EXPERT                                                       = 1            # Visible for experts or Gurus
    VISIBILITY_GURU                                                         = 2            # Visible for Gurus
    VISIBILITY_INVISIBLE                                                   = 3             # Not Visible
    VISIBILITY_UNDEFINEDVISIBILITY                              = 99          # Object is not yet initialized

    def __init__(self):
        pass

class GxNodeStreamableList:
    STREAMABLE_NO                                                        = 0            # node is not streamable
    STREAMABLE_YES                                                        = 1            # node is streamable
    STREAMABLE_UNDEFINEDYESNO                             = 2            # Object is not yet initialized

    def __init__(self):
        pass

class GxNodeCachableList:
    CACHABLE_NOCACHE                                                  = 0            # Do not use cache
    CACHABLE_WRITETHROUGH                                       = 1            # Write to cache and register
    CACHABLE_WRITEAROUND                                          = 2            # Write to register, write to cache on read
    CACHABLE_UNDEFINEDCACHINGMODE                    = 3             # Object is not yet initialized

    def __init__(self):
        pass

# image mirror method
class DxImageMirrorMode:
    HORIZONTAL_MIRROR = 0                               # Horizontal mirror
    VERTICAL_MIRROR = 1                                 # Vertical mirror

    def __init__(self):
        pass


# RGB channel order
class DxRGBChannelOrder:
    ORDER_RGB = 0
    ORDER_BGR = 1

    def __init__(self):
        pass

# Image Info
class GxImageInfo:
    image_width = 0
    image_height = 0
    image_buf = None
    image_pixel_format = GxPixelFormatEntry.UNDEFINED

    def __init__(self):
        pass

