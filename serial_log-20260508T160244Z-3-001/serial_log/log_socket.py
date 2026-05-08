import socket
import threading

def bridge_socket(source: socket.socket, target: socket.socket, label: str):
    while True:
        try:
            data = source.recv(4096)
            if not data:
                print(f"[{label}] Conexão encerrada.")
                try:
                    source.close()
                except:
                    pass
                try:
                    target.close()
                except:
                    pass
                break
            try:
                text = data.decode("utf-8", errors="replace")
            except Exception as e:
                text = f"<decode error: {e}>"
            print(f"[{label}] {text}")
            target.sendall(data)
        except Exception as e:
            print(f"[{label}] Error: {e}")
            try:
                source.close()
            except:
                pass
            try:
                target.close()
            except:
                pass
            break

def main():
    dest_ip = "192.168.1.102"
    dest_port = 9100

    # Cria servidor em localhost na mesma porta
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", dest_port))
    server.listen(1)

    print(f"🔌 Ponte socket: localhost:{dest_port} ↔ {dest_ip}:{dest_port}")

    while True:
        try:
            print(f"Aguardando conexão local em localhost:{dest_port}")
            local_conn, local_addr = server.accept()
            print(f"Conexão local: {local_addr}")

            # Tenta conectar ao destino
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                remote.connect((dest_ip, dest_port))
                print(f"Conectado ao destino: {dest_ip}:{dest_port}")
            except Exception as e:
                print(f"Erro ao conectar ao destino: {e}")
                local_conn.close()
                remote.close()
                continue

            # Inicia ponte
            t1 = threading.Thread(target=bridge_socket, args=(local_conn, remote, "local → remoto"), daemon=True)
            t2 = threading.Thread(target=bridge_socket, args=(remote, local_conn, "remoto → local"), daemon=True)
            t1.start()
            t2.start()

            # Espera as threads terminarem (conexão encerrada)
            t1.join()
            t2.join()

            print("Ponte encerrada. Reiniciando...")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
