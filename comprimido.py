import os
import zipfile
from pathlib import Path

# Nombre de la carpeta raíz del repositorio
REPO_NAME = "linux-workspace-repo"
ZIP_NAME = "linux-workspace-repo.zip"

# Definición del contenido de los archivos de configuración recomendados
files_content = {}

# 1. README.md
files_content = """# Estación de Trabajo Linux Personalizada: Hacking Ético, IA Agéntica y Ricing Premium

Este repositorio consolida la configuración de bajo nivel y el entorno de usuario para una estación de trabajo optimizada en Arch Linux, diseñada específicamente para laptops con gráficos híbridos Nvidia RTX 3050.

## 🚀 Componentes Principales y Enlaces Recomendados

Para lograr la experiencia visual inmersiva, fluida y controlada mediante el teclado que buscas, debes clonar e instalar los siguientes repositorios de la comunidad sobre esta base limpia:

1. **Entorno Visual de Usuario (Rice Premium)**: 
   - [end-4/dots-hyprland](https://github.com/end-4/dots-hyprland): El "rice" de nivel experto por excelencia para Hyprland. Gestiona el compositor mediante una interfaz interactiva de alta fidelidad estética basada en Material Design 3.
   -(https://github.com/Jas-SinghFSU/HyprPanel): Una barra de estado y panel de control altamente personalizable con soporte directo para métricas Nvidia.
2. **Lanzadores y Menús Temáticos**:
   - [adi1090x/rofi](https://github.com/adi1090x/rofi): Colección masiva de menús personalizados, applets y diseños circulares/radiales para Rofi.
3. **Menú de Energía Circular Avanzado (Estilo Donut)**:
   -(https://github.com/Sleep-No-More/SNMenu): Un powermenu circular moderno con soporte para submenús escrito en Rust y Cairo para animaciones fluidas a 60 FPS.
4. **Gestor de Gráficos Híbridos**:
   - [bayasdev/envycontrol](https://github.com/bayasdev/envycontrol): Utilidad ligera CLI para conmutar modos de GPU (Integrated, Hybrid, Nvidia) sin daemons activos en segundo plano.

---

## 🛠️ Estructura del Repositorio

- `env/setup_nvidia.sh`: Script de configuración de controladores propietarios Nvidia y carga temprana de KMS.
- `scripts/toggle_performance.sh`: Script para conmutar de inmediato entre el perfil súper animado (Estético) y el modo de rendimiento ultra-ligero.
- `scripts/rofi-ai-assistant.sh`: Lanzador Rofi integrado con Ollama local para consultas instantáneas en una ventana de Kitty flotante.
- `snmenu/layout.json`: Configuración circular personalizada para SNMenu con soporte para submenús estéticos.
- `distrobox/create_kali.sh`: Despliegue seguro y aislado de Kali Linux mediante Distrobox.
- `docker/docker-compose.yml`: Infraestructura de Docker para levantar Ollama y Open-WebUI con passthrough de GPU Nvidia (CUDA).
- `docker/agent_test.py`: Script de prueba de desarrollo agéntico local utilizando la librería AutoGen y Ollama.

---

## 💻 Requisitos de Memoria para Agentes de IA en GPU de 4GB
Para evitar errores de falta de memoria (Out of Memory), el consumo proyectado de la VRAM debe respetar el límite matemático:
$M_{\\text{VRAM}}\\approx\\frac{P\\times{Q}}{8}\\times{1.25}$

Donde:
- $P$ es el número de parámetros del modelo (en Billions).
- $Q$ es la cuantización en bits (por ejemplo, 4 o 5 bits para el balance óptimo).
- El factor $1.25$ estima la sobrecarga de contexto y caché KV.

*Modelos recomendados*: `qwen2.5-coder:3b` para programación local agéntica y `llama3.2:3b` para orquestación de flujos.
"""

# 2. setup_nvidia.sh
files_content["env/setup_nvidia.sh"] = """#!/usr/bin/env bash
# Script para configurar controladores Nvidia en Arch Linux con carga KMS y manejo de suspensión profunda.

echo "[*] Instalando controladores propietarios de Nvidia..."
sudo pacman -S --needed nvidia-dkms nvidia-utils lib32-nvidia-utils egl-wayland libva-nvidia-driver

echo "[*] Configurando carga temprana de módulos (Early KMS) en /etc/mkinitcpio.conf..."
if! grep -q "nvidia" /etc/mkinitcpio.conf; then
    sudo sed -i 's/MODULES=(/MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm /' /etc/mkinitcpio.conf
fi

echo "[*] Regenerando el initramfs..."
sudo mkinitcpio -P

echo "[*] Habilitando servicios de Systemd para preservar la VRAM tras suspender el equipo..."
sudo systemctl enable nvidia-suspend.service nvidia-hibernate.service nvidia-resume.service

echo "[!] Configuración completada. Asegúrate de añadir 'nvidia-drm.modeset=1 nvidia.NVreg_PreserveVideoMemoryAllocations=1' a tus parámetros del Kernel en GRUB y reinicia."
"""

