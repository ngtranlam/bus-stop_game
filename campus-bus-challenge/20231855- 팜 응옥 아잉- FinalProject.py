"""Campus Bus Challenge (캠퍼스 셔틀 정차 챌린지)

Nhấn Space đúng lúc để dừng xe buýt trường sao cho TÂM xe trùng tâm trạm.
Cấu trúc theo 5 hàm chính của môn học:
    init() -> handle_input() -> update_game() -> render() -> run_game()

Trạng thái game lưu trong một dict. Các hàm logic không sửa dict cũ mà trả về
dict mới ({**state, ...}) để dễ kiểm thử.
"""

import os
import random

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

# ---------------------------------------------------------------------------
# Hằng số: màn hình
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
FPS = 60
MAX_DT = 0.05            # chặn delta time khi máy bị giật
PIXEL = 4                # 1 ô pixel-art = 4x4 px

HORIZON_Y = 300
SIDEWALK_TOP = 384
ROAD_TOP = 404
ROAD_BOTTOM = 548
LANE_LINE_Y = 516

# ---------------------------------------------------------------------------
# Hằng số: xe buýt, trạm, tốc độ
# ---------------------------------------------------------------------------
BUS_WIDTH = 120
BUS_HEIGHT = 60
BUS_TOP_Y = 420
BUS_START_X = -60.0      # tâm xe lúc xuất phát (ngoài mép trái)

STOP_MIN_X = 560
STOP_MAX_X = 800

BASE_SPEED = 260         # px/giây ở màn 1
SPEED_GROWTH = 1.15
MAX_SPEED = 520
MAX_SPEED_EXPONENT = 20  # chặn số mũ để level rất lớn không tràn số

# ---------------------------------------------------------------------------
# Hằng số: chấm điểm, mạng, thời gian
# ---------------------------------------------------------------------------
PERFECT, GOOD, OK, MISS = "PERFECT", "GOOD", "OK", "MISS"
PERFECT_LIMIT = 12
GOOD_LIMIT = 32
OK_LIMIT = 65
GRADE_POINTS = {PERFECT: 100, GOOD: 60, OK: 30, MISS: 0}
COMBO_STEP = 20
MAX_COMBO_BONUS_STEPS = 5

OK_ZONE_WIDTH = 130
GOOD_ZONE_WIDTH = 64
PERFECT_ZONE_WIDTH = 24

STARTING_LIVES = 3
STOPS_PER_LEVEL = 3
RESULT_DURATION = 0.9
TRANSITION_DURATION = 1.2

# Trạng thái màn hình
TITLE, PLAYING, RESULT = "TITLE", "PLAYING", "RESULT"
LEVEL_TRANSITION, PAUSED, GAME_OVER = "LEVEL_TRANSITION", "PAUSED", "GAME_OVER"
PAUSABLE_STATES = (PLAYING, RESULT, LEVEL_TRANSITION)

# ---------------------------------------------------------------------------
# Màu sắc
# ---------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
PANEL_FILL = (28, 32, 56)
PANEL_BORDER = (250, 250, 250)
GRADE_COLORS = {PERFECT: (255, 214, 64), GOOD: (80, 214, 120),
                OK: (90, 170, 255), MISS: (255, 90, 90)}
ZONE_COLORS = {OK: (52, 120, 210), GOOD: (52, 178, 98), PERFECT: (255, 206, 60)}
CONFETTI_COLORS = [(255, 214, 64), (255, 110, 150), (90, 200, 255), (130, 230, 120)]

THEMES = [
    {"name": "MORNING",
     "sky": [(110, 190, 255), (135, 205, 255), (160, 218, 255), (190, 232, 255)],
     "sun": (255, 230, 90), "cloud": (255, 255, 255),
     "building": (232, 214, 180), "roof": (176, 82, 70), "window": (110, 160, 210),
     "grass": (100, 190, 80), "grass_dark": (70, 150, 60),
     "leaf": (60, 160, 70), "leaf_light": (110, 200, 90),
     "sidewalk": (205, 205, 200), "road": (80, 84, 96)},
    {"name": "AFTERNOON",
     "sky": [(240, 130, 90), (248, 160, 105), (252, 190, 130), (255, 218, 160)],
     "sun": (255, 120, 60), "cloud": (255, 225, 205),
     "building": (225, 190, 150), "roof": (150, 70, 60), "window": (240, 200, 140),
     "grass": (122, 172, 72), "grass_dark": (92, 136, 56),
     "leaf": (82, 140, 60), "leaf_light": (132, 176, 82),
     "sidewalk": (208, 192, 176), "road": (82, 80, 92)},
    {"name": "NIGHT",
     "sky": [(18, 22, 58), (28, 34, 78), (40, 48, 98), (56, 64, 118)],
     "sun": (240, 240, 210), "cloud": (78, 86, 128),
     "building": (70, 76, 112), "roof": (58, 42, 66), "window": (255, 220, 110),
     "grass": (40, 92, 62), "grass_dark": (28, 70, 48),
     "leaf": (30, 82, 56), "leaf_light": (52, 112, 72),
     "sidewalk": (112, 114, 128), "road": (50, 52, 66)},
]

