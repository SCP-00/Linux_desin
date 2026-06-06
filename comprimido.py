#!/usr/bin/env python3
"""
KALI LINUX WORKSPACE GENERATOR
Genera toda la configuracion de Kali Linux + GNOME + NVIDIA + Seguridad
Uso: python3 comprimido.py  -> genera kali-linux-workspace.zip
"""

import os
import zipfile
from pathlib import Path

REPO_NAME = "kali-linux-workspace"
ZIP_NAME = "kali-linux-workspace.zip"

files_content = {}

# =============================================================================
# 1. README.md
# =============================================================================
files_content["README.md"] = """# Kali Linux Workspace — Hacking, IA y Ricing GNOME

Configuracion completa para **Kali Linux 2026.2 + GNOME 49 + Wayland**, optimizada para
graficos hibridos **Intel + NVIDIA RTX 3050** con **CUDA 12.4**.

## Hardware
| Componente | Especificacion |
|------------|---------------|
| CPU | Intel Core i5-13420H |
| GPU | NVIDIA GeForce RTX 3050 6GB GDDR6 |
| RAM | 32 GB |
| Disco | 954 GB NVMe |
| SO | Kali Linux 2026.2 |

## Dual-Boot
- Windows 11 + Kali Linux via GRUB
- Boot order: Kali -> Windows -> USB -> DVD -> Network
- Timeout: 10s

## Componentes instalados

### NVIDIA
- Driver propietario 550.163.01
- CUDA 12.4
- DKMS compilado (nvidia-current)
- Modo hibrido Intel+NVIDIA

### Seguridad (tmux + ZSH)
- `~/.tmux.conf`: Historial 50k, proteccion de sesiones, atajos para hacking
- `~/.zsh_custom/safety.zsh`: Protege Codebuff contra kills, wrappers para comandos peligrosos
- Comandos protegidos: `kill`, `pkill`, `killall`, `exit`, `logout`, `shutdown`, `reboot`, `systemctl`
- `danger <comando>`: Ejecuta cualquier comando en tmux aislado
- `tmux-hack`: Abre sesion tmux con 3 ventanas para pentesting

### Atajos de Teclado
| Atajo | Accion |
|-------|--------|
| Super+P | Ciclar modos de pantalla (Extend/Mirror/Internal/External) |
| Super+E | Abrir explorador de archivos (Nautilus) |
| Super+T | Terminal |
| Ctrl+Alt+T | Terminal alternativo |

### IA Local
- Docker Compose con Ollama + Open WebUI
- GPU Passthrough (CUDA)
- Modelos recomendados: llama3.2:3b, qwen2.5-coder:3b

## Estructura
```
kali-linux-workspace/
  README.md
  env/
    setup_nvidia_kali.sh     # Instalacion NVIDIA para Kali/Debian
    toggle_performance.sh    # Alternar rendimiento/estetico
    uefi_grub.sh            # Configuracion dual-boot
  scripts/
    gnome-cycle-display.py   # Super+P: ciclar modos de pantalla
    safety.zsh              # Proteccion de procesos criticos
    tmux.conf               # Configuracion tmux
  docker/
    docker-compose.yml      # Ollama + Open WebUI
    agent_test.py           # Test AutoGen
```

## Quick Start
```bash
# 1. NVIDIA Driver
sudo bash env/setup_nvidia_kali.sh

# 2. Seguridad tmux
cp scripts/tmux.conf ~/.tmux.conf
mkdir -p ~/.zsh_custom
cp scripts/safety.zsh ~/.zsh_custom/
echo 'if [[ -f ~/.zsh_custom/safety.zsh ]]; then source ~/.zsh_custom/safety.zsh; fi' >> ~/.zshrc

# 3. Display Cycling (Super+P)
mkdir -p ~/.local/bin
cp scripts/gnome-cycle-display.py ~/.local/bin/
chmod +x ~/.local/bin/gnome-cycle-display.py

# 4. Docker IA
cd docker && docker compose up -d

# 5. Dual-boot
sudo bash env/uefi_grub.sh
```
"""

