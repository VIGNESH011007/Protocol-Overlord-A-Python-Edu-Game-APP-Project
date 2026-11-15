import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import math
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

DB_FILE = "stark_ninjago_save.db"


class NinjagoStarkQuest:
    # Vibrant Cyber-Ninjago x Stark HUD Color Palette
    BG_DEEP = "#060B19"
    BG_PANEL = "#0C162C"
    BG_CARD = "#132240"
    BG_HOVER = "#1B315C"
    CYAN = "#00F0FF"
    GOLD = "#FACC15"
    RED_STARK = "#EF4444"
    ORANGE_KAI = "#F97316"
    BLUE_JAY = "#3B82F6"
    GREEN_LLOYD = "#10B981"
    PURPLE_VIRUS = "#A855F7"
    TEXT_WHITE = "#F8FAFC"
    TEXT_MUTED = "#94A3B8"
    BORDER = "#1E3A6E"

    FONT_HERO = ("Consolas", 16, "bold")
    FONT_TITLE = ("Consolas", 12, "bold")
    FONT_BODY = ("Consolas", 10)
    FONT_SMALL = ("Consolas", 9)

    def __init__(self, root):
        self.root = root
        self.root.title("STARK x NINJAGO // PROTOCOL OVERLORD")
        self.root.geometry("1220x750")
        self.root.minsize(1060, 680)
        self.root.configure(bg=self.BG_DEEP)

        self.type_job = None
        self.boss_timer_job = None
        self.sound_enabled = True

        self.init_db()
        self.build_shell()

        unlocked, intro_seen = self.get_progress()
        if not intro_seen:
            self.start_story_intro(0)
        else:
            self.show_level_map()

    # ---------------- SOUND ENGINE ----------------
    def play_sfx(self, kind):
        if not self.sound_enabled:
            return
        if HAS_WINSOUND:
            try:
                if kind == "hit":
                    winsound.Beep(780, 75)
                    winsound.Beep(1040, 95)
                elif kind == "wrong":
                    winsound.Beep(240, 180)
                elif kind == "hint":
                    winsound.Beep(620, 60)
                    winsound.Beep(880, 70)
                elif kind == "win":
                    for freq in (523, 659, 784, 1046):
                        winsound.Beep(freq, 85)
                elif kind == "click":
                    winsound.Beep(520, 35)
                return
            except Exception:
                pass
        try:
            self.root.bell()
        except Exception:
            pass

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.sound_btn.config(
            text="🔊 SFX: ON" if self.sound_enabled else "🔇 SFX: OFF",
            fg=self.GREEN_LLOYD if self.sound_enabled else self.TEXT_MUTED,
        )

    # ---------------- DATABASE ----------------
    def connect(self):
        return sqlite3.connect(DB_FILE)

    def init_db(self):
        with self.connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS campaign (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    unlocked_level INTEGER DEFAULT 1,
                    intro_seen INTEGER DEFAULT 0,
                    nindroids_defeated INTEGER DEFAULT 0
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS level_stars (
                    level_num INTEGER PRIMARY KEY,
                    best_score INTEGER DEFAULT 0
                )
            """)
            con.execute("INSERT OR IGNORE INTO campaign (id, unlocked_level, intro_seen, nindroids_defeated) VALUES (1, 1, 0, 0)")

    def get_progress(self):
        with self.connect() as con:
            row = con.execute("SELECT unlocked_level, intro_seen FROM campaign WHERE id=1").fetchone()
            return row[0], row[1]

    def get_stats(self):
        with self.connect() as con:
            row = con.execute("SELECT unlocked_level, nindroids_defeated FROM campaign WHERE id=1").fetchone()
            stars = dict(con.execute("SELECT level_num, best_score FROM level_stars").fetchall())
            return row[0], row[1], stars

    def mark_intro_seen(self):
        with self.connect() as con:
            con.execute("UPDATE campaign SET intro_seen=1 WHERE id=1")

    def record_level_victory(self, level_num, score, defeated_add):
        with self.connect() as con:
            cur_unlocked = con.execute("SELECT unlocked_level FROM campaign WHERE id=1").fetchone()[0]
            new_unlocked = max(cur_unlocked, min(15, level_num + 1))
            con.execute(
                "UPDATE campaign SET unlocked_level=?, nindroids_defeated=nindroids_defeated+? WHERE id=1",
                (new_unlocked, defeated_add),
            )
            old_best = con.execute("SELECT best_score FROM level_stars WHERE level_num=?", (level_num,)).fetchone()
            if not old_best or score > old_best[0]:
                con.execute("INSERT OR REPLACE INTO level_stars (level_num, best_score) VALUES (?, ?)", (level_num, score))
        self.refresh_top_bar()

    # ---------------- VECTOR AVATAR ARTIST (CANVAS PORTRAITS) ----------------
    def draw_avatar(self, canvas, character, cx, cy, scale=1.0, mood="normal"):
        """Draws detailed stylized character helmets/faces directly on a Tkinter Canvas."""
        s = scale
        if character == "ironman":
            # Red & Gold Mark-XLIII Helmet
            canvas.create_oval(cx - 46*s, cy - 54*s, cx + 46*s, cy + 54*s, fill="#B91C1C", outline=self.GOLD, width=2)
            # Gold faceplate
            pts = [
                cx - 32*s, cy - 32*s, cx - 12*s, cy - 22*s, cx + 12*s, cy - 22*s, cx + 32*s, cy - 32*s,
                cx + 34*s, cy + 16*s, cx + 18*s, cy + 44*s, cx - 18*s, cy + 44*s, cx - 34*s, cy + 16*s
            ]
            canvas.create_polygon(pts, fill=self.GOLD, outline="#92400E", width=2)
            # Glowing eyes (glitch red if damaged)
            eye_col = self.RED_STARK if mood == "glitch" else "#E0F2FE"
            canvas.create_polygon(cx - 26*s, cy - 8*s, cx - 8*s, cy - 3*s, cx - 10*s, cy + 4*s, cx - 25*s, cy, fill=eye_col, outline=self.CYAN)
            canvas.create_polygon(cx + 26*s, cy - 8*s, cx + 8*s, cy - 3*s, cx + 10*s, cy + 4*s, cx + 25*s, cy, fill=eye_col, outline=self.CYAN)
            # Mouth slit
            canvas.create_line(cx - 16*s, cy + 26*s, cx + 16*s, cy + 26*s, fill="#7F1D1D", width=3)

        elif character == "zane":
            # Titanium Ninja Hood + Glowing Ice Eyes
            canvas.create_oval(cx - 46*s, cy - 52*s, cx + 46*s, cy + 52*s, fill="#E2E8F0", outline=self.CYAN, width=2)
            # Metallic brow plate
            canvas.create_polygon(cx - 38*s, cy - 22*s, cx + 38*s, cy - 22*s, cx + 32*s, cy - 38*s, cx - 32*s, cy - 38*s, fill="#94A3B8", outline="#475569")
            # Visor slit
            canvas.create_rectangle(cx - 34*s, cy - 14*s, cx + 34*s, cy + 6*s, fill="#0F172A", outline=self.CYAN)
            # Ice-blue ninja eyes
            canvas.create_polygon(cx - 26*s, cy - 8*s, cx - 9*s, cy - 3*s, cx - 24*s, cy + 1*s, fill=self.CYAN)
            canvas.create_polygon(cx + 26*s, cy - 8*s, cx + 9*s, cy - 3*s, cx + 24*s, cy + 1*s, fill=self.CYAN)
            # Lower ninja mask wrap
            canvas.create_polygon(cx - 38*s, cy + 8*s, cx + 38*s, cy + 8*s, cx + 26*s, cy + 46*s, cx - 26*s, cy + 46*s, fill="#CBD5E1", outline="#64748B")
            canvas.create_line(cx - 28*s, cy + 22*s, cx + 28*s, cy + 14*s, fill="#94A3B8", width=2)

        elif character in ("kai", "jay", "lloyd"):
            hood_colors = {
                "kai": ("#DC2626", "#991B1B", self.GOLD),
                "jay": ("#2563EB", "#1E40AF", self.CYAN),
                "lloyd": ("#16A34A", "#166534", self.GOLD),
            }
            main_c, dark_c, eye_c = hood_colors[character]
            canvas.create_oval(cx - 46*s, cy - 52*s, cx + 46*s, cy + 52*s, fill=main_c, outline=eye_c, width=2)
            # Forehead emblem band
            canvas.create_rectangle(cx - 36*s, cy - 30*s, cx + 36*s, cy - 20*s, fill=dark_c, outline=eye_c)
            # Eye opening
            canvas.create_rectangle(cx - 33*s, cy - 14*s, cx + 33*s, cy + 5*s, fill="#FDE68A", outline="#1E293B")
            # Determined ninja eyebrows & eyes
            canvas.create_oval(cx - 22*s, cy - 8*s, cx - 10*s, cy + 2*s, fill="#0F172A")
            canvas.create_oval(cx + 10*s, cy - 8*s, cx + 22*s, cy + 2*s, fill="#0F172A")
            canvas.create_line(cx - 26*s, cy - 11*s, cx - 8*s, cy - 5*s, fill="#0F172A", width=3)
            canvas.create_line(cx + 26*s, cy - 11*s, cx + 8*s, cy - 5*s, fill="#0F172A", width=3)
            # Lower mask
            canvas.create_polygon(cx - 38*s, cy + 6*s, cx + 38*s, cy + 6*s, cx + 26*s, cy + 46*s, cx - 26*s, cy + 46*s, fill=dark_c)

        elif character == "jarvis":
            # Holographic AI Matrix Sphere
            for r, col, w in [(48*s, "#0284C7", 2), (38*s, self.CYAN, 2), (26*s, self.GOLD, 2)]:
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=col, width=w, dash=(5, 3))
            canvas.create_oval(cx - 16*s, cy - 16*s, cx + 16*s, cy + 16*s, fill="#082F49", outline=self.CYAN, width=2)
            canvas.create_text(cx, cy, text="AI", fill=self.CYAN, font=("Consolas", int(12*s), "bold"))

        elif character == "nindroid":
            # Evil Cyber-Nindroid Warrior
            canvas.create_polygon(cx - 38*s, cy - 48*s, cx + 38*s, cy - 48*s, cx + 44*s, cy + 12*s, cx + 24*s, cy + 48*s, cx - 24*s, cy + 48*s, cx - 44*s, cy + 12*s, fill="#1E293B", outline=self.RED_STARK, width=2)
            # Half-exposed red cybernetic plate
            canvas.create_polygon(cx, cy - 46*s, cx + 36*s, cy - 46*s, cx + 40*s, cy + 10*s, cx + 20*s, cy + 44*s, cx, cy + 44*s, fill="#475569", outline="#94A3B8")
            # Glowing crimson scanner eye
            canvas.create_oval(cx + 8*s, cy - 14*s, cx + 26*s, cy + 4*s, fill=self.RED_STARK, outline="#FCA5A5", width=2)
            canvas.create_line(cx - 26*s, cy - 6*s, cx - 8*s, cy - 2*s, fill=self.RED_STARK, width=4)
            # Mechanical teeth grille
            for gx in range(-18, 20, 8):
                canvas.create_line(cx + gx*s, cy + 20*s, cx + gx*s, cy + 34*s, fill="#94A3B8", width=2)

        elif character == "overlord":
            # The Digital Overlord (Horned Purple/Crimson Virus Sovereign)
            canvas.create_polygon(cx - 46*s, cy - 15*s, cx - 56*s, cy - 58*s, cx - 22*s, cy - 36*s, fill="#3B0764", outline=self.PURPLE_VIRUS, width=2)
            canvas.create_polygon(cx + 46*s, cy - 15*s, cx + 56*s, cy - 58*s, cx + 22*s, cy - 36*s, fill="#3B0764", outline=self.PURPLE_VIRUS, width=2)
            canvas.create_polygon(cx - 42*s, cy - 36*s, cx + 42*s, cy - 36*s, cx + 34*s, cy + 42*s, cx, cy + 54*s, cx - 34*s, cy + 42*s, fill="#1E1B4B", outline=self.PURPLE_VIRUS, width=3)
            # Menacing glowing virus eyes
            canvas.create_polygon(cx - 28*s, cy - 12*s, cx - 8*s, cy - 2*s, cx - 24*s, cy + 6*s, fill=self.PURPLE_VIRUS, outline="#F0ABFC")
            canvas.create_polygon(cx + 28*s, cy - 12*s, cx + 8*s, cy - 2*s, cx + 24*s, cy + 6*s, fill=self.PURPLE_VIRUS, outline="#F0ABFC")
            # Digital crown core
            canvas.create_polygon(cx, cy - 32*s, cx - 10*s, cy - 18*s, cx + 10*s, cy - 18*s, fill=self.RED_STARK)

    # ---------------- STORY INTRO SCENES ----------------
    STORY_SCENES = [
        {
            "tag": "ACT I // SKYLINE OVER NEW YORK",
            "title": "A Digital Anomaly Strikes Stark",
            "left_char": "ironman",
            "left_name": "TONY STARK (MARK-XLIII)",
            "left_mood": "glitch",
            "right_char": "jarvis",
            "right_name": "J.A.R.V.I.S. (CORRUPTED)",
            "right_mood": "glitch",
            "text": (
                "High above the clouds, Iron Man is mid-battle against rogue drones when his HUD suddenly "
                "fractures with violet static. Thrusters misfire and targeting locks scramble!\n\n"
                "Drawing on pure instinct, Tony barely wins the fight and crash-lands in his lab. "
                "Scanning his armor, he discovers a foreign cyber-virus attacked J.A.R.V.I.S. "
                "After executing an emergency reboot, Tony traces the dark signal across dimensions—and launches straight toward its source..."
            ),
        },
        {
            "tag": "ACT II // NEW NINJAGO CITY UNDER SIEGE",
            "title": "Return of the Digital Overlord",
            "left_char": "lloyd",
            "left_name": "NINJA DEFENDERS (LLOYD & TEAM)",
            "left_mood": "normal",
            "right_char": "nindroid",
            "right_name": "OVERLORD'S NINDROID LEGION",
            "right_mood": "normal",
            "text": (
                "For years, the Ninjas fought tirelessly to protect New Ninjago City and keep its light alive. "
                "But tonight, the skies turn dark purple—the Overlord has returned in pure digital form!\n\n"
                "Commanding from the shadows without stepping onto the battlefield, the Digital Overlord unleashes "
                "an endless army of armored Nindroids. Outnumbered and exhausted, Kai, Jay, Cole, Lloyd, Nya, and Zane "
                "are pushed to the brink of defeat..."
            ),
        },
        {
            "tag": "ACT III // REINFORCEMENTS FROM THE SKY",
            "title": "Repulsors Meet Spinjitzu",
            "left_char": "ironman",
            "left_name": "IRON MAN",
            "left_mood": "normal",
            "right_char": "kai",
            "right_name": "KAI & THE NINJAS",
            "right_mood": "normal",
            "text": (
                "Just as the Nindroids close in, a sonic boom shatters the clouds—Iron Man streaks into Ninjago City, "
                "blasting the frontline drones with twin repulsor beams!\n\n"
                "Fighting side by side, Iron Man and the Ninjas shatter the first Nindroid wave. "
                "The surviving Nindroids retreat into the digital shadows, warning: 'THE OVERLORD WILL RETURN!'"
            ),
        },
        {
            "tag": "ACT IV // THE ALLIANCE OF CODE & LIGHT",
            "title": "Zane & J.A.R.V.I.S. Take Command",
            "left_char": "zane",
            "left_name": "ZANE (TITANIUM NINJA)",
            "left_mood": "normal",
            "right_char": "jarvis",
            "right_name": "J.A.R.V.I.S. PROTOCOL",
            "right_mood": "normal",
            "text": (
                "After the battle, the Ninjas and Tony Stark form a pact. Because the Overlord is a living cyber-virus, "
                "swords alone won't destroy him—every Ninja must master programming to dismantle his code from within!\n\n"
                "Tony leaves J.A.R.V.I.S. with Zane to train the Ninja team across 14 tactical coding levels before heading off "
                "to handle urgent unfinished business. Your mission: Master each lesson, defeat the returning Nindroids, "
                "and breach the Overlord's 20-layer Firewall in Level 15!"
            ),
        },
    ]

    # ---------------- UI SHELL ----------------
    def build_shell(self):
        top = tk.Frame(self.root, bg=self.BG_PANEL, height=60,
                       highlightbackground=self.BORDER, highlightthickness=1)
        top.pack(fill="x", padx=14, pady=(12, 8))
        top.pack_propagate(False)

        tk.Label(
            top, text="⚡ STARK x NINJAGO // PROTOCOL OVERLORD",
            bg=self.BG_PANEL, fg=self.CYAN, font=self.FONT_HERO
        ).pack(side="left", padx=18)

        self.sound_btn = tk.Button(
            top, text="🔊 SFX: ON", command=self.toggle_sound,
            bg=self.BG_CARD, fg=self.GREEN_LLOYD, relief="flat", bd=0,
            font=self.FONT_SMALL, padx=10, pady=5, cursor="hand2"
        )
        self.sound_btn.pack(side="right", padx=14)

        self.replay_story_btn = tk.Button(
            top, text="📖 REPLAY STORY", command=lambda: self.start_story_intro(0),
            bg=self.BG_CARD, fg=self.GOLD, relief="flat", bd=0,
            font=self.FONT_SMALL, padx=10, pady=5, cursor="hand2"
        )
        self.replay_story_btn.pack(side="right", padx=6)

        self.map_btn = tk.Button(
            top, text="🗺 15-LEVEL MAP", command=self.show_level_map,
            bg=self.BG_CARD, fg=self.CYAN, relief="flat", bd=0,
            font=self.FONT_SMALL, padx=10, pady=5, cursor="hand2"
        )
        self.map_btn.pack(side="right", padx=6)

        self.top_stats_lbl = tk.Label(
            top, text="", bg=self.BG_PANEL, fg=self.TEXT_WHITE, font=self.FONT_BODY
        )
        self.top_stats_lbl.pack(side="right", padx=16)

        self.main_area = tk.Frame(self.root, bg=self.BG_DEEP)
        self.main_area.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.refresh_top_bar()

    def clear_main(self):
        if self.type_job:
            try:
                self.root.after_cancel(self.type_job)
            except Exception:
                pass
            self.type_job = None
        if self.boss_timer_job:
            try:
                self.root.after_cancel(self.boss_timer_job)
            except Exception:
                pass
            self.boss_timer_job = None
        for w in self.main_area.winfo_children():
            w.destroy()

    def refresh_top_bar(self):
        unlocked, defeated, _ = self.get_stats()
        self.top_stats_lbl.config(
            text=f"UNLOCKED: LEVEL {unlocked}/15   |   NINDROIDS DEFEATED: {defeated}"
        )

    def make_btn(self, parent, text, cmd, accent=None, width=None):
        fg = accent or self.CYAN
        btn = tk.Button(
            parent, text=text, command=lambda: (self.play_sfx("click"), cmd()),
            bg="#0E1E38", fg=fg, activebackground=self.BG_HOVER,
            activeforeground=self.TEXT_WHITE, relief="flat", bd=0,
            font=self.FONT_TITLE, padx=16, pady=9, cursor="hand2",
            highlightbackground=fg, highlightthickness=1
        )
        if width:
            btn.config(width=width)
        btn.bind("<Enter>", lambda e: btn.config(bg=self.BG_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg="#0E1E38"))
        return btn

    # ---------------- PACED STORY VIEWER ----------------
    def start_story_intro(self, scene_idx):
        self.clear_main()
        scene = self.STORY_SCENES[scene_idx]
        self._full_scene_text = scene["text"]
        self._typing_done = False

        card = tk.Frame(self.main_area, bg=self.BG_PANEL,
                        highlightbackground=self.CYAN, highlightthickness=2)
        card.pack(fill="both", expand=True, padx=36, pady=14)

        # Header
        hdr = tk.Frame(card, bg="#081224")
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  {scene['tag']}  (SCENE {scene_idx + 1} OF {len(self.STORY_SCENES)})",
                 bg="#081224", fg=self.GOLD, font=self.FONT_TITLE, pady=10).pack(side="left", padx=12)
        tk.Button(
            hdr, text="SKIP INTRO ⏭", command=self.finish_intro,
            bg=self.BG_CARD, fg=self.TEXT_MUTED, relief="flat", font=self.FONT_SMALL,
            padx=10, pady=4, cursor="hand2"
        ).pack(side="right", padx=14)

        tk.Label(card, text=scene["title"], bg=self.BG_PANEL, fg=self.CYAN,
                 font=("Consolas", 18, "bold")).pack(pady=(16, 8))

        # Dual Character Portrait Stage
        stage = tk.Canvas(card, bg="#070E1F", height=165, width=760,
                          highlightbackground=self.BORDER, highlightthickness=1)
        stage.pack(pady=6)

        self.draw_avatar(stage, scene["left_char"], 190, 74, scale=0.95, mood=scene["left_mood"])
        stage.create_text(190, 146, text=scene["left_name"], fill=self.CYAN, font=self.FONT_SMALL)

        stage.create_text(380, 78, text="⚡ VS / LINK ⚡", fill=self.GOLD, font=self.FONT_TITLE)

        self.draw_avatar(stage, scene["right_char"], 570, 74, scale=0.95, mood=scene["right_mood"])
        stage.create_text(570, 146, text=scene["right_name"], fill=self.GOLD, font=self.FONT_SMALL)

        # Typewriter Narrative Box
        self.story_lbl = tk.Label(
            card, text="", bg=self.BG_CARD, fg=self.TEXT_WHITE,
            font=("Consolas", 11), wraplength=920, justify="left", anchor="nw",
            padx=24, pady=20, highlightbackground=self.BORDER, highlightthickness=1
        )
        self.story_lbl.pack(fill="both", expand=True, padx=32, pady=12)
        self.story_lbl.bind("<Button-1>", lambda e: self.instant_finish_text())

        # Footer Controls
        footer = tk.Frame(card, bg=self.BG_PANEL)
        footer.pack(fill="x", padx=32, pady=(0, 18))

        tk.Label(footer, text="TIP: Click the text box to reveal full dialogue immediately.",
                 bg=self.BG_PANEL, fg=self.TEXT_MUTED, font=self.FONT_SMALL).pack(side="left")

        if scene_idx < len(self.STORY_SCENES) - 1:
            self.make_btn(
                footer, "NEXT SCENE →",
                lambda: self.start_story_intro(scene_idx + 1),
                accent=self.CYAN
            ).pack(side="right")
        else:
            self.make_btn(
                footer, "ENTER TRAINING & MISSION MAP 🚀",
                self.finish_intro,
                accent=self.GREEN_LLOYD
            ).pack(side="right")

        self.run_typewriter(0)

    def run_typewriter(self, idx):
        if not hasattr(self, "story_lbl") or not self.story_lbl.winfo_exists():
            return
        if idx <= len(self._full_scene_text):
            self.story_lbl.config(text=self._full_scene_text[:idx])
            self.type_job = self.root.after(16, lambda: self.run_typewriter(idx + 1))
        else:
            self._typing_done = True

    def instant_finish_text(self):
        if self.type_job:
            self.root.after_cancel(self.type_job)
            self.type_job = None
        if hasattr(self, "story_lbl") and self.story_lbl.winfo_exists():
            self.story_lbl.config(text=self._full_scene_text)
        self._typing_done = True

    def finish_intro(self):
        self.mark_intro_seen()
        self.show_level_map()

    # ---------------- 15-LEVEL CAMPAIGN MAP ----------------
    def show_level_map(self):
        self.clear_main()
        unlocked, _, stars = self.get_stats()

        hdr = tk.Frame(self.main_area, bg=self.BG_PANEL,
                       highlightbackground=self.BORDER, highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Label(
            hdr,
            text="NINJAGO DEFENSE GRID // SELECT A LEVEL (LEARN LESSON → DEFEAT 7 NINDROIDS)",
            bg=self.BG_PANEL, fg=self.GOLD, font=self.FONT_TITLE
        ).pack(side="left", padx=18, pady=12)

        grid = tk.Frame(self.main_area, bg=self.BG_DEEP)
        grid.pack(fill="both", expand=True)

        ninjas = ["kai", "jay", "lloyd", "zane"]
        for idx, lvl in enumerate(LEVELS):
            lnum = lvl["level"]
            r, c = divmod(idx, 5)
            is_boss = (lnum == 15)
            is_open = (lnum <= unlocked)
            best = stars.get(lnum, 0)

            border_c = self.PURPLE_VIRUS if is_boss else (
                self.GREEN_LLOYD if best >= 5 else (self.CYAN if is_open else self.BORDER)
            )
            bg_c = "#1B1035" if is_boss else (self.BG_PANEL if is_open else "#080F1E")

            card = tk.Frame(grid, bg=bg_c, highlightbackground=border_c,
                            highlightthickness=2 if is_open else 1)
            card.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
            grid.rowconfigure(r, weight=1)
            grid.columnconfigure(c, weight=1)

            top_tag = "👑 BOSS: OVERLORD" if is_boss else f"LEVEL {lnum:02d}"
            tag_col = self.PURPLE_VIRUS if is_boss else (self.GOLD if is_open else self.TEXT_MUTED)
            tk.Label(card, text=top_tag, bg=bg_c, fg=tag_col, font=self.FONT_TITLE).pack(anchor="w", padx=12, pady=(10, 2))

            tk.Label(
                card, text=lvl["topic"], bg=bg_c,
                fg=self.TEXT_WHITE if is_open else "#475569",
                font=("Consolas", 10, "bold"), wraplength=195, justify="left"
            ).pack(anchor="w", padx=12)

            ninja_mentor = ninjas[(lnum - 1) % 4]
            mentor_txt = "ALL NINJAS + J.A.R.V.I.S." if is_boss else f"MENTOR: ZANE & {ninja_mentor.upper()}"
            tk.Label(card, text=mentor_txt, bg=bg_c, fg=self.TEXT_MUTED, font=self.FONT_SMALL).pack(anchor="w", padx=12, pady=(4, 0))

            if best > 0:
                total_q = 20 if is_boss else 7
                tk.Label(card, text=f"BEST: {best}/{total_q} ★", bg=bg_c, fg=self.GREEN_LLOYD, font=self.FONT_SMALL).pack(anchor="w", padx=12, pady=(2, 0))

            btn_area = tk.Frame(card, bg=bg_c)
            btn_area.pack(side="bottom", fill="x", padx=10, pady=10)

            if is_open:
                btn_lbl = "BREACH FIREWALL ⚡" if is_boss else "START LESSON →"
                btn_acc = self.PURPLE_VIRUS if is_boss else self.CYAN
                self.make_btn(btn_area, btn_lbl, lambda d=lvl: self.open_lesson(d), accent=btn_acc).pack(fill="x")
            else:
                tk.Label(btn_area, text="🔒 LOCKED", bg="#0D172A", fg="#475569",
                         font=self.FONT_SMALL, pady=7).pack(fill="x")

    # ---------------- STEP 1: ZANE & J.A.R.V.I.S. LESSON BRIEFING ----------------
    def open_lesson(self, level_data):
        if level_data["level"] == 15:
            self.start_boss_battle(level_data)
            return

        self.clear_main()
        lnum = level_data["level"]
        ninjas = ["kai", "jay", "lloyd", "zane"]
        student_ninja = ninjas[(lnum - 1) % 4]

        card = tk.Frame(self.main_area, bg=self.BG_PANEL,
                        highlightbackground=self.CYAN, highlightthickness=2)
        card.pack(fill="both", expand=True, padx=32, pady=12)

        # Top Bar with Avatars
        top = tk.Frame(card, bg="#081224")
        top.pack(fill="x")

        ava_canvas = tk.Canvas(top, bg="#081224", width=260, height=96, highlightthickness=0)
        ava_canvas.pack(side="left", padx=14, pady=4)
        self.draw_avatar(ava_canvas, "zane", 55, 48, scale=0.72)
        self.draw_avatar(ava_canvas, "jarvis", 130, 48, scale=0.68)
        self.draw_avatar(ava_canvas, student_ninja, 205, 48, scale=0.72)

        title_col = tk.Frame(top, bg="#081224")
        title_col.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(title_col, text=f"LEVEL {lnum:02d} TRAINING MODULE // {level_data['topic'].upper()}",
                 bg="#081224", fg=self.GOLD, font=self.FONT_HERO).pack(anchor="w", pady=(18, 4))
        tk.Label(title_col, text=f"Zane & J.A.R.V.I.S. briefing {student_ninja.upper()} before Nindroid wave arrives...",
                 bg="#081224", fg=self.CYAN, font=self.FONT_BODY).pack(anchor="w")

        # Lesson Content
        lesson_box = tk.Frame(card, bg=self.BG_CARD,
                              highlightbackground=self.BORDER, highlightthickness=1)
        lesson_box.pack(fill="both", expand=True, padx=26, pady=14)

        tk.Label(
            lesson_box, text=level_data["lesson"], bg=self.BG_CARD, fg=self.TEXT_WHITE,
            font=("Consolas", 11), justify="left", anchor="nw", wraplength=1040
        ).pack(fill="both", expand=True, padx=22, pady=18)

        # Action Bar
        footer = tk.Frame(card, bg=self.BG_PANEL)
        footer.pack(fill="x", padx=26, pady=(0, 18))

        self.make_btn(footer, "← BACK TO MAP", self.show_level_map, accent=self.TEXT_MUTED).pack(side="left")
        self.make_btn(
            footer, "⚔ ENGAGE NINDROID SQUAD (7 RANDOM QUESTIONS) →",
            lambda d=level_data: self.start_nindroid_battle(d),
            accent=self.GREEN_LLOYD
        ).pack(side="right")

    # ---------------- STEP 2: REGULAR NINDROID BATTLE (7 RANDOM QUESTIONS) ----------------
    def start_nindroid_battle(self, level_data):
        self.clear_main()
        self.cur_level = level_data
        # Pick 7 random questions from the 12-question pool
        self.battle_questions = random.sample(level_data["questions"], 7)
        self.q_idx = 0
        self.score = 0
        self.ninja_hp = 100
        self.nindroids_left = 7
        self.answered_current = False

        ninjas = ["kai", "jay", "lloyd", "zane"]
        self.active_hero = ninjas[(level_data["level"] - 1) % 4]

        # Battle Visual Arena Canvas
        self.battle_canvas = tk.Canvas(
            self.main_area, bg="#070D1D", height=185,
            highlightbackground=self.CYAN, highlightthickness=2
        )
        self.battle_canvas.pack(fill="x", pady=(0, 10))

        # Quiz Panel
        self.quiz_card = tk.Frame(
            self.main_area, bg=self.BG_PANEL,
            highlightbackground=self.BORDER, highlightthickness=1
        )
        self.quiz_card.pack(fill="both", expand=True)

        self.render_battle_scene("Nindroids ambushed the sector! Answer accurately to strike!")
        self.render_question_card()

    def render_battle_scene(self, status_banner, blast_dir=None):
        c = self.battle_canvas
        c.delete("all")
        w = c.winfo_width() or 1160

        # Cyber grid background
        for x in range(0, w, 50):
            c.create_line(x, 0, x, 185, fill="#0D1933")

        # Hero Avatar (Left)
        self.draw_avatar(c, self.active_hero, 120, 82, scale=0.9)
        c.create_text(120, 152, text=f"NINJA {self.active_hero.upper()}", fill=self.CYAN, font=self.FONT_TITLE)

        # J.A.R.V.I.S. Support Core
        self.draw_avatar(c, "jarvis", 245, 78, scale=0.62)
        c.create_text(245, 134, text="J.A.R.V.I.S.", fill=self.GOLD, font=self.FONT_SMALL)

        # Hero Shield Bar
        c.create_rectangle(60, 164, 180, 174, fill="#1E293B", outline=self.CYAN)
        hp_w = max(0, int(120 * (self.ninja_hp / 100.0)))
        hp_col = self.GREEN_LLOYD if self.ninja_hp > 40 else self.RED_STARK
        c.create_rectangle(60, 164, 60 + hp_w, 174, fill=hp_col, outline="")

        # Center Status Banner
        c.create_text(w // 2, 34, text=f"LEVEL {self.cur_level['level']:02d}: {self.cur_level['topic'].upper()}",
                      fill=self.GOLD, font=self.FONT_TITLE)
        c.create_text(w // 2, 68, text=status_banner, fill=self.TEXT_WHITE, font=self.FONT_BODY)
        c.create_text(w // 2, 102, text=f"NINDROIDS REMAINING: {self.nindroids_left}   |   HITS SCORED: {self.score}/7",
                      fill=self.CYAN, font=self.FONT_TITLE)

        # Blast Beam Effect
        if blast_dir == "hero":
            c.create_line(175, 82, w - 185, 82, fill=self.CYAN, width=6)
            c.create_line(175, 82, w - 185, 82, fill="#FFFFFF", width=2)
        elif blast_dir == "enemy":
            c.create_line(w - 185, 82, 175, 82, fill=self.RED_STARK, width=6)

        # Nindroid Avatar (Right)
        if self.nindroids_left > 0:
            self.draw_avatar(c, "nindroid", w - 130, 82, scale=0.9)
            c.create_text(w - 130, 152, text=f"NINDROID UNIT #{8 - self.nindroids_left}", fill=self.RED_STARK, font=self.FONT_TITLE)
        else:
            c.create_text(w - 140, 88, text="SQUAD DEFEATED!", fill=self.GREEN_LLOYD, font=self.FONT_HERO)

    def render_question_card(self):
        for w in self.quiz_card.winfo_children():
            w.destroy()

        if self.q_idx >= 7:
            self.finish_regular_battle()
            return

        self.answered_current = False
        q_text, raw_options, correct_idx, hint_txt = self.battle_questions[self.q_idx]

        # Shuffle options every time so answer position cannot be memorized
        indexed = list(enumerate(raw_options))
        random.shuffle(indexed)
        shuffled_opts = [opt for _, opt in indexed]
        new_correct_idx = [i for i, (orig_i, _) in enumerate(indexed) if orig_i == correct_idx][0]

        hdr = tk.Frame(self.quiz_card, bg=self.BG_PANEL)
        hdr.pack(fill="x", padx=26, pady=(16, 6))
        tk.Label(hdr, text=f"COMBAT CHALLENGE {self.q_idx + 1} OF 7",
                 bg=self.BG_PANEL, fg=self.CYAN, font=self.FONT_TITLE).pack(side="left")

        self.hint_lbl = tk.Label(hdr, text="", bg=self.BG_PANEL, fg=self.GOLD, font=self.FONT_SMALL)
        self.hint_lbl.pack(side="right", padx=10)
        self.make_btn(
            hdr, "💡 J.A.R.V.I.S. HINT",
            lambda h=hint_txt: (self.play_sfx("hint"), self.hint_lbl.config(text=f"J.A.R.V.I.S.: {h}")),
            accent=self.GOLD
        ).pack(side="right")

        tk.Label(
            self.quiz_card, text=q_text, bg=self.BG_CARD, fg=self.TEXT_WHITE,
            font=("Consolas", 11, "bold"), wraplength=1060, justify="left",
            padx=20, pady=16, highlightbackground=self.BORDER, highlightthickness=1
        ).pack(fill="x", padx=26, pady=8)

        self.feedback_lbl = tk.Label(self.quiz_card, text="", bg=self.BG_PANEL, font=self.FONT_TITLE)
        self.feedback_lbl.pack(pady=4)

        opts_frame = tk.Frame(self.quiz_card, bg=self.BG_PANEL)
        opts_frame.pack(fill="x", padx=26, pady=4)

        self.opt_buttons = []
        for i, opt in enumerate(shuffled_opts):
            btn = tk.Button(
                opts_frame, text=f"  [{chr(65 + i)}]   {opt}",
                command=lambda chosen=i, corr=new_correct_idx, s_opts=shuffled_opts: self.handle_regular_answer(chosen, corr, s_opts),
                bg=self.BG_CARD, fg=self.TEXT_WHITE, activebackground=self.BG_HOVER,
                activeforeground=self.CYAN, relief="flat", bd=0,
                font=("Consolas", 11), anchor="w", padx=18, pady=11,
                cursor="hand2", highlightbackground=self.BORDER, highlightthickness=1
            )
            btn.pack(fill="x", pady=4)
            self.opt_buttons.append(btn)

        footer = tk.Frame(self.quiz_card, bg=self.BG_PANEL)
        footer.pack(fill="x", padx=26, pady=(6, 14))
        self.make_btn(footer, "← RETREAT TO LESSON", lambda: self.open_lesson(self.cur_level), accent=self.TEXT_MUTED).pack(side="left")

        self.next_q_btn = self.make_btn(footer, "NEXT TARGET →", self.advance_regular_q, accent=self.CYAN)

    def handle_regular_answer(self, chosen, correct, shuffled_opts):
        if self.answered_current:
            return
        self.answered_current = True

        for idx, btn in enumerate(self.opt_buttons):
            if idx == correct:
                btn.config(bg="#064E3B", fg=self.GREEN_LLOYD, highlightbackground=self.GREEN_LLOYD)
            elif idx == chosen:
                btn.config(bg="#4C0519", fg=self.RED_STARK, highlightbackground=self.RED_STARK)

        if chosen == correct:
            self.play_sfx("hit")
            self.score += 1
            self.nindroids_left -= 1
            self.feedback_lbl.config(text="⚡ DIRECT HIT! Nindroid Unit neutralized!", fg=self.GREEN_LLOYD)
            self.render_battle_scene("ELEMENTAL STRIKE LANDED! NINDROID DESTROYED!", blast_dir="hero")
        else:
            self.play_sfx("wrong")
            self.ninja_hp = max(10, self.ninja_hp - 15)
            self.feedback_lbl.config(
                text=f"✖ SHIELD HIT! Correct code: {shuffled_opts[correct]}",
                fg=self.RED_STARK
            )
            self.render_battle_scene("NINDROID COUNTER-ATTACK! REVIEW THE SYNTAX!", blast_dir="enemy")

        self.next_q_btn.pack(side="right")

    def advance_regular_q(self):
        self.q_idx += 1
        self.render_question_card()

    def finish_regular_battle(self):
        lnum = self.cur_level["level"]
        if self.score >= 5:
            self.play_sfx("win")
            self.record_level_victory(lnum, self.score, self.score)
            messagebox.showinfo(
                "SECTOR CLEARED!",
                f"Victory! You scored {self.score}/7 and defeated {self.score} Nindroids!\n\n"
                f"ZANE: 'Excellent work! Level {lnum + 1} is now unlocked on the Defense Grid.'"
            )
            self.show_level_map()
        else:
            self.play_sfx("wrong")
            messagebox.showwarning(
                "TACTICAL RETREAT",
                f"You scored {self.score}/7 (Minimum 5/7 required to clear the Nindroid squad).\n\n"
                "J.A.R.V.I.S.: 'Let us review Zane's briefing and re-engage with a fresh randomized Nindroid wave!'"
            )
            self.open_lesson(self.cur_level)

    # ---------------- STEP 3: LEVEL 15 GRAND BOSS FIGHT (20 QUESTIONS + FIREWALL) ----------------
    def start_boss_battle(self, boss_data):
        self.clear_main()
        # Gather 20 random questions across all 14 levels
        all_pool = []
        for lvl in LEVELS[:-1]:
            all_pool.extend(lvl["questions"])
        self.boss_questions = random.sample(all_pool, 20)
        self.boss_idx = 0
        self.boss_score = 0
        self.firewall_hp = 100
        self.boss_time_left = 240  # 4 minutes for 20 questions
        self.boss_answered = False

        # Boss Arena Canvas
        self.boss_canvas = tk.Canvas(
            self.main_area, bg="#090514", height=190,
            highlightbackground=self.PURPLE_VIRUS, highlightthickness=2
        )
        self.boss_canvas.pack(fill="x", pady=(0, 10))

        self.boss_card = tk.Frame(
            self.main_area, bg=self.BG_PANEL,
            highlightbackground=self.PURPLE_VIRUS, highlightthickness=1
        )
        self.boss_card.pack(fill="both", expand=True)

        self.render_boss_arena("FINAL SHOWDOWN: Break the Digital Overlord's 20 Firewall Nodes!")
        self.render_boss_question()
        self.tick_boss_timer()

    def tick_boss_timer(self):
        if not hasattr(self, "boss_timer_lbl") or not self.boss_timer_lbl.winfo_exists():
            return
        mins, secs = divmod(self.boss_time_left, 60)
        self.boss_timer_lbl.config(text=f"⏱ FIREWALL LOCKOUT: {mins:02d}:{secs:02d}")
        if self.boss_time_left <= 0:
            self.finish_boss_battle(timed_out=True)
            return
        self.boss_time_left -= 1
        self.boss_timer_job = self.root.after(1000, self.tick_boss_timer)

    def render_boss_arena(self, status_msg, pulse=None):
        c = self.boss_canvas
        c.delete("all")
        w = c.winfo_width() or 1160

        for x in range(0, w, 45):
            c.create_line(x, 0, x, 190, fill="#160B2E")

        # Team Avatars on Left (Zane + J.A.R.V.I.S. + Lloyd)
        self.draw_avatar(c, "zane", 95, 84, scale=0.82)
        self.draw_avatar(c, "jarvis", 195, 84, scale=0.72)
        self.draw_avatar(c, "lloyd", 295, 84, scale=0.82)
        c.create_text(195, 156, text="NINJA ALLIANCE + J.A.R.V.I.S.", fill=self.CYAN, font=self.FONT_TITLE)

        # Center Status
        c.create_text(w // 2, 34, text="LEVEL 15 // DIGITAL OVERLORD VIRUS CORE",
                      fill=self.PURPLE_VIRUS, font=self.FONT_HERO)
        c.create_text(w // 2, 70, text=status_msg, fill=self.TEXT_WHITE, font=self.FONT_BODY)
        c.create_text(w // 2, 106, text=f"FIREWALL NODES BREACHED: {self.boss_score}/20",
                      fill=self.GOLD, font=self.FONT_TITLE)

        if pulse == "breach":
            c.create_line(340, 84, w - 190, 84, fill=self.CYAN, width=7)
            c.create_line(340, 84, w - 190, 84, fill=self.GOLD, width=2)

        # Digital Overlord Avatar on Right
        self.draw_avatar(c, "overlord", w - 130, 82, scale=0.95)
        c.create_text(w - 130, 152, text="DIGITAL OVERLORD", fill=self.PURPLE_VIRUS, font=self.FONT_TITLE)

        # Overlord Firewall Bar
        c.create_rectangle(w - 210, 165, w - 50, 176, fill="#1E1B4B", outline=self.PURPLE_VIRUS)
        fw_w = max(0, int(160 * (self.firewall_hp / 100.0)))
        c.create_rectangle(w - 210, 165, w - 210 + fw_w, 176, fill=self.PURPLE_VIRUS, outline="")

    def render_boss_question(self):
        for w in self.boss_card.winfo_children():
            w.destroy()

        if self.boss_idx >= 20:
            self.finish_boss_battle()
            return

        self.boss_answered = False
        q_text, raw_options, correct_idx, hint_txt = self.boss_questions[self.boss_idx]

        indexed = list(enumerate(raw_options))
        random.shuffle(indexed)
        shuffled_opts = [opt for _, opt in indexed]
        new_correct_idx = [i for i, (orig_i, _) in enumerate(indexed) if orig_i == correct_idx][0]

        hdr = tk.Frame(self.boss_card, bg=self.BG_PANEL)
        hdr.pack(fill="x", padx=26, pady=(14, 6))

        tk.Label(hdr, text=f"FIREWALL LAYER {self.boss_idx + 1} OF 20",
                 bg=self.BG_PANEL, fg=self.PURPLE_VIRUS, font=self.FONT_TITLE).pack(side="left")

        mins, secs = divmod(self.boss_time_left, 60)
        self.boss_timer_lbl = tk.Label(
            hdr, text=f"⏱ FIREWALL LOCKOUT: {mins:02d}:{secs:02d}",
            bg=self.BG_PANEL, fg=self.RED_STARK, font=self.FONT_TITLE
        )
        self.boss_timer_lbl.pack(side="right", padx=12)

        self.boss_hint_lbl = tk.Label(hdr, text="", bg=self.BG_PANEL, fg=self.GOLD, font=self.FONT_SMALL)
        self.boss_hint_lbl.pack(side="right", padx=10)

        self.make_btn(
            hdr, "💡 J.A.R.V.I.S. HINT",
            lambda h=hint_txt: (self.play_sfx("hint"), self.boss_hint_lbl.config(text=f"J.A.R.V.I.S.: {h}")),
            accent=self.GOLD
        ).pack(side="right")

        tk.Label(
            self.boss_card, text=q_text, bg=self.BG_CARD, fg=self.TEXT_WHITE,
            font=("Consolas", 11, "bold"), wraplength=1060, justify="left",
            padx=20, pady=15, highlightbackground=self.PURPLE_VIRUS, highlightthickness=1
        ).pack(fill="x", padx=26, pady=8)

        self.boss_fb_lbl = tk.Label(self.boss_card, text="", bg=self.BG_PANEL, font=self.FONT_TITLE)
        self.boss_fb_lbl.pack(pady=3)

        opts_frame = tk.Frame(self.boss_card, bg=self.BG_PANEL)
        opts_frame.pack(fill="x", padx=26, pady=4)

        self.boss_opt_btns = []
        for i, opt in enumerate(shuffled_opts):
            btn = tk.Button(
                opts_frame, text=f"  [{chr(65 + i)}]   {opt}",
                command=lambda chosen=i, corr=new_correct_idx, s_opts=shuffled_opts: self.handle_boss_answer(chosen, corr, s_opts),
                bg=self.BG_CARD, fg=self.TEXT_WHITE, activebackground=self.BG_HOVER,
                activeforeground=self.CYAN, relief="flat", bd=0,
                font=("Consolas", 11), anchor="w", padx=18, pady=10,
                cursor="hand2", highlightbackground=self.BORDER, highlightthickness=1
            )
            btn.pack(fill="x", pady=4)
            self.boss_opt_btns.append(btn)

        footer = tk.Frame(self.boss_card, bg=self.BG_PANEL)
        footer.pack(fill="x", padx=26, pady=(6, 12))
        self.make_btn(footer, "← ABORT BOSS RUN", self.show_level_map, accent=self.TEXT_MUTED).pack(side="left")
        self.boss_next_btn = self.make_btn(footer, "NEXT FIREWALL NODE →", self.advance_boss_q, accent=self.PURPLE_VIRUS)

    def handle_boss_answer(self, chosen, correct, shuffled_opts):
        if self.boss_answered:
            return
        self.boss_answered = True

        for idx, btn in enumerate(self.boss_opt_btns):
            if idx == correct:
                btn.config(bg="#064E3B", fg=self.GREEN_LLOYD, highlightbackground=self.GREEN_LLOYD)
            elif idx == chosen:
                btn.config(bg="#4C0519", fg=self.RED_STARK, highlightbackground=self.RED_STARK)

        if chosen == correct:
            self.play_sfx("hit")
            self.boss_score += 1
            self.firewall_hp = max(0, 100 - (self.boss_score * 5))
            self.boss_fb_lbl.config(text="⚡ FIREWALL NODE SHATTERED!", fg=self.GREEN_LLOYD)
            self.render_boss_arena("J.A.R.V.I.S. & NINJAS BREACHED A FIREWALL LAYER!", pulse="breach")
        else:
            self.play_sfx("wrong")
            self.boss_fb_lbl.config(
                text=f"✖ VIRUS BLOCKED DECRYPT! Correct answer: {shuffled_opts[correct]}",
                fg=self.RED_STARK
            )
            self.render_boss_arena("OVERLORD COUNTER-SURGE! KEEP PUSHING!")

        self.boss_next_btn.pack(side="right")

    def advance_boss_q(self):
        self.boss_idx += 1
        self.render_boss_question()

    def finish_boss_battle(self, timed_out=False):
        if self.boss_timer_job:
            try:
                self.root.after_cancel(self.boss_timer_job)
            except Exception:
                pass
            self.boss_timer_job = None

        if self.boss_score < 5:
            self.play_sfx("wrong")
            reason = "Time ran out" if timed_out else f"You scored {self.boss_score}/20 (below 5)"
            messagebox.showwarning(
                "FIREWALL HELD — RELEARN & RETRY",
                f"{reason}! The Digital Overlord's virus repelled the reboot.\n\n"
                "ZANE: 'Review any earlier levels on the map, then return—the firewall questions will randomize again!'"
            )
            self.show_level_map()
        else:
            self.play_sfx("win")
            self.record_level_victory(15, self.boss_score, 10)
            messagebox.showinfo(
                "★ LIGHT RESTORED TO NINJAGO! ★",
                f"FIREWALL DEFEATED! Final Score: {self.boss_score}/20!\n\n"
                "J.A.R.V.I.S.: 'Overlord virus purged. System reboot complete.'\n"
                "ZANE: 'Peace and light return to New Ninjago City. Stark would be proud!'"
            )
            self.show_level_map()


# ==============================================================================
# 15-LEVEL CURRICULUM & QUESTION BANK (12 QUESTIONS PER LEVEL = 168+ QUESTIONS)
# Format of each question: (question_text, [4 options], correct_index, jarvis_hint)
# ==============================================================================
LEVELS = [
    {
        "level": 1,
        "topic": "Variables & Output",
        "lesson": (
            "ZANE: 'Before we debug the Overlord's virus, we must master how data is stored and displayed.'\n"
            "J.A.R.V.I.S.: 'In Python, variables bind names to values without needing explicit type declarations.'\n\n"
            "KEY RULES:\n"
            "• `print('Hello Ninjago')` outputs text or values to the console.\n"
            "• Variable names can use letters, numbers, and underscores (`ninja_power = 100`), never starting with a digit.\n"
            "• Python is case-sensitive: `Zane` and `zane` are two completely different variables.\n"
            "• Comments start with `#` and are ignored during execution."
        ),
        "questions": [
            ("Which function displays text on the screen in Python?", ["echo()", "print()", "console.log()", "display()"], 1, "Starts with 'p' and takes arguments in parentheses."),
            ("Which of these is a VALID Python variable name?", ["2ninja", "ninja-name", "ninja_name", "class"], 2, "Underscores are allowed; starting with digits or hyphens is not."),
            ("What symbol starts a single-line comment in Python?", ["//", "/*", "#", "--"], 2, "It looks like a hash / pound sign."),
            ("What is the output of: `x = 10; x = 25; print(x)`?", ["10", "25", "35", "Error"], 1, "Reassigning `x` overwrites the older value."),
            ("Are `arcPower` and `arcpower` treated as the same variable in Python?", ["Yes", "No, Python is case-sensitive", "Only inside functions", "Only for integers"], 1, "Capitalization matters in Python identifiers."),
            ("Which keyword cannot be used as a variable name because it is reserved?", ["hero", "score", "for", "ninjago"], 2, "Loop keywords are reserved by Python."),
            ("What does `print('A', 'B')` output by default?", ["AB", "A B", "A,B", "Error"], 1, "Multiple arguments in print() are separated by a space by default."),
            ("Which line assigns the value 50 to `shield`?", ["shield == 50", "50 = shield", "shield = 50", "int shield = 50"], 2, "Single `=` performs assignment."),
            ("What happens if you print a variable before assigning a value to it?", ["Prints 0", "Prints None", "Raises NameError", "Prints empty string"], 2, "Python raises an error when a name isn't defined yet."),
            ("How do you assign 10 to both `a` and `b` in one line?", ["a = b = 10", "a == b == 10", "10 -> a, b", "a & b = 10"], 0, "Chained assignment uses `=`."),
            ("What is printed by `print(3 + 4)`?", ["3 + 4", "7", "34", "Error"], 1, "Without quotes, Python evaluates the math expression."),
            ("What is printed by `print('3 + 4')`?", ["7", "3 + 4", "34", "Error"], 1, "Quotes turn the expression into literal string text."),
        ],
    },
    {
        "level": 2,
        "topic": "Data Types & Casting",
        "lesson": (
            "J.A.R.V.I.S.: 'The Overlord's virus disguises strings as numbers to crash suit sensors.'\n"
            "ZANE: 'Checking `type()` and converting types safely prevents runtime crashes.'\n\n"
            "CORE DATA TYPES:\n"
            "• `int`: Whole numbers (`42`, `-7`)\n"
            "• `float`: Decimal numbers (`3.14`, `99.5`)\n"
            "• `str`: Text enclosed in quotes (`'Titanium'`, `\"Mark-7\"`)\n"
            "• `bool`: Logical truth values (`True` or `False` — capitalized!)\n"
            "• Type Casting: `int('10')` -> `10`, `str(99)` -> `'99'`, `float(5)` -> `5.0`."
        ),
        "questions": [
            ("What does `type(3.14)` return?", ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"], 1, "Decimal numbers belong to `float`."),
            ("Which boolean value is valid in Python?", ["true", "TRUE", "True", "1_true"], 2, "Python booleans must start with an uppercase letter."),
            ("What does `int('25') + 5` evaluate to?", ["'255'", "30", "TypeError", "25.5"], 1, "`int('25')` converts the string into integer 25."),
            ("What is the data type of `'100'`?", ["int", "float", "str", "bool"], 2, "Anything inside quotes is a string (`str`)."),
            ("What does `bool(0)` return?", ["True", "False", "0", "Error"], 1, "Zero is falsy in Python; non-zero numbers are truthy."),
            ("What is the result of `float(7)`?", ["7", "7.0", "'7.0'", "Error"], 1, "Casting an int to float adds `.0`."),
            ("What happens when you run `'Score: ' + 10`?", ["'Score: 10'", "10", "TypeError", "'Score:10'"], 2, "You cannot add a `str` and an `int` without `str(10)`."),
            ("Which function converts a number into text?", ["text()", "toString()", "str()", "char()"], 2, "Short for string: `str()`."),
            ("What is `int(9.99)` in Python?", ["10", "9", "9.9", "Error"], 1, "`int()` truncates toward zero rather than rounding up."),
            ("What does `bool('False')` evaluate to?", ["False", "True", "None", "Error"], 1, "Any non-empty string—even `'False'`—is truthy!"),
            ("Which type represents whole numbers without decimals?", ["float", "int", "char", "num"], 1, "Short for integer."),
            ("What does `type(True)` return?", ["<class 'int'>", "<class 'bool'>", "<class 'str'>", "<class 'bit'>"], 1, "True/False are of type `bool`."),
        ],
    },
    {
        "level": 3,
        "topic": "Operators & Math Logic",
        "lesson": (
            "TONY STARK (Recording): 'Precision targeting requires exact arithmetic operators.'\n\n"
            "PYTHON OPERATORS:\n"
            "• `+`, `-`, `*`: Addition, subtraction, multiplication\n"
            "• `/`: True division (always returns a `float`, e.g., `10 / 2 == 5.0`)\n"
            "• `//`: Floor division (drops decimal, e.g., `10 // 3 == 3`)\n"
            "• `%`: Modulo / remainder (`10 % 3 == 1` — great for checking even/odd!)\n"
            "• `**`: Exponentiation / power (`2 ** 3 == 8`)"
        ),
        "questions": [
            ("What is `17 // 5` in Python?", ["3.4", "3", "2", "4"], 1, "`//` performs integer floor division."),
            ("What is `17 % 5`?", ["3", "2", "3.4", "1"], 1, "`%` returns the remainder after division."),
            ("What does `2 ** 4` equal?", ["8", "6", "16", "24"], 2, "`**` raises 2 to the power of 4."),
            ("What type does `8 / 2` always return in Python 3?", ["int", "float", "bool", "str"], 1, "Single `/` always produces a floating-point result (`4.0`)."),
            ("How do you check if integer `n` is even?", ["n / 2 == 0", "n % 2 == 0", "n // 2 == 0", "n ** 2 == 0"], 1, "Even numbers have a remainder of 0 when divided by 2."),
            ("What is `10 + 2 * 3` according to operator precedence?", ["36", "16", "26", "15"], 1, "Multiplication happens before addition."),
            ("What does `x += 5` mean?", ["x = 5", "x = x + 5", "x == 5", "x = +5"], 1, "Augmented assignment adds 5 to the current value of `x`."),
            ("What is `9 % 3`?", ["3", "1", "0", "9"], 2, "9 divides evenly by 3, leaving no remainder."),
            ("What is `(10 + 2) * 3`?", ["16", "36", "24", "15"], 1, "Parentheses override standard precedence."),
            ("What is `5 ** 0`?", ["0", "5", "1", "Error"], 2, "Any non-zero number to the power of 0 is 1."),
            ("Which operator checks inequality?", ["<>", "!=", "=/=", "not="], 1, "Exclamation mark followed by equals: `!=`."),
            ("What does `'Ha' * 3` produce?", ["'Ha3'", "'HaHaHa'", "TypeError", "'HHHaaa'"], 1, "Multiplying a string by an integer repeats it."),
        ],
    },
    {
        "level": 4,
        "topic": "Strings & Slicing",
        "lesson": (
            "ZANE: 'Encrypted Overlord transmissions arrive as character strings. We slice them to extract coordinates.'\n\n"
            "STRING ESSENTIALS:\n"
            "• Indexing starts at `0`: `s = 'NINJAGO'` -> `s[0] == 'N'`, `s[-1] == 'O'`.\n"
            "• Slicing `s[start:stop]`: includes `start`, excludes `stop` (`s[0:5] == 'NINJA'`).\n"
            "• Useful methods: `.upper()`, `.lower()`, `.strip()`, `.replace(old, new)`, `.split()`.\n"
            "• f-Strings embed expressions cleanly: `f'Power: {lvl * 10}%'`."
        ),
        "questions": [
            ("For `s = 'TITANIUM'`, what is `s[0:4]`?", ["'TITA'", "'TITAN'", "'ITAN'", "'TIT'"], 0, "Indices 0, 1, 2, 3 are included; index 4 is excluded."),
            ("What does `'stark'.upper()` return?", ["'Stark'", "'STARK'", "'stark'", "None"], 1, "`.upper()` converts all characters to uppercase."),
            ("What does `'  hello  '.strip()` do?", ["Removes all letters", "Removes leading and trailing spaces", "Splits into list", "Capitalizes text"], 1, "`.strip()` trims whitespace from both ends."),
            ("For `word = 'PYTHON'`, what is `word[-2]`?", ["'N'", "'O'", "'H'", "'P'"], 1, "`-1` is 'N', so `-2` is 'O'."),
            ("What does `'a-b-c'.split('-')` return?", ["'abc'", "['a', 'b', 'c']", "('a', 'b', 'c')", "['a-b-c']"], 1, "`.split('-')` breaks a string into a list at each hyphen."),
            ("How do you reverse string `s` using slicing?", ["s[::-1]", "s[-1:0]", "s[1::-1]", "reverse(s)"], 0, "A step of `-1` walks backward through the string."),
            ("What does `len('Zane')` return?", ["3", "4", "5", "0"], 1, "There are 4 characters in 'Zane'."),
            ("Are Python strings mutable (can you do `s[0] = 'X'`)?", ["Yes", "No, strings are immutable", "Only lowercase strings", "Only with f-strings"], 1, "Strings cannot be modified in place; you must create a new string."),
            ("What does `'ninjago'.replace('ninja', 'cyber')` return?", ["'cybergo'", "'ninjago'", "'cyber'", "Error"], 0, "Replaces matching substring with the new text."),
            ("What is `f'{2 + 3}'`?", ["'2 + 3'", "'5'", "5", "Error"], 1, "f-strings evaluate expressions inside `{}` and format as string."),
            ("What does `'cy' in 'cyber'` evaluate to?", ["True", "False", "0", "Error"], 0, "The `in` operator checks substring membership."),
            ("What does `'abc'.find('z')` return when not found?", ["0", "False", "-1", "ValueError"], 2, "`.find()` returns `-1` if the substring doesn't exist."),
        ],
    },
    {
        "level": 5,
        "topic": "Conditionals (if / elif / else)",
        "lesson": (
            "J.A.R.V.I.S.: 'Automated defense routines rely on branching logic trees.'\n\n"
            "DECISION MAKING:\n"
            "• `if` tests the primary condition; `elif` tests backup conditions; `else` catches everything remaining.\n"
            "• Indentation (4 spaces) defines which code belongs inside each branch.\n"
            "• Logical combinators: `and` (both True), `or` (at least one True), `not` (flips True/False)."
        ),
        "questions": [
            ("How does Python group code blocks inside an `if` statement?", ["Curly braces {}", "Parentheses ()", "Indentation (spaces)", "begin / end"], 2, "Consistent indentation defines block scope in Python."),
            ("What is `not (True and False)`?", ["False", "True", "None", "Error"], 1, "`True and False` is `False`; `not False` is `True`."),
            ("How many `elif` blocks can follow a single `if` statement?", ["Only 1", "At most 3", "As many as needed", "None"], 2, "You can chain any number of `elif` branches."),
            ("If `x = 15`, what prints? `if x > 20: print('A') elif x > 10: print('B') else: print('C')`", ["A", "B", "C", "B and C"], 1, "First condition is False, second (`15 > 10`) is True, so it stops at B."),
            ("Which symbol is required at the end of an `if condition` line?", [";", ":", ".", "->"], 1, "A colon `:` introduces an indented suite."),
            ("When is `A or B` False?", ["When A is False", "When B is False", "Only when BOTH A and B are False", "Never"], 2, "`or` only needs one True operand to be True."),
            ("What does `10 <= 10` evaluate to?", ["False", "True", "SyntaxError", "None"], 1, "Less than OR equal to 10 is True."),
            ("What is the shorthand ternary expression in Python?", ["a ? b : c", "b if a else c", "if a then b else c", "a -> b : c"], 1, "Python writes `value_if_true if condition else value_if_false`."),
            ("What happens if you write `if x = 5:` instead of `if x == 5:`?", ["Sets x to 5", "SyntaxError", "Evaluates to True", "Evaluates to False"], 1, "Assignment `=` is invalid inside an `if` header."),
            ("Which value is considered Falsy in an `if` test?", ["[0]", "'0'", "[]", "-1"], 2, "An empty list `[]` evaluates to False."),
            ("If `a = True` and `b = False`, what is `a and not b`?", ["False", "True", "None", "Error"], 1, "`not b` is True, so `True and True` is True."),
            ("Does an `if` statement require an `else` clause?", ["Yes, always", "No, `else` is optional", "Only inside loops", "Only with `elif`"], 1, "`else` is completely optional."),
        ],
    },
    {
        "level": 6,
        "topic": "Lists & Tuple Sequences",
        "lesson": (
            "KAI: 'A Ninja's inventory changes mid-fight, while coordinates of Ninjago temples never change.'\n"
            "ZANE: 'Use Lists `[]` for mutable collections, and Tuples `()` for locked, immutable data.'\n\n"
            "SEQUENCE OPERATIONS:\n"
            "• `items.append(x)` adds to end; `items.pop()` removes & returns last item.\n"
            "• `items.sort()` sorts in place; `sorted(items)` returns a new sorted list.\n"
            "• Tuples `(10, 20)` cannot be changed after creation, making them faster and safer for fixed coordinates."
        ),
        "questions": [
            ("Which brackets define a Python List?", ["()", "{}", "[]", "<>"], 2, "Square brackets `[]` create lists."),
            ("What is the main difference between a List and a Tuple?", ["Tuples hold only numbers", "Lists are mutable; Tuples are immutable", "Tuples are slower", "Lists cannot hold strings"], 1, "Once created, tuple elements cannot be modified."),
            ("What does `[1, 2, 3].pop()` return?", ["1", "2", "3", "None"], 2, "`.pop()` without an index removes and returns the final item."),
            ("How do you insert `'Zane'` at index 0 of list `team`?", ["team.append('Zane')", "team.insert(0, 'Zane')", "team.add(0, 'Zane')", "team[0] = 'Zane'"], 1, "`.insert(index, item)` shifts existing elements right."),
            ("What does `[1, 2] + [3, 4]` produce?", ["[4, 6]", "[1, 2, 3, 4]", "[[1, 2], [3, 4]]", "TypeError"], 1, "`+` concatenates two lists into one."),
            ("How do you create a single-element tuple containing `5`?", ["(5)", "(5,)", "[5]", "tuple(5)"], 1, "A trailing comma `(5,)` distinguishes a tuple from parenthesized math."),
            ("What does `len([[1, 2], [3, 4, 5]])` return?", ["5", "2", "3", "6"], 1, "The outer list contains 2 inner list elements."),
            ("Which method removes the first matching value `x` from a list?", ["list.delete(x)", "list.remove(x)", "list.pop(x)", "list.clear(x)"], 1, "`.remove(value)` searches by value, whereas `.pop(index)` uses position."),
            ("What does `3 in [1, 2, 3, 4]` return?", ["2", "True", "False", "3"], 1, "`in` checks membership and returns a boolean."),
            ("What is `nums[1:3]` if `nums = [10, 20, 30, 40]`?", ["[10, 20, 30]", "[20, 30]", "[20, 30, 40]", "[30, 40]"], 1, "Starts at index 1 (`20`) and stops before index 3 (`40`)."),
            ("What does `list('ABC')` return?", ["['ABC']", "['A', 'B', 'C']", "('A', 'B', 'C')", "Error"], 1, "`list()` iterates over the string's characters."),
            ("Which function returns the largest number in list `scores`?", ["top(scores)", "max(scores)", "high(scores)", "scores.max()"], 1, "Built-in `max()` works on any comparable sequence."),
        ],
    },
    {
        "level": 7,
        "topic": "Loops (for & while)",
        "lesson": (
            "JAY: 'Spinning once is a strike; spinning 100 times in a `while` loop is a tornado!'\n\n"
            "LOOP MECHANICS:\n"
            "• `for x in collection:` iterates cleanly over every item in a list, string, or `range()`.\n"
            "• `while condition:` repeats as long as the condition stays True.\n"
            "• `break` exits the loop immediately; `continue` skips the rest of the current iteration and jumps to the next."
        ),
        "questions": [
            ("What values does `range(1, 5)` yield?", ["1, 2, 3, 4, 5", "1, 2, 3, 4", "0, 1, 2, 3, 4", "2, 3, 4, 5"], 1, "`range(start, stop)` stops one before `stop`."),
            ("Which statement skips the rest of the current loop iteration?", ["break", "pass", "continue", "skip"], 2, "`continue` jumps straight to the next cycle."),
            ("What causes an infinite `while` loop?", ["Using `break`", "Condition never becomes False", "Using `range(10)`", "Empty list"], 1, "If the loop condition stays True forever, it never terminates."),
            ("What does `range(0, 10, 2)` generate?", ["0, 2, 4, 6, 8", "0, 2, 4, 6, 8, 10", "2, 4, 6, 8, 10", "0, 5, 10"], 0, "The third argument `2` is the step size."),
            ("How many times does `for i in range(4):` run?", ["3", "4", "5", "0"], 1, "Runs for `i = 0, 1, 2, 3` (4 times total)."),
            ("Which built-in gives both index and value when looping over a list?", ["zip()", "enumerate()", "items()", "index()"], 1, "`for idx, val in enumerate(items):` provides both."),
            ("What does `pass` do inside a loop?", ["Exits loop", "Restarts loop", "Does nothing (placeholder)", "Skips iteration"], 2, "`pass` is a null no-op statement."),
            ("What is `total` after: `total = 0; for n in [1, 2, 3]: total += n`?", ["3", "6", "123", "0"], 1, "Sums 1 + 2 + 3 = 6."),
            ("Which loop is best when you don't know beforehand how many iterations are needed?", ["for loop", "while loop", "range loop", "import loop"], 1, "`while` loops run until a dynamic condition changes."),
            ("What happens when `break` executes inside a nested inner loop?", ["Exits ALL loops", "Exits ONLY the inner loop", "Exits the program", "Raises StopIteration"], 1, "`break` only terminates the innermost enclosing loop."),
            ("What does `list(range(3, 0, -1))` produce?", ["[3, 2, 1]", "[3, 2, 1, 0]", "[1, 2, 3]", "[]"], 0, "Counts down by -1, stopping before 0."),
            ("Can a `for` loop iterate directly over characters in a string?", ["Yes", "No", "Only if converted to list", "Only ASCII strings"], 0, "Strings are iterable sequences in Python."),
        ],
    },
    {
        "level": 8,
        "topic": "Dictionaries & Sets",
        "lesson": (
            "J.A.R.V.I.S.: 'My threat database maps every villain ID to their weakness in O(1) instant lookup time.'\n\n"
            "HASH COLLECTIONS:\n"
            "• Dictionary `{'key': 'value'}` stores key-value pairs.\n"
            "• `d.get('key', default)` safely retrieves a value without crashing if the key is missing.\n"
            "• Set `{1, 2, 3}` stores **unique** unordered elements—automatically eliminating duplicates!"
        ),
        "questions": [
            ("What does `len({1, 2, 2, 3, 3, 3})` return?", ["6", "3", "1", "SyntaxError"], 1, "Sets automatically strip duplicate values."),
            ("How do you safely access key `'armor'` in dict `suit` without risking KeyError?", ["suit['armor']", "suit.get('armor')", "suit.find('armor')", "suit->armor"], 1, "`.get()` returns `None` (or a default) instead of raising KeyError."),
            ("What does `d.keys()` return?", ["All values", "All keys in the dictionary", "Key-value tuples", "Number of items"], 1, "Returns a view of all dictionary keys."),
            ("How do you create an EMPTY set in Python?", ["{}", "set()", "[]", "empty_set()"], 1, "`{}` creates an empty dictionary; `set()` creates an empty set."),
            ("Can a Python list be used as a dictionary key?", ["Yes", "No, keys must be hashable/immutable", "Only empty lists", "Only inside functions"], 1, "Mutable objects like lists cannot be hashed as dict keys; tuples can."),
            ("What does `d.items()` yield when looping over a dictionary?", ["Only keys", "Only values", "(key, value) pairs", "Sorted indices"], 2, "`.items()` provides `(key, value)` tuples."),
            ("How do you add key `'ice'` with value `100` to dict `stats`?", ["stats.add('ice', 100)", "stats['ice'] = 100", "stats.append('ice': 100)", "stats.insert('ice', 100)"], 1, "Assigning to a new key inserts it into the dictionary."),
            ("Which set operation finds elements common to both `A` and `B`?", ["A | B", "A & B", "A - B", "A + B"], 1, "`&` computes set intersection."),
            ("What happens if you access `d['missing']` directly with square brackets?", ["Returns None", "Returns False", "Raises KeyError", "Creates the key"], 2, "Direct bracket lookup raises `KeyError` when absent."),
            ("Which operator unites all unique elements from sets `A` and `B`?", ["A | B", "A & B", "A ^ B", "A / B"], 0, "`|` performs set union."),
            ("How do you remove key `'temp'` and return its value from dict `d`?", ["d.remove('temp')", "d.pop('temp')", "d.delete('temp')", "d.cut('temp')"], 1, "`.pop(key)` deletes the entry and returns its value."),
            ("Are dictionary keys unique in Python?", ["Yes, duplicate keys overwrite older values", "No, keys can repeat", "Only integer keys", "Only string keys"], 0, "Each key in a dict maps to a single latest value."),
        ],
    },
    {
        "level": 9,
        "topic": "Functions & Scope",
        "lesson": (
            "TONY STARK: 'Modular suits win wars. If a thruster breaks, you swap the module—not the whole armor.'\n\n"
            "FUNCTION ARCHITECTURE:\n"
            "• Defined with `def func_name(param1, param2=default):`\n"
            "• `return` sends data back and exits the function. Without `return`, a function returns `None`.\n"
            "• **Local Scope:** Variables created inside a function exist only inside that function."
        ),
        "questions": [
            ("What does a Python function return if it has no `return` statement?", ["0", "False", "None", "Empty string"], 2, "Functions implicitly return `None` by default."),
            ("What is a default parameter in `def boost(power=50):`?", ["power is always 50", "power uses 50 if no argument is passed", "SyntaxError", "power cannot be changed"], 1, "Callers can override it with `boost(90)` or omit it."),
            ("Where are variables created inside a function accessible?", ["Everywhere globally", "Only inside that function (local scope)", "Only in `main()`", "In all imported files"], 1, "Local variables are destroyed once the function returns."),
            ("What do `*args` allow a function to accept?", ["Only keyword arguments", "Any number of positional arguments", "Only lists", "Pointer addresses"], 1, "`*args` packs extra positional arguments into a tuple."),
            ("What do `**kwargs` collect?", ["Positional args as list", "Keyword arguments as a dictionary", "Global variables", "Return values"], 1, "`**kwargs` packs `key=value` arguments into a `dict`."),
            ("Which keyword allows modifying a global variable from inside a function?", ["outer", "public", "global", "shared"], 2, "Declaring `global var_name` binds to module scope."),
            ("What is a `lambda` in Python?", ["A loop type", "A small anonymous one-line function", "A file format", "A memory error"], 1, "Example: `lambda x: x * 2`."),
            ("Can a Python function return multiple values like `return a, b`?", ["No", "Yes, packed as a tuple", "Only if they are ints", "Only with global"], 1, "`return a, b` returns a tuple `(a, b)` that can be unpacked."),
            ("What is a docstring?", ["A crash log", "A triple-quoted string documenting a function/module", "A type declaration", "A syntax error"], 1, "Placed right below `def` to explain what the function does."),
            ("What happens to code written right after a `return` statement in the same block?", ["Runs last", "Never executes (unreachable)", "Runs twice", "Raises SyntaxError"], 1, "`return` immediately exits the function."),
            ("In `def add(a, b): return a + b`, what are `a` and `b` called?", ["Arguments", "Parameters", "Modules", "Attributes"], 1, "Parameters are the names in the definition; arguments are the values passed in."),
            ("What does `(lambda x: x + 10)(5)` evaluate to?", ["10", "5", "15", "Error"], 2, "Passes `5` into the lambda and returns `5 + 10 = 15`."),
        ],
    },
    {
        "level": 10,
        "topic": "Comprehensions & Built-ins",
        "lesson": (
            "ZANE: 'Concise code executes cleanly and leaves zero room for hidden virus bugs.'\n\n"
            "PYTHONIC EXPRESSIONS:\n"
            "• **List Comprehension:** `[x * 2 for x in nums if x > 0]` builds a transformed, filtered list in one line.\n"
            "• **Built-in Powerhouses:** `zip(list1, list2)` pairs items together; `any()` checks if at least one item is True; `all()` checks if every item is True."
        ),
        "questions": [
            ("What does `[x**2 for x in range(4)]` produce?", ["[1, 4, 9, 16]", "[0, 1, 4, 9]", "[0, 2, 4, 6]", "[0, 1, 2, 3]"], 1, "Squares `0, 1, 2, 3` -> `0, 1, 4, 9`."),
            ("What does `[n for n in [1, 2, 3, 4] if n % 2 == 0]` return?", ["[1, 3]", "[2, 4]", "[True, False]", "[2]"], 1, "Filters only numbers divisible by 2."),
            ("What does `all([True, True, False])` return?", ["True", "False", "None", "2"], 1, "`all()` requires EVERY element to be truthy."),
            ("What does `any([False, 0, '', 'Zane'])` return?", ["False", "True", "None", "Error"], 1, "Because `'Zane'` is truthy, `any()` returns `True`."),
            ("What does `list(zip([1, 2], ['a', 'b']))` produce?", ["[(1, 'a'), (2, 'b')]", "[1, 'a', 2, 'b']", "{1: 'a', 2: 'b'}", "Error"], 0, "`zip()` pairs corresponding elements into tuples."),
            ("Which comprehension creates a Set instead of a List?", ["[x for x in s]", "{x for x in s}", "(x for x in s)", "<x for x in s>"], 1, "Curly braces without colons create a set comprehension."),
            ("What does `(x for x in range(5))` create?", ["A tuple", "A generator expression", "A list", "A syntax error"], 1, "Parentheses around a comprehension create a lazy generator."),
            ("What does `sum([10, 20, 30])` return?", ["3", "60", "30", "10"], 1, "`sum()` adds all numeric items in an iterable."),
            ("What does `sorted([3, 1, 2], reverse=True)` return?", ["[1, 2, 3]", "[3, 2, 1]", "None", "[2, 1, 3]"], 1, "`reverse=True` sorts from highest to lowest."),
            ("How do you create a dict mapping `x` to `x*2` for `x in [1, 2]`?", ["[x: x*2 for x in [1, 2]]", "{x: x*2 for x in [1, 2]}", "(x: x*2 for x in [1, 2])", "dict(x*2)"], 1, "Dict comprehensions use `{key: val for ...}`."),
            ("If `zip([1, 2, 3], ['x', 'y'])` runs on unequal lengths, what happens?", ["Raises ValueError", "Stops at the shortest iterable", "Pads with None", "Loops forever"], 1, "`zip()` stops as soon as the shortest input runs out."),
            ("What does `abs(-42)` return?", ["-42", "42", "0", "42.0"], 1, "`abs()` returns the non-negative magnitude."),
        ],
    },
    {
        "level": 11,
        "topic": "Exception Handling",
        "lesson": (
            "J.A.R.V.I.S.: 'The Overlord injects malformed inputs to trigger unhandled crashes. Wrap risky operations in shields!'\n\n"
            "ERROR SHIELDING:\n"
            "• `try:` runs code that might fail.\n"
            "• `except ValueError:` catches and recovers from specific errors.\n"
            "• `else:` runs only if NO exception occurred.\n"
            "• `finally:` ALWAYS executes (cleanup, closing connections), whether an error happened or not."
        ),
        "questions": [
            ("Which block ALWAYS runs regardless of whether an exception occurred?", ["try", "except", "else", "finally"], 3, "`finally` is guaranteed to execute for cleanup."),
            ("What exception is raised when dividing by zero (`10 / 0`)?", ["ValueError", "ZeroDivisionError", "ArithmeticType", "NullError"], 1, "Python has a dedicated `ZeroDivisionError`."),
            ("What exception occurs when running `int('ninjago')`?", ["TypeError", "ValueError", "NameError", "IndexError"], 1, "The type `str` is valid, but its value cannot become an int -> `ValueError`."),
            ("Which keyword lets you manually trigger an exception?", ["throw", "raise", "trigger", "error"], 1, "Python uses `raise ValueError('msg')`."),
            ("When does the `else` block in a `try...except...else` structure execute?", ["Only when an error occurs", "Only when NO error occurs in `try`", "Always", "Never"], 1, "`else` runs on clean, exception-free execution."),
            ("What exception occurs when accessing index 10 of a 3-item list?", ["KeyError", "IndexError", "RangeError", "OutOfBounds"], 1, "Out-of-range sequence indices raise `IndexError`."),
            ("Why is bare `except:` discouraged compared to `except ValueError:`?", ["It is a syntax error", "It can hide unexpected bugs like KeyboardInterrupt", "It slows down loops", "It only catches strings"], 1, "Catching specific exceptions avoids masking real bugs."),
            ("What exception occurs when referencing an undefined variable `xyz`?", ["ValueError", "NameError", "AttributeError", "ImportError"], 1, "Unknown identifiers raise `NameError`."),
            ("Can one `try` block have multiple `except` clauses?", ["No", "Yes, to handle different error types separately", "Only two", "Only with `finally`"], 1, "You can stack multiple `except` handlers."),
            ("What exception is raised when calling `'hello'.non_existent_method()`?", ["NameError", "AttributeError", "MethodError", "TypeError"], 1, "Missing methods/properties raise `AttributeError`."),
            ("How do you capture the exception object into variable `e`?", ["except ValueError -> e:", "except ValueError as e:", "except e = ValueError:", "catch (ValueError e):"], 1, "Use the `as` keyword."),
            ("What happens if an exception is raised inside `try` and NO matching `except` exists?", ["Program ignores it", "Exception propagates up and crashes if unhandled", "Returns None", "Restarts `try`"], 1, "Unhandled exceptions bubble up the call stack."),
        ],
    },
    {
        "level": 12,
        "topic": "File I/O & JSON Persistence",
        "lesson": (
            "ZANE: 'Memory banks wipe on reboot unless data is written safely to disk.'\n\n"
            "FILE & JSON HANDLING:\n"
            "• Always use `with open('log.txt', 'r') as f:` — the `with` context manager automatically closes the file.\n"
            "• Modes: `'r'` (read), `'w'` (write/overwrite), `'a'` (append).\n"
            "• `json.dumps(obj)` converts Python dicts/lists to JSON string; `json.loads(text)` parses JSON back."
        ),
        "questions": [
            ("Why is `with open('data.txt') as f:` preferred over `f = open(...)`?", ["Faster disk speed", "Automatically closes the file even if errors occur", "Encrypts the file", "Creates backups"], 1, "Context managers guarantee clean resource release."),
            ("Which file mode adds new text to the end WITHOUT erasing existing content?", ["'r'", "'w'", "'a'", "'x'"], 2, "`'a'` stands for append mode."),
            ("What does `open('file.txt', 'w')` do if `'file.txt'` already exists?", ["Raises an error", "Overwrites / truncates existing contents", "Appends to end", "Opens read-only"], 1, "Write mode `'w'` clears existing file contents."),
            ("Which standard library module parses and writes JSON data?", ["csv", "json", "pickle", "os"], 1, "Python includes `import json` in its standard library."),
            ("What does `f.readlines()` return?", ["A single giant string", "A list of strings (one per line)", "Line count integer", "A dictionary"], 1, "Returns every line as an element in a `list`."),
            ("Which `json` function converts a Python dictionary into a JSON-formatted string?", ["json.loads()", "json.dumps()", "json.parse()", "json.read()"], 1, "`dumps` = dump string."),
            ("What happens if you open a non-existent file in `'r'` mode?", ["Creates an empty file", "Raises FileNotFoundError", "Returns None", "Opens in write mode"], 1, "Read mode requires the file to exist."),
            ("What does `json.loads('{\"a\": 1}')` return?", ["A string", "A Python dictionary {'a': 1}", "A list", "A tuple"], 1, "`loads` = load string into native Python objects."),
            ("Which file mode creates a new file and fails if it already exists?", ["'w'", "'a'", "'x'", "'r+'"], 2, "`'x'` stands for exclusive creation."),
            ("What method reads the entire remaining file content as one string?", ["f.read()", "f.readline()", "f.lines()", "f.all()"], 0, "`f.read()` returns the full text string."),
            ("When writing text across OS platforms, which encoding is best practice?", ["ascii", "utf-8", "latin-0", "binary"], 1, "`encoding='utf-8'` supports international characters safely."),
            ("Does `f.write('line1')` automatically add a newline character `\\n`?", ["Yes", "No, you must include '\\n' explicitly", "Only on Windows", "Only in `'a'` mode"], 1, "Unlike `print()`, `file.write()` writes exact characters without adding `\\n`."),
        ],
    },
    {
        "level": 13,
        "topic": "Recursion & Algorithms",
        "lesson": (
            "J.A.R.V.I.S.: 'The Overlord's maze replicates infinitely unless we apply a Base Case and Big-O search efficiency.'\n\n"
            "ALGORITHMIC THINKING:\n"
            "• **Recursion:** A function that calls itself on a smaller subproblem until hitting a **Base Case**.\n"
            "• Without a Base Case, recursion causes a `RecursionError` (stack overflow).\n"
            "• **Binary Search** finds items in a **sorted** list in `O(log n)` steps—far faster than `O(n)` linear scan."
        ),
        "questions": [
            ("What prevents a recursive function from calling itself forever?", ["A `for` loop", "A Base Case", "A global variable", "A `try` block"], 1, "The base case stops recursion and returns a direct answer."),
            ("What exception does Python raise if recursion goes too deep?", ["MemoryCrash", "RecursionError", "LoopError", "InfiniteError"], 1, "Python caps call stack depth and raises `RecursionError`."),
            ("What is the time complexity of Binary Search on a sorted list of `n` items?", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 1, "Halving the search space each step yields logarithmic time."),
            ("What prerequisite is REQUIRED for Binary Search to work properly?", ["List must contain only integers", "List must be sorted", "List length must be even", "No duplicates allowed"], 1, "Binary search relies on ordering to discard half the list."),
            ("In `factorial(n)`, what is the standard base case?", ["if n == 0 or n == 1: return 1", "if n == 10: return 0", "if n < 0: return n", "No base case needed"], 0, "`0!` and `1!` both equal `1`."),
            ("What is the time complexity of looking up a key in a Python dictionary?", ["O(1) average", "O(n)", "O(n log n)", "O(2^n)"], 0, "Hash tables achieve constant-time average lookups."),
            ("Which data structure follows LIFO (Last-In, First-Out), like the recursion call stack?", ["Queue", "Stack", "Set", "Graph"], 1, "Function calls push onto and pop off the Call Stack."),
            ("Which data structure follows FIFO (First-In, First-Out)?", ["Stack", "Queue", "Tree", "Heap"], 1, "Queues process items in arrival order."),
            ("In Fibonacci (`fib(n) = fib(n-1) + fib(n-2)`), how many base cases are needed?", ["1", "2 (for n=0 and n=1)", "3", "0"], 1, "Because it looks back 2 steps, both `n=0` and `n=1` must stop."),
            ("What is the time complexity of scanning an unsorted list from start to finish?", ["O(1)", "O(log n)", "O(n)", "O(n!)"], 2, "Linear search checks up to all `n` elements."),
            ("Which sorting algorithm repeatedly divides a list in half and merges sorted halves?", ["Bubble Sort", "Merge Sort", "Selection Sort", "Bogo Sort"], 1, "Merge Sort is a classic `O(n log n)` divide-and-conquer algorithm."),
            ("What happens to memory usage in deep recursion compared to an iterative loop?", ["Uses less memory", "Uses more stack frame memory", "Uses zero memory", "Identical memory"], 1, "Each recursive call allocates a new frame on the call stack."),
        ],
    },
    {
        "level": 14,
        "topic": "Object-Oriented Programming",
        "lesson": (
            "TONY STARK & ZANE: 'We blueprint our suits as Classes so every Ninja can instantiate custom armor!'\n\n"
            "OOP BLUEPRINTS:\n"
            "• `class NinjaSuit:` defines a blueprint; `zane_suit = NinjaSuit('Ice')` creates an **instance (object)**.\n"
            "• `__init__(self, ...)` is the constructor that initializes attributes when an object is created.\n"
            "• `self` refers to the specific object instance.\n"
            "• **Inheritance:** `class TitaniumSuit(NinjaSuit):` inherits attributes and methods from its parent class."
        ),
        "questions": [
            ("What is the special constructor method called automatically when creating an object?", ["__start__", "__init__", "__create__", "__main__"], 1, "Double-underscore `init`: `__init__`."),
            ("What does the `self` parameter inside a class method represent?", ["The parent class", "The current object instance", "A global module", "The return type"], 1, "`self` binds attributes and methods to that specific instance."),
            ("How do you define class `TitanSuit` inheriting from `BaseSuit`?", ["class TitanSuit extends BaseSuit:", "class TitanSuit(BaseSuit):", "class TitanSuit -> BaseSuit:", "inherit BaseSuit in TitanSuit:"], 1, "Parent classes go inside parentheses after the child class name."),
            ("Which function calls a method from the parent class inside a child class?", ["parent()", "super()", "base()", "upper()"], 1, "`super().__init__(...)` delegates initialization to the parent."),
            ("What is creating an object from a class called?", ["Compilation", "Instantiation", "Recursion", "Serialization"], 1, "Each created object is an *instance* of the class."),
            ("Which dunder method controls what `print(my_object)` displays?", ["__repr_str__", "__str__", "__print__", "__show__"], 1, "`__str__(self)` returns the human-readable string representation."),
            ("What is Encapsulation in OOP?", ["Deleting unused classes", "Bundling data and methods inside a class and restricting direct access", "Running two loops at once", "Importing external files"], 1, "Encapsulation protects internal state behind clean methods."),
            ("By Python convention, how do you signal an attribute is 'private' / internal?", ["private x", "_x or __x leading underscore", "$x", "const x"], 1, "Leading underscores indicate internal implementation details."),
            ("What is Polymorphism?", ["A class with no methods", "Different classes sharing the same method name with tailored behavior", "A syntax error", "Copying files"], 1, "For example, both `IronMan.attack()` and `Zane.attack()` share `.attack()`."),
            ("How do you check if `obj` is an instance of `NinjaSuit`?", ["typeof(obj, NinjaSuit)", "isinstance(obj, NinjaSuit)", "obj.is(NinjaSuit)", "check(obj, NinjaSuit)"], 1, "`isinstance(object, Class)` returns a boolean."),
            ("Can multiple independent objects be created from a single class?", ["No, only one", "Yes, as many as needed", "Only up to 10", "Only with inheritance"], 1, "A class is a reusable factory for any number of instances."),
            ("What happens if you omit `self` as the first parameter of an instance method?", ["Works fine", "Raises TypeError when called on an instance", "Makes it global", "Returns None"], 1, "Python automatically passes the instance as the first argument."),
        ],
    },
    {
        "level": 15,
        "topic": "OVERLORD VIRUS FIREWALL (BOSS)",
        "lesson": "GRAND BOSS FIGHT — 20 RANDOM QUESTIONS ACROSS ALL 14 LEVELS!",
        "questions": [],
    },
]


if __name__ == "__main__":
    root = tk.Tk()
    app = NinjagoStarkQuest(root)
    root.mainloop()