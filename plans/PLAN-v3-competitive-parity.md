# PLAN: EmbedEval v3 — Competitive Parity with Leading Benchmarks

**Project:** embedeval
**Created:** 2026-03-25
**Source:** Insight #12 (Cross-Benchmark Competitive Analysis)

---

## Executive Summary

> **TL;DR:** 5가지 개선으로 EmbedEval을 EmbedBench/LiveCodeBench/SWE-bench 수준으로 끌어올린다.

### 현재 vs 목표

| 축 | 현재 | 목표 | 근거 |
|----|------|------|------|
| 코드 실행 | X (regex only) | **L1 빌드 CI + L2 native_sim 실행** | 모든 경쟁자가 실행 기반 |
| 오염 방지 | 20 private cases | **Temporal rotation** | LiveCodeBench gold standard |
| 재시도 | Single-shot | **Compiler feedback loop** | EmbedBench 전략 |
| 런타임 검증 | 없음 | **QEMU/native_sim 실행** | IoT-SkillsBench |
| 에이전트 평가 | 없음 | **Multi-turn agent mode** | SWE-bench |

---

## Feature 1: L1 Docker CI 통합

### 현재 상태
- Docker 이미지 빌드 성공 (Zephyr v4.1.0 + SDK)
- 15/15 카테고리 west build 성공 확인 (native_sim + nrf52840dk)
- 하지만 **벤치마크 실행 시 L1이 비활성** (Docker 밖에서 실행)

### 구현 계획

**Step 1: GitHub Actions workflow**
```yaml
# .github/workflows/benchmark.yml
name: Benchmark L1
on:
  workflow_dispatch:
    inputs:
      model: { type: string, default: "mock" }
jobs:
  build-and-eval:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/ecro/embedeval-zephyr:latest
    env:
      EMBEDEVAL_ENABLE_BUILD: "1"
    steps:
      - uses: actions/checkout@v4
      - run: uv sync && uv run embedeval run --model ${{ inputs.model }}
      - uses: actions/upload-artifact@v4
        with: { name: results, path: results/ }
```

**Step 2: Docker 이미지 CI 빌드 + 레지스트리 퍼블리시**
```yaml
# .github/workflows/docker.yml — ghcr.io/ecro/embedeval-zephyr
```

**Step 3: evaluator.py 보드 자동 선택**
```python
# case별 metadata.yaml에 build_board 필드 추가
# evaluator가 자동으로 적절한 보드 선택
build_board: native_sim  # 또는 nrf52840dk/nrf52840
```

**파일:**
- `.github/workflows/benchmark.yml` (신규)
- `.github/workflows/docker.yml` (신규)
- `cases/*/metadata.yaml` — `build_board` 필드 추가
- `src/embedeval/evaluator.py` — 보드 자동 선택 로직

**난이도:** Medium
**예상 시간:** 1일

---

## Feature 2: Temporal TC Rotation