# =============================================================================
# 2. setup_nvidia_kali.sh
# =============================================================================
files_content["env/setup_nvidia_kali.sh"] = """#!/usr/bin/env bash
# Configuracion de NVIDIA para Kali Linux (basado en Debian/testing)
# Uso: sudo bash setup_nvidia_kali.sh

set -e

echo "[*] Instalando driver NVIDIA para Kali Linux..."
sudo apt update
sudo apt install -y nvidia-driver linux-headers-$(uname -r) nvidia-smi

echo "[*] Desactivando nouveau (driver open-source)..."
echo -e "blacklist nouveau\noptions nouveau modeset=0" | sudo tee /etc/modprobe.d/blacklist-nouveau.conf

echo "[*] Configurando parametros del modulo NVIDIA..."
echo -e "options nvidia-drm modeset=1\noptions nvidia NVreg_DynamicPowerManagement=0x02" | sudo tee /etc/modprobe.d/nvidia.conf

echo "[*] Actualizando initramfs..."
sudo update-initramfs -u

echo "[!] Listo.REINICIA el sistema y ejecuta: nvidia-smi"
echo "    Si usas Optimus (hibrido): sudo envycontrol -m nvidia (o integrated/hybrid)"
"""

# =============================================================================
# 3. toggle_performance.sh (GNOME version)
# =============================================================================
files_content["env/toggle_performance.sh"] = """#!/usr/bin/env bash
# Alternar entre modo estetico (animado) y modo rendimiento (ultra-ligero)
# Para GNOME 49+ en Wayland

STATE=$(gsettings get org.gnome.desktop.interface enable-animations)

if [ "$STATE" = "true" ]; then
    # -> MODO RENDIMIENTO
    echo "[*] Activando modo rendimiento maximo..."
    gsettings set org.gnome.desktop.interface enable-animations false
    gsettings set org.gnome.desktop.interface clock-show-seconds false
    gsettings set org.gnome.desktop.wm.preferences button-layout ''
    
    # CPU governor a performance
    echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
    
    # Desactivar blur y effects
    if command -v gnome-extensions &>/dev/null; then
        gnome-extensions disable blur-my-shell@hellorio 2>/dev/null || true
    fi
    
    notify-send -u critical "Rendimiento" "Animaciones OFF | CPU Performance"
else
    # -> MODO ESTETICO
    echo "[*] Activando modo estetico completo..."
    gsettings set org.gnome.desktop.interface enable-animations true
    gsettings set org.gnome.desktop.interface clock-show-seconds true
    gsettings set org.gnome.desktop.wm.preferences button-layout ':minimize,maximize,close'
    
    # CPU governor a powersave
    echo 'powersave' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true
    
    if command -v gnome-extensions &>/dev/null; then
        gnome-extensions enable blur-my-shell@hellorio 2>/dev/null || true
    fi
    
    notify-send "Estetico" "Animaciones ON | Blur activado"
fi
"""

# =============================================================================
# 4. uefi_grub.sh - Dual-boot Windows + Kali
# =============================================================================
files_content["env/uefi_grub.sh"] = """#!/usr/bin/env bash
# Configurar GRUB para dual-boot Windows 11 + Kali Linux
# Uso: sudo bash uefi_grub.sh

set -e

echo "[*] Instalando os-prober..."
sudo apt install -y os-prober

echo "[*] Configurando GRUB timeout 10s..."
sudo sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=10/' /etc/default/grub 2>/dev/null || true
sudo sed -i 's/^#GRUB_DISABLE_OS_PROBER=false/GRUB_DISABLE_OS_PROBER=false/' /etc/default/grub 2>/dev/null || true
echo 'GRUB_DISABLE_OS_PROBER=false' | sudo tee -a /etc/default/grub 2>/dev/null

echo "[*] Actualizando GRUB..."
sudo update-grub

echo "[*] Configurando boot order: Kali -> Windows -> USB..."
# Obtener entradas UEFI
KALI_BOOT=$(efibootmgr | grep -i kali | grep -oP 'Boot\\\\K\\d+' | head -1 || echo "0006")
WIN_BOOT=$(efibootmgr | grep -i "Windows Boot" | grep -oP 'Boot\\K\\d+' | head -1 || echo "0003")
sudo efibootmgr -o ${KALI_BOOT},${WIN_BOOT},2001,2002,2003

echo "[+] Listo. Al reiniciar veras:"
echo "   1. Kali Linux (default, 10s)"
echo "   2. Windows Boot Manager"
echo "   3. UEFI Firmware Settings"
sudo efibootmgr -v | grep -E 'Boot[0-9]|BootOrder'
"""

