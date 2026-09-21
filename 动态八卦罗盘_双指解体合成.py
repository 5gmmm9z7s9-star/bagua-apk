# -*- coding: utf-8 -*-

import pygame
import math
import random
import os


# ============================================================
# 全局变量
# ============================================================

WIDTH = 0
HEIGHT = 0
CENTER_X = 0
CENTER_Y = 0
SHORT = 0

screen = None
clock = None

rotation_angle = 0.0
rotation_speed = 0.0
pressing_center = False

# 双指
active_fingers = {}

# 太极解体动画
DECOMP_IDLE = 0
DECOMP_EXPAND = 1
DECOMP_MERGE = 2

decomp_state = DECOMP_IDLE
decomp_progress = 0.0
decomp_time = 0.0
decomp_particles = []

DECOMP_DURATION = 1.05


# ============================================================
# 旋转参数
# ============================================================

ACCELERATION = 0.018
FRICTION = 0.985
MAX_SPEED = 1.8


# ============================================================
# 颜色
# ============================================================

BLACK = (3, 3, 7)
WHITE = (245, 245, 245)
GRAY = (110, 110, 120)

GOLD = (220, 180, 70)
GOLD2 = (145, 110, 35)

# 解体彩色能量
ORANGE = (255, 145, 45)
BLUE = (55, 175, 255)
PURPLE = (175, 80, 255)
CYAN = (80, 225, 255)


# ============================================================
# 字体
# ============================================================

CHINESE_FONT_PATH = None

FONT_SMALL = None
FONT_MEDIUM = None
FONT_BIG = None


# ============================================================
# 星空和粒子
# ============================================================

stars = []

particle_ring_1 = []
particle_ring_2 = []


# ============================================================
# 文字缓存
# ============================================================

tiangan_surfaces = []
dizhi_surfaces = []
trigram_name_surfaces = []


# ============================================================
# 八卦
# ============================================================

TRIGRAMS = [
    [1, 1, 1],  # 乾
    [1, 1, 0],  # 兑
    [1, 0, 1],  # 离
    [1, 0, 0],  # 震
    [0, 1, 1],  # 巽
    [0, 1, 0],  # 坎
    [0, 0, 1],  # 艮
    [0, 0, 0],  # 坤
]

TRIGRAM_NAMES = [
    "乾",
    "兑",
    "离",
    "震",
    "巽",
    "坎",
    "艮",
    "坤"
]


# ============================================================
# 天干
# ============================================================

TIANGAN = [
    "甲", "乙", "丙", "丁", "戊",
    "己", "庚", "辛", "壬", "癸"
]


# ============================================================
# 地支
# ============================================================

DIZHI = [
    "子", "丑", "寅", "卯",
    "辰", "巳", "午", "未",
    "申", "酉", "戌", "亥"
]


# ============================================================
# 初始化 Pygame
# ============================================================

def init_game():

    global WIDTH
    global HEIGHT
    global CENTER_X
    global CENTER_Y
    global SHORT
    global screen
    global clock

    pygame.init()
    pygame.font.init()

    try:
        pygame.mixer.quit()
    except:
        pass

    screen = pygame.display.set_mode(
        (0, 0),
        pygame.FULLSCREEN
    )

    WIDTH, HEIGHT = screen.get_size()

    CENTER_X = WIDTH // 2
    CENTER_Y = HEIGHT // 2

    SHORT = min(
        WIDTH,
        HEIGHT
    )

    pygame.display.set_caption(
        "动态八卦罗盘"
    )

    clock = pygame.time.Clock()


# ============================================================
# 查找中文字体
# ============================================================

