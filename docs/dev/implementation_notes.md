# Implementation Notes

## Architecture Changes (2026-03-02)

### ActionScheduler — Random Action Selection
이전: `WindowCloseBehavior`와 `CursorStealBehavior`가 각각 독립된 타이머를 가지고 독립적으로 동작.
변경: `ActionScheduler`가 통합 관리. 하나의 타이머로 랜덤하게 다음 액션을 선택.

- 사용 가능한 액션 중 `random.choice()`로 선택
- 선택된 액션의 delay range를 사용하여 다음 트리거 시간 설정
- 액션 완료 후 자동으로 다음 액션 예약
- `force_trigger(behavior)`: 키보드로 특정 액션 강제 실행
- `stop_current()`: 현재 진행 중인 액션 중단

### Behavior 리팩토링
각 Behavior 클래스가 공통 인터페이스를 따르도록 변경:
- `trigger(on_complete)`: 액션 시작
- `cancel()`: 진행 중인 액션 취소
- `update()`: 프레임별 업데이트 (추적, 페이드 등)
- `available` 속성: 현재 플랫폼에서 사용 가능한지
- `delay_range` 속성: (min_delay, max_delay) 튜플

### 새 기능들

#### Lurking (지우기 공포 연출)
CursorStealBehavior 시퀀스에 통합:
1. 화면 가장자리로 빠르게 이동 (lurk_speed = wander_speed × 2.5)
2. LURKING 상태 진입 — 빛나는 눈만 보이는 스프라이트
3. LURK_DURATION_S (1.5초) 후 커서를 향해 돌진

#### Screen Doodle (연필 낙서)
새 ScreenDoodleBehavior:
1. 랜덤 위치로 이동
2. DOODLING 상태 — 낙서 애니메이션 재생
3. 캔버스에 랜덤 꺾은선(scribble) 생성 (windowed 모드만)
4. 낙서 라인은 DOODLE_FADE_DURATION_S 후 3단계로 페이드 아웃

#### Pencil Particle Effect (연필 가루)
Character 클래스에 내장된 파티클 시스템:
- PARTICLE_SPAWN_INTERVAL_S마다 PARTICLE_COUNT_PER_SPAWN개 파티클 생성
- 파티클은 연필 끝 위치에서 생성, 아래로 떨어지며 크기 감소
- PARTICLE_LIFETIME_S 후 소멸
- windowed 모드에서만 동작 (floating 모드에서는 윈도우가 캐릭터와 같이 이동하므로 부적합)

### 키보드 컨트롤
`app.py`에서 tkinter key binding으로 구현:
- `C`: CursorStealBehavior 강제 실행
- `W`: WindowCloseBehavior 강제 실행
- `D`: ScreenDoodleBehavior 강제 실행
- `S`: 현재 액션 중단, wandering으로 복귀
- `Space`: 일시정지/재개

### Sprite Sheet 시스템
`sprite_gen.py`에 구현:
- `create_sprite_sheet(output_path, scale)`: 개별 스프라이트 → 시트 조합
- `split_sprite_sheet(sheet_path, output_dir)`: 시트 → 개별 PNG 분리
- `_load_from_sheet(name, scale)`: 시트에서 직접 로드 (개별 PNG 없을 때 fallback)

시트 레이아웃 (9 rows × 4 cols):
| Row | Name | Frames | Description |
|-----|------|--------|-------------|
| 0 | walk | 4 | 일반 걷기, 중립 표정 |
| 1 | chase | 4 | 분노 추격 |
| 2 | erase | 4 | 커서 지우기 |
| 3 | approach | 4 | 창 닫기 접근 |
| 4 | idle | 2 | 정지/흔들림 |
| 5 | draw | 4 | 커서 다시 그리기 |
| 6 | pencil_press | 4 | 버튼 누르기 |
| 7 | lurk | 2 | 빛나는 눈 (잠복) |
| 8 | doodle | 4 | 낙서 그리기 |

### 타이밍 변경 (config.py)
- 커서 뽑기: 15~20초 (이전: 10~20초)
- 창 닫기: 20~25초 (이전: 30~90초)
- 낙서: 25~40초 (신규)

### Character 상태 머신 (State enum)
기존: IDLE, WANDERING, APPROACHING_WINDOW, PENCIL_PRESSING, CHASING_CURSOR, ERASING, WALKING_TO_DRAW, DRAWING
추가: LURKING, LURK_CHARGING, DOODLING