# =============================================================================
# 5. gnome-cycle-display.py (Super+P)
# =============================================================================
files_content["scripts/gnome-cycle-display.py"] = """#!/usr/bin/env python3
# GNOME Display Cycler - Super+P como Windows

import subprocess, re, sys, os

# STATE_FILE disabled - not needed with D-Bus state detection

def get_state():
    r = subprocess.run(["gdbus", "call", "--session",
        "--dest", "org.gnome.Mutter.DisplayConfig",
        "--object-path", "/org/gnome/Mutter/DisplayConfig",
        "--method", "org.gnome.Mutter.DisplayConfig.GetCurrentState"
    ], capture_output=True, text=True, timeout=10)
    return r.stdout

def notify(msg):
    subprocess.run(["notify-send", "Display Mode", msg], capture_output=True, timeout=5)

def _is_internal(c):
    return c.startswith("eDP") or c.startswith("LVDS")

def parse_state(raw):
    m = re.search(r"uint32 (\\d+)", raw)
    serial = int(m.group(1)) if m else 1
    sections = re.split(r"\\(\\('\"", raw)[1:]
    connectors, conn_modes = [], {}
    for sec in sections:
        conn = sec.split("'", 1)[0] if "'" in sec else ""
        if not conn or not re.match(r"[A-Za-z]+-\\d+", conn):
            continue
        connectors.append(conn)
        sub = sec[:2000]
        mod = re.search(r"'(\\d+x\\d+@[\\d.]+)'.*?is-current.*?true", sub, re.DOTALL)
        if not mod:
            mod = re.search(r"'(\\d+x\\d+@[\\d.]+)'.*?is-preferred.*?true", sub, re.DOTALL)
        if mod:
            conn_modes[conn] = mod.group(1)

    internal = [c for c in connectors if _is_internal(c)]
    external = [c for c in connectors if c not in internal]
    if not external:
        return serial, connectors, conn_modes, "internal"

    phys_end = raw.rfind("is-builtin")
    if phys_end < 0:
        phys_end = raw.rfind("layout-mode")
    if phys_end < 0:
        phys_end = len(raw) // 2
    logical_part = raw[phys_end:]

    lm = re.findall(r", (\\d+), ([\\d.]+), \\d+, (true|false), \\[\\(\\'\"", logical_part)
    if len(lm) >= 2:
        current = "extend"
    elif len(lm) == 1:
        x, scale, ip = lm[0]
        needle = f"{x}, {scale}, 0, {ip}, [('"
        pos = logical_part.find(needle)
        if pos >= 0:
            chunk = logical_part[pos:pos+3000]
            has_int = any(c in chunk for c in internal)
            has_ext = any(c in chunk for c in external)
            current = "mirror" if (has_int and has_ext) else ("external" if has_ext else "internal")
        else:
            current = "internal"
    else:
        current = "internal"
    return serial, connectors, conn_modes, current

def build_config(mode, connectors, conn_modes):
    internal = [c for c in connectors if _is_internal(c)]
    external = [c for c in connectors if c not in internal]
    def mf(c): return conn_modes.get(c, "1920x1080@60")

    if mode == "internal":
        c = (internal or connectors[:1])[0]
        return f"[(0, 0, 1.0, 0, true, [('{c}', '{mf(c)}', {{}})])]"
    elif mode == "external":
        if not external: return None
        ps = [f"('{c}', '{mf(c)}', {{}})" for c in external]
        return f"[(0, 0, 1.0, 0, true, [{', '.join(ps)}])]"
    elif mode == "mirror":
        ps = [f"('{c}', '{mf(c)}', {{}})" for c in connectors]
        return f"[(0, 0, 1.0, 0, true, [{', '.join(ps)}])]"
    elif mode == "extend":
        ps, x = [], 0
        for i, c in enumerate(connectors):
            mn = mf(c)
            ps.append(f"({x}, 0, 1.0, 0, {'true' if i==0 else 'false'}, [('{c}', '{mn}', {{}})])")
            wm = re.match(r"(\\d+)x", mn)
            x += int(wm.group(1)) if wm else 1920
        return "[" + ", ".join(ps) + "]"
    return None

def apply_config(serial, config_str):
    if config_str is None: return False
    cmd = ["gdbus", "call", "--session", "--dest", "org.gnome.Mutter.DisplayConfig",
        "--object-path", "/org/gnome/Mutter/DisplayConfig",
        "--method", "org.gnome.Mutter.DisplayConfig.ApplyMonitorsConfig",
        str(serial), "2", f"@a(iiduba(ssa{{sv}})) {config_str}", "@a{sv} {}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return r.returncode == 0

def main():
    try: raw = get_state()
    except Exception as e: notify(f"Error: {e}"); sys.exit(1)
    serial, connectors, conn_modes, current = parse_state(raw)
    if not connectors: notify("No se detectaron monitores"); sys.exit(1)
    external = [c for c in connectors if not _is_internal(c)]
    if not external:
        apply_config(serial, build_config("internal", connectors, conn_modes))
        notify("Solo monitor interno")
        return
    modes = ["extend", "mirror", "internal", "external"]
    try: idx = modes.index(current)
    except ValueError: idx = 0
    next_mode = modes[(idx+1)%len(modes)]
    config = build_config(next_mode, connectors, conn_modes)
    if config is None:
        ni = (modes.index(next_mode)+1)%len(modes)
        while ni != (idx+1)%len(modes):
            next_mode = modes[ni]
            config = build_config(next_mode, connectors, conn_modes)
            if config: break
            ni = (ni+1)%len(modes)
    ok = apply_config(serial, config)
    labels = {"extend":"Extendido", "mirror":"Duplicado", "internal":"Solo Interno", "external":"Solo Externo"}
    notify(f"Pantalla: {labels.get(next_mode,next_mode)}" if ok else "Error al cambiar modo")
    # State persistence handled by Mutter D-Bus

if __name__ == "__main__": main()
"""

