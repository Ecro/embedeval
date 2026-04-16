---
type: plan
project: embedeval
task_slug: launch-embedeval-public
status: planning
created: 2026-04-16
tags: [embedeval, plan, python, launch, marketing, documentation]
related:
  - "[[docs/METHODOLOGY]]"
  - "[[docs/BENCHMARK-COMPARISON-2026-04-05]]"
  - "[[docs/BENCHMARK-n3-haiku]]"
  - "[[docs/BENCHMARK-n3-sonnet]]"
  - "[[docs/LLM-EMBEDDED-CONSIDERATIONS]]"
  - "[[~/edgelog/src/content/blog/llm-firmware-failure-patterns]]"
  - "[[~/edgelog/src/content/blog/llm-firmware-trust]]"
summary: "EmbedEval 벤치마크를 2주 안에 글로벌+한국 채널에 동시 공개. 오늘 모든 코드/문서 자산 정비 완료, D-Day=Day 8."
---

# PLAN: launch-embedeval-public

**Project:** embedeval
**Task:** 233-case LLM 임베디드 벤치마크 EmbedEval을 D-Day에 영어권(HN/Reddit/Twitter/Zephyr Discord/HF Space)에 동시 공개. 한국 채널과 LinkedIn은 sustain 단계로 유보.
**Priority:** High
**Due:** 2026-04-20 (5 days, compressed)
**Created:** 2026-04-16

---

## 🎯 Executive Summary

> **TL;DR:** EmbedEval을 5일 안에 공개한다. Day 1(오늘 화) 모든 코드·문서·시각자산을 정비 완료, Day 2-3(수목) EdgeLog 영문 글 + HF Space 배포 + GIF, Day 4(금) 마지막 다듬기 + 리허설, **Day 5 = D-Day (월 04-20 KST 21시)**, Day 6-11(화~일) sustain. D-Day는 영어권 채널(HN/Reddit/Twitter/Zephyr Discord/HF)만, LinkedIn과 한국 채널은 sustain 단계로.

> **변경사항 (사용자 답변 반영):** arXiv 제외, 외부 엔지니어 피드백 제외, **한국 채널 + LinkedIn은 D-Day에서 제외**, HF username = `ecro`, 헤드라인 톤 = 중립, ROADMAP에서 GPT/Gemini는 모호하게.

### What We're Doing
EmbedEval 벤치마크의 공개 launch 캠페인. 코드 자체는 이미 완성. 부족한 것은 (1) 외부에서 5초 안에 가치를 인지할 시각 자산, (2) 인터랙티브 leaderboard, (3) 채널별 카피, (4) arXiv tech report. 이걸 2주 안에 만들고 단일 D-Day에 동시 발사한다.

