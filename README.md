# civil-engineer-tone — 토목 엔지니어 어투 스킬

> ## 🚀 가장 쉬운 사용법 (설치 없음, 1분)
>
> ChatGPT · Gemini · Claude 어디서나 됩니다.
>
> 1. **[👉 여기를 눌러 지침 열기](https://raw.githubusercontent.com/ktr218/civil-engineer-tone/main/prompts/universal.md)**
> 2. 열린 화면에서 전체 선택(**Ctrl+A**) → 복사(**Ctrl+C**)
>    (휴대폰은 화면을 길게 눌러 전체 선택 → 복사)
> 3. AI 채팅창에 붙여넣고 **"앞으로 이대로 써줘"** 입력
> 4. 바꾸고 싶은 글을 붙여넣으면 끝!
>
> 새 대화마다 다시 붙여넣어야 합니다. 매번 하기 번거로우면 ChatGPT의 **GPT 만들기**나 Gemini의 **Gem 만들기**에서 지침 칸에 한 번만 넣어 두세요.
>
> 도움이 됐다면 오른쪽 위 ⭐ **Star**를 눌러 주세요 🙏

---

AI가 쓴 글, 메모, 일반 문장을 **국내 토목 엔지니어링 실무 문서의 어투와 용어**로 바꿔 주는 AI 지침·스킬입니다.
도화엔지니어링 실무 문서의 문체를 참고해 만들었습니다. 문체·기호·단위는 전 부문 공통이고, 전문 용어는 부문별 팩(물산업·교통·인프라·도시·에너지·CM·건설·지원)으로 나눴습니다. 지원 팩을 뺀 모든 팩은 해당 부문의 실무 문서를 근거로 만들었습니다. 회사가 공식 배포하는 자료는 아닙니다.

기본계획·타당성조사·기본 및 실시설계 보고서, 착수·중간·최종보고 장표, 협의자료, 검토의견서·VE 검토, 조치계획서, 재원협의, 설계VE 제안, 과업지시서, 회의록, 실정보고, 검측·공사일보, 공문, 발표 시나리오, 내부 보고 메일을 지원합니다.

## 무엇을 하나

| 모드 | 하는 일 |
|---|---|
| 작성 | 메모·요점을 받아 해당 문서 유형의 골격과 어투로 작성 |
| 윤문 | 일반·AI 문장을 실무 문체로 변환 (수치·사실은 유지) |
| 점검 | 용어·단위·종결어미 위반을 목록으로 지적 |

문서 유형마다 어투가 다릅니다. 스킬은 유형을 먼저 정하고 그 규칙만 적용합니다.

| 유형 | 예시 종결 |
|---|---|
| 보고서 본문 | ~한다, ~하였다, ~것으로 판단된다, ~실정이다 |
| 설계기준·시방 | ~을 원칙으로 한다, ~에 따른다, ~할 수 있다 |
| 보고 장표·협의자료 | ~수립, ~검토, ~필요 (□ ○ - · 개조식) |
| 검토의견서 | ~제시 필요, ~불일치, ~수정바람 |
| 조치계획·결과서 | ~반영하였음, ~제시하였음 |
| 설계VE 제안 | ~변경하자, ~최적화하자 |
| 발표 시나리오 | ~보고 드리겠습니다, ~되겠습니다 |
| 내부 메일 | ~공유드립니다, ~검토 부탁드립니다 |
| 공문(시행문) | ~제출하오니 검토하여 주시기 바랍니다. 끝. |
| 회의록·실정보고 | □ 일 시 :, ~하기로 함, → 발주처 의견 : |

## 예시

Before
> 이번 사업은 ○○읍 지역의 하수관로를 새로 설치하고 오래된 관을 교체하는 매우 중요한 프로젝트입니다. 이를 통해 주민들의 삶의 질이 획기적으로 향상될 것으로 기대됩니다.

After
> 금회 사업은 ○○읍 일원의 하수관로 신설 및 노후관로 개량을 위한 사업이다. 본 사업 시행 시 우·오수의 신속한 배제로 침수피해 예방 및 생활환경 개선에 기여할 것으로 판단된다.

더 많은 예시는 [examples.md](skills/civil-engineer-tone/references/examples.md)를 보세요.

## 설치

### Claude Code 플러그인 마켓플레이스

```
/plugin marketplace add ktr218/civil-engineer-tone
/plugin install civil-engineer-tone@civil-engineer-tone
```

### 수동 설치

`skills/civil-engineer-tone` 폴더를 스킬 폴더에 복사합니다.

- macOS/Linux: `~/.claude/skills/civil-engineer-tone`
- Windows: `%USERPROFILE%\.claude\skills\civil-engineer-tone`

```bash
git clone https://github.com/ktr218/civil-engineer-tone.git
cp -r civil-engineer-tone/skills/civil-engineer-tone ~/.claude/skills/
```

claude.ai에서 쓰려면 `skills/civil-engineer-tone` 폴더를 zip으로 묶어 설정 > 기능 > 스킬에서 업로드합니다.

### ChatGPT · Gemini (웹·앱)

[`prompts/universal.md`](prompts/universal.md)는 규칙, 용어, 예시를 한 파일(약 4,800자)로 압축한 지침입니다.

- **ChatGPT**: GPT 만들기 → 구성 → 지침 칸에 `universal.md` 내용을 그대로 붙여 넣습니다. 지침 한도 8,000자 안에 들어갑니다.
- **Gemini**: Gem 만들기 → 안내 칸에 같은 내용을 붙여 넣습니다.
- 맞춤 GPT·Gem을 만들기 어렵다면, 대화 첫 메시지로 붙여 넣고 "앞으로 이 지침대로 써줘"라고 해도 됩니다.
- 검사·자동교정 스크립트는 Python을 실행할 수 있는 환경에서만 동작합니다. 이 방식으로는 문체 규칙만 적용됩니다.

### Gemini CLI

```bash
gemini extensions install https://github.com/ktr218/civil-engineer-tone
```

`GEMINI.md`(= `prompts/universal.md` 사본)를 컨텍스트로 불러옵니다. 아직 실제 설치로 확인하지 않았습니다.

## 사용

자연어로 요청하면 됩니다.

- "이 문단 엔지니어 보고서체로 바꿔줘"
- "메모 줄 테니 착수보고 장표 문구로 개조식 정리해줘"
- "이 검토의견에 대한 조치결과 써줘"
- "보고서 용어랑 단위 점검해줘"

스크립트만 따로 쓸 수도 있습니다(Python 3.10+, 표준 라이브러리만 사용).

```bash
# 문서 유형 자동 판별 + 위반 목록 + 등급(A~D)
python skills/civil-engineer-tone/scripts/check_tone.py draft.md

# 단위·수치 표기 자동 교정 (기본은 변경 목록만 출력, --write로 반영)
python skills/civil-engineer-tone/scripts/fix_notation.py draft.md --write
```

출력 예

```
[유형 R(자동)] 등급 D | 위반 12건 (S1 6, S2 3, S3 3) | 500자당 37.5점
  1) END   S1    1행 " 프로젝트입니다" → 명사형 / 평서형(~다)
       유형 R에 맞지 않는 종결: 경어체(~니다)
  8) U-01  S2    2행 "0 m3/day" → ㎥/일 [자동교정]
```

등급은 500자당 가중 점수(S1 5점, S2 2점, S3 0.5점)로 매깁니다: A < 0.5 ≤ B < 1.5 ≤ C < 3.0 ≤ D.

## 검증

- 실무 문서 본문 약 340건으로 규칙과 유형 자동 판별을 보정했습니다. 원문은 저장소에 포함하지 않습니다.
- 실무 문서 306건을 검사기에 넣으면 88%가 A등급으로 나옵니다(사람이 쓴 문서를 잘못 지적하지 않는지 확인하는 기준).
- 다른 부문(도로·철도·하천·환경평가·항만·구조·지반·도시·에너지·CM) 실무 문서 409건에서도 86%가 A등급, 92%가 B등급 이상으로 나와 공통 규칙이 전 부문에 맞는 것을 확인했습니다.
- `tests/`에 유형별 가상 샘플과 회귀 테스트가 있습니다.

```bash
python -m unittest discover -s tests -v
```

## 구성

```
skills/civil-engineer-tone/
├── SKILL.md                      # 절차·규칙·체크리스트
├── references/
│   ├── style-taxonomy.md         # 문체 패턴 카탈로그 (A~K, ID·심각도)
│   ├── glossary.md               # 전 부문 공통 용어, 일반어→실무어
│   ├── divisions/                # 부문별 용어 팩 (water, transport, infra, urban, energy, cm, support)
│   ├── units-and-notation.md     # 단위·금액·날짜·표·인용 표기
│   ├── document-templates.md     # 유형별 문서 골격
│   ├── phrasebank.md             # 상황별 상투구
│   ├── examples.md               # Before/After
│   └── lexicon.json              # 어휘집 (자동교정 표기 + 문맥 판단 용어)
└── scripts/
    ├── tonelib.py                # 공통 엔진 (유형 판별·검사·등급·교정)
    ├── check_tone.py             # 검사기 CLI
    └── fix_notation.py           # 표기 자동 교정 CLI
tests/                            # 회귀 테스트와 유형별 샘플
prompts/universal.md              # ChatGPT·Gemini용 통합 지침 (한 파일)
GEMINI.md, gemini-extension.json  # Gemini CLI 확장
```

## 원칙

- 수치·사업명·근거는 사용자가 준 것만 씁니다. 없으면 `○○`, `[확인 필요]`로 남깁니다.
- 업계에서 굳은 표현(`~에 의거하여`, `Sheet Pile`, `OPEN CUT`)은 번역투로 보지 않고 유지합니다.
- 예시의 지명·수치는 가상입니다.

## 부문별 기여 방법

- 부문 담당자는 `division/<부문>` 브랜치(예: `division/transport`)에서 `references/divisions/<부문>.md`를 실제 성과품과 대조해 고칩니다.
- 고친 뒤 main으로 PR을 보내면 검토 후 합칩니다. 공통 규칙(끝맺음·기호·단위)은 main에서만 고칩니다.
- 원문·사업명·실제 수치는 올리지 않습니다.

## 기여

새 패턴은 `style-taxonomy.md`의 해당 범주 끝 번호로 추가하고, `examples.md`에 Before/After를 함께 넣어 주세요.

## 라이선스

MIT
