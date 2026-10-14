// Stream only the requested bytes from R2; never download a whole video to seek.
const videoKeys = new Map([
  ['/Course/PPT/assets/video_llm.mp4', 'video_llm.mp4'],
  ['/Course/PPT/assets/video_io.mp4', 'video_io.mp4'],
]);
export default {
  async fetch(request, env) {
    const key = videoKeys.get(new URL(request.url).pathname);
    if (!key) return env.ASSETS.fetch(request);
    if (!['GET', 'HEAD'].includes(request.method)) return new Response(null, {status: 405, headers: {Allow: 'GET, HEAD'}});
    const meta = await env.COURSE_MEDIA.head(key);
    if (!meta) return new Response('Video not found', {status: 404});
    const headers = new Headers();
    meta.writeHttpMetadata(headers);
    headers.set('Content-Type', 'video/mp4');
    headers.set('ETag', meta.httpEtag);
    headers.set('Last-Modified', meta.uploaded.toUTCString());
    headers.set('Accept-Ranges', 'bytes');
    headers.set('Cache-Control', 'public, max-age=86400');
    headers.set('X-Content-Type-Options', 'nosniff');
    if (request.headers.get('If-None-Match') === meta.httpEtag) return new Response(null, {status: 304, headers});
    headers.set('Content-Length', String(meta.size));
    if (request.method === 'HEAD') return new Response(null, {headers});
    const validator = request.headers.get('If-Range');
    const match = /^bytes=(\d*)-(\d*)$/.exec(request.headers.get('Range') || '');
    let range;
    if (match && (match[1] || match[2]) && (!validator || validator === meta.httpEtag || validator === meta.uploaded.toUTCString())) {
      const start = match[1] ? Number(match[1]) : Math.max(0, meta.size - Number(match[2]));
      const end = match[1] && match[2] ? Math.min(Number(match[2]), meta.size - 1) : meta.size - 1;
      if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= meta.size) {
        headers.set('Content-Range', `bytes */${meta.size}`);
        headers.set('Content-Length', '0');
        return new Response(null, {status: 416, headers});
      }
      range = {offset: start, length: end - start + 1};
      headers.set('Content-Range', `bytes ${start}-${end}/${meta.size}`);
      headers.set('Content-Length', String(range.length));
    }
    const object = await env.COURSE_MEDIA.get(key, range ? {range} : undefined);
    if (!object) return new Response('Video not found', {status: 404});
    return new Response(object.body, {status: range ? 206 : 200, headers});
  }
};