def find_chinese_font():

    global CHINESE_FONT_PATH

    paths = [
        "/system/fonts/NotoSansCJK-Regular.ttc",
        "/system/fonts/NotoSansCJK-Regular.otf",
        "/system/fonts/NotoSansSC-Regular.otf",
        "/system/fonts/NotoSansSC-Regular.ttf",
        "/system/fonts/DroidSansFallback.ttf",
        "/system/fonts/NotoSerifCJK-Regular.ttc",
        "/system/fonts/NotoSansCJKSC-Regular.otf",

        "/sdcard/Download/NotoSansCJK-Regular.ttc",
        "/sdcard/Download/NotoSansSC-Regular.ttf"
    ]

    for path in paths:

        if os.path.exists(path):

            CHINESE_FONT_PATH = path

            return


# ============================================================
# 获取字体
# ============================================================

def get_font(size):

    try:

        if CHINESE_FONT_PATH:

            return pygame.font.Font(
                CHINESE_FONT_PATH,
                size
            )

    except Exception:
        pass

    try:

        return pygame.font.SysFont(
            "sans",
            size
        )

    except Exception:

        return pygame.font.Font(
            None,
            size
        )


# ============================================================
# 初始化字体
# ============================================================

def init_fonts():

    global FONT_SMALL
    global FONT_MEDIUM
    global FONT_BIG

    FONT_SMALL = get_font(
        max(
            16,
            SHORT // 45
        )
    )

    FONT_MEDIUM = get_font(
        max(
            20,
            SHORT // 32
        )
    )

    FONT_BIG = get_font(
        max(
            28,
            SHORT // 20
        )
    )


# ============================================================
# 创建文字缓存
# ============================================================

def create_text_cache():

    global tiangan_surfaces
    global dizhi_surfaces
    global trigram_name_surfaces

    tiangan_surfaces = []
    dizhi_surfaces = []
    trigram_name_surfaces = []

    for text in TIANGAN:

        surf = FONT_SMALL.render(
            text,
            True,
            WHITE
        )

        tiangan_surfaces.append(
            surf
        )

    for text in DIZHI:

        surf = FONT_SMALL.render(
            text,
            True,
            (200, 200, 210)
        )

        dizhi_surfaces.append(
            surf
        )

    for text in TRIGRAM_NAMES:

        surf = FONT_SMALL.render(
            text,
            True,
            GOLD
        )

        trigram_name_surfaces.append(
            surf
        )


# ============================================================
# 创建星空
# ============================================================

def create_stars():

    global stars

    stars = []

    count = int(
        WIDTH * HEIGHT / 9000
    )

    if count < 120:
        count = 120

    if count > 280:
        count = 280

    for i in range(count):

        x = random.randint(
            0,
            WIDTH
        )

        y = random.randint(
            0,
            HEIGHT
        )

        radius = random.choice(
            [1, 1, 1, 1, 2]
        )

        brightness = random.randint(
            70,
            180
        )

        stars.append(
            (
                x,
                y,
                radius,
                brightness
            )
        )


# ============================================================
# 创建粒子环
# ============================================================

def create_particle_rings():

    global particle_ring_1
    global particle_ring_2

    particle_ring_1 = []
    particle_ring_2 = []

    for i in range(60):

        angle = (
            360.0 / 60
        ) * i

        size = random.choice(
            [1, 1, 1, 2]
        )

        particle_ring_1.append(
            (angle, size)
        )

    for i in range(42):

        angle = (
            360.0 / 42
        ) * i

        size = random.choice(
            [1, 1, 2]
        )

        particle_ring_2.append(
            (angle, size)
        )


# ============================================================
# 星空背景
# ============================================================

def draw_background():

    screen.fill(
        BLACK
    )

    for x, y, radius, brightness in stars:

        color = (
            brightness,
            brightness,
            brightness
        )

        pygame.draw.circle(
            screen,
            color,
            (x, y),
            radius
        )


# ============================================================
# 极坐标
# ============================================================

def polar_point(
    radius,
    angle
):

    rad = math.radians(
        angle
    )

    x = (
        CENTER_X
        + math.cos(rad) * radius
    )

    y = (
        CENTER_Y
        + math.sin(rad) * radius
    )

    return (
        int(x),
        int(y)
    )