# 3. toggle_performance.sh
files_content["scripts/toggle_performance.sh"] = """#!/usr/bin/env bash
# Script de conmutación dinámica de perfiles gráficos en Hyprland
# Mapeado por defecto a SUPER + CTRL + M

STATE=$(hyprctl getoption animations:enabled | awk 'NR==1{print $2}')

if; then
    # ACTIVACIÓN DEL MODO RENDIMIENTO EXTREMO (Desactivación de carga visual pesada)
    hyprctl --batch "\\
        keyword animations:enabled 0;\\
        keyword decoration:blur:enabled 0;\\
        keyword decoration:shadow:enabled 0;\\
        keyword general:gaps_in 0;\\
        keyword general:gaps_out 0;\\
        keyword general:border_size 0;\\
        keyword decoration:active_opacity 1.0;\\
        keyword decoration:inactive_opacity 1.0"
    
    # Detener contenedores Docker activos para liberar CPU/VRAM de inmediato
    if [ "$(docker ps -q)" ]; then
        echo "[*] Deteniendo contenedores Docker de desarrollo..."
        docker stop $(docker ps -q)
    fi
    
    notify-send -e -u critical "Perfil de Hardware" "Modo Rendimiento Máximo: Animaciones e interfaces visuales desactivadas. VRAM liberada."
else
    # RETORNO AL MODO ESTÉTICO COMPLETO
    hyprctl reload
    notify-send -e -u normal "Perfil de Hardware" "Modo Estético Activo: Animaciones fluidas, bordes redondeados y desenfoque gaussianos activados."
fi
"""

# 4. rofi-ai-assistant.sh
files_content["scripts/rofi-ai-assistant.sh"] = """#!/usr/bin/env bash
# Script para lanzar consultas rápidas a la IA local mediante un lanzador integrado con Rofi y Ollama
# Lanza un terminal flotante Kitty para mostrar la respuesta en formato Markdown enriquecido con 'glow'

PREGUNTA=$(rofi -dmenu -p "Pregunta a la IA (Local):" -theme ~/.config/rofi/clock_style.rasi)

if; then
    TEMP_FILE=$(mktemp)
    
    # Consulta síncrona al servicio Ollama en el puerto por defecto 11434
    curl -s -X POST http://localhost:11434/api/generate \\
        -d "{\\"model\\": \\"llama3.2:3b\\", \\"prompt\\": \\"$PREGUNTA\\", \\"stream\\": false}" \\
        | jq -r '.response' > "$TEMP_FILE"
    
    # Invocar Kitty de manera flotante (la regla de ventana de Hyprland la centrará y redimensionará)
    kitty --class="floating_ai" -e sh -c "glow -s dark '$TEMP_FILE' && rm '$TEMP_FILE' && read -p 'Presiona cualquier tecla para salir...'"
fi
"""

# 5. distrobox create_kali.sh
files_content["distrobox/create_kali.sh"] = """#!/usr/bin/env bash
# Inicializa de manera segura y aislada un laboratorio completo de Kali Linux
# Comparte de manera transparente el servidor de audio PipeWire y el compositor Wayland de tu sistema Arch Linux

echo "[*] Creando el contenedor Distrobox con Kali Linux Rolling..."
distrobox create --name kali-offensive \\
    --image docker.io/kalilinux/kali-rolling:latest \\
    --additional-packages "kali-linux-default systemd libpam-systemd pipewire-audio-client-libraries"

echo "[+] Contenedor creado de manera exitosa."
echo "[+] Para ingresar al contenedor ejecuta: distrobox enter kali-offensive"
echo "[+] Para exportar herramientas gráficas (ej. Burp Suite): distrobox-export --app burpsuite (ejecutado dentro de Kali)"
"""

# 6. docker-compose.yml
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

# 7. agent_test.py (AutoGen Boilerplate)
files_content["docker/agent_test.py"] = """#!/usr/bin/env python3
import os
from pathlib import Path

try:
    from autogen import AssistantAgent, UserProxyAgent
    from autogen.coding import LocalCommandLineCodeExecutor
except ImportError:
    print("[!] Error: AutoGen no está instalado.")
    print("[*] Instálalo con: pip install pyautogen[ollama]")
    exit(1)

# Configuración del LLM local de Ollama (ejecutándose en Docker o Local)
config_list =

print("[*] Configurando el agente ejecutor local...")
workdir = Path("workspace")
workdir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=workdir)

# El agente usuario que ejecutará el código provisto por la IA de forma local
user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: "TERMINAR" in x.get("content", ""),
    code_execution_config={"executor": code_executor},
)

# El asistente inteligente agéntico encargado de resolver la tarea escribiendo código de Python
assistant = AssistantAgent(
    name="AgenticCoder",
    system_message="Eres un asistente experto en programación. Escribe bloques de código python de manera limpia. Cuando la tarea esté resuelta de manera exitosa, escribe la palabra TERMINAR en tu respuesta final.",
    llm_config={"config_list": config_list},
)

# Iniciar flujo de trabajo de resolución automática
user_proxy.initiate_chat(
    assistant,
    message="Escribe un script en Python que descargue el precio histórico de Bitcoin utilizando una API pública y libre, luego calcula su valor máximo y finaliza."
)
"""

# 8. snmenu layout.json (Circular Menu Custom Design)
files_content["snmenu/layout.json"] = """
"""

def create_workspace_and_zip():
    print(f"[*] Creando estructura del repositorio en./{REPO_NAME}...")
    
    # Crear la carpeta raíz y las subcarpetas del proyecto
    for filepath in files_content.keys():
        full_path = Path(REPO_NAME) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escribir el contenido del archivo con codificación UTF-8
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(files_content[filepath].strip())
            
        # Hacer ejecutables los scripts de Bash
        if filepath.endswith(".sh") or filepath.endswith(".py"):
            os.chmod(full_path, 0o755)
            
    print(f"[+] Archivos de configuración y scripts creados correctamente.")
    
    # Empaquetar todo en un archivo.zip
    print(f"[*] Comprimiendo el repositorio en {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(REPO_NAME):
            for file in files:
                file_path = Path(root) / file
                archive_name = file_path.relative_to(REPO_NAME)
                zipf.write(file_path, archive_name)
                
    print(f"[✓] ¡Éxito! Tu archivo {ZIP_NAME} ha sido generado y está listo para ser cargado a GitHub.")

if __name__ == "__main__":
    create_workspace_and_zip()