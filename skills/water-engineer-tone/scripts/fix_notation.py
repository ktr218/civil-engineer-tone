#!/usr/bin/env python3
"""단위·수치 표기 자동 교정기 (값은 바꾸지 않고 표기만 정규화).

lexicon.json에서 auto=true인 항목만 적용한다. 용어·문체처럼 문맥 판단이 필요한 항목은
고치지 않는다(check_tone.py로 확인 후 사람이나 Claude가 고친다).

사용법:
    python fix_notation.py 파일.md              # 변경 목록만 출력 (dry-run)
    python fix_notation.py 파일.md --write      # 파일에 반영 (원본은 .bak 백업)
    python fix_notation.py 파일.md -o 결과.md   # 다른 파일로 저장
    python fix_notation.py - < 입력 > 출력      # 표준입출력
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tonelib  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description="단위·수치 표기 자동 교정기")
    ap.add_argument("path")
    ap.add_argument("--type", choices=list(tonelib.TYPES))
    ap.add_argument("--write", action="store_true", help="원본 파일에 반영(.bak 백업)")
    ap.add_argument("-o", "--output", help="결과 저장 경로")
    a = ap.parse_args(argv)
    try:
        if a.path == "-":
            text = sys.stdin.read()
        else:
            with open(a.path, encoding="utf-8") as f:
                text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"입력 오류: {e}", file=sys.stderr)
        return 2
    new, changes = tonelib.fix(text, a.type)
    if a.path == "-" and not a.output:
        sys.stdout.write(new)
        for c in changes:
            print(f"{c['line']}행 {c['id']}: {c['before']} → {c['after']}", file=sys.stderr)
        return 0
    for c in changes:
        print(f"{c['line']:>4}행 {c['id']}: \"{c['before']}\" → \"{c['after']}\"")
    print(f"변경 {len(changes)}건")
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"저장: {a.output}")
    elif a.write and changes:
        shutil.copyfile(a.path, a.path + ".bak")
        with open(a.path, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"반영: {a.path} (백업 {a.path}.bak)")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