# (x, rộng, cao) của các tòa nhà trường trên đường chân trời
BUILDINGS = [(40, 170, 150), (230, 210, 110), (460, 150, 175), (630, 230, 125), (880, 110, 185)]
TREE_X = [10, 200, 420, 610, 860, 955]
STARS = [(60, 40), (180, 90), (300, 30), (420, 120), (540, 60), (700, 100),
         (780, 30), (900, 140), (130, 180), (620, 170), (350, 200), (960, 70)]

# ---------------------------------------------------------------------------
# Sprite pixel-art: mỗi ký tự là 1 ô màu, "." là trong suốt
# ---------------------------------------------------------------------------
BUS_COLORS = {"K": (30, 30, 40), "Y": (255, 200, 40), "O": (232, 120, 32),
              "W": (120, 200, 255), "w": (225, 246, 255), "D": (60, 70, 92),
              "L": (255, 250, 190), "R": (232, 50, 50), "G": (40, 40, 48),
              "g": (176, 176, 186)}
BUS_BODY = [
    "...KKKKKKKKKKKKKKKKKKKKKKK....",
    "..KYYYYYYYYYYYYYYYYYYYYYYYKK..",
    ".KYYYYYYYYYYYYYYYYYYYYYYYYYYK.",
    ".KYKKKKKKKKKKKKKKKKKKKKKKKKKK.",
    ".KYKWWWKWWWKWWWKWWWKKDDKKWWKK.",
    ".KYKwWWKwWWKwWWKwWWKKDDKKwWKK.",
    ".KYKWWWKWWWKWWWKWWWKKDDKKWWKK.",
    ".KYKKKKKKKKKKKKKKKKKKDDKKKKKK.",
    ".KYYYYYYYYYYYYYYYYYYKDDKYYYYK.",
    ".KOOOOOOOOOOOOOOOOOOKDDKOOOLK.",
    ".RYYYYYYYYYYYYYYYYYYKDDKYYYLK.",
    ".KYYYYYYYYYYYYYYYYYYKDDKYYYYK.",
    ".KKKGGGGGKKKKKKKKKKKKGGGGGKKK.",
]
BUS_WHEEL_FRAMES = [  # 2 khung hình để bánh xe trông như đang quay
    ["....GgGgG............GgGgG....", ".....GGG..............GGG....."],
    ["....GGgGG............GGgGG....", ".....GgG..............GgG....."],
]

SHELTER_COLORS = {"K": (30, 30, 40), "P": (60, 110, 200), "W": (170, 220, 240),
                  "w": (240, 252, 255), "B": (150, 90, 50)}
SHELTER_ROWS = [
    "KKKKKKKKKKKKKKKKKKKKKK",
    "KPPPPPPPPPPPPPPPPPPPPK",
    "KKKKKKKKKKKKKKKKKKKKKK",
    ".K..................K.",
    ".KWWWWWWWWWWWWWWWWWWK.",
    ".KWwWWWWWWWWWWWWWWWWK.",
    ".KWWwWWWWWWWWWWWWWWWK.",
    ".KWWWWWWWWWWWWWWWWWWK.",
    ".KWWWWWWWWWWWWWWWWWWK.",
    ".K..................K.",
    ".K..BBBBBBBBBBBBBB..K.",
    ".K..K............K..K.",
    ".K..K............K..K.",
    ".K..................K.",
]

TREE_ROWS = [
    "....GGGG....",
    "..GGGGgGGG..",
    ".GGGgGGGGGG.",
    "GGGGGGGGgGGG",
    "GGgGGGGGGGGG",
    "GGGGGGGGGGgG",
    ".GGGGGgGGGG.",
    "..GGGGGGGG..",
    ".....TT.....",
    ".....TT.....",
    ".....TT.....",
]

CLOUD_ROWS = [
    "......XXXX......",
    "...XXXXXXXXXX...",
    ".XXXXXXXXXXXXXX.",
    "XXXXXXXXXXXXXXXX",
    ".XXXXXXXXXXXXXX.",
]

SUN_ROWS = ["..XXXX..", ".XXXXXX.", "XXXXXXXX", "XXXXXXXX",
            "XXXXXXXX", "XXXXXXXX", ".XXXXXX.", "..XXXX.."]
