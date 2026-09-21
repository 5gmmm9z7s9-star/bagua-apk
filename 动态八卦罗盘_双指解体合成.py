# -*- coding: utf-8 -*-

import os
import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivy.core.window import Window
from kivy import platform


# ============================================================
# 配置
# ============================================================

ACCELERATION = 0.018
FRICTION = 0.985
MAX_SPEED = 1.8

DECOMP_DURATION = 1.05

DECOMP_IDLE = 0
DECOMP_EXPAND = 1
DECOMP_MERGE = 2


# ============================================================
# 颜色
# ============================================================

BLACK = (3 / 255, 3 / 255, 7 / 255, 1)
WHITE = (245 / 255, 245 / 255, 245 / 255, 1)
GRAY = (110 / 255, 110 / 255, 120 / 255, 1)

GOLD = (220 / 255, 180 / 255, 70 / 255, 1)
GOLD2 = (145 / 255, 110 / 255, 35 / 255, 1)

ORANGE = (255 / 255, 145 / 255, 45 / 255, 1)
BLUE = (55 / 255, 175 / 255, 255 / 255, 1)
PURPLE = (175 / 255, 80 / 255, 255 / 255, 1)
CYAN = (80 / 255, 225 / 255, 255 / 255, 1)


# ============================================================
# 字体
# ============================================================

FONT_NAME = None