# =============================================================================
# 6. safety.zsh
# =============================================================================
files_content["scripts/safety.zsh"] = """# SAFETY.ZSH - Proteccion de procesos criticos y comandos peligrosos
# Cargar desde .zshrc: source ~/.zsh_custom/safety.zsh

[[ -n "$_SAFETY_LOADED" ]] && return 0
export _SAFETY_LOADED=1

CODECRITICAL_PROCESSES=("codebuff" "buffy" "node.*codebuff")

_is_codebuff() {
    local s="$1"; [[ -z "$s" ]] && return 1
    for p in "${CODECRITICAL_PROCESSES[@]}"; do
        if echo "$s" | grep -qiE "(^|[^a-zA-Z])$p([^a-zA-Z]|$)"; then return 0; fi
    done
    return 1
}

_shutdown_warning() {
    local cmd="$1"
    echo ""
    echo "[SEGURIDAD] Estas a punto de ejecutar: $cmd"
    if [[ -n "$TMUX" ]]; then
        echo "  (Estas DENTRO de tmux - ejecucion segura)"
        return 0
    fi
    echo "  [1] Si, ejecutar dentro de tmux (recomendado)"
    echo "  [2] Si, ejecutar aqui directamente"
    echo "  [3] Cancelar"
    read -r "sel?Selecciona [1-3]: "
    case "$sel" in
        1) danger "$cmd"; return 1 ;;
        2) return 0 ;;
        *) return 1 ;;
    esac
}

# --- WRAPPERS DE SEGURIDAD ---

exit() {
    if [[ -z "$TMUX" ]]; then
        echo "[SEGURIDAD] 'exit' fuera de tmux cerrara la sesion."
        echo "  Escribe 'exit' de nuevo para confirmar, o Ctrl+C para cancelar."
        read -r "confirm?Confirmar (s/N): "
        [[ "$confirm" =~ ^[Ss]$ ]] || return 1
    fi
    builtin exit "$@"
}

logout() {
    _shutdown_warning "logout" || return 1
    builtin logout
}

kill() {
    local all_args="$*"
    local target_pids=()
    for arg in "$@"; do
        [[ "$arg" =~ ^[0-9]+$ ]] && target_pids+=("$arg")
    done
    for pid in "${target_pids[@]}"; do
        local proc_name=$(ps -p "$pid" -o comm= 2>/dev/null)
        local full_cmd=$(ps -p "$pid" -o args= 2>/dev/null)
        if _is_codebuff "$proc_name" || _is_codebuff "$full_cmd"; then
            echo "[SEGURIDAD] BLOQUEADO: No puedes matar Codebuff (PID: $pid)"
            return 1
        fi
    done
    if echo " $all_args " | grep -qE ' (-9| -KILL| -SIGKILL)'; then
        echo "[SEGURIDAD] Estas usando kill -9. Confirmar?"
        read -r "confirm?Confirmar (s/N): "
        [[ "$confirm" =~ ^[Ss]$ ]] || return 1
    fi
    command kill "$@"
}

pkill() {
    for arg in "$@"; do
        if _is_codebuff "$arg"; then
            echo "[SEGURIDAD] BLOQUEADO: No puedes matar Codebuff"
            return 1
        fi
    done
    command pkill "$@"
}

killall() {
    for arg in "$@"; do
        if _is_codebuff "$arg"; then
            echo "[SEGURIDAD] BLOQUEADO: No puedes matar Codebuff"
            return 1
        fi
    done
    command killall "$@"
}

shutdown() { _shutdown_warning "shutdown $*" || return 1; command shutdown "$@"; }
reboot() { _shutdown_warning "reboot $*" || return 1; command reboot "$@"; }
poweroff() { _shutdown_warning "poweroff $*" || return 1; command poweroff "$@"; }
halt() { _shutdown_warning "halt $*" || return 1; command halt "$@"; }

systemctl() {
    local has_danger=0
    for arg in "$@"; do
        case "$arg" in
            poweroff|reboot|halt|shutdown|emergency|rescue) has_danger=1 ;;
        esac
    done
    [[ $has_danger -eq 1 ]] && { _shutdown_warning "systemctl $*" || return 1; }
    command systemctl "$@"
}

init() {
    case "$1" in
        0|6|reboot|poweroff) _shutdown_warning "init $*" || return 1 ;;
    esac
    command init "$@"
}

# --- FUNCIONES TMUX ---
danger() {
    if ! command -v tmux &>/dev/null; then echo "tmux no instalado"; return 1; fi
    local session_name="danger_$(date +%s)"
    tmux new-session -d -s "$session_name" "$*; echo ''; echo 'Sesion terminada. Presiona Enter para cerrar.'; read"
    tmux attach-session -t "$session_name"
}

tmux-hack() {
    if ! command -v tmux &>/dev/null; then echo "tmux no instalado"; return 1; fi
    local s="hack_$(date +%H%M%S)"
    tmux new-session -d -s "$s" -n "shell"
    tmux new-window -t "$s" -n "scan"
    tmux new-window -t "$s" -n "exploit"
    tmux select-window -t "$s:0"
    tmux attach-session -t "$s"
}

in_tmux() { [[ -n "$TMUX" ]] && return 0 || return 1; }

check-codebuff() {
    local found=0
    echo "=== Verificando procesos Codebuff ==="
    for proc in "${CODECRITICAL_PROCESSES[@]}"; do
        for pid in $(pgrep -f "$proc" 2>/dev/null); do
            echo "  [ACTIVO] $proc - PID: $pid"
            ps -p $pid -o pid,user,lstart,args --no-headers 2>/dev/null
            found=1
        done
    done
    [[ $found -eq 0 ]] && echo "  No hay procesos Codebuff activos."
    echo ""
    echo "=== Sesiones tmux ==="
    tmux list-sessions 2>/dev/null || echo "  No hay sesiones activas"
}

# Mensaje de bienvenida
if pgrep -f "codebuff|buffy" > /dev/null 2>&1; then
    echo "[SEGURIDAD] Codebuff detectado - protegido contra kills"
fi
"""

