import argparse
import io
import mimetypes
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent
WEB_ROOT = PROJECT_ROOT / "build" / "web"
CDN_HOST = "https://pygame-web.github.io/cdn/"
CDN_ROUTE = "/__runtime_cdn__/"
mimetypes.add_type("application/wasm", ".wasm")


def rewrite_html(content):
    content = re.sub(
        rb"https://pygame-web\.github\.io/cdn/(\d+(?:\.\d+)*)/",
        CDN_ROUTE.encode() + rb"\1/",
        content,
    )
    return re.sub(
        rb"<script\b[^>]*browserfs\.min\.js[^>]*>\s*</script>",
        b"",
        content,
        flags=re.IGNORECASE,
    )


class GameRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def send_head(self):
        request_path = urlsplit(self.path).path
        if request_path == "/" or request_path.endswith("/index.html"):
            index_path = Path(self.translate_path(self.path))
            if index_path.is_file():
                content = rewrite_html(index_path.read_bytes())
                response = io.BytesIO(content)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                return response
        return super().send_head()

    def _serve_cdn(self, include_body):
        path = unquote(urlsplit(self.path).path)
        if not path.startswith(CDN_ROUTE):
            return False

        relative_path = path[len(CDN_ROUTE):]
        if not relative_path or ".." in Path(relative_path).parts:
            self.send_error(404)
            return True

        version, separator, resource = relative_path.partition("/")
        if not separator or not resource or not re.fullmatch(r"\d+(?:\.\d+)*", version):
            self.send_error(404)
            return True

        upstream_url = CDN_HOST + quote(relative_path, safe="/.-_~")
        request = Request(upstream_url, method="GET" if include_body else "HEAD")
        try:
            upstream = urlopen(request, timeout=90)
        except HTTPError as error:
            self.send_error(error.code)
            return True
        except Exception as error:
            self.send_error(502, explain=str(error))
            return True

        with upstream:
            self.send_response(upstream.status)
            for header in ("Content-Type", "Content-Length", "Last-Modified", "ETag"):
                value = upstream.headers.get(header)
                if value:
                    self.send_header(header, value)
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            if include_body:
                while chunk := upstream.read(1024 * 1024):
                    self.wfile.write(chunk)
        return True

    def do_GET(self):
        if not self._serve_cdn(include_body=True):
            super().do_GET()

    def do_HEAD(self):
        if not self._serve_cdn(include_body=False):
            super().do_HEAD()


def main():
    parser = argparse.ArgumentParser(description="Sirve la build web de Coral Orange.")
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    if not (WEB_ROOT / "index.html").is_file():
        parser.error("Primero genera la build con: python -m pygbag --build main.py")

    handler = partial(GameRequestHandler, directory=str(WEB_ROOT))
    server = ThreadingHTTPServer((args.bind, args.port), handler)
    print(f"Coral Orange listo en http://{args.bind}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()