MOON_ROWS = ["..XXXX..", ".XXXX...", "XXXX....", "XXX.....",
             "XXX.....", "XXXX....", ".XXXX...", "..XXXX.."]

HEART_ROWS = [".RR.RR.", "RRRRRRR", "RRRRRRR", ".RRRRR.", "..RRR..", "...R..."]


# ===========================================================================
# PHẦN 1. LOGIC THUẦN (không vẽ, dễ kiểm thử)
# ===========================================================================
def calculate_speed(level: int) -> float:
    """Tốc độ của màn: 260 * 1.15^(level-1), tối đa 520 px/giây."""
    exponent = min(level - 1, MAX_SPEED_EXPONENT)
    return min(BASE_SPEED * SPEED_GROWTH ** exponent, MAX_SPEED)


def calculate_grade(distance: float) -> str:
    """Xếp loại theo khoảng cách giữa tâm xe và tâm trạm."""
    if distance <= PERFECT_LIMIT:
        return PERFECT
    if distance <= GOOD_LIMIT:
        return GOOD
    if distance <= OK_LIMIT:
        return OK
    return MISS


def calculate_points(grade: str, combo: int) -> tuple[int, int]:
    """Trả về (điểm nhận được, combo mới). Chỉ Perfect mới nối dài combo."""
    if grade != PERFECT:
        return GRADE_POINTS[grade], 0
    new_combo = combo + 1
    bonus = min(new_combo - 1, MAX_COMBO_BONUS_STEPS) * COMBO_STEP
    return GRADE_POINTS[PERFECT] + bonus, new_combo


def new_game_state() -> dict:
    """Trạng thái khi vừa mở game (màn hình tiêu đề)."""
    return {
        "state": TITLE, "previous_state": None, "running": True,
        "level": 1, "stop_index": 1, "score": 0, "lives": STARTING_LIVES,
        "combo": 0, "max_combo": 0, "total_stops": 0, "perfect_count": 0,
        "bus_x": BUS_START_X, "stop_center_x": (STOP_MIN_X + STOP_MAX_X) / 2,
        "speed": calculate_speed(1),
        "result_grade": None, "result_points": 0, "distance": 0.0,
        "result_timer": 0.0, "transition_timer": 0.0, "anim_time": 0.0,
    }


def start_stop(state: dict, rng=random) -> dict:
    """Chuẩn bị một lượt mới: đặt lại xe, chọn tâm trạm ngẫu nhiên."""
    return {
        **state, "state": PLAYING,
        "bus_x": BUS_START_X,
        "stop_center_x": rng.randint(STOP_MIN_X, STOP_MAX_X),
        "speed": calculate_speed(state["level"]),
        "result_grade": None, "result_points": 0, "distance": 0.0,
        "result_timer": 0.0, "transition_timer": 0.0,
    }


def new_run(rng=random) -> dict:
    """Bắt đầu một ván mới hoàn toàn từ màn 1."""
    return start_stop(new_game_state(), rng)


def resolve_stop(state: dict, distance: float) -> dict:
    """Chấm điểm lượt hiện tại. Chỉ chấm khi đang PLAYING => mỗi lượt đúng 1 lần."""
    if state["state"] != PLAYING:
        return state
    grade = calculate_grade(distance)
    points, combo = calculate_points(grade, state["combo"])
    lives = state["lives"] - 1 if grade == MISS else state["lives"]
    return {
        **state, "state": RESULT,
        "result_grade": grade, "result_points": points, "distance": distance,
        "result_timer": RESULT_DURATION,
        "score": state["score"] + points,
        "lives": max(lives, 0),
        "combo": combo,
        "max_combo": max(state["max_combo"], combo),
        "total_stops": state["total_stops"] + 1,
        "perfect_count": state["perfect_count"] + (1 if grade == PERFECT else 0),
    }


def press_space(state: dict) -> dict:
    """Dừng xe ngay tại vị trí hiện tại rồi chấm điểm."""
    distance = abs(state["bus_x"] - state["stop_center_x"])
    return resolve_stop(state, distance)


def finish_result(state: dict, rng=random) -> dict:
    """Sau khi hiện kết quả: Game Over, sang màn mới hoặc sang lượt kế tiếp."""
    if state["lives"] <= 0:
        return {**state, "state": GAME_OVER}
    if state["stop_index"] >= STOPS_PER_LEVEL:
        return {**state, "state": LEVEL_TRANSITION,
                "level": state["level"] + 1, "stop_index": 1,
                "speed": calculate_speed(state["level"] + 1),
                "bus_x": BUS_START_X, "transition_timer": TRANSITION_DURATION}
    return start_stop({**state, "stop_index": state["stop_index"] + 1}, rng)