# ============================================================
# 圆环
# ============================================================

def draw_ring(
    radius,
    width=1,
    color=GOLD2
):

    pygame.draw.circle(
        screen,
        color,
        (
            CENTER_X,
            CENTER_Y
        ),
        int(radius),
        width
    )


# ============================================================
# 刻度环
# ============================================================

def draw_scale_ring(
    radius,
    count,
    angle
):

    for i in range(count):

        a = (
            angle
            + 360.0 / count * i
        )

        inner = radius - 8
        outer = radius + 8

        p1 = polar_point(
            inner,
            a
        )

        p2 = polar_point(
            outer,
            a
        )

        width = 1

        if i % 5 == 0:
            width = 2

        pygame.draw.line(
            screen,
            (120, 105, 70),
            p1,
            p2,
            width
        )


# ============================================================
# 粒子
# ============================================================

def draw_particles(
    radius,
    particles,
    angle,
    direction=1
):

    for base_angle, size in particles:

        a = (
            base_angle
            + angle * direction
        )

        x, y = polar_point(
            radius,
            a
        )

        pygame.draw.circle(
            screen,
            (200, 170, 90),
            (x, y),
            size
        )


# ============================================================
# 阳爻
# ============================================================

def draw_yang_line(
    x,
    y,
    length,
    width
):

    pygame.draw.line(
        screen,
        WHITE,
        (
            x - length // 2,
            y
        ),
        (
            x + length // 2,
            y
        ),
        width
    )


# ============================================================
# 阴爻
# ============================================================

def draw_yin_line(
    x,
    y,
    length,
    width
):

    gap = max(
        5,
        length // 7
    )

    pygame.draw.line(
        screen,
        WHITE,
        (
            x - length // 2,
            y
        ),
        (
            x - gap // 2,
            y
        ),
        width
    )

    pygame.draw.line(
        screen,
        WHITE,
        (
            x + gap // 2,
            y
        ),
        (
            x + length // 2,
            y
        ),
        width
    )


# ============================================================
# 单个八卦
# ============================================================

def draw_single_trigram(
    cx,
    cy,
    angle,
    trigram
):

    length = int(
        SHORT * 0.045
    )

    width = max(
        2,
        int(SHORT * 0.006)
    )

    gap = int(
        SHORT * 0.018
    )

    rad = math.radians(
        angle
    )

    for index, value in enumerate(
        trigram
    ):

        local_y = (
            index - 1
        ) * gap

        dx = (
            -math.sin(rad)
            * local_y
        )

        dy = (
            math.cos(rad)
            * local_y
        )

        x = int(
            cx + dx
        )

        y = int(
            cy + dy
        )

        if value == 1:

            draw_yang_line(
                x,
                y,
                length,
                width
            )

        else:

            draw_yin_line(
                x,
                y,
                length,
                width
            )


# ============================================================
# 八卦环
# ============================================================

def draw_trigrams(
    radius,
    angle
):

    count = 8

    small_radius = int(
        SHORT * 0.026
    )

    for i in range(count):

        a = (
            angle
            + 360.0 / count * i
        )

        x, y = polar_point(
            radius,
            a
        )

        pygame.draw.circle(
            screen,
            (10, 10, 16),
            (x, y),
            small_radius + 15
        )

        pygame.draw.circle(
            screen,
            GOLD2,
            (x, y),
            small_radius + 15,
            1
        )

        draw_single_trigram(
            x,
            y,
            a + 90,
            TRIGRAMS[i]
        )

        text = trigram_name_surfaces[i]

        rect = text.get_rect(
            center=(
                x,
                y + small_radius + 28
            )
        )

        screen.blit(
            text,
            rect
        )


# ============================================================
# 天干
# ============================================================

def draw_tiangan(
    radius,
    angle
):

    count = len(
        TIANGAN
    )

    for i in range(count):

        a = (
            angle
            + 360.0 / count * i
        )

        x, y = polar_point(
            radius,
            a
        )

        text = tiangan_surfaces[i]

        rect = text.get_rect(
            center=(x, y)
        )

        screen.blit(
            text,
            rect
        )


