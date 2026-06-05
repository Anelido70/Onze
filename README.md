# ⚽ Onze - Simulador de Fútbol Manager

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?logo=python)
![Estado](https://img.shields.io/badge/Estado-Completo-success)

**Onze** es un simulador de gestión de fútbol desarrollado en Python con interfaz gráfica Tkinter. Permite simular partidos en tiempo real, gestionar una liga completa con 6 equipos, visualizar estadísticas detalladas y disfrutar de una experiencia inmersiva minuto a minuto.

<p align="center">
  <img src="screenshots/menu_principal.png" alt="Menú Principal" width="400">
</p>

---

## 🎮 Características

### ⚽ Simulación de Partidos en Vivo
- Partidos minuto a minuto con narración en tiempo real
- Eventos detallados: goles, penaltis, tarjetas, lesiones, sustituciones
- Marcador en directo con actualización automática
- Descanso a los 45' y tiempo de descuento

### 🏆 Modo Temporada
- Liga completa con 6 equipos (ida y vuelta = 10 jornadas)
- Calendario navegable jornada a jornada
- Simulación de jornada completa o partido individual
- Clasificación actualizada en tiempo real
- Barra de progreso de la temporada

### 📊 Estadísticas Avanzadas
- Tiros, tiros a puerta, posesión, córners, faltas
- xG (Goles Esperados) y precisión de pases
- Máximos goleadores y récords de temporada
- Estadísticas comparativas entre equipos

### 🟥 Sistema Disciplinario
- Tarjetas amarillas y rojas con impacto real en el partido
- Expulsiones por doble amarilla o roja directa
- Sanciones por acumulación de tarjetas
- Penaltis con narración y tarjeta al infractor

### 🎨 Interfaz Visual
- Diseño moderno con colores personalizados por equipo
- Visualización táctica de formaciones (4-4-2, 4-3-3, etc.)
- Mini-campo con jugadores posicionados
- Pestañas con eventos, estadísticas y alineaciones

### 🩹 Lesiones
- Sistema de lesiones con 3 niveles de gravedad
- Narrativa visual: 🤕 leve, 🚑 moderada, 🏥 grave

---

## 🛠️ Tecnologías

- **Python 3.14**: Lógica del juego y simulación
- **Tkinter**: Interfaz gráfica de usuario
- **SQLite3**: Base de datos local
- **Threading**: Simulación en tiempo real con hilos
- **POO**: Arquitectura orientada a objetos

---

## 📁 Estructura del Proyecto

onze/
├── database/
│ ├── init_database.py # Creación de la BD
│ └── updates/
│ └── run_all_updates.py # Actualizaciones de la BD
├── simulation/
│ ├── match_simulator.py # Motor de simulación de partidos
│ ├── live_match.py # Simulación en vivo minuto a minuto
│ ├── league_simulator.py # Simulador de liga
│ ├── season_manager.py # Gestor de temporadas
│ └── tactics.py # Sistema táctico
├── gui_main.py # Interfaz gráfica principal
├── utils.py # Funciones auxiliares
├── team_colors.py # Colores y estilos de equipos
├── main.py # Menú de consola
├── clean_db.py # Limpieza de base de datos
└── README.md


---

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.8 o superior
- No requiere instalación de paquetes adicionales (Tkinter y SQLite vienen incluidos)

### Pasos

1. **Clona el repositorio**
```bash
git clone https://github.com/Anelido70/onze.git
cd onze

2. **Inicializa la base de datos**
python database/init_database.py
python database/updates/run_all_updates.py

3. **Ejecuta el juego**
python gui_main.py

📸 Capturas de Pantalla
Menú Principal	Partido en Vivo
https://Screenshots/menu.png	https://Screenshots/partido.png
Resultado	Clasificación
https://Screenshots/resultado.png	https://Screenshots/clasificacion.png
Modo Temporada	Visor Táctico
https://Screenshots/temporada.png	https://Screenshots/tactico.png

👤 Autor
Víctor Fernández García
📚 Estudiante de 1º DAW (Desarrollo de Aplicaciones Web)
🔗 GitHub: Anelido70
💼 LinkedIn: www.linkedin.com/in/víctor-fernández-24b5b9253