def toggle_pause(state: dict) -> dict:
    """P: tạm dừng (nhớ trạng thái trước) hoặc tiếp tục đúng trạng thái đó."""
    if state["state"] == PAUSED:
        return {**state, "state": state["previous_state"], "previous_state": None}
    if state["state"] in PAUSABLE_STATES:
        return {**state, "state": PAUSED, "previous_state": state["state"]}
    return state


def move_bus(state: dict, dt: float) -> dict:
    """Di chuyển xe theo delta time; tự Miss khi xe đã vượt qua vùng hợp lệ."""
    bus_x = state["bus_x"] + state["speed"] * dt
    moved = {**state, "bus_x": bus_x}
    if bus_x > state["stop_center_x"] + OK_LIMIT:
        return resolve_stop(moved, bus_x - state["stop_center_x"])
    return moved


# ===========================================================================
# PHẦN 2. NĂM HÀM CHÍNH
# ===========================================================================
def init():
    """Khởi tạo Pygame, cửa sổ, đồng hồ, font, sprite và dữ liệu game."""
    pygame.init()
    pygame.display.set_caption("Campus Bus Challenge")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.key.set_repeat()  # tắt lặp phím: giữ Space không tạo nhiều KEYDOWN
    clock = pygame.time.Clock()
    assets = load_assets()
    return screen, clock, assets, new_game_state()


def handle_input(state: dict, events, rng=random) -> dict:
    """Xử lý sự kiện: đóng cửa sổ, Enter, Space, P, R, Esc (chỉ KEYDOWN)."""
    for event in events:
        state = handle_event(state, event, rng)
        if not state["running"]:
            break  # đã yêu cầu thoát: bỏ qua các phím còn lại trong frame này
    return state


def handle_event(state: dict, event, rng=random) -> dict:
    if event.type == pygame.QUIT:
        return {**state, "running": False}
    if event.type != pygame.KEYDOWN:
        return state

    key, current = event.key, state["state"]
    if key == pygame.K_ESCAPE:
        return {**state, "running": False}
    if key == pygame.K_p:
        return toggle_pause(state)
    if current == TITLE and key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        return new_run(rng)
    if current == PLAYING and key == pygame.K_SPACE:
        return press_space(state)
    if current == GAME_OVER and key == pygame.K_r:
        return new_run(rng)
    return state


def update_game(state: dict, dt: float, rng=random) -> dict:
    """Cập nhật theo thời gian: xe chạy, tự Miss, đếm giờ kết quả/banner."""
    current = state["state"]
    if current == PAUSED:
        return state  # mọi thứ đứng yên khi tạm dừng

    state = {**state, "anim_time": state["anim_time"] + dt}
    if current == PLAYING:
        return move_bus(state, dt)
    if current == RESULT:
        timer = state["result_timer"] - dt
        if timer <= 0:
            return finish_result(state, rng)
        return {**state, "result_timer": timer}
    if current == LEVEL_TRANSITION:
        timer = state["transition_timer"] - dt
        if timer <= 0:
            return start_stop(state, rng)
        return {**state, "transition_timer": timer}
    return state


def render(screen, state: dict, assets: dict) -> None:
    """Vẽ màn hình ứng với trạng thái hiện tại."""
    shown = state["previous_state"] if state["state"] == PAUSED else state["state"]
    draw_world(screen, state, assets, shown)

    if shown == TITLE:
        draw_title(screen, state, assets)
    elif shown == GAME_OVER:
        draw_game_over(screen, state, assets)
    else:
        draw_hud(screen, state, assets, shown)
        if shown == RESULT:
            draw_result(screen, state, assets)
        elif shown == LEVEL_TRANSITION:
            draw_transition(screen, state, assets)

    if state["state"] == PAUSED:
        draw_pause(screen, assets)
    pygame.display.flip()


def run_game() -> None:
    """Khởi tạo, chạy vòng lặp chính (input -> update -> render) và thoát sạch."""
    screen, clock, assets, state = init()
    rng = random.Random()
    try:
        while state["running"]:
            dt = min(clock.tick(FPS) / 1000, MAX_DT)
            state = handle_input(state, pygame.event.get(), rng)
            if not state["running"]:
                break
            state = update_game(state, dt, rng)
            render(screen, state, assets)
    finally:
        pygame.quit()