# ============================================================
# 地支
# ============================================================

def draw_dizhi(
    radius,
    angle
):

    count = len(
        DIZHI
    )

    for i in range(count):

        a = (
            angle
            - 360.0 / count * i
        )

        x, y = polar_point(
            radius,
            a
        )

        text = dizhi_surfaces[i]

        rect = text.get_rect(
            center=(x, y)
        )

        screen.blit(
            text,
            rect
        )


# ============================================================
# 连接线
# ============================================================

def draw_connection_lines(
    radius,
    angle
):

    count = 12

    for i in range(count):

        a = (
            angle
            + i * 30
        )

        p1 = polar_point(
            radius - 22,
            a
        )

        p2 = polar_point(
            radius + 22,
            a
        )

        pygame.draw.line(
            screen,
            (70, 70, 80),
            p1,
            p2,
            1
        )


# ============================================================
# 椭圆轨道
# ============================================================

def draw_orbit(
    radius,
    angle
):

    points = []

    for i in range(37):

        t = (
            2 * math.pi
            * i / 36
        )

        x = (
            math.cos(t)
            * radius
        )

        y = (
            math.sin(t)
            * radius
            * 0.42
        )

        rad = math.radians(
            angle
        )

        rx = (
            x * math.cos(rad)
            - y * math.sin(rad)
        )

        ry = (
            x * math.sin(rad)
            + y * math.cos(rad)
        )

        points.append(
            (
                int(CENTER_X + rx),
                int(CENTER_Y + ry)
            )
        )

    pygame.draw.lines(
        screen,
        (90, 90, 100),
        False,
        points,
        1
    )


# ============================================================
# 判断某一点位于太极黑半还是白半
# ============================================================

