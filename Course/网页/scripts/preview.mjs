import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { extname, join, relative, resolve } from "node:path";
import { createServer } from "node:http";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const dist = resolve(dirname(fileURLToPath(import.meta.url)), "../dist");
const port = Number(process.env.PORT || 4173);
const types = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".csv": "text/csv; charset=utf-8", ".json": "application/json" };
createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    const candidate = resolve(join(dist, pathname === "/" ? "index.html" : pathname));
    const fromDist = relative(dist, candidate);
    if (fromDist.startsWith("..") || fromDist === "") {
      if (fromDist !== "") { response.writeHead(403).end("Forbidden"); return; }
    }
    const info = await stat(candidate);
    if (!info.isFile()) throw new Error();
    response.writeHead(200, { "content-type": types[extname(candidate).toLowerCase()] || "application/octet-stream" });
    createReadStream(candidate).pipe(response);
  } catch (error) {
    if (error instanceof URIError) response.writeHead(400).end("Bad request");
    else response.writeHead(404).end("Not found");
  }
}).listen(port, "127.0.0.1", () => console.log(`预览：http://localhost:${port}`));
