"""Claude 스킬 업로드용 zip(docs/civil-engineer-tone-skill.zip)을 다시 만든다. 실행: python tools/build_skill_zip.py"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "civil-engineer-tone")
OUT = os.path.join(ROOT, "docs", "civil-engineer-tone-skill.zip")


def skill_files():
    for d, dirs, files in os.walk(SKILL):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__")
        for f in sorted(files):
            if not f.endswith(".pyc"):
                p = os.path.join(d, f)
                yield p, "civil-engineer-tone/" + os.path.relpath(p, SKILL).replace(os.sep, "/")


def build(out=OUT):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p, arc in skill_files():
            z.write(p, arc)
    return out


if __name__ == "__main__":
    print(build())