def taiji_color_at(
    px,
    py,
    radius
):

    dx = px - CENTER_X
    dy = py - CENTER_Y

    if dx * dx + dy * dy > radius * radius:
        return None

    # 下方白色圆
    lower_dx = dx
    lower_dy = dy - radius // 2

    if (
        lower_dx * lower_dx
        + lower_dy * lower_dy
        <= (radius // 2) ** 2
    ):
        return "white"

    # 上方黑色圆
    upper_dx = dx
    upper_dy = dy + radius // 2

    if (
        upper_dx * upper_dx
        + upper_dy * upper_dy
        <= (radius // 2) ** 2
    ):
        return "black"

    # 主体左右区域
    if dx < 0:
        return "white"

    return "black"


# ============================================================
# 创建解体粒子
# ============================================================

def create_decomposition_particles():

    global decomp_particles

    decomp_particles = []

    radius = int(
        SHORT * 0.15
    )

    # 大量细小粒子
    for i in range(260):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        distance = (
            random.random() ** 0.65
            * radius
        )

        x = math.cos(angle) * distance
        y = math.sin(angle) * distance

        # 一部分粒子集中在中心
        if random.random() < 0.35:

            x *= 0.55
            y *= 0.55

        if i % 3 == 0:
            color = ORANGE
        elif i % 3 == 1:
            color = BLUE
        else:
            color = PURPLE

        decomp_particles.append(
            [
                x,
                y,
                random.uniform(0.7, 2.4),
                random.uniform(0.7, 1.5),
                random.uniform(-1.2, 1.2),
                color
            ]
        )


# ============================================================
# 开始解体
# ============================================================

def start_decomposition():

    global decomp_state
    global decomp_progress
    global decomp_time

    # 正在播放时不重复触发
    if decomp_state != DECOMP_IDLE:
        return

    create_decomposition_particles()

    decomp_state = DECOMP_EXPAND
    decomp_progress = 0.0
    decomp_time = 0.0


# ============================================================
# 更新解体
# ============================================================

def update_decomposition(dt):

    global decomp_state
    global decomp_progress
    global decomp_time

    if decomp_state == DECOMP_IDLE:
        return

    decomp_time += dt

    p = decomp_time / DECOMP_DURATION

    if p > 1.0:
        p = 1.0

    if decomp_state == DECOMP_EXPAND:

        decomp_progress = p

        if p >= 1.0:

            decomp_state = DECOMP_MERGE
            decomp_time = 0.0

    elif decomp_state == DECOMP_MERGE:

        decomp_progress = 1.0 - p

        if p >= 1.0:

            decomp_progress = 0.0
            decomp_state = DECOMP_IDLE


# ============================================================
# 缓动
# ============================================================

def ease_out(t):

    return 1.0 - (1.0 - t) ** 3


def ease_in(t):

    return t ** 3


# ============================================================
# 太极细线背景
# ============================================================

def draw_taiji_detail_lines(
    radius
):

    # 中心增加大量非常细的轨迹线
    # 让中心不会显得空

    for i in range(48):

        angle = (
            i * 7.5
            + rotation_angle * 0.35
        )

        inner = radius * 0.70
        outer = radius * 1.12

        p1 = polar_point(
            inner,
            angle
        )

        p2 = polar_point(
            outer,
            angle + 1.5
        )

        if i % 2 == 0:
            color = (70, 60, 35)
        else:
            color = (45, 55, 65)

        pygame.draw.line(
            screen,
            color,
            p1,
            p2,
            1
        )


# ============================================================
# 绘制解体状态
# ============================================================

def draw_decomposition(
    radius
):

    p = decomp_progress

    if decomp_state == DECOMP_EXPAND:

        progress = ease_out(p)

    else:

        progress = ease_in(p)

    r = float(radius)

    # --------------------------------------------------------
    # 中心大量细线
    # --------------------------------------------------------

    for i in range(100):

        angle = (
            i * 3.6
            + rotation_angle
        )

        # 解体后线越来越长
        inner = r * (
            0.08
            + progress * 0.20
        )

        outer = r * (
            0.55
            + progress * 3.4
        )

        x1, y1 = polar_point(
            inner,
            angle
        )

        x2, y2 = polar_point(
            outer,
            angle + math.sin(i) * 3
        )

        if i % 3 == 0:
            color = ORANGE
        elif i % 3 == 1:
            color = BLUE
        else:
            color = PURPLE

        pygame.draw.line(
            screen,
            color,
            (x1, y1),
            (x2, y2),
            1
        )

    # --------------------------------------------------------
    # 密集同心能量环
    # --------------------------------------------------------

    for i in range(16):

        rr = (
            r * 0.25
            + progress
            * r
            * (0.25 + i * 0.20)
        )

        if i % 2 == 0:

            color = (
                140,
                75,
                35
            )

        else:

            color = (
                40,
                90,
                150
            )

        pygame.draw.circle(
            screen,
            color,
            (
                CENTER_X,
                CENTER_Y
            ),
            max(1, int(rr)),
            1
        )

    # --------------------------------------------------------
    # 黑白两半的彩色能量
    # --------------------------------------------------------

    energy_distance = (
        r * 0.18
        + progress * r * 1.8
    )

    # 橙色能量
    ox, oy = polar_point(
        energy_distance,
        145 + rotation_angle
    )

    pygame.draw.circle(
        screen,
        ORANGE,
        (ox, oy),
        max(
            3,
            int(r * 0.18 * (1.0 - progress * 0.45))
        ),
        2
    )

    # 蓝紫能量
    bx, by = polar_point(
        energy_distance,
        325 - rotation_angle
    )

    pygame.draw.circle(
        screen,
        BLUE,
        (bx, by),
        max(
            3,
            int(r * 0.18 * (1.0 - progress * 0.45))
        ),
        2
    )

    # --------------------------------------------------------
    # 粒子向外飞，再向中心回来
    # --------------------------------------------------------

    for particle in decomp_particles:

        x = particle[0]
        y = particle[1]
        size = particle[2]
        stretch = particle[3]
        spin = particle[4]
        color = particle[5]

        base_angle = math.atan2(
            y,
            x
        )

        distance = math.sqrt(
            x * x
            + y * y
        )

        # 解体时向外放大
        final_distance = (
            distance
            * (
                1.0
                + progress * 3.5
            )
        )

        angle = (
            base_angle
            + spin * progress
        )

        px = (
            CENTER_X
            + math.cos(angle)
            * final_distance
        )

        py = (
            CENTER_Y
            + math.sin(angle)
            * final_distance
        )

        px = int(px)
        py = int(py)

        particle_size = max(
            1,
            int(
                size
                * (
                    1.0
                    + progress * 1.6
                )
            )
        )

        pygame.draw.circle(
            screen,
            color,
            (px, py),
            particle_size
        )

        # 粒子拖尾
        if particle_size >= 2:

            tail_length = (
                particle_size
                * 5
                * (0.5 + progress)
            )

            tx = int(
                px
                - math.cos(angle)
                * tail_length
            )

            ty = int(
                py
                - math.sin(angle)
                * tail_length
            )

            pygame.draw.line(
                screen,
                color,
                (tx, ty),
                (px, py),
                1
            )

    # --------------------------------------------------------
    # 中心核心
    # --------------------------------------------------------

    core_radius = int(
        r * (
            0.16
            + (1.0 - progress) * 0.18
        )
    )

    pygame.draw.circle(
        screen,
        ORANGE,
        (
            CENTER_X,
            CENTER_Y
        ),
        core_radius,
        1
    )

    pygame.draw.circle(
        screen,
        BLUE,
        (
            CENTER_X,
            CENTER_Y
        ),
        max(
            2,
            core_radius - 7
        ),
        1
    )

    # 中央白色核心
    pygame.draw.circle(
        screen,
        WHITE,
        (
            CENTER_X,
            CENTER_Y
        ),
        max(
            2,
            int(4 + 5 * (1.0 - progress))
        )
    )


# ============================================================
# 太极
# ============================================================

def draw_taiji(
    radius
):

    r = int(radius)

    # 解体/合成时不画普通太极
    if decomp_state != DECOMP_IDLE:

        draw_decomposition(
            radius
        )

        return

    # --------------------------------------------------------
    # 外金色边框
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        GOLD,
        (
            CENTER_X,
            CENTER_Y
        ),
        r + 4,
        2
    )

    # --------------------------------------------------------
    # 黑色基础圆
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        BLACK,
        (
            CENTER_X,
            CENTER_Y
        ),
        r
    )

    # --------------------------------------------------------
    # 白色左半圆
    # --------------------------------------------------------

    points = []

    for i in range(61):

        angle = math.radians(
            90 + i * 3
        )

        x = (
            CENTER_X
            + math.cos(angle) * r
        )

        y = (
            CENTER_Y
            + math.sin(angle) * r
        )

        points.append(
            (
                int(x),
                int(y)
            )
        )

    points.append(
        (
            CENTER_X,
            CENTER_Y
        )
    )

    pygame.draw.polygon(
        screen,
        WHITE,
        points
    )

    # --------------------------------------------------------
    # 黑色上半圆
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        BLACK,
        (
            CENTER_X,
            CENTER_Y - r // 2
        ),
        r // 2
    )

    # --------------------------------------------------------
    # 白色下半圆
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        WHITE,
        (
            CENTER_X,
            CENTER_Y + r // 2
        ),
        r // 2
    )

    # --------------------------------------------------------
    # 两个眼睛
    # --------------------------------------------------------

    eye_r = max(
        3,
        r // 7
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (
            CENTER_X,
            CENTER_Y - r // 2
        ),
        eye_r
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (
            CENTER_X,
            CENTER_Y + r // 2
        ),
        eye_r
    )

    # --------------------------------------------------------
    # 最外金色轮廓
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        GOLD,
        (
            CENTER_X,
            CENTER_Y
        ),
        r,
        2
    )


