"""Seven Swords Wedge keyboard PCB: single source of truth for parts and nets.

Original SSP design. The RP2040 support circuit (flash, crystal, decoupling,
USB series resistors, BOOT/RUN) follows Raspberry Pi's MIT-licensed
"Minimal RP2040 board" reference design (Raspberry Pi Ltd).
See ../NOTICE.md.
"""
ROWS, COLS = 4, 12
PITCH = 19.05

# ---- GPIO map (keep in sync with firmware/keyboard.toml) ----
COL_GPIO = list(range(0, 12))       # COL0..COL11 -> GPIO0..GPIO11
ROW_GPIO = [12, 13, 14, 15]         # ROW0..ROW3  -> GPIO12..GPIO15
ENC_A_GPIO, ENC_B_GPIO = 16, 17
ENC_ROW_GPIO = 18                   # ROW4: encoder push sits in the matrix at (4, 11)

FP = {
    "R": "Resistor_SMD:R_0402_1005Metric",
    "C": "Capacitor_SMD:C_0402_1005Metric",
    "C10u": "Capacitor_SMD:C_0805_2012Metric",
    "D": "Diode_SMD:D_SOD-123",
    "MCU": "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm",
    "FLASH": "Package_SO:SOIC-8_5.3x5.3mm_P1.27mm",
    "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
    "USB": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
    "ESD": "Package_TO_SOT_SMD:SOT-23-6",
    "LDO": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
    "ENC": "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm",
    "BTN": "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A",
    "KEY": "SSP_Wedge:SW_MX_Hotswap_Kailh_1.00u",
    "HOLE": "MountingHole:MountingHole_2.2mm_M2",
    "SWD": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
}

# LCSC numbers are candidates; verify each one on lcsc.com before any order.
LCSC = {
    "RP2040": "C2040", "W25Q128JVSIQ": "C97521", "AMS1117-3.3": "C6186",
    "USBLC6-2SC6": "C7519", "TYPE-C-31-M-12": "C165948", "1N4148W": "C81598",
    "12MHz": "C9002", "100nF": "C1525", "1uF": "C52923", "10uF": "C15850",
    "33pF": "C1562", "27R": "C25100", "1k": "C11702", "10k": "C25744",
    "5.1k": "C25905", "TS-1187A": "C318884", "EC11": "C370970", "Kailh-MX-socket": "C5156480",
}

parts = []  # dicts: ref, lib, value, fp, lcsc, pins{pin:net}, side, dnp


def add(ref, lib, value, fp, pins, lcsc="", side="top", dnp=False, bom=True):
    parts.append(dict(ref=ref, lib=lib, value=value, fp=FP[fp], lcsc=lcsc, pins=pins,
                      side=side, dnp=dnp, bom=bom))


def R(ref, val, a, b):
    add(ref, "Device:R", val, "R", {"1": a, "2": b}, LCSC[val])


def C(ref, val, a, b="GND"):
    add(ref, "Device:C", val, "C10u" if val == "10uF" else "C", {"1": a, "2": b}, LCSC[val])


