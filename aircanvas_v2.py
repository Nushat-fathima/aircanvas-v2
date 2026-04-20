import cv2
import numpy as np
import mediapipe as mp
import math
import time
import threading
import collections

# Try to import cross-platform sound
try:
    import winsound
    AUDIO_AVAILABLE = True
    AUDIO_PLATFORM = "windows"
except ImportError:
    try:
        import beepy
        AUDIO_AVAILABLE = True
        AUDIO_PLATFORM = "beepy"
    except ImportError:
        AUDIO_AVAILABLE = False
        AUDIO_PLATFORM = None


# ==============================
# Configuration
# ==============================
class Config:
    WIDTH, HEIGHT = 1280, 720

    # Sensitivity
    PINCH_THRESHOLD = 40
    SMOOTHING = 0.5

    # Brush defaults
    BRUSH_SIZE = 8
    ERASER_SIZE = 30

    # HUD
    HUD_COLOR = (255, 255, 0)

    # Arc palette
    ARC_CENTER = (640, 0)
    ARC_RADIUS = 150
    ARC_THICKNESS = 60

    # Undo/Redo
    MAX_UNDO = 20


# ==============================
# Sound Engine (cross-platform)
# ==============================
class SoundEngine:
    def __init__(self):
        self.active = False
        self.velocity = 0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()

    def set_drawing(self, is_drawing, velocity):
        self.active = is_drawing
        self.velocity = velocity

    def _loop(self):
        while not self.stop_event.is_set():
            if AUDIO_AVAILABLE and self.active:
                try:
                    if AUDIO_PLATFORM == "windows":
                        freq = int(200 + (self.velocity * 5))
                        freq = max(100, min(freq, 800))
                        winsound.Beep(freq, 40)
                    else:
                        time.sleep(0.05)
                except:
                    pass
            else:
                time.sleep(0.05)