# ============================================================
# 中心光环
# ============================================================

def draw_center_glow(
    radius
):

    if decomp_state == DECOMP_IDLE:

        for i in range(3):

            r = (
                radius
                + 8
                + i * 8
            )

            pygame.draw.circle(
                screen,
                (100, 80, 35),
                (
                    CENTER_X,
                    CENTER_Y
                ),
                r,
                1
            )

        # 额外细线
        draw_taiji_detail_lines(
            radius
        )

    else:

        p = decomp_progress

        r = int(
            radius
            * (
                1.0
                + p * 2.8
            )
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            (
                CENTER_X,
                CENTER_Y
            ),
            r,
            1
        )

        pygame.draw.circle(
            screen,
            BLUE,
            (
                CENTER_X,
                CENTER_Y
            ),
            max(
                1,
                r - 7
            ),
            1
        )


# ============================================================
# 更新旋转
# ============================================================

def update_rotation():

    global rotation_angle
    global rotation_speed

    if pressing_center:

        rotation_speed += ACCELERATION

        if rotation_speed > MAX_SPEED:

            rotation_speed = MAX_SPEED

    else:

        rotation_speed *= FRICTION

        if abs(rotation_speed) < 0.002:

            rotation_speed = 0.0

    rotation_angle += rotation_speed


