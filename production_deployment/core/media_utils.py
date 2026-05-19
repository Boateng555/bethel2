"""
Compress images and videos before storage so uploads work on slow connections
and stay within server limits.
"""
import logging
import os
import shutil
import subprocess
import tempfile
from io import BytesIO

from django.core.files import File
from django.core.files.base import ContentFile
from PIL import Image

logger = logging.getLogger(__name__)

# Hero carousel: sharp enough on screen, small on disk
HERO_IMAGE_MAX_WIDTH = 1920
HERO_IMAGE_MAX_HEIGHT = 1080
HERO_IMAGE_MAX_KB = 400

# General uploads (speakers, news, etc.)
DEFAULT_IMAGE_MAX_WIDTH = 1600
DEFAULT_IMAGE_MAX_HEIGHT = 1200
DEFAULT_IMAGE_MAX_KB = 350

HERO_VIDEO_MAX_MB = 8
HERO_VIDEO_MAX_WIDTH = 1280


def _jpeg_name(original_name: str, suffix: str = '') -> str:
    base = os.path.splitext(os.path.basename(original_name or 'upload'))[0]
    base = ''.join(c if c.isalnum() or c in '-_' else '_' for c in base)[:80]
    return f"{base}{suffix}.jpg"


def compress_image_upload(
    uploaded_file,
    *,
    max_width=HERO_IMAGE_MAX_WIDTH,
    max_height=HERO_IMAGE_MAX_HEIGHT,
    max_kb=HERO_IMAGE_MAX_KB,
):
    """
    Resize and re-encode an uploaded image to JPEG under max_kb.
    Returns a ContentFile or the original file if compression fails.
    """
    if not uploaded_file:
        return None

    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.load()
    except Exception as exc:
        logger.warning('Could not open image for compression: %s', exc)
        uploaded_file.seek(0)
        return uploaded_file

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode in ('RGBA', 'LA'):
            background.paste(img, mask=img.split()[-1])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        img = img.resize(
            (int(width * ratio), int(height * ratio)),
            Image.Resampling.LANCZOS,
        )

    out_name = _jpeg_name(getattr(uploaded_file, 'name', 'image'))
    for quality in (85, 75, 65, 55, 45, 35, 25):
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = len(buffer.getvalue()) / 1024
        if size_kb <= max_kb or quality == 25:
            buffer.seek(0)
            return ContentFile(buffer.getvalue(), name=out_name)

    buffer.seek(0)
    return ContentFile(buffer.getvalue(), name=out_name)


def _ffmpeg_available() -> bool:
    return shutil.which('ffmpeg') is not None


