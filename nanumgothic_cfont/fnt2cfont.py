import os
import re
import textwrap
from PIL import Image

FONT_DIR = ".fnt 파일 위치"
FNT_FILE = os.path.join(FONT_DIR, "*.fnt")
TGA_PREFIX = "nanumgothicsffgall_{:01d}.tga"
OUTPUT_CPP = ".cpp 출력파일 위치"

# 1비트 threshold
THRESHOLD = 128

def parse_fnt_file(fnt_path):
    with open(fnt_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    chars = []
    for line in lines:
        if line.startswith("char id="):
            d = dict(re.findall(r"(\w+)=([-\w]+)", line))
            chars.append({
                "id": int(d["id"]),
                "char": chr(int(d["id"])),
                "x": int(d["x"]),
                "y": int(d["y"]),
                "width": int(d["width"]),
                "height": int(d["height"]),
                "page": int(d["page"]),
            })
    return chars

def extract_bitmap(image, x, y, w, h):
    crop = image.crop((x, y, x + w, y + h)).convert("L")
    data = []
    for row in range(h):
        byte = 0
        bit_count = 0
        for col in range(w):
            pixel = crop.getpixel((col, row))
            bit = 1 if pixel >= THRESHOLD else 0
            byte = (byte << 1) | bit
            bit_count += 1
            if bit_count == 8:
                data.append(byte)
                byte = 0
                bit_count = 0
        if bit_count > 0:
            byte <<= (8 - bit_count)
            data.append(byte)
    return data

def generate_cpp(chars, tga_dir):
    # 페이지별 이미지 캐시
    pages = {}
    lines = []
    lines.append('#include "fonts.h"\n\n#ifdef __cplusplus\nextern "C" {\n#endif\n')
    lines.append("const CH_CN Font16CN_Table[] = \n{\n")

    for entry in chars:
        ch = entry["char"]
        if ord(ch) < 32:  # 제어문자 제외
            continue
        page = entry["page"]
        tga_path = os.path.join(tga_dir, TGA_PREFIX.format(page))
        if page not in pages:
            pages[page] = Image.open(tga_path)

        bitmap = extract_bitmap(pages[page], entry["x"], entry["y"], entry["width"], entry["height"])
        hex_data = ", ".join(f"0x{b:02X}" for b in bitmap)
        hex_lines = textwrap.wrap(hex_data, 60)

        body = "{\n\"" + ch + "\",\n" + "\n".join(" " + l for l in hex_lines) + "\n},"
        lines.append(body + "\n")

    lines.append("};\n\n#ifdef __cplusplus\n}\n#endif\n\ncFONT Font16CN = {\n\tFont16CN_Table,\n\tsizeof(Font16CN_Table)/sizeof(CH_CN),\n\t7,\n\t16,\n\t16,\n};\n")
    return "\n".join(lines)

def main():
    chars = parse_fnt_file(FNT_FILE)
    cpp = generate_cpp(chars, FONT_DIR)
    with open(OUTPUT_CPP, "w", encoding="utf-8") as f:
        f.write(cpp)
    print(f"{len(chars)} 글자 변환됨)")

if __name__ == "__main__":
    main()