# =============================================================================
# 7. tmux.conf
# =============================================================================
files_content["scripts/tmux.conf"] = """# TMUX CONFIG - Kali Linux 2026
# Seguridad: proteger sesiones y procesos criticos

# Prefijo
set -g prefix C-b
unbind C-b
bind C-b send-prefix

# Mouse
set -g mouse on

# Historia
set -g history-limit 50000

# Apariencia
set -g default-terminal "tmux-256color"
set -ga terminal-overrides ",xterm-256color:Tc"
set -g status-bg colour235
set -g status-fg white
set -g status-left "#[fg=green] #S #[default]"
set -g status-right "#[fg=yellow] %Y-%m-%d #[fg=cyan] %H:%M #[default]"
set -g window-status-format " #I:#W "
set -g window-status-current-format " #[fg=black,bg=cyan] #I:#W #[default]"
set -g pane-active-border-style "fg=cyan"
set -g pane-border-style "fg=colour240"
set -g escape-time 10

# Scroll como Vim
set -g mode-keys vi
bind -T copy-mode-vi v send-keys -X begin-selection
bind -T copy-mode-vi y send-keys -X copy-selection-and-cancel
bind -T copy-mode-vi Escape send-keys -X cancel

# Keybindings
bind r source-file ~/.tmux.conf \\; display "Config reloaded!"
bind | split-window -h
bind - split-window -v
bind H previous-window
bind L next-window
bind -r C-h select-pane -L
bind -r C-j select-pane -D
bind -r C-k select-pane -U
bind -r C-l select-pane -R
bind -n M-1 select-window -t 1
bind -n M-2 select-window -t 2
bind -n M-3 select-window -t 3

# Confirmacion antes de matar
bind k confirm-before -p "kill-pane #P? (y/n)" kill-pane
bind X confirm-before -p "kill-window #W? (y/n)" kill-window

# Lock screen
bind C-l lock-server

# Logging
bind P pipe-pane -o "exec cat >> ~/.tmux/logs/#S_#I_#W_$(date +%Y%m%d).log" \\; display "Logging toggled"

# Atajos hacking
bind S new-window -n "nmap" "sudo nmap -sV"
bind R new-window -n "responder" "sudo responder -I eth0"
bind N new-window -n "netcat" "nc -lvnp"
"""

