import serial
import threading

# Configure as portas e baudrate
PORT_A = "COM5"
PORT_B = "COM8"
BAUDRATE = 115200

def bridge(source: serial.Serial, target: serial.Serial, label: str):
    while True:
        if source.in_waiting:
            data = source.read(source.in_waiting)
            try:
                text = data.decode("utf-8", errors="replace")  # converte para string
            except Exception as e:
                text = f"<decode error: {e}>"
            print(f"[{label}] {text}")
            target.write(data)  # ainda escreve em bytes

def main():
    try:
        ser_a = serial.Serial(PORT_A, BAUDRATE, timeout=0.1)
        ser_b = serial.Serial(PORT_B, BAUDRATE, timeout=0.1)

        print(f"🔌 Serial bridge started: {PORT_A} ↔ {PORT_B} @ {BAUDRATE} baud")
        
        # Threads para espelhar bidirecionalmente
        threading.Thread(target=bridge, args=(ser_a, ser_b, f"{PORT_A} → {PORT_B}"), daemon=True).start()
        threading.Thread(target=bridge, args=(ser_b, ser_a, f"{PORT_B} → {PORT_A}"), daemon=True).start()

        # Mantenha a thread principal viva
        while True:
            pass

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
