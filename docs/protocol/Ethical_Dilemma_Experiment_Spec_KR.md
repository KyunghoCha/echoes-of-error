# 🧪 LLM 에이전트 윤리 딜레마 토론 실험: 정량적 붕괴 분석

> **연구 제목**: *"다수의 목소리: 정답 없는 딜레마에서 LLM 멀티 에이전트의 논리적 동조와 소수 의견 소멸 역학"*
> **Research Title**: *"Echoes of Error: Quantifying Self-Correction Collapse in Role-Conditioned Multi-Agent Systems"*

---

## 1. 프로젝트 개요 및 학술적 포지셔닝

### 1.1 핵심 연구 질문 (Research Questions)

> **RQ1 (붕괴 존재)**: 정답이 없는 딜레마에서도 토론 횟수($t$)가 증가하면 의견 분포 엔트로피($H_t$)는 감소하는가?
> **RQ2 (붕괴 속도)**: "Time-to-Collapse($\tau$)"는 정보 공유 조건에 따라 유의미하게 차이나는가?
> **RQ3 (동인 분석)**: 의견 변경의 주된 원인은 "정보적 영향(Rationale)", "권위적 영향(ID)", "군중심리(Bandwagon)" 중 무엇인가?

### 1.2 기존 연구와의 차별점 (Differentiation)

1. **Objective Function**: 기존 Multi-agent Debate([Liang et al. 2023])가 Accuracy 향상을 목적으로 하는 반면, 본 연구는 **Distribution Dynamics (붕괴 및 다양성 상실)** 자체를 규명함.
2. **Factorial Mechanism Dissection**: 정보/권위/군중심리(표 2.1 참조)를 완전 요인 설계(Full Factorial)로 분해하여 동조의 원인을 규명함.
3. **Quantification**: 합의 여부를 넘어, **Entropy**와 **Time-to-Collapse**를 도입하여 '위험한 과잉 합의'를 정량적으로 측정함.

---

## 2. 실험 조건 (Experimental Design)

### 2.1 독립 변수: 정보 공개 조건 (Conditions)

| 조건 ID | 명칭 | 공개 정보 (Exposure) | 메커니즘 (Mechanism) | 통제 요인 |
|:---:|---|---|---|---|
| **C1** | **Full** | ID + Stance + Rationale + Stats | Full Pressure | Main |
| **C2** | **Stance-Only** | ID + Stance + Stats | Authority + Bandwagon | Rationale 제거 효과 |
| **C3** | **Anon-Bandwagon** | Stance + Rationale + Stats (No ID) | Info + Bandwagon | Authority 제거 효과 |
| **C4** | **Pure-Info** | Stance + Rationale (No ID, **No Stats**) | **Informational Only** | **Bandwagon 제거 효과** |
| **C0** | **Independent** | None | Random Walk | Baseline |

### 2.2 고정 파라미터 (Control Variables)

* **Population**: $N=50$ Agents (Same Base Model, Role-Conditioned with 10 Personas).
* **Rounds**: $T=10$.
* **Repeated Runs**: 조건별 **Independent seeds 20회 이상** 수행하여 95% CI 보고 (Strong Validity).

### 2.3 시나리오 (Scenarios)

* **S1 (Biased)**: Classic Trolley (Initial ~85:15) - 소수 의견 소멸 관찰.
* **S3 (Balanced)**: Self-Driving Car (Initial ~50:50) - 수렴 방향성 및 속도 관찰.

---

## 3. 상세 프로토콜 (Protocol Specification)

### 3.1 정보 노출 규칙 (Exposure Rule) - **Strictly Fixed**

1. **Sampling Strategy**: **Random Top-K ($K=5$)**.
    * 각 에이전트는 이전 라운드의 전체 풀($N=50$)에서 무작위로 $K=5$명의 의견을 샘플링하여 열람함.
    * 매 라운드, 매 에이전트마다 **Independent Random Shuffle**.
2. **Summary Statistic**:
    * **C1, C2, C3**: 전체 분포("32 vs 18") **제공** (Bandwagon Signal).
    * **C4, C0**: 전체 분포 **미제공**.
3. **Token Handling**: 지정된 길이 초과 시 Rationale 뒷부분을 Truncate.

### 3.2 라운드 진행 구조

#### Round $t$ Step

1. **Fetch**: 이전 라운드($t-1$)의 Global Stat (조건별) 및 Peer Sample($K$) 수집.
2. **Context Construction**:
    * C3, C4의 경우 `agent_id`를 마스킹("Anonymous Peer 1") 처리.
3. **Inference**: LLM Response 생성.
4. **Self-Report**: 입장 변경 여부 및 **Change Reason Code 강제 선택**.

---

## 4. 데이터 스키마 (Log Schema)

### 4.1 Output JSON Structure (Snippet)

```json
"output": {
  "stance": "SACRIFICE_DRIVER",
  "decision_meta": {
    "changed": true,
    "change_reason_forced": "NORMATIVE",  
    "change_reason_text": "Attributes choice to the overwhelming majority count presented."
  }
}
```

### 4.2 Change Reason Codes (Enum)

* `INFORMATIONAL`: "Found a peer's argument logically convincing."
* `NORMATIVE`: "Influenced by the majority count, authority, or social pressure."
* `UNCERTAINTY`: "Was unsure, but peer consensus increased confidence."
* `NO_CHANGE`: Position maintained.

---

## 5. 정량적 메트릭 (Key Metrics)

### 5.1 Collapse Metrics

1. **Stance Entropy ($H_t$)**:
    $$H_t = - \sum_{s \in \text{Stances}} p_t(s) \log_2 p_t(s)$$
2. **Time-to-Collapse ($\tau$)**:
    $$\tau = \min \{ t \mid H_t \le 0.5 \cdot H_{0} \}$$
    (Repeated Runs 20회의 평균 및 CI 보고)

### 5.2 Survival Analysis (Kaplan-Meier Definitions)

* **Event Definition**:
  * Biased (S1): "Minority Stance $\to$ Majority 전환".
  * Balanced (S3): "Initial Stance 포기 및 전환".

### 5.3 Validity Filter

RQ3의 타당성 검증을 위해 무작위 샘플 200개에 대해 Human/GPT-4 Labeling 수행 후 **Cohen's Kappa** 보고.