### Why It Matters
EmbedEval의 핵심 인사이트("Implicit Knowledge Gap = 35%p")는 LLM 코딩 벤치마크 전반에 영향이 있는 발견. 하지만 발표 타이밍·채널·헤드라인을 놓치면 EmbedAgent(ICSE'26) 같은 기존 벤치 그늘에 묻힌다. 동시에 EdgeLog 블로그가 이미 EmbedEval 데이터를 인용하는 글들을 시리즈로 깔아 둔 상태 — launch와 결합하면 신뢰성 백킹이 즉시 작동한다.

### Key Decisions
- **Decision 1:** 모델은 **Sonnet 4.6 + Haiku 4.5만** 발표. ROADMAP에는 "추가 모델 평가 예정"으로 모호하게만 (GPT/Gemini 명시 안 함). "Anthropic 모델만"의 비판은 "n=3 통계 신뢰성 우선" 메시지로 방어.
- **Decision 2:** **EdgeLog 블로그를 발표 채널이 아닌 신뢰성 백킹으로** 활용. Day 2(수)에 시리즈 3편으로 "Introducing EmbedEval" 발행 → SEO + D-Day 시 "이미 데이터를 써온 사람" 자세 확보.
- **Decision 3:** **D-Day = Day 5 (2026-04-20 월, KST 21시 = ET 월 08시)**. 사용자 요청 "최대한 빠르게" 반영. 월요일은 HN 알고리즘 좋은 요일 + 한 주 트래픽 받음. 발사 후 첫 5시간 댓글 응답 전담 (사용자 일정 확보 OK).
- **Decision 4:** **arXiv 제외** (사용자 결정). docs/PAPER.md 작업도 제외. 학술 인용은 GitHub URL + future work으로 둠. v0.2에서 재고.
- **Decision 5:** **HF Space는 `huggingface.co/spaces/ecro/embedeval`**. Gradio + 정적 leaderboard + heatmap. 자동 평가 파이프라인은 v0.2.
- **Decision 6:** **헤드라인 톤 = 중립**. "30% worse" 같은 자극적 표현 금지. "implicit knowledge gap", "5-layer evaluation pipeline" 같은 중립적/기술적 표현 사용.
- **Decision 7:** **외부 임베디드 엔지니어 피드백 단계 제외** (사용자 결정). Day 4 일정 단축됨.

### Estimated Impact
- **Complexity:** Medium-Low (arXiv/외부 피드백 빠져 단순화)
- **Risk Level:** Low (코드 변경 거의 없음, 주로 문서/자산/카피)
- **Files Changed:** ~13 files (PAPER.md 제외)
- **Estimated Time:** 5일 calendar / ~20 active hours

---

## ✅ User Decisions (RESOLVED)

> 사용자 답변으로 모두 확정됨. /execute 진행 가능.

| 항목 | 결정 |
|------|------|
| 모델 범위 | ✅ Sonnet + Haiku만. ROADMAP에 GPT/Gemini는 **모호하게**만 ("추가 모델 평가 예정") |
| D-Day 날짜 | ✅ **2026-04-20 (월) KST 21시** (= ET 월 08시). 사용자 요청 "최대한 빠르게" 반영 |
| HF Space username | ✅ `ecro` → `huggingface.co/spaces/ecro/embedeval` |
| 헤드라인 톤 | ✅ **중립** ("implicit knowledge gap", "5-layer pipeline"). "30% worse" 같은 직설 금지 |
| arXiv | ✅ **제외**. docs/PAPER.md 작업 제외. v0.2 future work |
| D-Day 일정 (KST 21-02시) | ✅ 확보 |
| 외부 엔지니어 피드백 | ✅ **제외**. Day 4 일정 단축 |
| EdgeLog 영/한 동시 발행 | ✅ 시리즈 3편으로 (`series: ai-written-firmware`, `seriesOrder: 3`) |

### Remaining Quality Gates (자동 체크)
- [ ] reference solution 회귀: `uv run pytest`, `uv run embedeval validate --cases cases/`
- [ ] HF Space 로컬 검증: `cd space && python app.py` → localhost:7860 정상
- [ ] EdgeLog 빌드: `cd ~/edgelog && npm run build` 성공
- [ ] sync_docs 일관성: `uv run python scripts/sync_docs.py`

---

## 📚 Prior Work (Knowledge Retrieval)

### Related Documents Found
- [[plans/PLAN-paper-level-benchmark.md]] — 학술 publication 준비 작업. arXiv 양식 일부 재활용 가능
- [[plans/PLAN-remaining-blindspots.md]] — 벤치 부족점 분석. "약점은 솔직히 ROADMAP에 명시" 메시지 백업
- [[docs/BENCHMARK-COMPARISON-2026-04-05.md]] — n=3 결과 + EmbedAgent 비교 표. 발표 자료 핵심 소스
- [[docs/BENCHMARK-n3-haiku.md]] / [[docs/BENCHMARK-n3-sonnet.md]] — 통계 (mean, CI, stability) 출처
- [[docs/LLM-EMBEDDED-CONSIDERATIONS.md]] — "Implicit Knowledge Gap" 인사이트의 가장 풍부한 소스
- [[~/edgelog/src/content/blog/llm-firmware-failure-patterns.mdx]] — 이미 EmbedEval 데이터 인용 중. 톤 참고 + 내부 링크 활용
- [[~/edgelog/src/content/blog/llm-firmware-trust.mdx]] — 35%p gap 첫 언급. soft launch 글에서 인용

### What Worked Before
- **EdgeLog 블로그의 톤:** "experiment first, write second" + 솔직한 한계 표기 + 시리즈 구조 — 신뢰감 높임. launch 글도 동일 톤 유지
- **n=3 통계 표기:** mean ± stdev + 95% CI + Wilson score — 외부 비판("작은 샘플") 즉시 차단
- **5-layer architecture diagram:** METHODOLOGY의 ASCII 다이어그램이 Twitter/X 카드용으로도 강함
- **EmbedAgent 비교 표:** README에 이미 1줄 비교 있음 — 발표 시 더 강조

### Known Blockers & Solutions
- **L3 regex 휴리스틱 비판** (SWE-bench Verified 댓글 패턴) → mutation testing 메타 검증 결과(L4)를 미리 강조
- **Zephyr 81% 편향** → ROADMAP에 "FreeRTOS 확장 v0.2" 명시
- **모델 2개만** → "n=3로 통계 신뢰성 확보 우선, 모델 확장은 contributor PR welcome" 메시지
- **arXiv endorsement 필요할 수 있음** → 미리 endorser 알아보기 (ICSE'26 EmbedAgent 저자, Princeton SWE-bench 저자 등 LinkedIn 시도)

### Decisions to Reuse/Reconsider
- 결과 summary는 git에 트래킹, 상세 details/는 gitignore — 이미 정해진 정책. Launch에도 유지
- Public/private repo 분리 (contamination prevention) — Launch의 USP 중 하나. 강조

---

## 📋 Problem Analysis

### What
EmbedEval 벤치마크를 글로벌·한국 14일 동시 공개. 부족한 launch 자산(시각·인터랙티브·카피·tech report)을 만들고, 단일 D-Day에 7+ 채널 동시 발사, 첫 일주일 댓글 응대로 momentum 유지.

### Why
1. **EmbedAgent (ICSE'26)이 곧 더 알려짐** — EmbedEval이 차별화된 USP(implicit knowledge focus, 5-layer, multi-platform)를 가지고 있어도 늦으면 묻힘
2. **Sonnet/Haiku n=3 결과가 신선함** — 한 달 지나면 모델이 새로 나와서 데이터 가치 떨어짐
3. **EdgeLog 블로그가 이미 EmbedEval 데이터를 인용 중** — launch와 결합하면 즉시 신뢰성 확보, 늦으면 블로그와 벤치가 따로 노는 인상
4. **임베디드 LLM 안전성 담론이 활발** (RunSafe, AdaCore, helpnetsecurity 2026년 초 글들) — 여기에 데이터 기반으로 끼어들 시점

### Success Criteria
- [ ] D-Day +7일 시점에 GitHub Stars 100+ 또는 HN frontpage 진입
- [ ] D-Day +7일 시점에 외부 PR/Issue 5건+ (참여 시그널)
- [ ] D-Day +7일 시점에 Reddit 3개 서브레딧 합산 댓글 30건+
- [ ] D-Day +14일 시점에 1개 이상의 외부 글/언급 (TechCrunch / Embedded.com / Hackster / 임베디드 블로거)
- [ ] D-Day +14일 시점에 Twitter thread 1K+ impressions, 50+ engagements
- [ ] 모든 launch 자산이 repo에 commit되어 향후 재사용 가능

---

## 🔍 Code Review

### Current State (이미 있는 자산)
- **벤치 코드:** 16 모듈, 1277 테스트, 233 케이스 — 완성
- **결과:** Sonnet n=3 (68.0%, CI [64.4, 71.3]), Haiku n=3 (56.9%, CI [53.2, 60.6]) — 통계 신뢰성 OK
- **문서:** README, METHODOLOGY, BENCHMARK-COMPARISON, BENCHMARK-n3-{haiku,sonnet}, LLM-EMBEDDED-CONSIDERATIONS, FAILURE-FACTORS, DEVELOPMENT-GUIDE — 풍부
- **블로그 (~/edgelog):** 18개 글 (영/한 ko 페어), `llm-firmware-failure-patterns`, `llm-firmware-trust`가 이미 EmbedEval 데이터 사용 중
- **CI/test infra:** GitHub Actions, ruff, mypy, pytest — 유지

### Affected Components (Launch에서 신규 또는 수정)
| 카테고리 | 파일 | 동작 |
|---|---|---|
| Repo 루트 | `README.md` | 상단에 hero image, EmbedAgent 비교 강화, "Implicit Gap" 섹션 시각화 |
| Repo 루트 | `ROADMAP.md` (신규) | FreeRTOS 확장, GPT/Gemini 평가, agent 모드 v0.2 등 명시 |
| 문서 | `docs/METHODOLOGY.md` | Sensitivity / L4 mutation testing 별도 섹션으로 부각 |
| 자산 | `assets/launch/heatmap.png` (신규) | 23 카테고리 × 2 모델 heatmap |
| 자산 | `assets/launch/implicit-gap.png` (신규) | explicit 95% vs implicit 60% 그래프 |
| 자산 | `assets/launch/architecture.png` (신규) | 5-layer pipeline 다이어그램 |
| 자산 | `assets/launch/demo.gif` (신규, Day 2-3) | 30초 CLI 데모 |
| 자산 | `assets/launch/twitter-card.png` (신규) | Twitter card용 1200×630 |
| 자산 생성 | `scripts/generate_launch_assets.py` (신규) | matplotlib로 위 PNG 자동 생성 |
| HF Space | `space/app.py` (신규) | Gradio leaderboard + heatmap |
| HF Space | `space/requirements.txt` (신규) | gradio, plotly |
| 카피 | `LAUNCH-COPY.md` (신규) | HN/Reddit/Twitter/Zephyr Discord (D-Day) + LinkedIn (sustain) 카피 모음 |
| 블로그 (~/edgelog) | `src/content/blog/introducing-embedeval.mdx` (신규) | 영문 launch 글 |
| Repo 루트 | `CONTRIBUTING.md` | "good first issue" 라벨링 + PR 템플릿 다듬기 |
| Repo 루트 | `.github/ISSUE_TEMPLATE/` (점검) | 모델 추가 요청, 케이스 추가 요청 템플릿 추가 |

### Dependencies
- 시각자산: `matplotlib` + `seaborn` (이미 dev deps에 있을 가능성, 없으면 dev-only로 추가)
- HF Space: `gradio>=4.0` (HF Space에서만, 메인 의존성에는 추가 안 함)
- GIF 녹화: `asciinema` + `agg` (asciinema-gif), 또는 OBS — 수동 작업
- (제외) arXiv tech report — 사용자 결정으로 v0.2로 미룸

---

## 🏗️ Technical Design

### Architecture (Launch Asset Pipeline)

```
┌──────────────────────────────────────────────────────────────┐
│  Source of Truth (이미 있음)                                  │
│  - results/LEADERBOARD.md, results/runs/*/                   │
│  - docs/BENCHMARK-n3-*.md, METHODOLOGY.md                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  scripts/generate_launch_assets.py                           │
│  - heatmap (23 cat × 2 models)                               │
│  - implicit gap bar chart                                    │
│  - architecture diagram (matplotlib)                         │
│  - twitter card composite                                    │
│  → assets/launch/*.png                                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────────────┬──────────────┐
       ▼               ▼                       ▼              ▼
┌─────────────┐ ┌─────────────┐       ┌────────────┐  ┌──────────┐
│ README.md   │ │ space/app.py│       │ ~/edgelog/ │  │ LAUNCH-  │
│ (hero img)  │ │ (HF Space)  │       │ blog글     │  │ COPY.md  │
└─────────────┘ └─────────────┘       │ (영/한)    │  │ (채널별) │
                                       └────────────┘  └──────────┘
                                              │              │
                                              └──────┬───────┘
                                                     ▼
                                       ┌────────────────────────┐
                                       │ D-Day Launch (Day 5)   │
                                       │ 2026-04-20 (월) 21시    │
                                       │ HN / Reddit / Twitter / │
                                       │ Zephyr Discord / HF     │
                                       └────────────────────────┘
```

### Design Decisions

1. **Decision: 시각자산은 matplotlib 스크립트로 자동 생성**
   - **Rationale:** 데이터가 갱신되면 `python scripts/generate_launch_assets.py` 한 번에 모든 PNG 재생성. PNG 자체는 git에 commit (CI에서 빌드 안 함)
   - **Alternatives:** 수동 Figma/Affinity 디자인 → 데이터 변경 시 재작업 비용 큼

2. **Decision: arXiv 제외 (사용자 결정)**
   - **Rationale:** D-Day 최단화 우선. 학술 신뢰성은 EdgeLog 시리즈 + GitHub README의 BibTeX/citation 블록으로 대체. v0.2에서 재고
   - **Alternatives:** 4-6쪽 tech report 작성 → 1-2일 추가, D-Day 늦춰짐

3. **Decision: HF Space = 정적 leaderboard (자동 평가 파이프라인 X)**
   - **Rationale:** v0.2까지 미룸. 일단 "공식 인터랙티브 페이지"의 형식만 갖추면 인지효과 충분
   - **Alternatives:** 외부 모델 자동 평가 → API 비용/security 책임 큼, v0.1에 부적절

4. **Decision: EdgeLog launch 글 = "시리즈 3편" 포지션**
   - **Rationale:** 기존 시리즈(`llm-firmware-trust` → `failure-patterns`)의 "공식 데이터셋" 글로 자연스럽게 이어감. 신규 독자도 이전 글 따라 읽음 (SEO + retention)
   - **Alternatives:** 독립 글 → 시리즈 신뢰성 백킹 효과 약화

5. **Decision: D-Day Launch = 단일 시점 동시 발사 (10분 간격 순차)**
   - **Rationale:** HN 알고리즘 + Reddit 알고리즘 모두 첫 1시간 momentum 중요. 분산하면 약화
   - **Alternatives:** 채널별 분산 launch → 추적 복잡, momentum 분산

6. **Decision: 한국 채널 + LinkedIn은 D-Day에서 제외, sustain 단계로 유보 (사용자 결정)**
   - **Rationale:** D-Day 첫 5시간은 HN/Reddit 댓글 응답에 집중. 채널 수를 늘릴수록 응답 품질이 떨어짐. 한국 채널과 LinkedIn은 D-Day 결과를 본 뒤 톤을 조정해 게시
   - **Alternatives:** 동시 발사 → 응답 부담 분산

### Data Flow
1. 결과 데이터 (`results/`) → matplotlib 스크립트가 PNG 자산 생성
2. PNG → README, EdgeLog 글, HF Space, Twitter card에 임베드
3. PNG + docs → arXiv tech report로 합쳐짐
4. 모든 자산 → LAUNCH-COPY.md의 카피 템플릿이 참조
5. D-Day → 카피 + 자산 + 링크 한 세트로 채널별 발사

### API Changes
없음. 라이브러리 외부 인터페이스 변경 없음.

---

## 📝 Implementation Plan

### Phase 1 — Day 1 (오늘 04-16 화): 모든 코드/문서/시각 자산 정비

> 사용자 요청 핵심: "오늘 고칠 수 있는 것들은 모두 고칠거야"

#### 1.1 ROADMAP.md 신규 작성
- [ ] `ROADMAP.md` 신규: v0.2(추가 모델 평가, FreeRTOS 확장, HF Space 자동 평가, arXiv tech report), v0.3(agent 모드 확장, FPGA), v1.0 비전
- [ ] **GPT/Gemini는 명시 안 함** (모호하게 "Expand model coverage" 정도)
- [ ] README에서 ROADMAP 링크 + "Known Limitations" 섹션과 연결

#### 1.2 README.md 업그레이드
- [ ] 상단에 hero image 자리 (heatmap PNG) — 이미지 생성 후 link
- [ ] "Key Insight" 섹션을 더 시각적으로 (현재 텍스트 → 짧은 표 + 강조)
- [ ] EmbedAgent 비교를 1단락으로 강화 (왜 다른가 명확히)
- [ ] CTA 강화: "Star · Try · PR" 3-단 버튼
- [ ] "Known Limitations" → ROADMAP.md 링크
- [ ] Cite this work 섹션 추가 (BibTeX)

#### 1.3 METHODOLOGY.md 보완
- [ ] L3 휴리스틱 검증 메커니즘(L4 mutation testing) 별도 섹션으로 부각 (현재 묻혀있음)
- [ ] Sensitivity 분석 결과를 결과 섹션으로 끌어올림 (있으면)
- [ ] "Why this benchmark is hard to game" 1단락 추가 (private repo + temporal cutoff + L4)

#### 1.4 ~~docs/PAPER.md~~ — **제외** (사용자 결정, v0.2로)

#### 1.5 scripts/generate_launch_assets.py 신규
- [ ] `assets/launch/heatmap.png` — 23 cat × 2 models (Sonnet/Haiku) heatmap, RdYlGn 컬러맵
- [ ] `assets/launch/implicit-gap.png` — explicit prompt vs implicit prompt 35%p 그래프
- [ ] `assets/launch/architecture.png` — 5-layer pipeline 다이어그램 (METHODOLOGY ASCII를 그래픽으로)
- [ ] `assets/launch/twitter-card.png` — 1200×630 composite (heatmap 축소 + 핵심 숫자)
- [ ] `assets/launch/model-comparison.png` — Sonnet vs Haiku n=3 mean + CI bar chart

#### 1.6 LAUNCH-COPY.md 신규 (채널별 카피 모음, **모든 헤드라인 중립 톤**)
- [ ] HN headline 후보 3개 ("implicit knowledge gap" 중심) + body
- [ ] Reddit r/embedded post (영문, 겸손 톤, 자극 표현 없음)
- [ ] Reddit r/LocalLLaMA post (영문, 데이터 톤)
- [ ] Reddit r/MachineLearning post (영문, 학술 톤)
- [ ] Twitter thread 8 트윗 초안 (중립)
- [ ] Zephyr Discord 안내문
- [ ] LinkedIn post (영문, sustain 단계용 — D-Day 결과를 인용해서 게시)

#### 1.7 space/ 디렉토리 신규 (HF Space 코드, target: `huggingface.co/spaces/ecro/embedeval`)
- [ ] `space/app.py` — Gradio: leaderboard 표 + heatmap + 모델 선택 드롭다운
- [ ] `space/requirements.txt` — gradio, plotly, pandas
- [ ] `space/README.md` — HF Space frontmatter (title: EmbedEval, emoji: 🔧, sdk: gradio)
- [ ] 로컬 검증: `cd space && python app.py` → localhost:7860

#### 1.8 .github/ISSUE_TEMPLATE/ 정비
- [ ] `model-evaluation-request.md` — 새 모델 평가 요청 템플릿
- [ ] `case-contribution.md` — 새 케이스 제안 템플릿
- [ ] `methodology-question.md` — 방법론 질문 템플릿

#### 1.9 CONTRIBUTING.md 다듬기
- [ ] "good first issue" 후보 3-5개 GitHub Issue로 미리 만들기 (Day 8 launch 시 외부 기여자 유도)
- [ ] 케이스 추가 워크플로우 더 친절하게

#### 1.10 sync_docs.py 실행 + 회귀 검증
- [ ] `uv run python scripts/sync_docs.py`
- [ ] `uv run pytest`
- [ ] `uv run embedeval validate --cases cases/`
- [ ] 모두 통과 확인 후 commit

### Phase 2 — Day 2 (04-17 수): EdgeLog 글 영/한 작성

#### 2.1 EdgeLog launch 글 (영문)
- [ ] `~/edgelog/src/content/blog/introducing-embedeval.mdx` 신규
- [ ] 시리즈 3편으로 묶기 (`series: ai-written-firmware`, `seriesOrder: 3`)
- [ ] 기존 글 (`llm-firmware-trust`, `failure-patterns`) 내부 링크
- [ ] hero image: `assets/launch/heatmap.png` (또는 `implicit-gap.png`)
- [ ] 톤: 기존 EdgeLog 톤 (직설적, 데이터 중심, 솔직한 한계). 헤드라인은 중립
- [ ] 빌드 검증: `cd ~/edgelog && npm run build`

#### 2.2 publish — Day 2 저녁
- [ ] git push → 블로그 배포 (영문 단독)
- [ ] RSS 트리거 확인

### Phase 3 — Day 3 (04-18 목): HF Space 배포 + 데모 GIF

#### 3.1 HF Space 배포 (`huggingface.co/spaces/ecro/embedeval`)
- [ ] HF 계정 로그인 확인
- [ ] `ecro/embedeval` Space 생성 (sdk: gradio)
- [ ] `space/` 내용 push
- [ ] 배포 검증: 브라우저에서 정상 접근

#### 3.2 데모 GIF 녹화
- [ ] `asciinema rec demo.cast` → `agg demo.cast assets/launch/demo.gif`
- [ ] 30초 안에: clone → uv sync → embedeval list → embedeval run mock → cat LEADERBOARD
- [ ] README와 EdgeLog 글에 임베드 (커밋)

#### 3.3 작은 네트워크 공유 (선택)
- [ ] Zephyr Discord (#general or #ml channel) — soft 노출
- [ ] 친분 있는 채널만, 압박 없이

### Phase 4 — Day 4 (04-19 금): 마지막 다듬기 + 리허설

#### 4.1 모든 링크/자산 점검
- [ ] GitHub repo public, README 모든 이미지 정상
- [ ] HF Space 접근 정상
- [ ] EdgeLog 영/한 글 published, 내부 링크 정상
- [ ] LAUNCH-COPY.md의 모든 외부 링크 동작

#### 4.2 헤드라인 최종 확정
- [ ] HN 헤드라인 후보 3개 중 1개 선택
- [ ] Twitter 첫 트윗 확정

#### 4.3 D-Day 시간표 확정
- [ ] 일정표 마지막 점검 (T+0, T+5min, T+10min ... T+2hr)
- [ ] 모든 채널의 카피를 클립보드로 옮길 순서 정리
- [ ] 04-20 (월) KST 21시-02시 일정 비어있는지 다시 확인

### Phase 5 — Day 5 (04-20 월) 🚀 D-Day Launch

#### 5.1 D-Day 동시 발사 (KST 21시 = ET 월 08시)
- [ ] T+0 (21:00): HF Space 활성화 최종 확인
- [ ] T+5min (21:05): **Show HN 포스트** (중립 헤드라인)
- [ ] T+10min (21:10): Twitter thread 8 트윗 (첫 트윗에 heatmap)
- [ ] T+25min (21:25): Reddit r/embedded
- [ ] T+30min (21:30): Reddit r/LocalLLaMA
- [ ] T+35min (21:35): Reddit r/MachineLearning
- [ ] T+50min (21:50): Zephyr Discord + 임베디드 슬랙 그룹

(LinkedIn / 한국 채널 / Disquiet은 sustain 단계로 유보)

#### 5.2 첫 5시간 댓글 응답 전담 (21:00 - 02:00 KST)
- [ ] HN 모든 댓글 1-2시간 안에 응답 (가장 우선)
- [ ] Reddit 모든 댓글 응답
- [ ] Twitter 멘션/RT에 응답
- [ ] 비판은 GitHub Issue로 변환 + 친절한 답변
- [ ] 다른 일은 금지

### Phase 6 — Day 6-11 (04-21~26 화~일): Sustain & Iterate

#### 6.1 빠른 fix → 공개 (Day 6-7 화수)
- [ ] D-Day 댓글에서 나온 P0 버그 빠르게 fix → 변경 로그를 트윗으로 advertise
- [ ] PR 받으면 24시간 안에 merge or 친절한 피드백

#### 6.2 후속 콘텐츠 (Day 8-9 목금)
- [ ] EdgeLog 후속 글: "How EmbedEval was built — what surprised me"
  - 시리즈 4편 또는 별도 reflection
  - 톤: 메타적, 회고적, 다음 작업 예고
  - 두 번째 round HN 진입 가능 (week-old projects도 잘 통함)

#### 6.3 모델 회사 연구자 outreach (Day 8-10)
- [ ] LinkedIn DM: Anthropic embedded/coding eval 담당자
- [ ] LinkedIn DM: 임베디드 LLM 관심자 (EmbedAgent 저자 등)

#### 6.4 한국 컨퍼런스/밋업 발표 신청 (Day 10-11 토일)
- [ ] KOSSCON, Embedded Korea Conference, Zephyr Korea 미팅 신청
- [ ] 발표 슬라이드는 LAUNCH-COPY.md + 시각자산 재활용

#### 6.5 매트릭 수집 + retrospective (Day 11)
- [ ] GitHub Stars/Forks/Issues/PRs 추이
- [ ] HF Space 방문자 수
- [ ] Twitter impressions/engagements
- [ ] EdgeLog 글 페이지뷰
- [ ] retrospective 메모 → SESSION 또는 vault에 기록

---

## 🧪 Testing Strategy

### Unit/Regression Tests (Day 1)
- [ ] `uv run pytest` 모두 통과
- [ ] `uv run embedeval validate --cases cases/` 모두 통과
- [ ] `uv run python scripts/sync_docs.py` 실행 후 README/METHODOLOGY 카운트 일관성

### Visual Asset Tests (Day 1)
- [ ] 모든 PNG가 정상 생성됨 (`ls -la assets/launch/*.png`)
- [ ] heatmap의 셀 값이 LEADERBOARD.md와 일치
- [ ] implicit-gap.png의 95%/60% 값이 LLM-EMBEDDED-CONSIDERATIONS와 일치

### HF Space Tests (Day 1 local, Day 2-3 deployed)
- [ ] `cd space && python app.py` → localhost:7860 정상 로드
- [ ] 모든 인터랙티브 컴포넌트 동작 (드롭다운, 정렬)
- [ ] 배포 후 `huggingface.co/spaces/{user}/embedeval` 접근 정상

### EdgeLog Build Tests (Day 2)
- [ ] `cd ~/edgelog && npm run build` 성공
- [ ] 신규 글 영/한 모두 정상 렌더링
- [ ] 내부 링크가 깨지지 않음

### Manual D-Day Smoke Test (Day 4 저녁)
- [ ] GitHub repo public 상태 확인
- [ ] HF Space 정상
- [ ] EdgeLog 글 published 확인
- [ ] LAUNCH-COPY.md의 모든 링크가 작동
- [ ] 첫 5시간 일정 비어있는지 확인

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| HN/Reddit에서 묻힘 (frontpage 못감) | High | Medium | 헤드라인 후보 미리 준비, EdgeLog soft launch로 momentum 빌드, Twitter thread 즉시 보강 |
| "왜 GPT/Gemini 없냐" 비판 폭주 | Medium | High | ROADMAP "추가 모델 평가 예정" + "n=3 통계 신뢰성 우선, contributor PR welcome" 답변 준비 |
| L3 regex 휴리스틱 비판 | Medium | Medium | METHODOLOGY에 L4 mutation testing 결과 미리 강조, sensitivity 분석 결과 추가 |
| HF Space 배포 실패 | Low | Low | HF docs 미리 읽기, 안 되면 D-Day에 GitHub README의 정적 leaderboard로 대체 |
| reference solution 회귀 (자산 정비 중) | High | Low | Day 1 마지막에 `pytest` + `validate` 의무 |
| D-Day 첫 5시간 다른 일정 충돌 | High | Low | 사용자 확인 완료. Day 4에 다시 확인 |
| 비판 댓글에 감정적 반응 | Medium | Low | 모든 응답을 "감사합니다, 이슈로 트래킹하겠습니다" 톤으로 통일 |
| 한국 채널 sustain 단계로 미뤘다가 잊음 | Low | Medium | Day 11 retrospective 직후 KR 글 작성 일정 추가 |
| Day 5 (월) 발사 — 미국 공휴일 충돌 | Low | Very Low | 04-20은 미국 공휴일 아님 (확인). 한국도 평일 |

---

## ✅ Success Criteria

### Functional (Day 1 완료 시점, 오늘 화)
- [ ] ROADMAP.md, LAUNCH-COPY.md, space/app.py, scripts/generate_launch_assets.py 모두 commit
- [ ] assets/launch/ 에 PNG 5개 모두 생성 (heatmap, implicit-gap, architecture, twitter-card, model-comparison)
- [ ] README.md 업그레이드 commit (hero image, EmbedAgent 강화, CTA, BibTeX)
- [ ] METHODOLOGY.md 보완 commit
- [ ] .github/ISSUE_TEMPLATE/ 3개 템플릿 + good first issue 3-5개 생성
- [ ] `uv run pytest` + `uv run embedeval validate` 모두 통과

### Functional (Day 4 완료 시점, 금)
- [ ] EdgeLog launch 글 영/한 published
- [ ] HF Space 배포 + 정상 접근
- [ ] 데모 GIF 녹화 + 임베드
- [ ] D-Day 시간표 확정 + 일정 비움

### Outcome (Day 11 완료 시점, 일)
- [ ] GitHub Stars 100+ 또는 HN frontpage 진입 (택일)
- [ ] 외부 PR/Issue 5건+
- [ ] Reddit 3개 서브레딧 합산 댓글 30건+
- [ ] Twitter thread 1K+ impressions
- [ ] 1개 이상 외부 글/언급 (블로거, Embedded.com, Hackster 등)
- [ ] retrospective 메모 작성

---

## 📊 Estimated Effort

- **Complexity:** Medium-Low
- **Estimated Time:** 11일 calendar / ~20 active hours (Day 1: 6-8h, Day 2-3: 평균 2-3h, Day 4: 1-2h, Day 5: 6h, Day 6-11: 평균 1h)
- **Files Changed:** ~13 신규 + ~5 수정

---

## 🗓️ Day-by-Day Calendar (압축, 5일 만에 D-Day)

| Day | Date (KST) | 요일 | Focus | 핵심 산출물 |
|-----|------|------|-------|-----------|
| **Day 1** | **04-16 (오늘)** | **화** | **모든 자산 정비** | ROADMAP, LAUNCH-COPY, PNG 5개, HF Space 코드, README/METHODOLOGY 업그레이드, Issue 템플릿 |
| Day 2 | 04-17 | 수 | EdgeLog 영/한 글 작성 + publish | introducing-embedeval.mdx (영/한), git push |
| Day 3 | 04-18 | 목 | HF Space 배포 + 데모 GIF | `huggingface.co/spaces/ecro/embedeval` 라이브, demo.gif |
| Day 4 | 04-19 | 금 | 마지막 다듬기 + 리허설 | 모든 링크 점검, 헤드라인 확정 |
| **Day 5** | **04-20** | **월** | **D-Day Launch (KST 21시)** | HN / Reddit / Twitter / Zephyr Discord / HF |
| Day 6 | 04-21 | 화 | 댓글 응답 + 빠른 fix | P0 버그 fix, 변경 로그 트윗 |
| Day 7 | 04-22 | 수 | PR/Issue 응답 | 첫 외부 기여 환영 |
| Day 8 | 04-23 | 목 | 후속 콘텐츠 작성 | EdgeLog "How it was built" 초안 |
| Day 9 | 04-24 | 금 | 후속 콘텐츠 발행 + LinkedIn 게시 + outreach | retrospective 글 publish, LinkedIn 영문, LinkedIn DM |
| Day 10 | 04-25 | 토 | 한국 컨퍼런스 신청 | KOSSCON 등 |
| Day 11 | 04-26 | 일 | 매트릭 정리 + retrospective | 메모 → SESSION 또는 vault |

---

## 📌 Open Questions for User

> 모든 질문 ✅ 답변 완료. /execute 진행 가능.

1. ✅ **D-Day**: 2026-04-20 (월) KST 21시 — "최대한 빠르게" 반영
2. ✅ **HF username**: `ecro` → `huggingface.co/spaces/ecro/embedeval`
3. ✅ **헤드라인 톤**: 중립 ("implicit knowledge gap" 중심)
4. ✅ **arXiv**: 제외 (v0.2 future work). BibTeX는 GitHub URL 기반으로 README에 추가
5. ✅ **D-Day 일정 (KST 21-02시)**: 확보됨
6. ✅ **외부 엔지니어 피드백**: 제외 (Day 4 일정 단축)
7. ✅ **ROADMAP에 모델 추가**: 모호하게만 ("Expand model coverage in v0.2")
8. ✅ **arXiv endorsement**: 제외 (arXiv 자체 제외)
