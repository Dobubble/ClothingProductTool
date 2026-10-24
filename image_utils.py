from pathlib import Path
import re
import shutil
import tempfile
from PIL import Image, ImageTk
from logger_utils import logger
from app_paths import IMAGE_DIR, ensure_directories

ensure_directories()

'''
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / 'images'
'''

IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')


def validate_code(code):
    code = str(code).strip()
    if not code or code in {'.', '..'} or re.search(r'[<>:"/\\|?*\x00-\x1f]', code):
        raise ValueError('商品编码为空或包含 Windows 非法文件名字符')
    if code.endswith(('.', ' ')):
        raise ValueError('商品编码不能以句点或空格结尾')
    if re.match(r'(?i)^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', code):
        raise ValueError('商品编码不能使用 Windows 保留文件名')
    return code


def find_product_image(code):
    code = validate_code(code)
    for ext in SUPPORTED_EXTENSIONS:
        candidate = IMAGE_DIR / (code + ext)
        if candidate.is_file():
            return candidate
    return None


def import_product_image(code, source_path):
    code = validate_code(code)
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError('图片文件不存在')
    ext = source.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError('不支持的图片格式')
    with Image.open(source) as img:
        img.verify()
    target = IMAGE_DIR / (code + ext)
    if source.resolve() == target.resolve():
        return target
    # 先复制到临时文件，再替换目标文件，避免复制失败留下半张图片。
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=IMAGE_DIR, prefix='image_', suffix='.tmp', delete=False) as handle:
            tmp = Path(handle.name)
        shutil.copyfile(source, tmp)
        tmp.replace(target)
        # 只在新图片成功保存后，清除该编码的其他扩展名旧图片。
        for other_ext in SUPPORTED_EXTENSIONS:
            other = IMAGE_DIR / (code + other_ext)
            if other != target and other.exists():
                other.unlink()
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    logger.info('商品图片导入成功，编码：%s，路径：%s', code, target)
    return target


def load_preview_image(code, max_width=340, max_height=420):
    path = find_product_image(code)
    if path is None:
        return None
    with Image.open(path) as source:
        img = source.convert('RGB')
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)
