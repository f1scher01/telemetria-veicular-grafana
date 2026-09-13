"""
Servidor Local Autônomo do Dashboard de Telemetria Veicular.
Executa o painel analítico interativo na porta 3000 sem necessidade de Docker ou banco externo.
"""

import os
import sys
import webbrowser
import http.server
import socketserver

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Silencia logs excessivos para manter o terminal limpo
        pass

def start_server():
    port = PORT
    max_attempts = 5
    httpd = None

    for attempt in range(max_attempts):
        try:
            httpd = socketserver.TCPServer(("", port), Handler)
            break
        except OSError:
            port += 1

    if not httpd:
        print(f"Erro: Nao foi possivel abrir porta a partir de {PORT}.")
        return

    url = f"http://localhost:{port}"
    print("=" * 70)
    print("🏎️  TELEMETRIA VEICULAR SIMULADA · COCKPIT WEB (TRAÇADO DE INTERLAGOS)")
    print("=" * 70)
    print(f"✅ Servidor Web de Telemetria ativo em: {url}")
    print("🌐 Abrindo seu navegador padrao automaticamente...")
    print("⚡ Pressione Ctrl+C para encerrar o servidor a qualquer momento.")
    print("=" * 70)

    try:
        webbrowser.open(url)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor de telemetria encerrado com sucesso.")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
