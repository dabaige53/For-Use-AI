"""Generate timed MiniMax narration and mux it into the existing presentation videos."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
import wave

COURSE = Path(__file__).resolve().parent.parent
VIDEOS = {
    'llm': COURSE / '02-AI的能力从哪里来/大语言模型简要说明',
    'io': COURSE / '03-信息输入与工具执行/AI的输入与输出',
}
RATE = 32000


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def duration(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'default=nw=1:nk=1', str(path)]).stdout)


def request_audio(text, voice, model, speed):
    key = os.environ.get('MINIMAX_API_KEY')
    if not key:
        raise RuntimeError('MINIMAX_API_KEY is required')
    payload = {'model': model, 'text': text, 'stream': False,
               'voice_setting': {'voice_id': voice, 'speed': speed, 'vol': 1, 'pitch': 0},
               'audio_setting': {'sample_rate': RATE, 'bitrate': 128000, 'format': 'mp3', 'channel': 1},
               'language_boost': 'Chinese', 'subtitle_enable': True}
    req = urllib.request.Request(os.environ.get('MINIMAX_TTS_URL', 'https://api.minimax.cn/v1/t2a_v2'),
                                 data=json.dumps(payload).encode(),
                                 headers={'Authorization': 'Bearer ' + key,
                                          'Content-Type': 'application/json', 'User-Agent': 'CourseNarration/1.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503) and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError(f'MiniMax HTTP error {error.code}') from None
        status = result.get('base_resp', {})
        if status.get('status_code') in (1002, 1008) and attempt < 2:
            time.sleep(3 * (attempt + 1))
            continue
        if status.get('status_code') != 0:
            raise RuntimeError(f'MiniMax status {status.get("status_code")}: '
                               + str(status.get('status_msg', '')).replace(key, '[redacted]'))
        audio = bytes.fromhex(result['data']['audio'])
        subtitle_url = result['data'].get('subtitle_file') or result.get('subtitle_file')
        subtitles = None
        if subtitle_url:
            with urllib.request.urlopen(subtitle_url, timeout=30) as response:
                subtitles = json.load(response)
        return audio, subtitles, result.get('extra_info', {})
    raise RuntimeError('MiniMax retries exhausted')


def normalize(text):
    return re.sub(r'\bAI\b', '人工智能', text)


def subtitle_rows(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ('subtitles', 'subtitle', 'data'):
            if isinstance(data.get(key), list):
                return data[key]
    raise RuntimeError('Missing MiniMax subtitle timestamps; cannot claim aligned subtitles')


def srt_stamp(seconds):
    value = round(seconds * 1000)
    return f'{value//3600000:02}:{value//60000%60:02}:{value//1000%60:02},{value%1000:03}'


def make_video(name, limit=None):
    root = VIDEOS[name]
    timeline_path = root / '时间线.json'
    timeline = json.loads(timeline_path.read_text())
    narration = timeline['narration']
    output = root / '生成/配音'
    output.mkdir(parents=True, exist_ok=True)
    segments = narration['segments'][:limit] if limit else narration['segments']
    frames = bytearray(round(timeline['scope_seconds'] * RATE) * 2)
    captions = []
    report = []
    for segment in segments:
        label = segment['id']
        text = normalize(segment['text'])
        available = segment['end'] - segment['start'] - .04
        meta_path = output / f'{label}.json'
        audio_path = output / f'{label}.mp3'
        signature = hashlib.sha256(json.dumps({'text': text, 'voice': narration['voice_id'],
                                               'model': narration['model']}, ensure_ascii=False).encode()).hexdigest()
        cached = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        if cached.get('signature') != signature or not audio_path.exists():
            audio, subtitles, usage = request_audio(text, narration['voice_id'], narration['model'], 1)
            audio_path.write_bytes(audio)
            cached = {'signature': signature, 'speed': 1, 'subtitles': subtitles, 'usage': usage}
            meta_path.write_text(json.dumps(cached, ensure_ascii=False, indent=2))
        raw_duration = duration(audio_path)
        if raw_duration > available * 1.12:
            speed = min(1.6, round(raw_duration / available * 1.02, 2))
            audio, subtitles, usage = request_audio(text, narration['voice_id'], narration['model'], speed)
            audio_path.write_bytes(audio)
            cached = {'signature': signature, 'speed': speed, 'subtitles': subtitles, 'usage': usage}
            meta_path.write_text(json.dumps(cached, ensure_ascii=False, indent=2))
            raw_duration = duration(audio_path)
        factor = max(1, raw_duration / available)
        if factor > 1.12:
            raise RuntimeError(f'{name}/{label} is too long; revise this narration instead of truncating it')
        filters = f'atempo={factor:.6f},afade=t=in:d=0.01,afade=t=out:st={max(0,raw_duration/factor-.02):.6f}:d=0.02'
        pcm = run(['ffmpeg', '-v', 'error', '-i', str(audio_path), '-af', filters,
                   '-ar', str(RATE), '-ac', '1', '-f', 's16le', '-']).stdout
        start = round(segment['start'] * RATE) * 2
        end = start + len(pcm)
        if end > round(segment['end'] * RATE) * 2 + 64:
            raise RuntimeError(f'{name}/{label} exceeds its allotted time')
        frames[start:end] = pcm
        actual = len(pcm) / (RATE * 2)
        for row in subtitle_rows(cached['subtitles']):
            a = segment['start'] + float(row['time_begin']) / 1000 / factor
            b = segment['start'] + float(row['time_end']) / 1000 / factor
            b = min(b, segment['start'] + actual)
            if b > a:
                captions.append((a, b, row['text']))
        report.append({'id': label, 'start': segment['start'], 'end': segment['end'],
                       'audio': str(audio_path.relative_to(root)), 'raw_seconds': raw_duration,
                       'speed': cached['speed'], 'local_tempo': factor, 'spoken_seconds': actual})
        print(f'{name}/{label}: {actual:.2f}s / {available:.2f}s', flush=True)
    if limit:
        return
    wav = output / '旁白.wav'
    with wave.open(str(wav), 'wb') as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(frames)
    srt = output / '字幕.srt'
    srt.write_text('\n\n'.join(f'{i+1}\n{srt_stamp(a)} --> {srt_stamp(b)}\n{text}'
                              for i, (a, b, text) in enumerate(captions)) + '\n', encoding='utf-8')
    target = output / ('大语言模型简要说明-配音.mp4' if name == 'llm' else 'AI的输入与输出-配音.mp4')
    source = COURSE / f'PPT/assets/video_{name}.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-i', str(wav), '-i', str(srt),
         '-map', '0:v:0', '-map', '1:a:0', '-map', '2:s:0', '-c:v', 'copy', '-c:a', 'aac',
         '-b:a', '192k', '-c:s', 'mov_text', '-metadata:s:a:0', 'language=zho',
         '-metadata:s:s:0', 'language=zho', '-movflags', '+faststart', str(target)])
    run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(target), '-f', 'null', '-'])
    media = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(target)]).stdout)
    audio_streams = [s for s in media['streams'] if s['codec_type'] == 'audio']
    assert len(audio_streams) == 1
    assert abs(float(media['format']['duration']) - timeline['scope_seconds']) < .1
    # Copying the compressed video stream preserves all existing pictures and chapter timings.
    hashes = []
    for path in (source, target):
        hashes.append(run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                           '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).stdout.decode().strip())
    assert hashes[0] == hashes[1]
    narration['rendered_segments'] = report
    narration['audio'] = str(wav.relative_to(root))
    narration['subtitles'] = str(srt.relative_to(root))
    narration['video'] = str(target.relative_to(root))
    timeline['audio'] = True
    (root / '时间线.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + '\n')
    verification = {'voice_id': narration['voice_id'], 'model': narration['model'],
                    'duration_seconds': float(media['format']['duration']), 'decode': 'passed',
                    'video_stream_identical': True, 'audio_streams': 1, 'subtitle_cues': len(captions),
                    'video_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                    'segments': report, 'listening_review': 'pending', 'media': media}
    (output / '验收.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n')
    print(f'Complete: {target}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', choices=['all', *VIDEOS], default='all')
    parser.add_argument('--limit', type=int, help='Generate only the first N segments; no full export')
    args = parser.parse_args()
    for name in VIDEOS if args.video == 'all' else [args.video]:
        make_video(name, args.limit)


if __name__ == '__main__':
    main()