# ============================================================
# 判断是否按住中心
# ============================================================

def is_center_pressed(
    pos
):

    dx = (
        pos[0]
        - CENTER_X
    )

    dy = (
        pos[1]
        - CENTER_Y
    )

    distance = math.sqrt(
        dx * dx
        + dy * dy
    )

    touch_radius = int(
        SHORT * 0.15
    )

    return distance <= touch_radius


# ============================================================
# 双指是否一黑一白
# ============================================================

def has_black_white_fingers():

    radius = int(
        SHORT * 0.15
    )

    colors = []

    for pos in active_fingers.values():

        color = taiji_color_at(
            pos[0],
            pos[1],
            radius
        )

        if color is not None:

            colors.append(
                color
            )

    return (
        "black" in colors
        and "white" in colors
    )


# ============================================================
# 事件处理
# ============================================================

def handle_events():

    global pressing_center

    for event in pygame.event.get():

        # ----------------------------------------------------
        # 退出
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            return False

        # ----------------------------------------------------
        # 鼠标按下
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if is_center_pressed(
                event.pos
            ):

                pressing_center = True

        # ----------------------------------------------------
        # 鼠标松开
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            pressing_center = False

        # ----------------------------------------------------
        # Android 手指按下
        # ----------------------------------------------------

        elif event.type == pygame.FINGERDOWN:

            x = int(
                event.x * WIDTH
            )

            y = int(
                event.y * HEIGHT
            )

            active_fingers[
                event.finger_id
            ] = (
                x,
                y
            )

            # 两根手指一根碰黑、一根碰白
            if (
                len(active_fingers) >= 2
                and has_black_white_fingers()
            ):

                start_decomposition()

            if is_center_pressed(
                (x, y)
            ):

                pressing_center = True

        # ----------------------------------------------------
        # Android 手指移动
        # ----------------------------------------------------

        elif event.type == pygame.FINGERMOTION:

            if event.finger_id in active_fingers:

                x = int(
                    event.x * WIDTH
                )

                y = int(
                    event.y * HEIGHT
                )

                active_fingers[
                    event.finger_id
                ] = (
                    x,
                    y
                )

                # 如果移动过程中变成一黑一白，也触发
                if (
                    len(active_fingers) >= 2
                    and has_black_white_fingers()
                ):

                    start_decomposition()

        # ----------------------------------------------------
        # Android 手指松开
        # ----------------------------------------------------

        elif event.type == pygame.FINGERUP:

            if event.finger_id in active_fingers:

                del active_fingers[
                    event.finger_id
                ]

            pressing_center = (
                len(active_fingers) > 0
            )

        # ----------------------------------------------------
        # 返回键 / ESC
        # ----------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                return False

    return True