# =============================================================================
# 8. docker-compose.yml
# =============================================================================
files_content["docker/docker-compose.yml"] = """version: '3.8'

services:
  ollama:
    container_name: ollama-service
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_storage:/root/.ollama
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  open-webui:
    container_name: open-webui-service
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - webui_storage:/app/backend/data
    depends_on:
      - ollama
    restart: unless-stopped

volumes:
  ollama_storage:
  webui_storage:
"""

# =============================================================================
# 9. agent_test.py (AutoGen)
# =============================================================================
files_content["docker/agent_test.py"] = """#!/usr/bin/env python3
# Test de agentes IA locales con AutoGen + Ollama + CUDA

import os
from pathlib import Path

try:
    from autogen import AssistantAgent, UserProxyAgent
    from autogen.coding import LocalCommandLineCodeExecutor
except ImportError:
    print("[!] pip install pyautogen[ollama]")
    exit(1)

config_list = [{
    "model": "llama3.2:3b",
    "base_url": "http://localhost:11434/v1",
    "api_type": "ollama",
}]

print("[*] Usando GPU NVIDIA con CUDA 12.4")
workdir = Path("workspace")
workdir.mkdir(exist_ok=True)

executor = LocalCommandLineCodeExecutor(work_dir=workdir)

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: "FIN" in x.get("content", ""),
    code_execution_config={"executor": executor},
)

assistant = AssistantAgent(
    name="AgenticCoder",
    system_message="Eres un experto en Python. Escribe codigo limpio. Para finalizar di FIN.",
    llm_config={"config_list": config_list},
)

user_proxy.initiate_chat(
    assistant,
    message="Escribe un script Python que descargue precios de BTC de una API publica, calcule el maximo y termine."
)
"""

# =============================================================================
# GENERADOR
# =============================================================================
def create_workspace_and_zip():
    print(f"[*] Creando estructura en ./{REPO_NAME}...")
    for filepath, content in files_content.items():
        full_path = Path(REPO_NAME) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        if filepath.endswith(".sh") or filepath.endswith(".py") or "/scripts/" in filepath:
            os.chmod(full_path, 0o755)
    print(f"[+] {len(files_content)} archivos creados.")
    print(f"[*] Comprimiendo en {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(REPO_NAME):
            for file in files:
                file_path = Path(root) / file
                archive_name = file_path.relative_to(REPO_NAME)
                zipf.write(file_path, archive_name)
    print(f"[✓] {ZIP_NAME} generado con exito!")

if __name__ == "__main__":
    create_workspace_and_zip()
