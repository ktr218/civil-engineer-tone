"""Claude 스킬 업로드용 zip(docs/civil-engineer-tone-skill.zip)을 다시 만든다. 실행: python tools/build_skill_zip.py

텍스트 파일은 줄끝을 LF로 맞추고 시각을 고정해, 운영체제·체크아웃 방식과 상관없이 같은 내용이면 같은 zip이 나온다.
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "civil-engineer-tone")
OUT = os.path.join(ROOT, "docs", "civil-engineer-tone-skill.zip")
TEXT = (".md", ".json", ".py", ".txt", ".yml", ".yaml")
STAMP = (2026, 1, 1, 0, 0, 0)


def skill_files():
    for d, dirs, files in os.walk(SKILL):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for f in sorted(files):
            if not f.endswith(".pyc"):
                p = os.path.join(d, f)
                yield p, "civil-engineer-tone/" + os.path.relpath(p, SKILL).replace(os.sep, "/")


def payload(path):
    """zip에 넣을 바이트. 텍스트는 CRLF를 LF로 바꾼다(.gitattributes eol=lf와 같은 기준)."""
    with open(path, "rb") as f:
        data = f.read()
    return data.replace(b"\r\n", b"\n") if path.endswith(TEXT) else data


def build(out=OUT):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p, arc in skill_files():
            info = zipfile.ZipInfo(arc, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, payload(p))
    return out


if __name__ == "__main__":
    print(build())