# ============================================================
# 速度信息
# ============================================================

def draw_speed_info():

    text = FONT_SMALL.render(
        "速度 %.2f" % abs(rotation_speed),
        True,
        WHITE
    )

    screen.blit(
        text,
        (20, 20)
    )

    if decomp_state != DECOMP_IDLE:

        state = "太极解体 / 合成"

    elif pressing_center:

        state = "加速中"

    elif rotation_speed > 0.05:

        state = "惯性旋转"

    else:

        state = "停止"

    state_text = FONT_SMALL.render(
        state,
        True,
        GOLD
    )

    screen.blit(
        state_text,
        (
            20,
            20 + FONT_SMALL.get_height() + 4
        )
    )


# ============================================================
# 底部提示
# ============================================================

def draw_hint():

    if decomp_state != DECOMP_IDLE:

        message = (
            "中心解体 → 向外放大 → 彩色粒子慢慢合成"
        )

    elif len(active_fingers) >= 2:

        message = (
            "双指一黑一白 · 正在触发"
        )

    elif pressing_center:

        message = (
            "按住中央太极 · 加速旋转"
        )

    elif rotation_speed > 0.05:

        message = (
            "松开 · 惯性旋转"
        )

    else:

        message = (
            "双指分别触碰黑白两半 · 触发解体"
        )

    text = FONT_MEDIUM.render(
        message,
        True,
        WHITE
    )

    rect = text.get_rect(
        center=(
            CENTER_X,
            HEIGHT - SHORT // 13
        )
    )

    screen.blit(
        text,
        rect
    )


# ============================================================
# 绘制整个场景
# ============================================================

def draw_scene():

    draw_background()

    r1 = int(
        SHORT * 0.15
    )

    r2 = int(
        SHORT * 0.22
    )

    r3 = int(
        SHORT * 0.30
    )

    r4 = int(
        SHORT * 0.38
    )

    r5 = int(
        SHORT * 0.45
    )

    # 外层圆环
    draw_ring(
        r5,
        1,
        (55, 55, 65)
    )

    draw_ring(
        r4,
        1,
        GOLD2
    )

    draw_ring(
        r3,
        1,
        (100, 90, 65)
    )

    draw_ring(
        r2,
        1,
        (70, 70, 80)
    )

    # 刻度
    draw_scale_ring(
        r5,
        72,
        rotation_angle
    )

    draw_scale_ring(
        r4,
        48,
        -rotation_angle
    )

    # 粒子
    draw_particles(
        r5,
        particle_ring_1,
        rotation_angle,
        1
    )

    draw_particles(
        r3,
        particle_ring_2,
        rotation_angle,
        -1
    )

    # 连接线
    draw_connection_lines(
        r4,
        rotation_angle
    )

    # 椭圆轨道
    draw_orbit(
        r4,
        rotation_angle * 0.7
    )

    draw_orbit(
        r5,
        -rotation_angle * 0.45
    )

    # 地支
    draw_dizhi(
        r5,
        -rotation_angle * 0.75
    )

    # 天干
    draw_tiangan(
        r4,
        rotation_angle
    )

    # 八卦
    draw_trigrams(
        r3,
        rotation_angle
    )

    # 中心光环
    draw_center_glow(
        r1
    )

    # 太极
    draw_taiji(
        r1
    )

    # UI
    draw_speed_info()

    draw_hint()


# ============================================================
# 主程序
# ============================================================

def main():

    init_game()

    find_chinese_font()

    init_fonts()

    create_text_cache()

    create_stars()

    create_particle_rings()

    running = True

    while running:

        running = handle_events()

        update_decomposition(
            1.0 / 60.0
        )

        update_rotation()

        draw_scene()

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":

    main()