def register_chinese_font():
    """探测并注册一个能显示中文的字体。"""
    global FONT_NAME

    candidates = [
        "/system/fonts/NotoSansCJK-Regular.ttc",
        "/system/fonts/NotoSansCJK-Regular.otf",
        "/system/fonts/NotoSansSC-Regular.otf",
        "/system/fonts/NotoSansSC-Regular.ttf",
        "/system/fonts/DroidSansFallback.ttf",
        "/system/fonts/NotoSerifCJK-Regular.ttc",
        "/system/fonts/NotoSansCJKSC-Regular.otf",
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                LabelBase.register(
                    name="CJKMix",
                    fn_regular=path,
                )
                FONT_NAME = "CJKMix"
                return
            except Exception:
                pass

    FONT_NAME = None


def get_font_name():
    return FONT_NAME or "Sans"


# ============================================================
# 八卦 / 天干 / 地支
# ============================================================

TRIGRAMS = [
    [1, 1, 1],
    [1, 1, 0],
    [1, 0, 1],
    [1, 0, 0],
    [0, 1, 1],
    [0, 1, 0],
    [0, 0, 1],
    [0, 0, 0],
]

TRIGRAM_NAMES = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


# ============================================================
# 主控件
# ============================================================

class BaguaWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rotation_angle = 0.0
        self.rotation_speed = 0.0
        self.pressing_center = False

        self.decomp_state = DECOMP_IDLE
        self.decomp_progress = 0.0
        self.decomp_time = 0.0
        self.decomp_particles = []

        self.stars = []
        self.particle_ring_1 = []
        self.particle_ring_2 = []

        self.tiangan_surfaces = []
        self.dizhi_surfaces = []
        self.trigram_name_surfaces = []

        self.font_small = None
        self.font_medium = None
        self.font_big = None

        self.canvas_group = InstructionGroup()

        self._fingers = {}          # 触控点
        self._last_drag_angle = None

        Clock.schedule_once(self._delayed_setup, 0)
        Clock.schedule_interval(self._tick, 1 / 60.0)

    # ------------------------------------------------------------
    # 初始化
    # ------------------------------------------------------------

    def _delayed_setup(self, dt):
        register_chinese_font()
        self._build_fonts()
        self._build_text_cache()
        self._build_stars()
        self._build_particle_rings()

    def _build_fonts(self):
        fn = get_font_name()
        base = min(self.width, self.height)

        self.font_small = fn
        self.font_medium = fn
        self.font_big = fn

        self._font_size_small = max(16, int(base / 45))
        self._font_size_medium = max(20, int(base / 32))
        self._font_size_big = max(28, int(base / 20))

    def _text(self, text, size, color):
        """用当前可用字体生成文字纹理（返回 Rectangle 指令）。"""
        from kivy.graphics.texture import Texture
        from kivy.core.text import Label as CoreLabel

        fn = get_font_name()
        label = CoreLabel(
            text=text,
            font_name=fn or "Sans",
            font_size=size,
            color=color,
        )
        label.refresh()
        texture = label.texture

        rect = Rectangle(
            texture=texture,
            size=texture.size,
            pos=(0, 0),
        )
        return rect

    def _build_text_cache(self):
        for text in TIANGAN:
            self.tiangan_surfaces.append(
                self._text(text, self._font_size_small, (1, 1, 1, 1))
            )
        for text in DIZHI:
            self.dizhi_surfaces.append(
                self._text(text, self._font_size_small, (200 / 255, 200 / 255, 210 / 255, 1))
            )
        for text in TRIGRAM_NAMES:
            self.trigram_name_surfaces.append(
                self._text(text, self._font_size_small, (GOLD[0], GOLD[1], GOLD[2], 1))
            )

    def _build_stars(self):
        w, h = self.width, self.height
        count = int(w * h / 9000)
        count = max(120, min(count, 280))
        for _ in range(count):
            x = random.randint(0, int(w))
            y = random.randint(0, int(h))
            radius = random.choice([1, 1, 1, 1, 2])
            brightness = random.randint(70, 180) / 255.0
            self.stars.append((x, y, radius, brightness))

    def _build_particle_rings(self):
        for i in range(60):
            self.particle_ring_1.append(
                ((360.0 / 60) * i, random.choice([1, 1, 1, 2]))
            )
        for i in range(42):
            self.particle_ring_2.append(
                ((360.0 / 42) * i, random.choice([1, 1, 2]))
            )

    # ------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------

    def _short(self):
        return min(self.width, self.height)

    def _polar(self, radius, angle):
        rad = math.radians(angle)
        return (
            self.center_x + math.cos(rad) * radius,
            self.center_y + math.sin(rad) * radius,
        )

    # ------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------

    def _tick(self, dt):
        self._update_rotation()
        self._update_decomposition(dt)
        self._redraw()

    def _update_rotation(self):
        if self.pressing_center:
            self.rotation_speed += ACCELERATION
            if self.rotation_speed > MAX_SPEED:
                self.rotation_speed = MAX_SPEED
        else:
            self.rotation_speed *= FRICTION
            if abs(self.rotation_speed) < 0.002:
                self.rotation_speed = 0.0

        self.rotation_angle += self.rotation_speed

    # ------------------------------------------------------------
    # 解体动画
    # ------------------------------------------------------------

    def start_decomposition(self):
        if self.decomp_state != DECOMP_IDLE:
            return
        self._create_decomposition_particles()
        self.decomp_state = DECOMP_EXPAND
        self.decomp_progress = 0.0
        self.decomp_time = 0.0

    def _create_decomposition_particles(self):
        self.decomp_particles = []
        radius = self._short() * 0.15
        for i in range(260):
            angle = random.uniform(0, math.pi * 2)
            distance = (random.random() ** 0.65) * radius
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            if random.random() < 0.35:
                x *= 0.55
                y *= 0.55
            if i % 3 == 0:
                color = ORANGE
            elif i % 3 == 1:
                color = BLUE
            else:
                color = PURPLE
            self.decomp_particles.append([
                x, y,
                random.uniform(0.7, 2.4),
                random.uniform(0.7, 1.5),
                random.uniform(-1.2, 1.2),
                color,
            ])

    def _update_decomposition(self, dt):
        if self.decomp_state == DECOMP_IDLE:
            return

        self.decomp_time += dt
        p = self.decomp_time / DECOMP_DURATION
        if p > 1.0:
            p = 1.0

        if self.decomp_state == DECOMP_EXPAND:
            self.decomp_progress = p
            if p >= 1.0:
                self.decomp_state = DECOMP_MERGE
                self.decomp_time = 0.0
        elif self.decomp_state == DECOMP_MERGE:
            self.decomp_progress = 1.0 - p
            if p >= 1.0:
                self.decomp_progress = 0.0
                self.decomp_state = DECOMP_IDLE

    # ============================================================
    # 绘制
    # ============================================================

    def _redraw(self):
        self.canvas.clear()

        with self.canvas:
            self._draw_background()
            self._draw_disc_backdrop()
            self._draw_tiangan(self._short() * 0.30, self.rotation_angle * 0.5)
            self._draw_dizhi(self._short() * 0.40, -self.rotation_angle * 0.4)
            self._draw_connection_lines(self._short() * 0.25, self.rotation_angle)
            self._draw_scale_ring(self._short() * 0.22, 24, -self.rotation_angle * 0.6)
            self._draw_trigrams(self._short() * 0.17, self.rotation_angle)
            self._draw_particles(self._short() * 0.20, self.particle_ring_1,
                                 self.rotation_angle * 0.8, 1)
            self._draw_particles(self._short() * 0.205, self.particle_ring_2,
                                 -self.rotation_angle * 0.6, -1)
            self._draw_center_glow(self._short() * 0.155)
            self._draw_taiji(self._short() * 0.155)

    # ------------------------------------------------------------
    # 背景
    # ------------------------------------------------------------

    def _draw_background(self):
        Color(*BLACK)
        Rectangle(pos=(0, 0), size=self.size)
        for x, y, radius, brightness in self.stars:
            Color(brightness, brightness, brightness, 1)
            Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius * 2))

    # ------------------------------------------------------------
    # 罗盘底盘
    # ------------------------------------------------------------

    def _draw_disc_backdrop(self):
        r = self._short() * 0.43
        Color(*GOLD2)
        Ellipse(
            pos=(self.center_x - r - 6, self.center_y - r - 6),
            size=(r * 2 + 12, r * 2 + 12),
        )
        Color(8 / 255, 8 / 255, 14 / 255, 1)
        Ellipse(
            pos=(self.center_x - r, self.center_y - r),
            size=(r * 2, r * 2),
        )
        Color(70 / 255, 70 / 255, 80 / 255, 1)
        Line(circle=(self.center_x, self.center_y, r - 2), width=1)

    # ------------------------------------------------------------
    # 圆环
    # ------------------------------------------------------------

    def _draw_ring(self, radius, width=1, color=GOLD2):
        Color(*color)
        Line(circle=(self.center_x, self.center_y, radius), width=width)

    def _draw_scale_ring(self, radius, count, angle):
        for i in range(count):
            a = angle + 360.0 / count * i
            p1 = self._polar(radius - 8, a)
            p2 = self._polar(radius + 8, a)
            w = 2 if i % 5 == 0 else 1
            Color(120 / 255, 105 / 255, 70 / 255, 1)
            Line(points=[p1[0], p1[1], p2[0], p2[1]], width=w)

    def _draw_connection_lines(self, radius, angle):
        for i in range(12):
            a = angle + i * 30
            p1 = self._polar(radius - 22, a)
            p2 = self._polar(radius + 22, a)
            Color(70 / 255, 70 / 255, 80 / 255, 1)
            Line(points=[p1[0], p1[1], p2[0], p2[1]], width=1)

    def _draw_particles(self, radius, particles, angle, direction=1):
        for base_angle, size in particles:
            a = base_angle + angle * direction
            x, y = self._polar(radius, a)
            Color(200 / 255, 170 / 255, 90 / 255, 1)
            Ellipse(pos=(x - size, y - size), size=(size * 2, size * 2))

    # ------------------------------------------------------------
    # 卦象
    # ------------------------------------------------------------

    def _draw_single_trigram(self, cx, cy, angle, trigram):
        length = int(self._short() * 0.045)
        width = max(2, int(self._short() * 0.006))
        gap = int(self._short() * 0.018)
        rad = math.radians(angle)

        for index, value in enumerate(trigram):
            local_y = (index - 1) * gap
            dx = -math.sin(rad) * local_y
            dy = math.cos(rad) * local_y
            x = int(cx + dx)
            y = int(cy + dy)

            if value == 1:
                self._draw_yang_line(x, y, length, width)
            else:
                self._draw_yin_line(x, y, length, width)

    def _draw_yang_line(self, x, y, length, width):
        Color(*WHITE)
        Line(points=[x - length / 2, y, x + length / 2, y], width=width)

    def _draw_yin_line(self, x, y, length, width):
        gap = max(5, length // 7)
        Color(*WHITE)
        Line(points=[x - length / 2, y, x - gap / 2, y], width=width)
        Line(points=[x + gap / 2, y, x + length / 2, y], width=width)

    def _draw_trigrams(self, radius, angle):
        small_radius = int(self._short() * 0.026)
        for i in range(8):
            a = angle + 360.0 / 8 * i
            x, y = self._polar(radius, a)
            Color(10 / 255, 10 / 255, 16 / 255, 1)
            Ellipse(
                pos=(x - small_radius - 15, y - small_radius - 15),
                size=(small_radius * 2 + 30, small_radius * 2 + 30),
            )
            Color(*GOLD2)
            Line(circle=(x, y, small_radius + 15), width=1)
            self._draw_single_trigram(x, y, a + 90, TRIGRAMS[i])

            text = self.trigram_name_surfaces[i]
            text.pos = (x - text.texture.size[0] / 2,
                        y + small_radius + 28 - text.texture.size[1] / 2)

    # ------------------------------------------------------------
    # 天干 / 地支
    # ------------------------------------------------------------

    def _draw_tiangan(self, radius, angle):
        for i, text in enumerate(self.tiangan_surfaces):
            a = angle + 360.0 / len(TIANGAN) * i
            x, y = self._polar(radius, a)
            text.pos = (x - text.texture.size[0] / 2,
                        y - text.texture.size[1] / 2)

    def _draw_dizhi(self, radius, angle):
        for i, text in enumerate(self.dizhi_surfaces):
            a = angle - 360.0 / len(DIZHI) * i
            x, y = self._polar(radius, a)
            text.pos = (x - text.texture.size[0] / 2,
                        y - text.texture.size[1] / 2)

    # ------------------------------------------------------------
    # 太极
    # ------------------------------------------------------------

    def _draw_taiji(self, radius):
        r = float(radius)

        if self.decomp_state != DECOMP_IDLE:
            self._draw_decomposition(radius)
            return

        # 金色外框
        Color(*GOLD)
        Line(circle=(self.center_x, self.center_y, r + 4), width=2)

        # 黑色底
        Color(*BLACK)
        Ellipse(
            pos=(self.center_x - r, self.center_y - r),
            size=(r * 2, r * 2),
        )

        # 白左半圆（用扇形多边形）
        points = []
        for i in range(61):
            angle = math.radians(90 + i * 3)
            points.append((
                self.center_x + math.cos(angle) * r,
                self.center_y + math.sin(angle) * r,
            ))
        points.append((self.center_x, self.center_y))
        Color(*WHITE)
        self._poly(points)

        # 黑白鱼
        Color(*BLACK)
        Ellipse(
            pos=(self.center_x - r / 2, self.center_y - r / 2 - r / 2),
            size=(r, r),
        )
        Color(*WHITE)
        Ellipse(
            pos=(self.center_x - r / 2, self.center_y - r / 2 + r / 2),
            size=(r, r),
        )

        # 鱼眼
        eye_r = max(3, r / 7)
        Color(*WHITE)
        Ellipse(
            pos=(self.center_x - eye_r, self.center_y - r / 2 - eye_r),
            size=(eye_r * 2, eye_r * 2),
        )
        Color(*BLACK)
        Ellipse(
            pos=(self.center_x - eye_r, self.center_y + r / 2 - eye_r),
            size=(eye_r * 2, eye_r * 2),
        )

        # 金色轮廓
        Color(*GOLD)
        Line(circle=(self.center_x, self.center_y, r), width=2)

    def _poly(self, points):
        """绘制填充多边形。"""
        from kivy.graphics import Mesh
        if len(points) < 3:
            return
        vertices = []
        indices = []
        for i, (x, y) in enumerate(points):
            vertices.extend([x, y, 0, 0])
            indices.append(i)
        Mesh(
            vertices=vertices,
            indices=indices,
            mode="triangle_fan",
            texture=None,
        )

    # ------------------------------------------------------------
    # 解体
    # ------------------------------------------------------------

    def _draw_decomposition(self, radius):
        p = self.decomp_progress
        if self.decomp_state == DECOMP_EXPAND:
            progress = 1.0 - (1.0 - p) ** 3
        else:
            progress = p ** 3

        r = float(radius)

        # 细线
        for i in range(100):
            angle = i * 3.6 + self.rotation_angle
            inner = r * (0.08 + progress * 0.20)
            outer = r * (0.55 + progress * 3.4)
            x1, y1 = self._polar(inner, angle)
            x2, y2 = self._polar(outer, angle + math.sin(i) * 3)
            if i % 3 == 0:
                Color(*ORANGE)
            elif i % 3 == 1:
                Color(*BLUE)
            else:
                Color(*PURPLE)
            Line(points=[x1, y1, x2, y2], width=1)

        # 能量环
        for i in range(16):
            rr = r * 0.25 + progress * r * (0.25 + i * 0.20)
            Color(*((140 / 255, 75 / 255, 35 / 255, 1))
                  if i % 2 == 0 else (40 / 255, 90 / 255, 150 / 255, 1))
            Line(circle=(self.center_x, self.center_y, max(1, rr)), width=1)

        # 能量球
        energy_distance = r * 0.18 + progress * r * 1.8
        ox, oy = self._polar(energy_distance, 145 + self.rotation_angle)
        Color(*ORANGE)
        Ellipse(
            pos=(ox - max(3, r * 0.18 * (1.0 - progress * 0.45)) / 2,
                 oy - max(3, r * 0.18 * (1.0 - progress * 0.45)) / 2),
            size=(max(3, r * 0.18 * (1.0 - progress * 0.45)),
                  max(3, r * 0.18 * (1.0 - progress * 0.45))),
        )
        bx, by = self._polar(energy_distance, 325 - self.rotation_angle)
        Color(*BLUE)
        Ellipse(
            pos=(bx - max(3, r * 0.18 * (1.0 - progress * 0.45)) / 2,
                 by - max(3, r * 0.18 * (1.0 - progress * 0.45)) / 2),
            size=(max(3, r * 0.18 * (1.0 - progress * 0.45)),
                  max(3, r * 0.18 * (1.0 - progress * 0.45))),
        )

        # 粒子
        for particle in self.decomp_particles:
            x, y = particle[0], particle[1]
            size = particle[2]
            spin = particle[4]
            color = particle[5]

            base_angle = math.atan2(y, x)
            distance = math.sqrt(x * x + y * y)
            final_distance = distance * (1.0 + progress * 3.5)
            angle = base_angle + spin * progress
            px = self.center_x + math.cos(angle) * final_distance
            py = self.center_y + math.sin(angle) * final_distance
            particle_size = max(1, int(size * (1.0 + progress * 1.6)))

            Color(*color)
            Ellipse(
                pos=(px - particle_size, py - particle_size),
                size=(particle_size * 2, particle_size * 2),
            )

            if particle_size >= 2:
                tail_length = particle_size * 5 * (0.5 + progress)
                tx = px - math.cos(angle) * tail_length
                ty = py - math.sin(angle) * tail_length
                Line(points=[tx, ty, px, py], width=1)

        # 中心核心
        core_radius = r * (0.16 + (1.0 - progress) * 0.18)
        Color(*ORANGE)
        Line(circle=(self.center_x, self.center_y, core_radius), width=1)
        Color(*BLUE)
        Line(circle=(self.center_x, self.center_y, max(2, core_radius - 7)), width=1)
        Color(*WHITE)
        Ellipse(
            pos=(self.center_x - max(2, 4 + 5 * (1.0 - progress)),
                 self.center_y - max(2, 4 + 5 * (1.0 - progress))),
            size=(max(2, 4 + 5 * (1.0 - progress)) * 2,
                  max(2, 4 + 5 * (1.0 - progress)) * 2),
        )

    # ------------------------------------------------------------
    # 中心光环
    # ------------------------------------------------------------

    def _draw_center_glow(self, radius):
        if self.decomp_state == DECOMP_IDLE:
            for i in range(3):
                r = radius + 8 + i * 8
                Color(100 / 255, 80 / 255, 35 / 255, 1)
                Line(circle=(self.center_x, self.center_y, r), width=1)
            self._draw_taiji_detail_lines(radius)
        else:
            p = self.decomp_progress
            r = radius * (1.0 + p * 2.8)
            Color(*ORANGE)
            Line(circle=(self.center_x, self.center_y, r), width=1)
            Color(*BLUE)
            Line(circle=(self.center_x, self.center_y, max(1, r - 7)), width=1)

    def _draw_taiji_detail_lines(self, radius):
        r = float(radius)
        for i in range(48):
            angle = i * 7.5 + self.rotation_angle * 0.35
            inner = r * 0.70
            outer = r * 1.12
            p1 = self._polar(inner, angle)
            p2 = self._polar(outer, angle + 1.5)
            Color(*((70 / 255, 60 / 255, 35 / 255, 1))
                  if i % 2 == 0 else (45 / 255, 55 / 255, 65 / 255, 1))
            Line(points=[p1[0], p1[1], p2[0], p2[1]], width=1)

    # ------------------------------------------------------------
    # 触屏 / 鼠标输入
    # ------------------------------------------------------------

    def on_touch_down(self, touch):
        self._fingers[touch.id] = (touch.x, touch.y)

        # 双指：触发解体动画
        if len(self._fingers) >= 2:
            self.start_decomposition()
            self._last_drag_angle = None
            return True

        # 单指：若在中心区域则按住加速
        dist = math.hypot(
            touch.x - self.center_x,
            touch.y - self.center_y,
        )
        if dist < self._short() * 0.15:
            self.pressing_center = True

        self._last_drag_angle = math.atan2(
            touch.y - self.center_y,
            touch.x - self.center_x,
        )
        return True

    def on_touch_move(self, touch):
        if touch.id not in self._fingers:
            self._fingers[touch.id] = (touch.x, touch.y)

        self._fingers[touch.id] = (touch.x, touch.y)

        # 双指：以中点为心旋转
        if len(self._fingers) >= 2:
            ids = list(self._fingers.keys())
            p1 = self._fingers[ids[0]]
            p2 = self._fingers[ids[1]]
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2
            new_angle = math.atan2(touch.y - my, touch.x - mx)
            if self._last_drag_angle is not None:
                delta = math.degrees(new_angle - self._last_drag_angle)
                # 归一化到 [-180, 180]
                delta = (delta + 180) % 360 - 180
                self.rotation_angle += delta
            self._last_drag_angle = new_angle
            return True

        # 单指：绕中心旋转
        new_angle = math.atan2(
            touch.y - self.center_y,
            touch.x - self.center_x,
        )
        if self._last_drag_angle is not None:
            delta = math.degrees(new_angle - self._last_drag_angle)
            delta = (delta + 180) % 360 - 180
            self.rotation_angle += delta
        self._last_drag_angle = new_angle
        return True

    def on_touch_up(self, touch):
        if touch.id in self._fingers:
            del self._fingers[touch.id]

        if not self._fingers:
            self.pressing_center = False
            self._last_drag_angle = None

        return True

    # ------------------------------------------------------------
    # 返回键退出（安卓）
    # ------------------------------------------------------------

    def handle_back(self):
        App.get_running_app().stop()


class BaguaApp(App):

    def build(self):
        self.title = "动态八卦罗盘"
        widget = BaguaWidget()
        # 安卓返回键
        if platform == "android":
            try:
                from android.runnable import run_on_ui_thread
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity

                @run_on_ui_thread
                def hook():
                    activity.onBackPressed = lambda: widget.handle_back()

            except Exception:
                pass
        return widget


if __name__ == "__main__":
    BaguaApp().run()
