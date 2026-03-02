# Gemini 스프라이트 시트 생성 프롬프트

## 사용법
1. 아래 프롬프트를 Gemini에 전달
2. 현재 `assets/sprites/spritesheet.png`를 참고 이미지로 첨부
3. 생성된 시트를 `python main.py --split-sheet <path>` 로 분리

---

## 프롬프트 (영문)

```
Create a sprite sheet for a 2D desktop pet character based on "DoodleBob" from SpongeBob SquarePants.

**Character Design:**
- A crudely hand-drawn, sketch-style paper character (like a child's doodle come to life)
- Rectangular white paper body with rough, wobbly outlines (not perfectly straight)
- Two large circular eyes with thick black outlines and black pupils
- Simple stick-figure arms and legs with round feet
- A small black triangle tie/bowtie at the bottom of the body
- MOST IMPORTANT: A giant yellow #2 pencil held above his head with both hands — the pencil is wider than the character itself. The pencil has: a dark graphite tip on the left, a yellow hexagonal body, a silver metal ferrule, and a pink eraser on the right end.
- Overall aesthetic: messy, sketchy, hand-drawn on notebook paper — NOT clean or polished

**Sprite Sheet Layout — STRICT GRID: 9 rows × 4 columns**
- Gray background (#C0C0C0)
- Each cell is the same size
- Character is centered in each cell
- Cells with no sprite should be left as plain gray background

**Row-by-row specification:**

Row 0 — WALK (4 frames): Neutral/happy expression. Legs alternate in a walk cycle. Pencil bobs slightly up and down with each step. Body sways gently.

Row 1 — CHASE (4 frames): Angry expression — furrowed eyebrows angled inward, mouth curved downward in a scowl. Pencil tilted aggressively forward (tip pointing in walking direction). Running/charging pose, leaning forward.

Row 2 — ERASE (4 frames): Angry/determined expression. Pencil is FLIPPED so the pink eraser end points forward. The character jabs the eraser forward in a stabbing motion across the 4 frames (wind-up → thrust → contact → recoil).

Row 3 — APPROACH (4 frames): Menacing expression — angry eyebrows, slight frown. Walking toward something with pencil tilted forward threateningly. Similar to chase but slower, more deliberate body language.

Row 4 — IDLE (2 frames, columns 2-3 empty): Relaxed/content expression, slight smile. Standing still with a gentle bobbing motion (body shifts up/down slightly between frames). Pencil held proudly overhead.

Row 5 — DRAW (4 frames): Surprised/focused expression — wide open eyes, small 'O' shaped mouth. Pencil tilted strongly downward as if drawing on the ground. The tip touches down progressively across frames.

Row 6 — PENCIL PRESS (4 frames): Angry/intense expression. The character jabs the pencil tip downward forcefully — frames show: wind-up (pencil raised), swing (pencil coming down), impact (pencil tip at lowest point, body compressed), recoil (pencil bounces back up).

Row 7 — LURK (2 frames, columns 2-3 empty): ONLY the character's eyes visible against a dark/shadowy rectangular silhouette. Eyes glow yellow/golden. Frame 0: eyes bright. Frame 1: eyes slightly dimmer. This represents the character hiding in shadows before attacking.

Row 8 — DOODLE (4 frames): Happy/mischievous expression with a grin. Pencil angled steeply downward with the tip touching the ground. The character leans forward as if scribbling. Slight variation in pencil angle across frames to show drawing motion.

**Style Notes:**
- Consistent character proportions across ALL frames
- Sketchy, hand-drawn line quality with slight wobble (not perfectly straight lines)
- The pencil must appear in every frame (except Row 7 lurk)
- Lines should be black, body should be off-white/cream
- Keep the "drawn on paper" aesthetic — think crayon/marker on notebook paper
- Each sprite should read clearly at small sizes (64×80 pixels base)
```

---

## 프롬프트 (한국어 버전, 필요시)

```
스폰지밥의 "낙서밥(DoodleBob)" 캐릭터를 기반으로 한 2D 데스크톱 펫 스프라이트 시트를 만들어주세요.

**캐릭터 디자인:**
- 아이가 대충 그린 것 같은 손그림 스타일의 종이 캐릭터
- 울퉁불퉁한 윤곽선의 직사각형 흰색 몸통
- 두꺼운 검정 테두리와 검정 동공이 있는 큰 원형 눈 두 개
- 단순한 막대 팔다리와 둥근 발
- 몸 아래쪽에 작은 검정 삼각형 넥타이
- 가장 중요: 양손으로 머리 위에 들고 있는 거대한 노란색 2번 연필. 연필은 캐릭터보다 넓음. 왼쪽 흑연 팁, 노란 육각 몸체, 은색 금속 페룰, 오른쪽 분홍 지우개.
- 전체 미학: 지저분하고, 스케치풍, 공책에 그린 듯 — 깔끔하지 않게

**스프라이트 시트 레이아웃 — 정확한 그리드: 9행 × 4열**
- 회색 배경 (#C0C0C0)
- 각 셀은 같은 크기, 캐릭터는 셀 중앙에 배치
- 스프라이트가 없는 셀은 빈 회색 배경

**행별 설명:**

Row 0 — 걷기 (4프레임): 중립/행복 표정. 다리가 걷기 사이클로 교차. 연필이 걸을 때마다 살짝 위아래로 흔들림.

Row 1 — 추격 (4프레임): 화난 표정 — 안쪽으로 찌푸린 눈썹, 아래로 굽은 입. 연필이 공격적으로 앞으로 기울어짐. 달리기/돌진 자세.

Row 2 — 지우기 (4프레임): 화남/결연한 표정. 연필이 뒤집혀서 분홍 지우개가 앞으로. 4프레임에 걸쳐 지우개를 찔러넣는 동작 (준비→찌르기→접촉→반동).

Row 3 — 접근 (4프레임): 위협적 표정 — 화난 눈썹, 약간의 찡그림. 연필을 위협적으로 기울이며 걸어감. 추격보다 느리고 의도적인 움직임.

Row 4 — 대기 (2프레임, 3-4열 비움): 편안한 표정, 살짝 미소. 가만히 서서 부드럽게 위아래로 흔들림. 연필을 자랑스럽게 머리 위에.

Row 5 — 그리기 (4프레임): 놀란/집중 표정 — 크게 뜬 눈, 작은 'O' 모양 입. 연필이 땅으로 강하게 기울어져 그리는 중.

Row 6 — 연필 찍기 (4프레임): 화남/강렬한 표정. 연필 팁을 아래로 세게 찍는 동작 — 준비, 스윙, 충격(최저점), 반동.

Row 7 — 잠복 (2프레임, 3-4열 비움): 어두운 직사각형 실루엣에서 눈만 보임. 눈이 노란색/금색으로 빛남. 프레임 0: 밝은 눈. 프레임 1: 약간 어두운 눈.

Row 8 — 낙서 (4프레임): 행복/장난기 표정. 연필이 가파르게 아래로 기울어 바닥에 닿음. 캐릭터가 낙서하듯 앞으로 기울어짐.

**스타일:**
- 모든 프레임에서 일관된 캐릭터 비율
- 약간 흔들리는 손그림 선 (완벽히 직선이 아님)
- Row 7 제외 모든 프레임에 연필 포함
- 검정 선, 크림색/미색 몸통
- "종이에 그린 듯한" 미학 유지
```
