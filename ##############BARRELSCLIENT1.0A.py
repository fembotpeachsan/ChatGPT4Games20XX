#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LunarLite Client — Tkinter + Pygame, System Blue dark/light, 120 FPS vibes
Author: ChatGPT (PhD GPT flavor)
License: MIT

Features
--------
- Clean, spyware-free Minecraft launcher UI inspired by Lunar-like aesthetics
- Dark/Light themes with exact "System Blue" accent (#0A84FF)
- Pygame animated background (target 120 FPS; UI updates ~60 FPS by default)
- Version list/refresh + install via minecraft-launcher-lib
- Ely.by online authentication (skins apply online) + offline launch
- OptiFine toggle: auto-detect installed OptiFine sub-versions; best-effort installer
- Local skin PNG preview (offline note: use CustomSkinLoader or Ely.by for actual in-game skin)
- Settings persistence (username, version, theme, optifine toggle, fps target, skin path, version type)

Dependencies (install as needed)
--------------------------------
pip install pillow pygame ttkthemes requests minecraft-launcher-lib
"""
import os
import sys
import json
import time
import uuid
import math
import threading
import subprocess
from typing import Optional, Dict, Any

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Optional deps
try:
    from ttkthemes import ThemedTk
except Exception:
    ThemedTk = None

try:
    import pygame
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
except Exception:
    pygame = None

try:
    import requests
except Exception:
    requests = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

# minecraft-launcher-lib (optional until actions require it)
try:
    import minecraft_launcher_lib as mll
except Exception:
    mll = None

# ------------------------------
# Config / Paths
# ------------------------------
HOME = os.path.expanduser("~")
MC_DIR = os.path.join(HOME, ".minecraft_lunarlite")
os.makedirs(MC_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(MC_DIR, "lunarlite_settings.json")
CLIENT_TOKEN_FILE = os.path.join(MC_DIR, "elyby_client.json")
ELYBY_AUTH_URL = "https://authserver.ely.by/auth/authenticate"

SYSTEM_BLUE = "#0A84FF"  # Apple's system blue
DARK_BG = "#121212"
DARK_FG = "#EDEDED"
LIGHT_BG = "#FFFFFF"
LIGHT_FG = "#0D0D0D"

# ------------------------------
# Helpers
# ------------------------------
def load_settings() -> Dict[str, Any]:
    default = {
        "offline_username": "Player",
        "elyby_user": "",
        "theme": "dark",
        "version_type": "release",
        "version": "",
        "use_optifine": False,
        "fps_target": 120,
        "skin_path": ""
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default.update({k: data.get(k, v) for k, v in default.items()})
    except Exception:
        pass
    return default

def save_settings(s: Dict[str, Any]) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

def get_client_token() -> str:
    try:
        if os.path.exists(CLIENT_TOKEN_FILE):
            with open(CLIENT_TOKEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                tok = data.get("clientToken")
                if tok:
                    return tok
    except Exception:
        pass
    tok = str(uuid.uuid4())
    try:
        with open(CLIENT_TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"clientToken": tok}, f)
    except Exception:
        pass
    return tok

def require_mll() -> bool:
    if mll is None:
        messagebox.showerror(
            "Missing dependency",
            "The package 'minecraft-launcher-lib' is not installed.\n\nInstall it:\n  pip install minecraft-launcher-lib"
        )
        return False
    return True

# ------------------------------
# UI thread helper
# ------------------------------
class UiThread:
    def __init__(self, root: tk.Tk):
        self.root = root
    def call(self, func, *args, **kwargs):
        self.root.after(0, lambda: func(*args, **kwargs))

# ------------------------------
# Pygame Background Renderer (headless surface -> Tk image)
# ------------------------------
class PygameVibes:
    def __init__(self, ui: UiThread, target_fps=120, ui_update_fps=60, size=(560, 520)):
        self.ui = ui
        self.size = size
        self.target_fps = max(30, int(target_fps))
        self.ui_update_fps = max(15, int(ui_update_fps))
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.fps = 0.0
        self.tk_target = None  # Tk Label to update
        self.frame_count = 0
        self.last_ui_update = 0.0

        self.surface = None
        if pygame:
            try:
                pygame.init()
                self.surface = pygame.Surface(self.size).convert_alpha()
            except Exception:
                self.surface = None

    def set_target(self, widget: tk.Label):
        self.tk_target = widget

    def start(self):
        if not pygame or self.surface is None:
            return
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def update_size(self, new_size):
        self.size = new_size
        if pygame and self.surface:
            self.surface = pygame.Surface(self.size).convert_alpha()

    def _loop(self):
        clock = pygame.time.Clock()
        t0 = time.time()
        while self.running:
            t = time.time() - t0
            self._draw_frame(t)
            self.frame_count += 1
            self.fps = clock.get_fps()
            # Update Tk at ui_update_fps
            now = time.time()
            if self.tk_target and (now - self.last_ui_update) >= (1.0 / self.ui_update_fps):
                self.last_ui_update = now
                self._push_to_tk()
            clock.tick(self.target_fps)

    def _draw_frame(self, t: float):
        w, h = self.size
        s = self.surface
        if s is None:
            return
        # Animated gradient + rings + subtle noise
        s.fill((18, 18, 18, 255))  # dark base
        cx, cy = w // 2, h // 2
        # Pulse radius
        base = (math.sin(t * 1.8) * 0.5 + 0.5) * 0.35 + 0.35  # 0.35..1.05
        rad = int(min(w, h) * base)
        # System blue RGB
        sb = (10, 132, 255, 180)
        # Draw concentric circles
        for i in range(6):
            rr = int(rad * (1 - i * 0.12))
            if rr <= 0:
                break
            pygame.draw.circle(s, sb, (cx, cy), rr, width=2)
        # Sweep line
        ang = t * 0.6
        x = int(cx + math.cos(ang) * rad)
        y = int(cy + math.sin(ang) * rad)
        pygame.draw.line(s, (10, 132, 255, 220), (cx, cy), (x, y), 3)
        # Glow-ish overlay
        glow_alpha = int((math.sin(t * 2.3) * 0.5 + 0.5) * 40) + 30
        glow = pygame.Surface((w, h), pygame.SRCALPHA)
        glow.fill((10, 132, 255, glow_alpha))
        s.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _push_to_tk(self):
        if not Image:
            return
        try:
            raw = pygame.image.tostring(self.surface, "RGBA", False)
            img = Image.frombytes("RGBA", self.size, raw)
            tk_img = ImageTk.PhotoImage(img)
            # Keep a reference to avoid GC
            self.tk_target.image = tk_img
            self.ui.call(self.tk_target.configure, image=tk_img)
        except Exception:
            pass

# ------------------------------
# Minecraft helpers
# ------------------------------
def get_versions(version_type="release"):
    if not require_mll():
        return []
    try:
        versions = []
        try:
            versions = mll.utils.get_available_versions(MC_DIR)
        except TypeError:
            versions = mll.utils.get_available_versions()
        items = [v["id"] for v in versions if v.get("type") == version_type]
        items.sort(key=lambda s: s, reverse=True)
        return items
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch versions:\n{e}")
        return []

def install_version(version: str, callback: Dict[str, Any]):
    if not require_mll():
        return
    try:
        mll.install.install_minecraft_version(version, MC_DIR, callback=callback)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install {version}:\n{e}")

def ensure_java(version_id: str) -> bool:
    if not require_mll():
        return False
    version_json_path = os.path.join(MC_DIR, "versions", version_id, f"{version_id}.json")
    if not os.path.exists(version_json_path):
        messagebox.showerror("Error", f"Version {version_id} not installed!")
        return False
    try:
        with open(version_json_path, "r", encoding="utf-8") as f:
            version_info = json.load(f)
        java_version = str(version_info.get("javaVersion", {}).get("majorVersion", 8))
    except Exception:
        java_version = "8"
    try:
        if hasattr(mll.install, "install_jvm_runtime"):
            mll.install.install_jvm_runtime(java_version, MC_DIR)
        return True
    except Exception:
        return True

def build_launch_cmd(version: str, username: str, access_token: str="", uuid_str: str="") -> Optional[list]:
    if not require_mll():
        return None
    opts = {
        "username": username,
        "uuid": uuid_str or str(uuid.uuid4()),
        "token": access_token or ""
    }
    try:
        cmd = mll.command.get_minecraft_command(version, MC_DIR, opts)
        return cmd
    except Exception as e:
        messagebox.showerror("Error", f"Failed to build Minecraft command:\n{e}")
        return None

def find_installed_optifine_versions(base_version: str):
    vdir = os.path.join(MC_DIR, "versions")
    results = []
    try:
        for name in os.listdir(vdir):
            if base_version in name and "OptiFine" in name:
                results.append(name)
    except Exception:
        pass
    return sorted(results, reverse=True)

def best_effort_install_optifine(base_version: str):
    """
    Try mll installer first (if available). Otherwise, prompt for an OptiFine JAR
    and run the official installer with Java.
    """
    if not require_mll():
        return False
    # Try library-provided methods (API varies across versions)
    try_methods = [
        ("install_optifine", getattr(mll.install, "install_optifine", None)),
        ("install_optifine_version", getattr(mll.install, "install_optifine_version", None)),
    ]
    for name, fn in try_methods:
        if callable(fn):
            try:
                fn(base_version, MC_DIR)
                return True
            except Exception:
                pass
    # Ask user for OptiFine installer jar
    messagebox.showinfo(
        "OptiFine Installer",
        "Select the official OptiFine installer JAR for your version.\n"
        "We'll run it with Java so it adds a new OptiFine profile."
    )
    jar = filedialog.askopenfilename(
        title="Select OptiFine installer JAR",
        filetypes=[("Java Archive", "*.jar"), ("All files", "*.*")]
    )
    if not jar:
        return False
    try:
        subprocess.run(["java", "-jar", jar], check=True)
        return True
    except Exception as e:
        messagebox.showerror("OptiFine", f"Failed to run OptiFine installer:\n{e}")
        return False

# ------------------------------
# Ely.by
# ------------------------------
def authenticate_elyby(username: str, password: str) -> Optional[Dict[str, str]]:
    if requests is None:
        messagebox.showerror("Error", "The package 'requests' is not installed.\n\nInstall it:\n  pip install requests")
        return None
    payload = {
        "username": username,
        "password": password,
        "clientToken": get_client_token(),
        "requestUser": True
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "LunarLite/1.0"
    }
    try:
        resp = requests.post(ELYBY_AUTH_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return {
            "access_token": data.get("accessToken", ""),
            "username": data.get("selectedProfile", {}).get("name", username),
            "uuid": data.get("selectedProfile", {}).get("id", str(uuid.uuid4()))
        }
    except Exception as e:
        try:
            r = e.response  # type: ignore[attr-defined]
            msg = "Authentication failed."
            if r is not None:
                try:
                    err = r.json()
                    msg = err.get("errorMessage") or err.get("error") or f"HTTP {r.status_code}"
                except Exception:
                    msg = f"HTTP {r.status_code if r is not None else '?'}"
        except Exception:
            msg = str(e)
        messagebox.showerror("Ely.by", f"Login failed: {msg}")
        return None

# ------------------------------
# Tk App
# ------------------------------
class LunarLiteApp:
    def __init__(self):
        self.settings = load_settings()

        # Root + theme
        if ThemedTk:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
        self.root.title("LunarLite Client — System Blue")
        self.root.geometry("900x640")
        self.root.minsize(820, 560)

        self.ui = UiThread(self.root)
        self._build_styles()

        # Layout
        self._build_layout()

        # Pygame vibes
        self.vibes = PygameVibes(self.ui, target_fps=int(self.settings["fps_target"]), ui_update_fps=60,
                                  size=(self.bg_width, self.bg_height))
        self.vibes.set_target(self.bg_label)
        self.vibes.start()

        # Populate versions
        self.refresh_versions(initial=True)

        # Loop
        self._update_fps_label()

    # ---------- Styles / Theme ----------
    def _build_styles(self):
        self.style = ttk.Style(self.root)
        self.apply_theme(self.settings.get("theme", "dark"))

    def apply_theme(self, theme: str):
        theme = theme.lower()
        self.theme = theme
        if theme == "light":
            bg, fg = LIGHT_BG, LIGHT_FG
        else:
            bg, fg = DARK_BG, DARK_FG
        self.root.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.configure("TRadiobutton", background=bg, foreground=fg)
        self.style.configure("TEntry", fieldbackground="#1E1E1E" if theme == "dark" else "#F2F2F2",
                             foreground=fg)
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        # Buttons default
        self.style.map("TButton",
                       background=[("active", SYSTEM_BLUE)],
                       foreground=[("active", "white")])
        try:
            self.style.configure("TButton", padding=6)
        except Exception:
            pass

    # ---------- UI Build ----------
    def _build_layout(self):
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        # Left: Controls
        left = ttk.Frame(main, width=300)
        left.pack(side="left", fill="y", padx=(16, 8), pady=16)
        left.pack_propagate(False)

        # Right: Canvas / background
        self.right = ttk.Frame(main)
        self.right.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)
        self.right.bind("<Configure>", self._on_resize)

        # Background area for vibes (scaled label)
        self.bg_width = 560
        self.bg_height = 520
        self.bg_label = ttk.Label(self.right)
        self.bg_label.pack(fill="both", expand=True)

        # Controls
        ttk.Label(left, text="LunarLite Client", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Label(left, text="Theme").pack(anchor="w")
        theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        self.theme_var = theme_var
        row_t = ttk.Frame(left)
        row_t.pack(anchor="w", pady=(2, 8))
        ttk.Radiobutton(row_t, text="Dark", value="dark", variable=theme_var,
                        command=lambda: self._on_theme_change("dark")).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(row_t, text="Light", value="light", variable=theme_var,
                        command=lambda: self._on_theme_change("light")).pack(side="left")

        ttk.Separator(left).pack(fill="x", pady=6)

        ttk.Label(left, text="Version Type").pack(anchor="w")
        self.version_type = tk.StringVar(value=self.settings.get("version_type", "release"))
        ttk.Combobox(left, textvariable=self.version_type, values=["release", "snapshot"], state="readonly",
                     width=16).pack(anchor="w", pady=(2, 6))

        btn_row = ttk.Frame(left); btn_row.pack(anchor="w")
        ttk.Button(btn_row, text="Refresh Versions", command=self.refresh_versions).pack(side="left")
        ttk.Button(btn_row, text="Install Selected", command=self.install_selected).pack(side="left", padx=(8, 0))

        ttk.Label(left, text="Select Version").pack(anchor="w", pady=(8, 2))
        self.versions_combo = ttk.Combobox(left, width=26, state="readonly")
        self.versions_combo.pack(anchor="w", pady=(0, 8))
        if self.settings.get("version"):
            self.versions_combo.set(self.settings["version"])

        self.use_optifine = tk.BooleanVar(value=bool(self.settings.get("use_optifine", False)))
        ttk.Checkbutton(left, text="Use OptiFine (if installed)", variable=self.use_optifine,
                        command=self._on_optifine_toggle).pack(anchor="w", pady=(0, 4))
        ttk.Button(left, text="Install / Detect OptiFine", command=self.install_or_detect_optifine).pack(anchor="w")

        ttk.Separator(left).pack(fill="x", pady=6)

        ttk.Label(left, text="Username (Offline)").pack(anchor="w")
        self.offline_username = tk.Entry(left)
        self.offline_username.pack(anchor="w", fill="x", pady=(2, 6))
        self.offline_username.insert(0, self.settings.get("offline_username", "Player"))

        ttk.Label(left, text="Ely.by Username/Email").pack(anchor="w")
        self.ely_user = tk.Entry(left)
        self.ely_user.pack(anchor="w", fill="x", pady=(2, 6))
        self.ely_user.insert(0, self.settings.get("elyby_user", ""))

        ttk.Label(left, text="Ely.by Password").pack(anchor="w")
        self.ely_pass = tk.Entry(left, show="*")
        self.ely_pass.pack(anchor="w", fill="x", pady=(2, 8))

        btn_row2 = ttk.Frame(left); btn_row2.pack(anchor="w")
        ttk.Button(btn_row2, text="Login & Launch (Online)", style="Accent.TButton",
                   command=self.login_and_launch).pack(side="left")
        ttk.Button(btn_row2, text="Launch (Offline)", style="Accent.TButton",
                   command=self.launch_offline).pack(side="left", padx=(8, 0))

        ttk.Separator(left).pack(fill="x", pady=6)

        # Skin preview / picker
        ttk.Label(left, text="Skin (PNG, 64x64 or 64x32)").pack(anchor="w")
        row_s = ttk.Frame(left); row_s.pack(anchor="w", fill="x")
        self.skin_path_var = tk.StringVar(value=self.settings.get("skin_path", ""))
        skin_entry = ttk.Entry(row_s, textvariable=self.skin_path_var, width=22)
        skin_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row_s, text="Browse", command=self.pick_skin).pack(side="left", padx=(6, 0))
        ttk.Button(row_s, text="Fetch Ely", command=self.fetch_ely_skin).pack(side="left", padx=(6, 0))

        self.skin_preview = ttk.Label(left)
        self.skin_preview.pack(anchor="w", pady=(6, 4))
        self._refresh_skin_preview()

        ttk.Separator(left).pack(fill="x", pady=6)

        ttk.Label(left, text="Pygame FPS Target").pack(anchor="w")
        self.fps_scale = tk.Scale(left, from_=60, to=240, orient="horizontal",
                                  command=self._on_fps_change, showvalue=True, length=220)
        self.fps_scale.set(int(self.settings.get("fps_target", 120)))
        self.fps_scale.pack(anchor="w", pady=(2, 6))

        self.status = ttk.Label(left, text="Ready", wraplength=240)
        self.status.pack(anchor="w", pady=(4, 2))

        self.fps_label = ttk.Label(left, text="BG: 0 fps")
        self.fps_label.pack(anchor="w")

        note = ("Offline: singleplayer/cracked servers. Online: Ely.by for skins/premium servers.\n"
                "OptiFine: install once, then toggle. Local skins need a mod like CustomSkinLoader.")
        ttk.Label(left, text=note, wraplength=260).pack(anchor="w", pady=(4, 0))

    def _on_resize(self, event):
        if self.vibes:
            self.vibes.update_size((event.width, event.height))

    # ---------- Events ----------
    def _on_theme_change(self, theme: str):
        self.apply_theme(theme)
        self.settings["theme"] = theme
        save_settings(self.settings)

    def _on_optifine_toggle(self):
        self.settings["use_optifine"] = bool(self.use_optifine.get())
        save_settings(self.settings)

    def _on_fps_change(self, val):
        v = int(float(val))
        self.settings["fps_target"] = v
        save_settings(self.settings)
        if self.vibes:
            self.vibes.target_fps = v

    def set_status(self, text: str):
        self.ui.call(self.status.configure, text=text)

    # ---------- Skin ----------
    def pick_skin(self):
        p = filedialog.askopenfilename(
            title="Select Skin PNG",
            filetypes=[("PNG Image", "*.png"), ("All files", "*.*")]
        )
        if not p:
            return
        self.skin_path_var.set(p)
        self.settings["skin_path"] = p
        save_settings(self.settings)
        self._refresh_skin_preview()

    def fetch_ely_skin(self):
        user = self.ely_user.get().strip()
        if not user:
            messagebox.showerror("Ely.by", "Enter Ely.by username first.")
            return
        if requests is None:
            messagebox.showerror("Error", "The package 'requests' is not installed.\n\nInstall it:\n  pip install requests")
            return
        url = f"https://skin.ely.by/{user}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            temp_path = os.path.join(MC_DIR, f"{user}_skin.png")
            with open(temp_path, "wb") as f:
                f.write(resp.content)
            self.skin_path_var.set(temp_path)
            self.settings["skin_path"] = temp_path
            save_settings(self.settings)
            self._refresh_skin_preview()
        except Exception as e:
            messagebox.showerror("Skin Fetch", f"Failed to fetch skin: {e}")

    def _refresh_skin_preview(self):
        if not Image:
            return
        p = self.skin_path_var.get().strip()
        if not p or not os.path.exists(p):
            self.ui.call(self.skin_preview.configure, image="", text="(No local skin selected)")
            self.skin_preview.image = None
            return
        try:
            im = Image.open(p).convert("RGBA")
            im = im.resize((64, 64), Image.NEAREST)
            ph = ImageTk.PhotoImage(im)
            self.skin_preview.image = ph
            self.ui.call(self.skin_preview.configure, image=ph, text="")
        except Exception:
            self.ui.call(self.skin_preview.configure, image="", text="(Skin preview failed)")
            self.skin_preview.image = None

    # ---------- Versions ----------
    def refresh_versions(self, initial=False):
        vt = self.version_type.get()
        self.set_status("Fetching versions...")
        def task():
            items = get_versions(vt)
            def done():
                self.versions_combo["values"] = items
                if initial and self.settings.get("version") in items:
                    self.versions_combo.set(self.settings["version"])
                elif items:
                    self.versions_combo.set(items[0])
                self.set_status("Versions refreshed" if items else "No versions found")
            self.ui.call(done)
        threading.Thread(target=task, daemon=True).start()

    def install_selected(self):
        version = self.versions_combo.get()
        if not version:
            messagebox.showerror("Error", "Select a version first!")
            return
        self.set_status(f"Installing {version}...")
        def task():
            cb = self._progress_callback()
            install_version(version, cb)
            self.set_status(f"Installed {version}")
        threading.Thread(target=task, daemon=True).start()

    # ---------- OptiFine ----------
    def install_or_detect_optifine(self):
        version = self.versions_combo.get()
        if not version:
            messagebox.showerror("OptiFine", "Select a base version first.")
            return
        # Detect
        of = find_installed_optifine_versions(version)
        if of:
            messagebox.showinfo("OptiFine", "Detected OptiFine versions:\n" + "\n".join(of))
            return
        # Install
        self.set_status("Installing OptiFine (best-effort)...")
        def task():
            ok = best_effort_install_optifine(version)
            if ok:
                self.set_status("OptiFine installed or scheduled by its installer.")
            else:
                self.set_status("OptiFine installation skipped/failed.")
        threading.Thread(target=task, daemon=True).start()

    # ---------- Launch ----------
    def login_and_launch(self):
        if requests is None:
            messagebox.showerror("Error", "Install 'requests' to use Ely.by online mode.")
            return
        version = self._resolve_version_with_optifine()
        if not version:
            return
        username = self.ely_user.get().strip()
        password = self.ely_pass.get()
        if not username or not password:
            messagebox.showerror("Ely.by", "Enter Ely.by username/email and password.")
            return

        self._persist_common(version)

        def task():
            self.set_status("Logging in to Ely.by...")
            auth = authenticate_elyby(username, password)
            if not auth:
                self.set_status("Ely.by auth failed.")
                return
            self.set_status(f"Ensuring Java for {version}...")
            if not ensure_java(version):
                self.set_status("Java check failed.")
                return
            cmd = build_launch_cmd(version, auth["username"], auth["access_token"], auth["uuid"])
            if not cmd:
                self.set_status("Failed to build launch command.")
                return
            self.set_status(f"Launching Minecraft {version}...")
            try:
                subprocess.Popen(cmd)
                self.set_status("Minecraft launched (online).")
            except Exception as e:
                messagebox.showerror("Launch", f"Failed to launch:\n{e}")
                self.set_status("Launch failed.")
        threading.Thread(target=task, daemon=True).start()

    def launch_offline(self):
        version = self._resolve_version_with_optifine()
        if not version:
            return
        username = self.offline_username.get().strip() or "Player"
        self._persist_common(version)

        def task():
            self.set_status(f"Ensuring Java for {version}...")
            if not ensure_java(version):
                self.set_status("Java check failed.")
                return
            cmd = build_launch_cmd(version, username)
            if not cmd:
                self.set_status("Failed to build launch command.")
                return
            self.set_status(f"Launching Minecraft {version} (offline)...")
            try:
                subprocess.Popen(cmd)
                self.set_status("Minecraft launched (offline).")
            except Exception as e:
                messagebox.showerror("Launch", f"Failed to launch:\n{e}")
                self.set_status("Launch failed.")
        threading.Thread(target=task, daemon=True).start()

    def _resolve_version_with_optifine(self) -> Optional[str]:
        base = self.versions_combo.get()
        if not base:
            messagebox.showerror("Error", "Select a version first!")
            return None
        self.settings["version_type"] = self.version_type.get()
        if self.use_optifine.get():
            ofv = find_installed_optifine_versions(base)
            if ofv:
                chosen = ofv[0]
                self.set_status(f"Using OptiFine profile: {chosen}")
                return chosen
            else:
                messagebox.showwarning("OptiFine",
                                       "OptiFine is toggled on but not detected for this version.\n"
                                       "Click 'Install / Detect OptiFine' first, or uncheck the option.")
                return None
        return base

    def _persist_common(self, version: str):
        self.settings["offline_username"] = self.offline_username.get().strip() or "Player"
        self.settings["elyby_user"] = self.ely_user.get().strip()
        self.settings["version"] = version
        self.settings["theme"] = self.theme
        self.settings["use_optifine"] = bool(self.use_optifine.get())
        save_settings(self.settings)

    # ---------- Progress callback ----------
    def _progress_callback(self):
        def set_progress(v):
            self.set_status(f"Downloading... {int(v)}/{int(max_value or 100)}")
        def set_max(m):
            nonlocal max_value
            max_value = m
        def set_status(s):
            self.set_status(s)
        max_value = 100
        return {"setProgress": set_progress, "setMax": set_max, "setStatus": set_status}

    # ---------- Housekeeping ----------
    def _update_fps_label(self):
        if self.vibes:
            self.fps_label.configure(text=f"BG: {self.vibes.fps:.0f} fps")
        self.root.after(250, self._update_fps_label)

def main():
    app = LunarLiteApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