# ===========================================================================
# PHẦN 3. TÀI NGUYÊN ĐỒ HỌA (tự vẽ, không dùng file ảnh)
# ===========================================================================
def build_sprite(rows: list[str], palette: dict, scale: int = PIXEL):
    """Biến danh sách chuỗi ký tự thành Surface pixel-art."""
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Mọi dòng của sprite phải có cùng độ dài")
    surface = pygame.Surface((width * scale, len(rows) * scale), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char != ".":
                surface.fill(palette[char], (x * scale, y * scale, scale, scale))
    return surface


def load_assets() -> dict:
    font = pygame.font.Font
    themed = [
        {"tree": build_sprite(TREE_ROWS, {"G": t["leaf"], "g": t["leaf_light"],
                                          "T": (110, 72, 42)}),
         "cloud": build_sprite(CLOUD_ROWS, {"X": t["cloud"]}, 6)}
        for t in THEMES
    ]
    assets = {
        "fonts": {"huge": font(None, 84), "large": font(None, 56),
                  "medium": font(None, 38), "small": font(None, 28)},
        "bus": [build_sprite(BUS_BODY + wheels, BUS_COLORS) for wheels in BUS_WHEEL_FRAMES],
        "shelter": build_sprite(SHELTER_ROWS, SHELTER_COLORS),
        "heart": build_sprite(HEART_ROWS, {"R": (235, 60, 80)}),
        "heart_empty": build_sprite(HEART_ROWS, {"R": (90, 90, 105)}),
        "themed": themed,
    }
    assets["backgrounds"] = [build_background(t, themed[i]["tree"]) for i, t in enumerate(THEMES)]
    return assets


def build_background(theme: dict, tree):
    """Vẽ sẵn phần nền tĩnh (trời, nhà, cỏ, đường) cho từng buổi."""
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    draw_sky(surface, theme)
    for x, width, height in BUILDINGS:
        draw_building(surface, theme, x, width, height)
    surface.fill(theme["grass"], (0, HORIZON_Y, SCREEN_WIDTH, SIDEWALK_TOP - HORIZON_Y))
    for x in TREE_X:
        surface.blit(tree, (x, SIDEWALK_TOP - tree.get_height() - 8))
    draw_road(surface, theme)
    draw_grass_tufts(surface, theme)
    return surface


def draw_sky(surface, theme: dict) -> None:
    band = HORIZON_Y // len(theme["sky"])
    for i, color in enumerate(theme["sky"]):
        surface.fill(color, (0, i * band, SCREEN_WIDTH, band + PIXEL))
        if i > 0:  # hàng chấm xen kẽ giữa 2 dải màu cho cảm giác pixel-art
            for x in range(0, SCREEN_WIDTH, PIXEL * 2):
                surface.fill(theme["sky"][i - 1], (x, i * band, PIXEL, PIXEL))
    if theme["name"] == "NIGHT":
        for x, y in STARS:
            surface.fill(WHITE, (x, y, PIXEL, PIXEL))
        surface.blit(build_sprite(MOON_ROWS, {"X": theme["sun"]}, 8), (370, 24))
    else:  # buổi sáng mặt trời ở cao, buổi chiều thấp dần
        sun_pos = (370, 24) if theme["name"] == "MORNING" else (330, 110)
        surface.blit(build_sprite(SUN_ROWS, {"X": theme["sun"]}, 8), sun_pos)


def draw_building(surface, theme: dict, x: int, width: int, height: int) -> None:
    top = HORIZON_Y - height
    surface.fill(BLACK, (x - PIXEL, top - PIXEL, width + 2 * PIXEL, height + PIXEL))
    surface.fill(theme["building"], (x, top, width, height))
    surface.fill(theme["roof"], (x, top, width, 12))
    for wx in range(x + 16, x + width - 20, 32):
        for wy in range(top + 28, HORIZON_Y - 24, 36):
            surface.fill(BLACK, (wx - PIXEL, wy - PIXEL, 20 + 2 * PIXEL, 20 + 2 * PIXEL))
            surface.fill(theme["window"], (wx, wy, 20, 20))


def draw_road(surface, theme: dict) -> None:
    surface.fill(theme["sidewalk"], (0, SIDEWALK_TOP, SCREEN_WIDTH, ROAD_TOP - SIDEWALK_TOP))
    for x in range(0, SCREEN_WIDTH, 32):  # khe gạch vỉa hè
        surface.fill(BLACK, (x, SIDEWALK_TOP, PIXEL, ROAD_TOP - SIDEWALK_TOP))
    surface.fill(theme["road"], (0, ROAD_TOP, SCREEN_WIDTH, ROAD_BOTTOM - ROAD_TOP))
    surface.fill(WHITE, (0, ROAD_TOP, SCREEN_WIDTH, PIXEL))
    surface.fill(WHITE, (0, ROAD_BOTTOM - PIXEL, SCREEN_WIDTH, PIXEL))
    for x in range(0, SCREEN_WIDTH, 64):  # vạch giữa đường nét đứt
        surface.fill(WHITE, (x + 8, LANE_LINE_Y, 32, PIXEL))
    surface.fill(theme["grass"], (0, ROAD_BOTTOM, SCREEN_WIDTH, SCREEN_HEIGHT - ROAD_BOTTOM))


def draw_grass_tufts(surface, theme: dict) -> None:
    tuft_rng = random.Random(42)  # cố định để nền không nhấp nháy
    areas = [(HORIZON_Y + 8, SIDEWALK_TOP - 12), (ROAD_BOTTOM + 12, SCREEN_HEIGHT - 8)]
    for top, bottom in areas:
        for _ in range(28):
            x = tuft_rng.randrange(0, SCREEN_WIDTH, PIXEL)
            y = tuft_rng.randrange(top, bottom, PIXEL)
            for dx, dy in ((0, 0), (PIXEL, -PIXEL), (2 * PIXEL, 0)):
                surface.fill(theme["grass_dark"], (x + dx, y + dy, PIXEL, PIXEL))


# ===========================================================================
# PHẦN 4. HÀM VẼ (chỉ đọc state, không đổi luật chơi)
# ===========================================================================
def theme_index(level: int) -> int:
    """Màn 1 sáng, màn 2 chiều, màn 3 tối, sau đó lặp lại."""
    return (level - 1) % len(THEMES)


def draw_world(screen, state: dict, assets: dict, shown: str) -> None:
    index = 0 if shown == TITLE else theme_index(state["level"])
    screen.blit(assets["backgrounds"][index], (0, 0))
    draw_clouds(screen, assets["themed"][index]["cloud"], state["anim_time"])

    if shown == TITLE:
        loop_width = SCREEN_WIDTH + BUS_WIDTH * 2
        draw_bus(screen, assets, (state["anim_time"] * 200) % loop_width - BUS_WIDTH, False)
        return
    draw_stop_zone(screen, state["stop_center_x"], assets)
    if shown != LEVEL_TRANSITION:
        draw_bus(screen, assets, state["bus_x"], True)


def draw_clouds(screen, cloud, anim_time: float) -> None:
    span = SCREEN_WIDTH + cloud.get_width()
    for base_x, y, speed in ((80, 60, 12), (430, 110, 8), (760, 50, 15)):
        x = (base_x + anim_time * speed) % span - cloud.get_width()
        screen.blit(cloud, (round(x), y))


def draw_stop_zone(screen, center_x: float, assets: dict) -> None:
    """Nhà chờ, biển BUS STOP và 3 vùng chấm điểm đồng tâm trên mặt đường."""
    cx = round(center_x)
    shelter = assets["shelter"]
    screen.blit(shelter, (cx - shelter.get_width() // 2, SIDEWALK_TOP - shelter.get_height() + 4))
    draw_bus_stop_sign(screen, cx + 64, assets)

    top, height = ROAD_TOP + 8, ROAD_BOTTOM - ROAD_TOP - 16
    screen.fill(WHITE, (cx - OK_ZONE_WIDTH // 2 - PIXEL, top - PIXEL,
                        OK_ZONE_WIDTH + 2 * PIXEL, height + 2 * PIXEL))
    for grade, width in ((OK, OK_ZONE_WIDTH), (GOOD, GOOD_ZONE_WIDTH),
                         (PERFECT, PERFECT_ZONE_WIDTH)):
        screen.fill(ZONE_COLORS[grade], (cx - width // 2, top, width, height))
    screen.fill(BLACK, (cx - 1, top, 2, height))  # đường tâm trạm
    screen.fill(BLACK, (cx - 6, ROAD_TOP - 8, 12, 8))  # chỉ dấu tâm trên vỉa hè


def draw_bus_stop_sign(screen, x: int, assets: dict) -> None:
    screen.fill(BLACK, (x - 2, SIDEWALK_TOP - 70, PIXEL, 74))
    plate = pygame.Rect(x - 48, SIDEWALK_TOP - 96, 96, 30)
    draw_panel(screen, plate, (40, 120, 220), WHITE)
    draw_text(screen, "BUS STOP", assets["fonts"]["small"], WHITE, plate.center, scale=0.7)


def draw_bus(screen, assets: dict, center_x: float, show_marker: bool) -> None:
    """Vẽ xe theo tâm; vạch đỏ ở giữa thân xe chính là điểm được chấm."""
    frame = assets["bus"][int(center_x // 10) % 2]
    left = round(center_x - BUS_WIDTH / 2)
    shadow = pygame.Surface((BUS_WIDTH - 8, 8), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 90))
    screen.blit(shadow, (left + 4, BUS_TOP_Y + BUS_HEIGHT - 4))
    screen.blit(frame, (left, BUS_TOP_Y))
    if show_marker:
        cx = round(center_x)
        marker_top = BUS_TOP_Y + BUS_HEIGHT - 8
        screen.fill(WHITE, (cx - 4, marker_top, 8, ROAD_BOTTOM - 14 - marker_top))
        screen.fill((230, 40, 40), (cx - 2, marker_top, PIXEL, ROAD_BOTTOM - 14 - marker_top))
        screen.fill((230, 40, 40), (cx - 6, ROAD_BOTTOM - 18, 12, PIXEL))


def draw_panel(screen, rect, fill=PANEL_FILL, border=PANEL_BORDER) -> None:
    """Khung kiểu pixel: viền dày 4 px, góc vát bậc thang."""
    x, y, w, h = rect
    screen.fill(border, (x + PIXEL, y, w - 2 * PIXEL, h))
    screen.fill(border, (x, y + PIXEL, w, h - 2 * PIXEL))
    screen.fill(fill, (x + PIXEL, y + PIXEL, w - 2 * PIXEL, h - 2 * PIXEL))


def draw_text(screen, text: str, font, color, center, scale: float = 1.0) -> None:
    """Chữ không khử răng cưa + bóng đổ để hợp phong cách pixel."""
    image = font.render(text, False, color)
    shadow = font.render(text, False, BLACK)
    if scale != 1.0:
        size = (round(image.get_width() * scale), round(image.get_height() * scale))
        image = pygame.transform.scale(image, size)
        shadow = pygame.transform.scale(shadow, size)
    rect = image.get_rect(center=center)
    screen.blit(shadow, rect.move(3, 3))
    screen.blit(image, rect)


def draw_overlay(screen, rgba) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(rgba)
    screen.blit(overlay, (0, 0))


def draw_hud(screen, state: dict, assets: dict, shown: str) -> None:
    fonts = assets["fonts"]
    draw_panel(screen, (16, 12, 300, 84))
    draw_text(screen, f"SCORE {state['score']:05d}", fonts["medium"], WHITE, (166, 38))
    draw_text(screen, f"LEVEL {state['level']}   STOP {state['stop_index']}/{STOPS_PER_LEVEL}",
              fonts["small"], (200, 220, 255), (166, 74))

    draw_panel(screen, (684, 12, 300, 84))
    for i in range(STARTING_LIVES):
        heart = assets["heart"] if i < state["lives"] else assets["heart_empty"]
        screen.blit(heart, (704 + i * 36, 24))
    combo_color = GRADE_COLORS[PERFECT] if state["combo"] >= 2 else WHITE
    draw_text(screen, f"COMBO x{state['combo']}", fonts["small"], combo_color, (900, 38))
    speed_percent = round(state["speed"] / BASE_SPEED * 100)
    draw_text(screen, f"SPEED {speed_percent}%", fonts["small"], (200, 220, 255), (834, 74))

    if shown == PLAYING:
        draw_panel(screen, (340, 572, 320, 56), (30, 60, 160))
        draw_text(screen, "SPACE TO STOP", fonts["medium"], WHITE, (500, 601))
    draw_text(screen, "P: PAUSE", fonts["small"], WHITE, (920, 620), scale=0.8)


def draw_result(screen, state: dict, assets: dict) -> None:
    grade, fonts = state["result_grade"], assets["fonts"]
    elapsed = RESULT_DURATION - state["result_timer"]
    if grade == MISS:
        draw_overlay(screen, (255, 40, 40, 60))
    elif grade == PERFECT:
        draw_perfect_effect(screen, state, elapsed)

    draw_panel(screen, (300, 128, 400, 168))
    draw_text(screen, f"{grade}!", fonts["huge"], GRADE_COLORS[grade], (500, 180))
    if grade == MISS:
        early = state["bus_x"] < state["stop_center_x"]
        detail = "TOO EARLY" if early else "TOO LATE"
        draw_text(screen, f"{detail}   -1 LIFE", fonts["medium"], WHITE, (500, 240))
    else:
        draw_text(screen, f"+{state['result_points']}", fonts["medium"], WHITE, (500, 236))
    draw_text(screen, f"OFF BY {state['distance']:.1f} PX", fonts["small"],
              (200, 220, 255), (500, 272))
    if grade == PERFECT and state["combo"] >= 2:
        draw_text(screen, f"COMBO x{state['combo']}", fonts["large"],
                  GRADE_COLORS[PERFECT], (500, 336))


def draw_perfect_effect(screen, state: dict, elapsed: float) -> None:
    """Lóe sáng + confetti. Chỉ trang trí, vị trí xe không thay đổi."""
    flash_alpha = max(0, 120 - int(elapsed * 500))
    if flash_alpha:
        draw_overlay(screen, (255, 255, 255, flash_alpha))
    confetti_rng = random.Random(state["total_stops"])
    origin_x, origin_y = state["bus_x"], BUS_TOP_Y
    for i in range(36):
        vx = confetti_rng.uniform(-260, 260)
        vy = confetti_rng.uniform(-420, -160)
        x = origin_x + vx * elapsed
        y = origin_y + vy * elapsed + 600 * elapsed ** 2
        color = CONFETTI_COLORS[i % len(CONFETTI_COLORS)]
        screen.fill(color, (round(x / PIXEL) * PIXEL, round(y / PIXEL) * PIXEL, 8, 8))


def draw_transition(screen, state: dict, assets: dict) -> None:
    fonts = assets["fonts"]
    level = state["level"]
    old_speed, new_speed = calculate_speed(level - 1), calculate_speed(level)
    if new_speed > old_speed:
        speed_text = f"SPEED UP!  {old_speed:.0f} > {new_speed:.0f} PX/S"
        if new_speed >= MAX_SPEED:
            speed_text += "  (MAX)"
    else:
        speed_text = f"MAX SPEED  {new_speed:.0f} PX/S"

    draw_overlay(screen, (0, 0, 0, 90))
    draw_panel(screen, (200, 180, 600, 200))
    draw_text(screen, f"LEVEL {level}", fonts["huge"], GRADE_COLORS[PERFECT], (500, 236))
    draw_text(screen, THEMES[theme_index(level)]["name"], fonts["small"], (200, 220, 255), (500, 288))
    draw_text(screen, speed_text, fonts["medium"], WHITE, (500, 334))


def draw_pause(screen, assets: dict) -> None:
    fonts = assets["fonts"]
    draw_overlay(screen, (0, 0, 0, 170))
    draw_text(screen, "PAUSED", fonts["huge"], WHITE, (500, 250))
    draw_text(screen, "P TO RESUME", fonts["medium"], (200, 220, 255), (500, 330))
    draw_text(screen, "ESC TO QUIT", fonts["medium"], (200, 220, 255), (500, 376))


def draw_title(screen, state: dict, assets: dict) -> None:
    fonts = assets["fonts"]
    draw_panel(screen, (130, 36, 740, 340))
    draw_text(screen, "CAMPUS BUS CHALLENGE", fonts["large"], GRADE_COLORS[PERFECT], (500, 84))
    draw_text(screen, "Stop the shuttle right at the center of the bus stop!",
              fonts["small"], WHITE, (500, 126))
    rows = [(PERFECT, "<= 12 PX", "100 + COMBO"), (GOOD, "<= 32 PX", "60"),
            (OK, "<= 65 PX", "30"), (MISS, "> 65 PX", "-1 LIFE")]
    for i, (grade, distance, reward) in enumerate(rows):
        y = 172 + i * 34
        draw_text(screen, grade, fonts["medium"], GRADE_COLORS[grade], (330, y))
        draw_text(screen, distance, fonts["medium"], WHITE, (500, y))
        draw_text(screen, reward, fonts["medium"], WHITE, (680, y))
    draw_text(screen, "SPACE: STOP    P: PAUSE    ESC: QUIT", fonts["small"],
              (200, 220, 255), (500, 334))
    if int(state["anim_time"] * 2) % 2 == 0:  # chữ nhấp nháy
        draw_panel(screen, (300, 572, 400, 56), (30, 60, 160))
        draw_text(screen, "PRESS ENTER TO START", fonts["medium"], WHITE, (500, 601))


def draw_game_over(screen, state: dict, assets: dict) -> None:
    fonts = assets["fonts"]
    draw_overlay(screen, (0, 0, 0, 120))
    draw_panel(screen, (250, 70, 500, 470))
    draw_text(screen, "GAME OVER", fonts["huge"], GRADE_COLORS[MISS], (500, 130))
    draw_text(screen, f"SCORE {state['score']}", fonts["large"], GRADE_COLORS[PERFECT], (500, 200))
    stats = [("LEVEL REACHED", state["level"]), ("STOPS PLAYED", state["total_stops"]),
             ("PERFECT STOPS", state["perfect_count"]), ("BEST COMBO", state["max_combo"])]
    for i, (label, value) in enumerate(stats):
        y = 262 + i * 44
        draw_text(screen, label, fonts["medium"], WHITE, (420, y))
        draw_text(screen, str(value), fonts["medium"], WHITE, (640, y))
    draw_text(screen, "R: RETRY      ESC: QUIT", fonts["medium"], (200, 220, 255), (500, 494))


if __name__ == "__main__":
    run_game()
