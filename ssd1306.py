# Simple SSD1306 driver (MicroPython)

from micropython import const
import framebuf

# commands
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xA4)
SET_NORM_INV        = const(0xA6)
SET_DISP            = const(0xAE)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xA0)
SET_MUX_RATIO       = const(0xA8)
SET_COM_OUT_DIR     = const(0xC0)
SET_DISP_OFFSET     = const(0xD3)
SET_COM_PIN_CFG     = const(0xDA)
SET_DISP_CLK_DIV    = const(0xD5)
SET_PRE_CHARGE      = const(0xD9)
SET_VCOM_DESEL      = const(0xDB)
SET_CHARGE_PUMP     = const(0x8D)

class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP,
            SET_MEM_ADDR, 0x00,
            SET_DISP_START_LINE,
            SET_SEG_REMAP | 0x1,
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x8,
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x12,
            SET_DISP_CLK_DIV, 0x80,
            SET_PRE_CHARGE, 0xF1 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL, 0x40,
            SET_CONTRAST, 0x7F,
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_CHARGE_PUMP, 0x14 if not self.external_vcc else 0x10,
            SET_DISP | 0x01
        ):
            self.write_cmd(cmd)

    def poweroff(self):
        self.write_cmd(SET_DISP)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.width - 1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_framebuf()

    def fill(self, color):
        self.framebuf.fill(color)

    def pixel(self, x, y, color):
        self.framebuf.pixel(x, y, color)

    def text(self, string, x, y):
        self.framebuf.text(string, x, y)

    # Subclasses must provide these
    def write_cmd(self, cmd):
        raise NotImplementedError

    def write_framebuf(self):
        raise NotImplementedError

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        # DC = 0 for commands
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def write_framebuf(self):
        # Data prefix = 0x40
        self.i2c.writeto(self.addr, bytearray([0x40]) + self.buffer)