def compress_video_upload(
    uploaded_file,
    *,
    max_mb=HERO_VIDEO_MAX_MB,
    max_width=HERO_VIDEO_MAX_WIDTH,
):
    """
    Re-encode video to H.264 MP4 suitable for web hero banners.
    Requires ffmpeg on the server; returns original file if unavailable.
    """
    if not uploaded_file:
        return None

    if not _ffmpeg_available():
        logger.info('ffmpeg not installed; storing video without re-encoding')
        uploaded_file.seek(0)
        return uploaded_file

    uploaded_file.seek(0, os.SEEK_END)
    size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)

    suffix = os.path.splitext(getattr(uploaded_file, 'name', 'video'))[1] or '.mp4'
    if size_mb <= max_mb and suffix.lower() in ('.mp4', '.webm'):
        # Still normalize for web playback if large resolution
        pass

    in_path = out_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
            for chunk in uploaded_file.chunks():
                tmp_in.write(chunk)
            in_path = tmp_in.name

        out_path = in_path + '_compressed.mp4'
        cmd = [
            'ffmpeg', '-y', '-i', in_path,
            '-vf', f'scale=min({max_width}\\,iw):-2',
            '-c:v', 'libx264', '-crf', '28', '-preset', 'fast',
            '-c:a', 'aac', '-b:a', '96k',
            '-movflags', '+faststart',
            '-max_muxing_queue_size', '1024',
            out_path,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            logger.warning('ffmpeg failed: %s', result.stderr[-500:] if result.stderr else '')
            uploaded_file.seek(0)
            return uploaded_file

        out_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        if out_size_mb > max_mb * 1.5:
            # Second pass — stronger compression
            out_path2 = in_path + '_compressed2.mp4'
            subprocess.run(
                [
                    'ffmpeg', '-y', '-i', out_path,
                    '-vf', f'scale=min(960\\,iw):-2',
                    '-c:v', 'libx264', '-crf', '32', '-preset', 'fast',
                    '-c:a', 'aac', '-b:a', '64k',
                    '-movflags', '+faststart',
                    out_path2,
                ],
                capture_output=True,
                timeout=600,
            )
            if os.path.exists(out_path2):
                os.remove(out_path)
                out_path = out_path2

        base = os.path.splitext(os.path.basename(getattr(uploaded_file, 'name', 'video')))[0]
        base = ''.join(c if c.isalnum() or c in '-_' else '_' for c in base)[:80]
        out_name = f"{base}_compressed.mp4"
        with open(out_path, 'rb') as f:
            data = f.read()
        return ContentFile(data, name=out_name)
    except Exception as exc:
        logger.warning('Video compression error: %s', exc)
        uploaded_file.seek(0)
        return uploaded_file
    finally:
        for path in (in_path, out_path, (in_path + '_compressed2.mp4') if in_path else None):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


def is_new_file_upload(instance, field_name: str) -> bool:
    """True when the file field has a new upload (not an unchanged existing file)."""
    field = getattr(instance, field_name, None)
    if not field:
        return False
    if not getattr(field, 'name', None):
        return False
    # New rows always compress
    if not instance.pk:
        return True
    try:
        old = instance.__class__.objects.get(pk=instance.pk)
        old_field = getattr(old, field_name, None)
        if not old_field:
            return True
        return old_field.name != field.name
    except instance.__class__.DoesNotExist:
        return True


def compress_model_media(instance, *, hero=False):
    """Compress image/video fields on a model instance before save."""
    image_kw = {}
    video_max_mb = HERO_VIDEO_MAX_MB
    if hero:
        image_kw = {
            'max_width': HERO_IMAGE_MAX_WIDTH,
            'max_height': HERO_IMAGE_MAX_HEIGHT,
            'max_kb': HERO_IMAGE_MAX_KB,
        }
    else:
        image_kw = {
            'max_width': DEFAULT_IMAGE_MAX_WIDTH,
            'max_height': DEFAULT_IMAGE_MAX_HEIGHT,
            'max_kb': DEFAULT_IMAGE_MAX_KB,
        }

    for field_name in ('image', 'photo', 'thumbnail', 'logo', 'banner_image',
                       'nav_logo', 'background_image', 'founder_image', 'extra_image',
                       'chairman_image', 'vice_chairman_image', 'board_image', 'team_image',
                       'leadership_photo_1', 'leadership_photo_2', 'leadership_photo_3',
                       'pastor_image', 'assistant_pastor_image', 'about_photo_1',
                       'about_photo_2', 'about_photo_3'):
        if not hasattr(instance, field_name):
            continue
        if not is_new_file_upload(instance, field_name):
            continue
        field = getattr(instance, field_name)
        if not field:
            continue
        try:
            compressed = compress_image_upload(field, **image_kw)
            if compressed:
                setattr(instance, field_name, compressed)
        except Exception as exc:
            logger.warning('Image compress failed for %s.%s: %s', instance.__class__.__name__, field_name, exc)

    for field_name in ('video', 'background_video', 'video_file'):
        if not hasattr(instance, field_name):
            continue
        if not is_new_file_upload(instance, field_name):
            continue
        field = getattr(instance, field_name)
        if not field:
            continue
        try:
            compressed = compress_video_upload(field, max_mb=video_max_mb)
            if compressed:
                setattr(instance, field_name, compressed)
        except Exception as exc:
            logger.warning('Video compress failed for %s.%s: %s', instance.__class__.__name__, field_name, exc)
