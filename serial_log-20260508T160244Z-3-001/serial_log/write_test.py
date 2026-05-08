import serial
import struct

def crc16(data: bytes) -> bytes:
    """Calculate CRC-16 (Modbus), LSB first."""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)  # LSB first

def build_write_command():
    Adr = 0xFF
    Cmd = 0x03

    # =====================
    # Parameters
    # =====================
    Wdt = bytes.fromhex("aaaaaaaaaaaa")  # EPC data to write (6 words / 12 bytes)
    WNum = len(Wdt) // 2                # Number of words = 6
    Mem = 0x01                          # EPC memory
    WordPtr = 0x02                       # Start address
    Pwd = bytes.fromhex("01020000")      # 4-byte password

    # Mask to filter tag by TID
    ENum = 0xFF
    MaskMem = 0x02
    MaskAdr = bytes.fromhex("0000")      # bit address
    MaskLen = 0x60                        # 12 bytes = 96 bits
    MaskData = bytes.fromhex("E2806915200050167A11B4E0")

    # =====================
    # Construct Data[]
    # =====================
    Data = struct.pack('B', WNum)          # WNum
    Data += struct.pack('B', ENum)         # ENum
    # EPC is ignored because ENum = 0xFF
    Data += struct.pack('B', Mem)          # Mem
    Data += struct.pack('B', WordPtr)      # WordPtr
    Data += Wdt                             # Wdt
    Data += Pwd                             # Pwd
    Data += struct.pack('B', MaskMem)      # MaskMem
    Data += MaskAdr                         # MaskAdr (2 bytes)
    Data += struct.pack('B', MaskLen)      # MaskLen
    Data += MaskData                        # MaskData

    # =====================
    # Full frame
    # =====================
    Len = 1 + 1 + len(Data)                # Adr + Cmd + Data
    frame_no_crc = struct.pack('B', Len) + struct.pack('B', Adr) + struct.pack('B', Cmd) + Data

    crc = crc16(frame_no_crc)
    full_frame = frame_no_crc + crc

    return full_frame

def send_command(com_port="COM12"):
    cmd = build_write_command()
    print("Sending command:", cmd.hex())

    with serial.Serial(com_port, 115200, timeout=1) as ser:
        ser.write(cmd)
        response = ser.read(64)
        print("Response:", response.hex())

if __name__ == "__main__":
    send_command("COM12")
