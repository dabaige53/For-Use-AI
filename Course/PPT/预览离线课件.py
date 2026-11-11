from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import re
from pathlib import Path

class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        if self.headers.get('Range') and self.path.split('?', 1)[0].endswith('.mp4'):
            path = self.translate_path(self.path)
            f = open(path, 'rb')
            size = os.fstat(f.fileno()).st_size
            match = re.fullmatch(r'bytes=(\d+)-(\d*)', self.headers['Range'])
            if not match or int(match[1]) >= size:
                f.close()
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.end_headers()
                return None
            start = int(match[1])
            end = min(int(match[2]) if match[2] else size - 1, size - 1)
            self.send_response(206)
            self.send_header('Content-Type', self.guess_type(path))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.send_header('Content-Length', str(end - start + 1))
            self.end_headers()
            f.seek(start)
            self.remaining = end - start + 1
            return f
        self.remaining = None
        return super().send_head()

    def copyfile(self, source, outputfile):
        if self.remaining is None:
            return super().copyfile(source, outputfile)
        while self.remaining:
            data = source.read(min(65536, self.remaining))
            if not data:
                break
            outputfile.write(data)
            self.remaining -= len(data)

os.chdir(Path(__file__).resolve().parent / '交付' / '和AI做同事-离线版')
ThreadingHTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