### 근거
LiveCodeBench(ICLR'25)는 매월 새 문제를 추가하고, 모델의 cutoff date 이후
문제만으로 평가하여 오염을 방지. EmbedEval도 TC를 rotation하면 오염 위험 감소.

### 구현 계획

**Step 1: TC에 created_date 필드 추가**
```yaml
# metadata.yaml
created_date: "2026-03-24"
rotation_group: "2026-Q1"
```

**Step 2: CLI에 --after-date 필터**
```bash
embedeval run --model sonnet --after-date 2026-01-01
```

**Step 3: 분기별 10개 TC 추가 + 10개 은퇴(retire)**
- 은퇴된 TC는 `cases/retired/`로 이동
- 새 TC는 최신 API/패턴 사용
- 은퇴 기준: 모든 모델이 100% pass (변별력 없음)

**Step 4: 모델별 cutoff date 매칭**
```python
# external_benchmarks.yaml에 cutoff_date 추가
models:
  sonnet:
    cutoff_date: "2025-04-01"
    humaneval: 93.7
```

**파일:**
- `cases/*/metadata.yaml` — `created_date`, `rotation_group` 필드
- `src/embedeval/runner.py` — `--after-date` 필터
- `src/embedeval/cli.py` — 옵션 추가
- `external_benchmarks.yaml` — cutoff_date 필드

**난이도:** Low
**예상 시간:** 0.5일

---

## Feature 3: Compiler Feedback Mode

### 근거
EmbedBench(ICSE'26)는 LLM에게 컴파일 에러를 돌려주고 재시도할 기회를 줌.
이게 더 현실적 — 개발자도 한 번에 완벽한 코드를 쓰지 않음.

### 구현 계획

**Step 1: runner.py에 feedback loop 추가**
```python
for attempt in range(max_feedback_rounds):
    result = evaluate(case_dir, generated_code, model)
    if result.passed or result.failed_at_layer > 1:
        break  # L0/L1 통과하면 더 이상 feedback 불필요

    # L0 또는 L1에서 실패 → 에러를 LLM에게 돌려줌
    error_msg = result.layers[result.failed_at_layer].error
    feedback_prompt = f"Your code had the following error:\n{error_msg}\n\nPlease fix it."
    generated_code = call_model(model, feedback_prompt)
```

**Step 2: CLI 옵션**
```bash
embedeval run --model sonnet --feedback-rounds 3
```

**Step 3: 채점**
- `pass@1_no_feedback`: 기존 (1회 시행)
- `pass@1_with_feedback`: feedback 후 최종 결과
- 둘 다 리포트에 표시

**Step 4: Feedback 유형별 분류**
```python
class FeedbackType(Enum):
    COMPILE_ERROR = "compile"     # L1 실패 → 컴파일 에러 전달
    STATIC_HINT = "static"        # L0 실패 → 어떤 체크가 실패했는지 힌트
    RUNTIME_ERROR = "runtime"     # L2 실패 → 크래시/타임아웃 정보
```

**파일:**
- `src/embedeval/runner.py` — feedback loop 로직
- `src/embedeval/cli.py` — `--feedback-rounds` 옵션
- `src/embedeval/models.py` — FeedbackResult 모델
- `src/embedeval/reporter.py` — feedback 결과 표시

**난이도:** Medium
**예상 시간:** 1일

---

## Feature 4: QEMU/native_sim 실행 (L2 활성화)

### 근거
L1(빌드)만으로는 부족. 코드가 컴파일되지만 실행 시 크래시/hang/무한루프가
발생하는 경우를 잡으려면 L2(실행)가 필요.

### 현재 상태
- native_sim 빌드 성공 (7/15 카테고리)
- `west build -t run`으로 실행 가능
- 하지만 벤치마크에서 L2 실행 로직이 활성화 안 됨

### 구현 계획

**Step 1: native_sim 실행 + 출력 캡처**
```python
def _run_runtime(case_dir, generated_code, timeout):
    result = subprocess.run(
        ["west", "build", "-t", "run"],
        capture_output=True, text=True, timeout=timeout,
        cwd=str(case_dir),
    )
    # native_sim은 main() return 후 종료
    # 타임아웃 = 무한루프/데드락
    # 비정상 종료 = 크래시
```

**Step 2: 출력 기반 L2 검증**
```python
# reference solution의 expected output을 checks/expected_output.txt에 저장
# 실행 결과와 비교
expected = (case_dir / "checks" / "expected_output.txt").read_text()
actual = result.stdout
# 키워드 매칭 (정확 매칭은 너무 엄격)
for keyword in expected.strip().splitlines():
    if keyword.strip() not in actual:
        return FAIL
```

**Step 3: 타임아웃 처리**
```python
# 5초 타임아웃 — native_sim에서 정상 프로그램은 1초 이내 종료
# 타임아웃 = 무한루프, 데드락, 또는 k_sleep(K_FOREVER)
# k_sleep(K_FOREVER)는 의도적이므로, 출력에서 "OK" 키워드 확인 후 kill
```

**Step 4: expected_output.txt 생성**
- 레퍼런스 솔루션을 native_sim에서 실행하여 출력 캡처
- `cases/*/checks/expected_output.txt`에 저장

**파일:**
- `src/embedeval/evaluator.py` — L2 실행 로직 강화
- `cases/*/checks/expected_output.txt` — 예상 출력 (빌드 가능 TC만)
- `scripts/generate-expected-outputs.sh` — 배치 생성 스크립트

**난이도:** Medium
**예상 시간:** 2일

---

## Feature 5: Multi-turn Agent Mode

### 근거
SWE-bench는 agent가 repo를 탐색하고 코드를 수정하는 multi-turn 평가.
EmbedBench도 compiler feedback을 통한 multi-turn 지원.
현실의 개발자도 한 번에 완벽한 코드를 쓰지 않음 — 반복적 디버깅이 핵심.

### 구현 계획

**Step 1: Agent 인터페이스 정의**
```python
class EmbedEvalAgent:
    """Multi-turn embedded development agent interface."""

    def generate(self, prompt: str, context: list[str]) -> str:
        """Generate code from prompt + context (previous errors, docs, etc.)."""
        ...

    def debug(self, code: str, error: str) -> str:
        """Fix code given an error message."""
        ...
```

**Step 2: Agent 평가 루프**
```python
def evaluate_agent(agent, case_dir, max_turns=5):
    prompt = load_prompt(case_dir)
    context = []

    for turn in range(max_turns):
        code = agent.generate(prompt, context)
        result = evaluate(case_dir, code)

        if result.passed:
            return AgentResult(passed=True, turns=turn+1)

        # 실패 정보를 context에 추가
        error = format_error(result)
        context.append(f"Attempt {turn+1} failed: {error}")

    return AgentResult(passed=False, turns=max_turns)
```

**Step 3: CLI 모드**
```bash
# Single-shot (기존)
embedeval run --model sonnet

# Agent mode (신규)
embedeval agent --model sonnet --max-turns 5
```

**Step 4: 채점 메트릭**
- `pass@1_single`: 기존 single-shot
- `pass@agent_k5`: agent mode, 최대 5 turns
- `avg_turns_to_pass`: 통과까지 평균 턴 수
- `first_turn_pass_rate`: 1턴에 통과하는 비율 (= pass@1)

**Step 5: Claude Code 통합**
```python
# claude-code:// provider는 이미 single-prompt
# Agent mode: 여러 번 호출하면서 context를 누적
def agent_generate(model, prompt, context):
    full_prompt = prompt + "\n\n" + "\n".join(context)
    return call_model(model, full_prompt)
```

**파일:**
- `src/embedeval/agent.py` (신규) — Agent 인터페이스 + 평가 루프
- `src/embedeval/cli.py` — `agent` 서브커맨드
- `src/embedeval/models.py` — AgentResult 모델
- `src/embedeval/reporter.py` — agent 결과 표시

**난이도:** High
**예상 시간:** 3일

---

## Implementation Timeline

```
Week 1:
  Day 1: Feature 2 (Temporal rotation) — Low, 바로 시작 가능
  Day 2: Feature 1 (L1 Docker CI) — Docker 이미지 + GH Actions
  Day 3: Feature 3 (Compiler feedback) — runner.py 확장

Week 2:
  Day 4-5: Feature 4 (QEMU 실행) — expected_output + L2 활성화
  Day 6-8: Feature 5 (Agent mode) — 새 모듈 + CLI

Week 3:
  재벤치마크 (Sonnet + Haiku, all modes)
  결과 분석 + 논문 초안
```

---

## Success Criteria

| Feature | 완료 기준 |
|---------|----------|
| 1. L1 CI | GH Actions에서 `embedeval run --model mock` L1 15/15 pass |
| 2. Rotation | `--after-date` 필터 동작, 10개 TC에 created_date |
| 3. Feedback | `--feedback-rounds 3`으로 실행, pass@1 vs pass@feedback 비교 |
| 4. L2 실행 | native_sim에서 7/15 카테고리 실행 성공, expected_output 매칭 |
| 5. Agent | `embedeval agent --model sonnet --max-turns 5` 실행, 턴별 결과 |

---

## Expected Impact

| 메트릭 | 현재 | Feature 1+4 후 | Feature 3 후 | Feature 5 후 |
|--------|------|---------------|-------------|-------------|
| Sonnet pass@1 | 89.5% | **~75%** (빌드 실패 추가) | ~80% (feedback 후) | ~85% (agent) |
| Check coverage | L0+L3 only | **L0+L1+L2+L3** | 동일 | 동일 |
| 오염 위험 | 높음 | 동일 | 동일 | 동일 → Feature 2로 해결 |
| 경쟁력 | HumanEval 수준 | **SWE-bench 수준** | EmbedBench 수준 | **최고 수준** |