def build():
    parts.clear()
    # ---------------- MCU ----------------
    mcu = {"57": "GND", "26": "RUN", "47": "USB_DP", "46": "USB_DM",
           "56": "QSPI_SS", "53": "QSPI_SD0", "55": "QSPI_SD1", "54": "QSPI_SD2",
           "51": "QSPI_SD3", "52": "QSPI_SCLK", "20": "XIN", "21": "XOUT",
           "24": "SWCLK", "25": "SWDIO", "19": "GND",  # TESTEN -> GND
           "45": "+1V1", "23": "+1V1", "50": "+1V1",
           "48": "+3V3", "43": "+3V3", "44": "+3V3"}
    for p in ["1", "10", "22", "33", "42", "49"]:
        mcu[p] = "+3V3"
    gpio_pin = {0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8", 7: "9",
                8: "11", 9: "12", 10: "13", 11: "14", 12: "15", 13: "16", 14: "17",
                15: "18", 16: "27", 17: "28", 18: "29", 19: "30", 20: "31", 21: "32",
                22: "34", 23: "35", 24: "36", 25: "37", 26: "38", 27: "39", 28: "40", 29: "41"}
    used = {}
    for c, g in enumerate(COL_GPIO):
        used[g] = f"COL{c}"
    for r, g in enumerate(ROW_GPIO):
        used[g] = f"ROW{r}"
    used[ENC_A_GPIO], used[ENC_B_GPIO], used[ENC_ROW_GPIO] = "ENC_A", "ENC_B", "ROW4"
    for g, pin in gpio_pin.items():
        mcu[pin] = used.get(g)  # None -> no-connect
    add("U1", "MCU_RaspberryPi:RP2040", "RP2040", "MCU", mcu, LCSC["RP2040"])

    # decoupling (per Raspberry Pi minimal design)
    for i in range(6):
        C(f"C{1+i}", "100nF", "+3V3")          # IOVDD x6
    C("C7", "100nF", "+3V3")                   # USB_VDD
    C("C8", "100nF", "+3V3")                   # ADC_AVDD
    C("C9", "1uF", "+3V3")                     # VREG_IN
    C("C10", "1uF", "+1V1")                    # VREG_VOUT
    C("C11", "100nF", "+1V1")                  # DVDD
    C("C12", "100nF", "+1V1")                  # DVDD
    C("C13", "100nF", "+3V3")                  # flash

    # ---------------- flash ----------------
    add("U2", "Memory_Flash:W25Q128JVS", "W25Q128JVSIQ", "FLASH",
        {"1": "QSPI_SS", "6": "QSPI_SCLK", "5": "QSPI_SD0", "2": "QSPI_SD1",
         "3": "QSPI_SD2", "7": "QSPI_SD3", "8": "+3V3", "4": "GND"}, LCSC["W25Q128JVSIQ"])
    R("R1", "10k", "+3V3", "QSPI_SS")          # CS pull-up
    R("R2", "1k", "QSPI_SS", "BOOT_SW")        # BOOT series R
    add("SW49", "Switch:SW_Push", "BOOT", "BTN", {"1": "BOOT_SW", "2": "GND"}, LCSC["TS-1187A"])

    # ---------------- RUN / reset ----------------
    R("R3", "10k", "+3V3", "RUN")
    add("SW50", "Switch:SW_Push", "RESET", "BTN", {"1": "RUN", "2": "GND"}, LCSC["TS-1187A"])

    # ---------------- crystal ----------------
    add("Y1", "Device:Crystal_GND24", "12MHz", "XTAL",
        {"1": "XIN", "3": "XTAL_OUT", "2": "GND", "4": "GND"}, LCSC["12MHz"])
    R("R4", "1k", "XOUT", "XTAL_OUT")
    C("C14", "33pF", "XIN")  # C9002 crystal is CL=20pF: 2*(20-~3.5pF stray) ~= 33pF
    C("C15", "33pF", "XTAL_OUT")

    # ---------------- USB-C + ESD + LDO ----------------
    add("J1", "Connector:USB_C_Receptacle_USB2.0_16P", "USB-C", "USB",
        {"S1": "GND", "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
         "A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS",
         "A5": "CC1", "B5": "CC2", "A6": "DP_C", "B6": "DP_C", "A7": "DM_C", "B7": "DM_C",
         "A8": None, "B8": None}, LCSC["TYPE-C-31-M-12"])
    R("R5", "5.1k", "CC1", "GND")
    R("R6", "5.1k", "CC2", "GND")
    add("U3", "Power_Protection:USBLC6-2SC6", "USBLC6-2SC6", "ESD",
        {"1": "DP_C", "6": "DP_C", "3": "DM_C", "4": "DM_C", "5": "VBUS", "2": "GND"},
        LCSC["USBLC6-2SC6"])
    R("R7", "27R", "DP_C", "USB_DP")
    R("R8", "27R", "DM_C", "USB_DM")
    add("U4", "Regulator_Linear:AMS1117-3.3", "AMS1117-3.3", "LDO",
        {"3": "VBUS", "1": "GND", "2": "+3V3"}, LCSC["AMS1117-3.3"])
    C("C16", "10uF", "VBUS")
    C("C17", "10uF", "+3V3")

    # ---------------- encoder ----------------
    add("ENC1", "Device:RotaryEncoder_Switch", "EC11E15244G1", "ENC",
        {"A": "ENC_A", "B": "ENC_B", "C": "GND", "S1": "COL11", "S2": "K_ENC", "MP": "GND"},
        LCSC["EC11"], side="top")
    # push switch is matrix key (row 4, col 11), COL2ROW like the others
    add("D49", "Device:D", "1N4148W", "D", {"2": "K_ENC", "1": "ROW4"}, LCSC["1N4148W"])

    # ---------------- SWD header (not populated) ----------------
    add("J2", "Connector_Generic:Conn_01x03", "SWD", "SWD",
        {"1": "SWCLK", "2": "GND", "3": "SWDIO"}, dnp=True, bom=False)

    # ---------------- matrix (COL2ROW) ----------------
    n = 0
    for r in range(ROWS):
        for c in range(COLS):
            n += 1
            add(f"SW{n}", "Switch:SW_Push", "MX", "KEY",
                {"1": f"COL{c}", "2": f"K{n}"}, LCSC["Kailh-MX-socket"], side="bottom")
            add(f"D{n}", "Device:D", "1N4148W", "D",
                {"2": f"K{n}", "1": f"ROW{r}"}, LCSC["1N4148W"])

    # ---------------- mounting holes ----------------
    for i in range(1, 9):
        add(f"H{i}", "Mechanical:MountingHole", "M2", "HOLE", {}, bom=False)
    return parts


if __name__ == "__main__":
    build()
    nets = sorted({n for p in parts for n in p["pins"].values() if n})
    print(len(parts), "parts;", len(nets), "nets")
