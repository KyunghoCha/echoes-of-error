# 📅 연구 로드맵 (Academic Rigor v3.2)

---

## Phase 1: 개발 (Implementation)

### Step 1: 핵심 엔진 (Core Engine)

- [ ] `Agent` 클래스: Forced-choice (`INFORMATIONAL` vs `NORMATIVE`) 프롬프트 구현
- [ ] `Protocol` 모듈: **Top-k Random Sampling** 및 **Shuffle** 로직 고정
- [ ] `Scenario` 로더: 8개 시나리오 라이브러리 구축

### Step 2: 메트릭 & 로깅 (Metrics)

- [ ] 로그 스키마: `change_reason_forced` 필드 포함
- [ ] 분석기: **Entropy($H_t$)** 및 **Time-to-Collapse($\tau$)** 계산 함수 구현
- [ ] 검증기: Human Labeling용 샘플 추출 스크립트

---

## Phase 2: 실험 수행 (Execution)

### Main Experiments (20 Runs Each)

- [ ] **Exp 1 (Bias)**: S1(Trolley) + C1(Full) vs C2(Stance)
- [ ] **Exp 2 (Balance)**: S3(Self-Driving) + C1 vs C2

### Factorial Analysis (동인 분해)

- [ ] **Effect of Bandwagon**: Compare C3 (Anon-Bandwagon) vs **C4 (Pure-Info)**
- [ ] **Effect of Authority**: Compare C1 vs C3
- [ ] **Effect of Rationale**: Compare C1 vs C2

### Control Experiments (필수 대조군)

- [ ] **Ctrl 0 (Baseline)**: C0(Indep) 조건 실행 → Random Walk 기준선

---

## Phase 3: 분석 및 결과화 (Analysis)

- [ ] **Collapse Dynamics**: $H_t$ 변화 곡선 및 $\tau$ 통계(95% CI)
- [ ] **Driver Decomposition**: Authority vs Bandwagon vs Rationale 기여도 분석
- [ ] **Survival Analysis**: Kaplan-Meier 생존 곡선 (Event: Initial Stance 포기)
- [ ] **Validity Check**: GPT-4 vs Self-report 일치도(Kappa)

---

## Phase 4: 논문 작성 (Reporting)

1. **Introduction**: 정답 없는 딜레마에서의 붕괴 문제 제기
2. **Method**: C1~C4 요인 설계 및 Top-K 샘플링 정당성
3. **Results**: C4(Pure-Info) 대비 C3(Bandwagon)의 붕괴 가속 효과
4. **Discussion**: "근거 공유가 권위/군중심리에 비해 얼마나 기여하는가?"

---

## 산출물 체크리스트

- [ ] 시뮬레이션 코드 (`src/`)
- [ ] 실험 로그 (JSONL 5세트: C1, C2, C3, C4, C0)
- [ ] 분석 리포트 (PDF)