# ==============================
# Hand Tracking (optimised)
# ==============================
class HandSystem:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_pos = (0, 0)

    def process(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        results = self.hands.process(img_rgb)
        img_rgb.flags.writeable = True

        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            h, w, _ = img.shape
            points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
            return points
        return None

    def draw_hud(self, img, points, pinch_dist):
        if not points:
            return img

        overlay = img.copy()

        connections = [
            [0,1],[1,2],[2,3],[3,4],
            [0,5],[5,6],[6,7],[7,8],
            [0,9],[9,10],[10,11],[11,12],
            [0,13],[13,14],[14,15],[15,16],
            [0,17],[17,18],[18,19],[19,20]
        ]
        for p1, p2 in connections:
            cv2.line(overlay, points[p1], points[p2], (0, 255, 255), 1, cv2.LINE_AA)
        for pt in points:
            cv2.circle(overlay, pt, 3, (0, 165, 255), -1)
            cv2.circle(overlay, pt, 6, (0, 255, 255), 1)

        idx_x, idx_y = points[8]
        cv2.circle(overlay, (idx_x, idx_y), 10, (255, 255, 255), 1)

        bar_len = 40
        bar_h = 6
        fill = max(0.0, min(1.0, (100 - pinch_dist) / 60))
        bar_color = (0, 255, 0) if pinch_dist < Config.PINCH_THRESHOLD else (0, 0, 255)

        if pinch_dist < Config.PINCH_THRESHOLD:
            cv2.putText(overlay, "ON", (idx_x + 20, idx_y - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, bar_color, 2)

        cv2.rectangle(overlay, (idx_x + 15, idx_y),
                      (idx_x + 15 + bar_len, idx_y + bar_h), (50, 50, 50), -1)
        cv2.rectangle(overlay, (idx_x + 15, idx_y),
                      (idx_x + 15 + int(bar_len * fill), idx_y + bar_h), bar_color, -1)

        return cv2.addWeighted(overlay, 0.7, img, 0.3, 0)


# ==============================
# Arc Color Palette
# ==============================
class ArcPalette:
    def __init__(self):
        self.colors = [
            ((0, 0, 255),    "RED"),
            ((0, 165, 255),  "ORANGE"),
            ((0, 255, 255),  "YELLOW"),
            ((0, 255, 0),    "GREEN"),
            ((255, 255, 0),  "CYAN"),
            ((255, 0, 255),  "PURPLE"),
            ((255, 255, 255),"WHITE"),
            ((128, 0, 128),  "PINK"),
        ]
        self.selected_index = 4

    def draw(self, img, hover_pt):
        num_colors = len(self.colors)
        sector_angle = 180 / num_colors
        cx, cy = Config.ARC_CENTER
        radius = Config.ARC_RADIUS
        hover_index = -1

        if hover_pt:
            hx, hy = hover_pt
            dist = math.hypot(hx - cx, hy - cy)
            if radius < dist < radius + Config.ARC_THICKNESS:
                dx, dy = hx - cx, hy - cy
                angle = math.degrees(math.atan2(dy, dx))
                if angle < 0:
                    angle += 360
                if 0 <= angle <= 180:
                    hover_index = int(angle / sector_angle)

        for i in range(num_colors):
            start_ang = i * sector_angle
            end_ang = (i + 1) * sector_angle
            color, name = self.colors[i]
            thickness = Config.ARC_THICKNESS
            shift = 0

            if i == self.selected_index:
                shift = 15
                cv2.ellipse(img, (cx, cy),
                            (radius + shift, radius + shift),
                            0, start_ang, end_ang, (255, 255, 255), -1)

            if i == hover_index:
                thickness += 10
                cv2.putText(img, name, (cx - 40, cy + radius + 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            cv2.ellipse(img, (cx, cy),
                        (radius + shift + thickness // 2,
                         radius + shift + thickness // 2),
                        0, start_ang, end_ang, color, thickness)

        return hover_index


# ==============================
# Brush Engine
# ==============================
class BrushEngine:
    BRUSHES = ["pen", "spray", "dotted", "calligraphy", "eraser"]

    def __init__(self):
        self.brush_index = 0

    @property
    def current(self):
        return self.BRUSHES[self.brush_index]

    def next_brush(self):
        self.brush_index = (self.brush_index + 1) % len(self.BRUSHES)

    def draw(self, canvas, p1, p2, color, size):
        if self.current == "pen":
            cv2.line(canvas, p1, p2, color, size, cv2.LINE_AA)
            cv2.circle(canvas, p2, size // 2, color, -1)

        elif self.current == "spray":
            num_dots = 40
            for _ in range(num_dots):
                angle = np.random.uniform(0, 2 * math.pi)
                r = np.random.uniform(0, size * 2.5)
                sx = int(p2[0] + r * math.cos(angle))
                sy = int(p2[1] + r * math.sin(angle))
                cv2.circle(canvas, (sx, sy), 1, color, -1)

        elif self.current == "dotted":
            mid = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
            cv2.circle(canvas, mid, size // 2 + 1, color, -1)

        elif self.current == "calligraphy":
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            angle = math.atan2(dy, dx)
            perp = angle + math.pi / 4
            offset = size
            ox = int(offset * math.cos(perp))
            oy = int(offset * math.sin(perp))
            pts = np.array([
                [p1[0] - ox, p1[1] - oy],
                [p1[0] + ox, p1[1] + oy],
                [p2[0] + ox, p2[1] + oy],
                [p2[0] - ox, p2[1] - oy]
            ], dtype=np.int32)
            cv2.fillPoly(canvas, [pts], color)

        elif self.current == "eraser":
            cv2.circle(canvas, p2, Config.ERASER_SIZE, (0, 0, 0), -1)


# ==============================
# On-Screen Toolbar
# ==============================
class Toolbar:
    TOOLBAR_X = 20
    TOOLBAR_Y = 80
    BTN_W = 90
    BTN_H = 44
    PADDING = 10

    def __init__(self, brush_engine):
        self.brush_engine = brush_engine
        self.buttons = [
            {"label": "PEN",        "action": "brush:pen"},
            {"label": "SPRAY",      "action": "brush:spray"},
            {"label": "DOTTED",     "action": "brush:dotted"},
            {"label": "CALLI",      "action": "brush:calligraphy"},
            {"label": "ERASER",     "action": "brush:eraser"},
            {"label": "UNDO",       "action": "undo"},
            {"label": "REDO",       "action": "redo"},
            {"label": "SAVE",       "action": "save"},
            {"label": "CLEAR",      "action": "clear"},
        ]
        self.hover_action = None

    def _btn_rect(self, i):
        x = self.TOOLBAR_X
        y = self.TOOLBAR_Y + i * (self.BTN_H + self.PADDING)
        return x, y, x + self.BTN_W, y + self.BTN_H

    def draw(self, img, cursor_pt):
        self.hover_action = None
        overlay = img.copy()

        for i, btn in enumerate(self.buttons):
            x1, y1, x2, y2 = self._btn_rect(i)
            action = btn["action"]

            is_active = (
                action.startswith("brush:") and
                action.split(":")[1] == self.brush_engine.current
            )

            hovered = False
            if cursor_pt:
                cx, cy = cursor_pt
                if x1 <= cx <= x2 and y1 <= cy <= y2:
                    hovered = True
                    self.hover_action = action

            bg_color = (0, 200, 100) if is_active else (30, 30, 30)
            if hovered:
                bg_color = (60, 60, 180)

            cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (100, 100, 100), 1)
            cv2.putText(overlay, btn["label"], (x1 + 4, y1 + 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                        (255, 255, 255), 1, cv2.LINE_AA)

        img[:] = cv2.addWeighted(overlay, 0.85, img, 0.15, 0)
        return self.hover_action


# ==============================
# Particle Effects
# ==============================
class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color):
        for _ in range(6):
            angle = np.random.uniform(0, 2 * math.pi)
            speed = np.random.uniform(1, 4)
            life = np.random.randint(8, 18)
            self.particles.append({
                "x": float(x), "y": float(y),
                "vx": speed * math.cos(angle),
                "vy": speed * math.sin(angle),
                "life": life, "max_life": life,
                "color": color
            })

    def update_and_draw(self, img):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15
            p["life"] -= 1
            if p["life"] > 0:
                alpha = p["life"] / p["max_life"]
                r = max(1, int(3 * alpha))
                px, py = int(p["x"]), int(p["y"])
                if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                    c = tuple(int(v * alpha) for v in p["color"])
                    cv2.circle(img, (px, py), r, c, -1)
                alive.append(p)
        self.particles = alive


# ==============================
# Undo / Redo Stack
# ==============================
class UndoStack:
    def __init__(self):
        self.undo_stack = collections.deque(maxlen=Config.MAX_UNDO)
        self.redo_stack = collections.deque(maxlen=Config.MAX_UNDO)

    def push(self, canvas):
        self.undo_stack.append(canvas.copy())
        self.redo_stack.clear()

    def undo(self, canvas):
        if self.undo_stack:
            self.redo_stack.append(canvas.copy())
            return self.undo_stack.pop()
        return canvas

    def redo(self, canvas):
        if self.redo_stack:
            self.undo_stack.append(canvas.copy())
            return self.redo_stack.pop()
        return canvas


# ==============================
# Main Application
# ==============================
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, Config.WIDTH)
    cap.set(4, Config.HEIGHT)

    hand_sys   = HandSystem()
    palette    = ArcPalette()
    brush_eng  = BrushEngine()
    toolbar    = Toolbar(brush_eng)
    particles  = ParticleSystem()
    undo_stack = UndoStack()
    sound      = SoundEngine()

    canvas = np.zeros((Config.HEIGHT, Config.WIDTH, 3), dtype=np.uint8)

    smooth_x, smooth_y = 0, 0
    current_color = (255, 255, 0)
    prev_draw_pt = None

    pinch_frames = 0
    PINCH_DEBOUNCE = 3

    print("=" * 40)
    print("  AIR CANVAS V2 - ACTIVATED")
    print("  Pinch fingers  = Draw / Select")
    print("  Left toolbar   = Brush / Undo / Save")
    print("  Top arc        = Color picker")
    print("  Q = Quit  |  S = Save screenshot")
    print("  Z = Undo  |  Y = Redo")
    print("=" * 40)

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        points = hand_sys.process(img)

        is_drawing = False
        velocity   = 0

        if points:
            idx_tip = points[8]
            thm_tip = points[4]

            cx, cy = idx_tip
            if smooth_x == 0:
                smooth_x, smooth_y = cx, cy

            smooth_x = int(smooth_x * (1 - Config.SMOOTHING) + cx * Config.SMOOTHING)
            smooth_y = int(smooth_y * (1 - Config.SMOOTHING) + cy * Config.SMOOTHING)
            cursor = (smooth_x, smooth_y)

            dist = math.hypot(idx_tip[0] - thm_tip[0],
                              idx_tip[1] - thm_tip[1])

            pinching = dist < Config.PINCH_THRESHOLD
            pinch_frames = pinch_frames + 1 if pinching else 0
            confirmed_pinch = pinch_frames >= PINCH_DEBOUNCE

            img = hand_sys.draw_hud(img, points, dist)
            hovered_action = toolbar.draw(img, cursor)
            hover_idx = palette.draw(img, cursor)

            if confirmed_pinch and hovered_action:
                action = hovered_action
                if action.startswith("brush:"):
                    b = action.split(":")[1]
                    brush_eng.brush_index = BrushEngine.BRUSHES.index(b)
                    prev_draw_pt = None
                elif action == "undo":
                    canvas = undo_stack.undo(canvas)
                    prev_draw_pt = None
                elif action == "redo":
                    canvas = undo_stack.redo(canvas)
                    prev_draw_pt = None
                elif action == "clear":
                    undo_stack.push(canvas)
                    canvas[:] = 0
                    prev_draw_pt = None
                elif action == "save":
                    filename = f"aircanvas_save_{int(time.time())}.png"
                    cv2.imwrite(filename, canvas)
                    print(f"[SAVED] {filename}")

            elif confirmed_pinch and hover_idx != -1:
                color, name = palette.colors[hover_idx]
                palette.selected_index = hover_idx
                current_color = color
                prev_draw_pt = None

            elif pinching and smooth_y > 200 and not hovered_action:
                is_drawing = True

                if prev_draw_pt is None:
                    undo_stack.push(canvas)
                    prev_draw_pt = (smooth_x, smooth_y)

                velocity = math.hypot(smooth_x - prev_draw_pt[0],
                                      smooth_y - prev_draw_pt[1])

                draw_color = (0, 0, 0) if brush_eng.current == "eraser" else current_color
                brush_eng.draw(canvas, prev_draw_pt, (smooth_x, smooth_y),
                               draw_color, Config.BRUSH_SIZE)

                particles.emit(smooth_x, smooth_y, current_color)
                prev_draw_pt = (smooth_x, smooth_y)

            else:
                prev_draw_pt = None

            smooth_x, smooth_y = cx, cy

        else:
            palette.draw(img, None)
            toolbar.draw(img, None)
            prev_draw_pt = None
            pinch_frames = 0

        sound.set_drawing(is_drawing, velocity)

        # Neon glow
        canvas_small = cv2.resize(canvas, (0, 0), fx=0.2, fy=0.2)
        blur = cv2.GaussianBlur(canvas_small, (15, 15), 0)
        blur_up = cv2.resize(blur, (Config.WIDTH, Config.HEIGHT))
        final_canvas = cv2.addWeighted(canvas, 1.0, blur_up, 1.5, 0)

        particles.update_and_draw(img)

        gray = cv2.cvtColor(final_canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        img_bg = cv2.bitwise_and(img, img, mask=mask_inv)
        img = cv2.add(img_bg, final_canvas)

        # Status bar
        brush_name = brush_eng.current.upper()
        color_name  = palette.colors[palette.selected_index][1]
        undo_count  = len(undo_stack.undo_stack)
        status = f"Brush: {brush_name}  |  Color: {color_name}  |  Undo: {undo_count}  |  [Q] Quit  [S] Save  [Z] Undo  [Y] Redo"
        cv2.rectangle(img, (0, Config.HEIGHT - 34), (Config.WIDTH, Config.HEIGHT), (20, 20, 20), -1)
        cv2.putText(img, status, (10, Config.HEIGHT - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("Air Canvas V2", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"aircanvas_save_{int(time.time())}.png"
            cv2.imwrite(filename, canvas)
            print(f"[SAVED] {filename}")
        elif key == ord('z'):
            canvas = undo_stack.undo(canvas)
        elif key == ord('y'):
            canvas = undo_stack.redo(canvas)

    sound.stop_event.set()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
