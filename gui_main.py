import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import sys
from simulation.match_simulator import MatchSimulator
from simulation.league_simulator import LeagueSimulator
from utils import *
from tactics_view import TacticsViewer
from simulation.live_match import LiveMatchSimulator
from simulation.season_manager import SeasonManager

# Configuración para mejorar resolución en Windows
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        pass

class FootballManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚽ Football Manager v1.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar simuladores
        self.match_simulator = MatchSimulator()
        self.league_simulator = LeagueSimulator()
        
        # Crear interfaz
        self.create_widgets()
    
    def setup_styles(self):
        """Configura los estilos visuales"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        self.bg_color = '#1a1a2e'
        self.fg_color = '#e94560'
        self.secondary_color = '#16213e'
        self.text_color = '#ffffff'
        
        # Configurar fuente por defecto
        default_font = ('Segoe UI', 10)
        self.root.option_add('*Font', default_font)
        
        # Estilo para botones
        style.configure('Custom.TButton',
                       background=self.fg_color,
                       foreground=self.text_color,
                       borderwidth=0,
                       focusthreshold=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'),
                       padding=10)
        
        style.map('Custom.TButton',
                 background=[('active', '#c73e54')])
        
        # Estilo para labels
        style.configure('Custom.TLabel',
                       background=self.bg_color,
                       foreground=self.text_color,
                       font=('Segoe UI', 10))
        
        # Estilo para el título
        style.configure('Title.TLabel',
                       background=self.bg_color,
                       foreground=self.fg_color,
                       font=('Segoe UI', 24, 'bold'))
    
    def create_widgets(self):
        """Crea todos los widgets de la ventana principal"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, 
                                text="⚽ ONZE v1.0 ⚽",
                                style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Subtítulo
        subtitle = ttk.Label(main_frame,
                            text="Simulador de Gestión Deportiva",
                            style='Custom.TLabel')
        subtitle.pack(pady=5)
        
        # Frame para los botones
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=40)
        
        
        # Crear botones del menú
        buttons = [
            ("⚽ Simular Partido", self.simulate_match),
            ("🏆 Simular Temporada Completa", self.simulate_season),
            ("🏆 Modo Temporada", self.start_season),
            ("📊 Ver Clasificación", self.show_standings),
            ("🎯 Visor Táctico", self.show_tactics_viewer),
            ("📈 Estadísticas", self.show_stats),
            ("📅 Calendario", self.show_fixtures),
            ("📋 Ver Plantilla", self.show_lineup),
            ("📜 Último Resultado", self.show_last_match),
            ("🟥 Sanciones", self.show_suspensions),
            ("🗑️ Reiniciar Base de Datos", self.reset_database),
            ("🚪 Salir", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame,
                           text=text,
                           style='Custom.TButton',
                           command=command,
                           width=30)
            btn.pack(pady=5)
        
        # Barra de estado
        self.status_bar = ttk.Label(main_frame,
                                    text="Listo para jugar | 6 equipos cargados",
                                    style='Custom.TLabel',
                                    relief='sunken')
        self.status_bar.pack(side='bottom', fill='x', pady=10)
    
    def simulate_match(self):
        """Abre la ventana de selección de partido"""
        MatchWindow(self.root, self.match_simulator)

    def start_season(self):
        """Inicia el modo temporada"""
        SeasonWindow(self.root, self.match_simulator)
    
    def simulate_season(self):
        """Simula una temporada completa"""
        if messagebox.askyesno("Confirmar", 
                              "¿Estás seguro? Esto borrará la temporada anterior."):
            # Limpiar partidos anteriores
            conn = sqlite3.connect("football_manager.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM match_events")
            cursor.execute("DELETE FROM matches")
            cursor.execute("DELETE FROM suspensions")
            conn.commit()
            conn.close()
            
            # Reiniciar simuladores
            self.match_simulator = MatchSimulator()
            self.league_simulator = LeagueSimulator()
            
            # Crear ventana de progreso
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Simulando Temporada")
            progress_window.geometry("400x200")
            progress_window.configure(bg=self.bg_color)
            
            label = ttk.Label(progress_window,
                            text="🏆 Simulando temporada...\nEsto puede tardar unos segundos",
                            style='Custom.TLabel',
                            font=('Segoe UI', 12))
            label.pack(pady=20)
            
            progress = ttk.Progressbar(progress_window,
                                      mode='indeterminate',
                                      length=300)
            progress.pack(pady=20)
            progress.start(10)
            
            # Actualizar la ventana
            progress_window.update()
            
            # Simular temporada
            self.league_simulator.simulate_season()
            
            progress.stop()
            progress_window.destroy()
            
            messagebox.showinfo("Éxito", "¡Temporada completada!\nRevisa la clasificación.")
            self.status_bar.config(text="Temporada completada | Clasificación actualizada")
    
    def show_standings(self):
        """Muestra la clasificación en una ventana"""
        StandingsWindow(self.root)

    def show_tactics_viewer(self):
        """Muestra el visor táctico para seleccionar equipo"""
        TeamSelectorWindow(self.root, "Seleccionar Equipo", self.open_tactics)

    def open_tactics(self, team_id):
        """Abre el visor táctico del equipo"""
        from tactics_view import TacticsViewer
        TacticsViewer(self.root, team_id=team_id)
    
    def show_stats(self):
        """Muestra las estadísticas de la temporada"""
        StatsWindow(self.root)
    
    def show_fixtures(self):
        """Muestra el calendario de jornadas"""
        FixtureWindow(self.root)
    
    def show_lineup(self):
        """Muestra la plantilla de un equipo"""
        TeamSelectorWindow(self.root, "Ver Plantilla", self.view_lineup_callback)
    
    def view_lineup_callback(self, team_id):
        """Callback para mostrar la plantilla del equipo seleccionado"""
        lineup = get_team_lineup(team_id)
        LineupWindow(self.root, lineup)
    
    def show_last_match(self):
        """Muestra el último partido jugado"""
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM matches WHERE played = 1 ORDER BY id DESC LIMIT 1")
        last_match = cursor.fetchone()
        conn.close()
        
        if last_match:
            ResultWindow(self.root, last_match[0])
        else:
            messagebox.showinfo("Info", "No hay partidos jugados todavía.")
    
    def show_suspensions(self):
        """Muestra los jugadores sancionados"""
        SuspensionsWindow(self.root)
    
    def reset_database(self):
        """Reinicia la base de datos"""
        if messagebox.askyesno("⚠️ Confirmar", 
                              "¿Estás seguro? Se perderán todos los datos."):
            import subprocess
            subprocess.run(["python", "init_database.py"])
            self.match_simulator = MatchSimulator()
            self.league_simulator = LeagueSimulator()
            self.status_bar.config(text="Base de datos reiniciada | Datos frescos")
            messagebox.showinfo("Éxito", "Base de datos reiniciada correctamente.")
    
    def close(self):
        self.match_simulator.close()
        self.league_simulator.close()


class MatchWindow:
    """Ventana para simular un partido"""
    def __init__(self, parent, simulator):
        self.simulator = simulator
        self.window = tk.Toplevel(parent)
        self.window.title("⚽ Simular Partido")
        self.window.geometry("800x600")
        self.window.configure(bg='#1a1a2e')
        
        # Obtener equipos
        self.teams = get_available_teams()
        # Crear diccionario para mapear texto -> id
        self.team_map = {f"{t[2]} - {t[1]}": t[0] for t in self.teams}
        
        self.create_widgets()
    
    def create_widgets(self):
        # Título
        title = ttk.Label(self.window,
                         text="Seleccionar Equipos",
                         style='Title.TLabel',
                         font=('Segoe UI', 18, 'bold'))
        title.pack(pady=20)
        
        # Frame para selección
        select_frame = tk.Frame(self.window, bg='#1a1a2e')
        select_frame.pack(pady=20)
        
        # Equipo local
        local_frame = tk.Frame(select_frame, bg='#1a1a2e')
        local_frame.pack(side='left', padx=30)
        
        ttk.Label(local_frame,
                 text="🏠 EQUIPO LOCAL",
                 style='Custom.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack()
        
        self.home_var = tk.StringVar()
        team_names = list(self.team_map.keys())
        home_combo = ttk.Combobox(local_frame,
                                 textvariable=self.home_var,
                                 values=team_names,
                                 state='readonly',
                                 width=30)
        home_combo.pack(pady=10)
        if team_names:
            home_combo.current(0)
        
        # VS
        ttk.Label(select_frame,
                 text="VS",
                 style='Custom.TLabel',
                 font=('Segoe UI', 20, 'bold')).pack(side='left', padx=30)
        
        # Equipo visitante
        away_frame = tk.Frame(select_frame, bg='#1a1a2e')
        away_frame.pack(side='left', padx=30)
        
        ttk.Label(away_frame,
                 text="🚌 EQUIPO VISITANTE",
                 style='Custom.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack()
        
        self.away_var = tk.StringVar()
        away_combo = ttk.Combobox(away_frame,
                                 textvariable=self.away_var,
                                 values=team_names,
                                 state='readonly',
                                 width=30)
        away_combo.pack(pady=10)
        if len(team_names) > 1:
            away_combo.current(1)
        
        # Botón simular
        sim_btn = ttk.Button(self.window,
                           text="⚡ SIMULAR PARTIDO",
                           style='Custom.TButton',
                           command=self.run_simulation,
                           width=20)
        sim_btn.pack(pady=30)
    
    def run_simulation(self):
        home_text = self.home_var.get()
        away_text = self.away_var.get()
        
        if not home_text or not away_text:
            messagebox.showwarning("Error", "Selecciona ambos equipos")
            return
        
        if home_text == away_text:
            messagebox.showwarning("Error", "No pueden ser el mismo equipo")
            return
        
        home_id = self.team_map[home_text]
        away_id = self.team_map[away_text]
        
        # Cerrar esta ventana
        self.window.destroy()
        
        # Abrir simulación en vivo
        LiveMatchWindow(self.window.master, self.simulator, home_id, away_id)


class ResultWindow:
    """Ventana de resultado con campos tácticos, alineaciones, stats y eventos"""
    def __init__(self, parent, match_id):
        self.window = tk.Toplevel(parent)
        self.window.title("📜 Resultado del Partido")
        self.window.geometry("1050x750")
        self.window.configure(bg='#1a1a2e')
        
        self.match_id = match_id
        
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        # Datos del partido
        cursor.execute('''
            SELECT th.short_name, th.id, ta.short_name, ta.id, m.home_score, m.away_score
            FROM matches m
            JOIN teams th ON m.home_team_id = th.id
            JOIN teams ta ON m.away_team_id = ta.id
            WHERE m.id = ?
        ''', (match_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
            
        home_short, home_id, away_short, away_id, home_score, away_score = result
        
        from team_colors import get_team_style
        home_style = get_team_style(home_short)
        away_style = get_team_style(away_short)
        
        # ===== MARCADOR =====
        score_frame = tk.Frame(self.window, bg='#1a1a2e')
        score_frame.pack(pady=5)
        
        home_frame = tk.Frame(score_frame, bg=home_style['color'], relief='raised', bd=2)
        home_frame.pack(side='left', padx=8)
        tk.Label(home_frame, text=f"{home_style['emoji']} {home_short}",
                bg=home_style['color'], fg='white', font=('Segoe UI', 12, 'bold')).pack(padx=15, pady=3)
        tk.Label(home_frame, text=str(home_score),
                bg=home_style['color'], fg='white', font=('Segoe UI', 28, 'bold')).pack(padx=15, pady=5)
        
        vs_frame = tk.Frame(score_frame, bg='#1a1a2e')
        vs_frame.pack(side='left', padx=10)
        tk.Label(vs_frame, text="VS", bg='#1a1a2e', fg='#e94560', font=('Segoe UI', 16, 'bold')).pack()
        
        away_frame = tk.Frame(score_frame, bg=away_style['color'], relief='raised', bd=2)
        away_frame.pack(side='left', padx=8)
        tk.Label(away_frame, text=f"{away_style['emoji']} {away_short}",
                bg=away_style['color'], fg='white', font=('Segoe UI', 12, 'bold')).pack(padx=15, pady=3)
        tk.Label(away_frame, text=str(away_score),
                bg=away_style['color'], fg='white', font=('Segoe UI', 28, 'bold')).pack(padx=15, pady=5)
        
        # ===== PANEL PRINCIPAL CON 3 COLUMNAS =====
        main_panel = tk.Frame(self.window, bg='#1a1a2e')
        main_panel.pack(fill='both', expand=True, padx=8, pady=5)
        
        # ===== COLUMNA 1: CAMPO + ALINEACIÓN LOCAL =====
        left_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=2)
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 4))
        
        tk.Label(left_col, text=f"{home_style['emoji']} {home_short}",
                bg=home_style['color'], fg='white', font=('Segoe UI', 10, 'bold')).pack(fill='x', pady=2)
        
        # Campo local
        home_canvas = tk.Canvas(left_col, bg='#27ae60', height=220, width=280, highlightthickness=0)
        home_canvas.pack(pady=3)
        self.draw_mini_pitch(home_canvas, 280, 220)
        
        # Dibujar jugadores locales
        home_players_data = self.get_lineup_data(match_id, 'home')
        for player in home_players_data:
            x = player['x'] * 2.6 + 10
            y = player['y'] * 2.0 + 10
            home_canvas.create_oval(x-7, y-7, x+7, y+7, fill=home_style['color'], outline='white', width=1)
            home_canvas.create_text(x, y-10, text=str(player['number']), fill='white', font=('Arial', 6, 'bold'))
            home_canvas.create_text(x, y+11, text=player['name'].split()[-1], fill='white', font=('Arial', 5))
        
        # Alineación local (lista debajo del campo)
        home_list_frame = tk.Frame(left_col, bg='#16213e')
        home_list_frame.pack(fill='both', expand=True, padx=5, pady=3)
        
        for player in home_players_data:
            tk.Label(home_list_frame, 
                    text=f" {player['number']:2d}  {player['name']} ({player['spec_pos']})",
                    bg='#16213e', fg='white', font=('Segoe UI', 7), anchor='w').pack(fill='x')
        
        # ===== COLUMNA 2: STATS + EVENTOS =====
        mid_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=2)
        mid_col.pack(side='left', fill='both', expand=True, padx=4)
        
        # Stats
        stats_label = tk.Label(mid_col, text="📊 ESTADÍSTICAS", bg='#e94560', fg='white',
                              font=('Segoe UI', 9, 'bold'))
        stats_label.pack(fill='x', pady=1)
        
        stats_frame = tk.Frame(mid_col, bg='#16213e')
        stats_frame.pack(fill='x', padx=3, pady=3)
        
        self.create_compact_stats(stats_frame, home_id, away_id, home_short, away_short)
        
        # Separador
        ttk.Separator(mid_col, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Eventos
        events_label = tk.Label(mid_col, text="📋 EVENTOS", bg='#e94560', fg='white',
                               font=('Segoe UI', 9, 'bold'))
        events_label.pack(fill='x', pady=1)
        
        events_frame = tk.Frame(mid_col, bg='#16213e')
        events_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        self.create_compact_events(events_frame, cursor)
        
        # ===== COLUMNA 3: CAMPO + ALINEACIÓN VISITANTE =====
        right_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=2)
        right_col.pack(side='right', fill='both', expand=True, padx=(4, 0))
        
        tk.Label(right_col, text=f"{away_style['emoji']} {away_short}",
                bg=away_style['color'], fg='white', font=('Segoe UI', 10, 'bold')).pack(fill='x', pady=2)
        
        # Campo visitante
        away_canvas = tk.Canvas(right_col, bg='#27ae60', height=220, width=280, highlightthickness=0)
        away_canvas.pack(pady=3)
        self.draw_mini_pitch(away_canvas, 280, 220)
        
        # Dibujar jugadores visitantes
        away_players_data = self.get_lineup_data(match_id, 'away')
        for player in away_players_data:
            x = player['x'] * 2.6 + 10
            y = player['y'] * 2.0 + 10
            away_canvas.create_oval(x-7, y-7, x+7, y+7, fill=away_style['color'], outline='white', width=1)
            away_canvas.create_text(x, y-10, text=str(player['number']), fill='white', font=('Arial', 6, 'bold'))
            away_canvas.create_text(x, y+11, text=player['name'].split()[-1], fill='white', font=('Arial', 5))
        
        # Alineación visitante
        away_list_frame = tk.Frame(right_col, bg='#16213e')
        away_list_frame.pack(fill='both', expand=True, padx=5, pady=3)
        
        for player in away_players_data:
            tk.Label(away_list_frame, 
                    text=f" {player['number']:2d}  {player['name']} ({player['spec_pos']})",
                    bg='#16213e', fg='white', font=('Segoe UI', 7), anchor='w').pack(fill='x')
        
        conn.close()
        
        ttk.Button(self.window, text="Cerrar", style='Custom.TButton',
                  command=self.window.destroy, width=15).pack(pady=5)
    
    def draw_mini_pitch(self, canvas, width, height):
        """Dibuja un mini campo de fútbol"""
        canvas.create_rectangle(3, 3, width-3, height-3, outline='white', width=1)
        canvas.create_line(3, height//2, width-3, height//2, fill='white', width=1)
        canvas.create_oval(width//2-15, height//2-15, width//2+15, height//2+15, outline='white', width=0.5)
        canvas.create_rectangle(20, 5, width-20, 40, outline='white', width=0.8)
        canvas.create_rectangle(20, height-40, width-20, height-5, outline='white', width=0.8)
        canvas.create_rectangle(45, 5, width-45, 20, outline='white', width=0.4)
        canvas.create_rectangle(45, height-20, width-45, height-5, outline='white', width=0.4)
        canvas.create_rectangle(55, 2, width-55, 5, outline='white', width=1)
        canvas.create_rectangle(55, height-5, width-55, height-2, outline='white', width=1)
    
    def get_lineup_data(self, match_id, side):
        """Obtiene los datos de alineación usando el mismo método que el visor táctico"""
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
    
        # Obtener team_id
        if side == 'home':
            cursor.execute("SELECT home_team_id FROM matches WHERE id = ?", (match_id,))
        else:
            cursor.execute("SELECT away_team_id FROM matches WHERE id = ?", (match_id,))
        team_id = cursor.fetchone()[0]
    
        # Obtener los IDs de los jugadores titulares en orden
        cursor.execute('''
            SELECT player_id FROM match_lineups
            WHERE match_id = ? AND side = ? AND is_starter = 1
            ORDER BY position_order
        ''', (match_id, side))
        
        starter_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
    
        # Usar TacticsManager para obtener la formación con posiciones
        from simulation.tactics import TacticsManager
        tm = TacticsManager()
        tactics = tm.get_team_tactics(team_id)
        formation_name = tactics['formation_name']
        
        # Obtener todos los jugadores del equipo
        all_players = tm.get_team_players_with_positions(team_id)
        
        # Filtrar solo los titulares (en el orden correcto)
        starters = []
        starter_dict = {p['id']: p for p in all_players}
        
        for pid in starter_ids:
            if pid in starter_dict:
                starters.append(starter_dict[pid])
        
        # Usar el método del visor táctico para asignar coordenadas
        positioned = tm.get_starting_eleven_with_positions(starters, formation_name)
        tm.close()
    
        result = []
        for player in positioned:
            result.append({
                'name': player['name'],
                'number': player.get('number', 0),
                'position': player['position'],
                'spec_pos': player.get('specific_position', player['position']),
                'x': player.get('field_x', 50),
                'y': player.get('field_y', 50)
            })
    
        return result
    
    def create_compact_stats(self, parent, home_id, away_id, home_short, away_short):
        """Crea tabla de estadísticas compacta"""
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT team_id, shots, shots_on_target, possession, corners, fouls, 
                   yellow_cards, red_cards, offsides, passes, tackles, xG, pass_accuracy
            FROM match_stats WHERE match_id = ?
        ''', (self.match_id,))
        
        stats = cursor.fetchall()
        conn.close()
        
        if len(stats) < 2:
            tk.Label(parent, text="Sin datos", bg='#16213e', fg='white',
                    font=('Segoe UI', 8)).pack()
            return
        
        home_stats = stats[0] if stats[0][0] == home_id else stats[1]
        away_stats = stats[1] if stats[1][0] == away_id else stats[0]
        
        # Datos simplificados
        rows = [
            ('Tiros', 1, 1, False),
            ('A puerta', 2, 2, False),
            ('xG', 11, 11, False),
            ('Posesión %', 3, 3, False),
            ('Pases %', 12, 12, False),
            ('Córners', 4, 4, False),
            ('Faltas', 5, 5, True),
            ('🟨 Amarillas', 6, 6, True),
            ('🟥 Rojas', 7, 7, True),
            ('Offsides', 8, 8, False),
        ]
        
        # Cabecera
        tk.Label(parent, text="", bg='#16213e', width=14).grid(row=0, column=0)
        tk.Label(parent, text=home_short, bg='#e94560', fg='white',
                font=('Segoe UI', 8, 'bold'), width=8).grid(row=0, column=1, padx=1)
        tk.Label(parent, text=away_short, bg='#e94560', fg='white',
                font=('Segoe UI', 8, 'bold'), width=8).grid(row=0, column=2, padx=1)
        
        for i, (name, home_idx, away_idx, lower_is_better) in enumerate(rows, 1):
            hv = home_stats[home_idx]
            av = away_stats[away_idx]
            
            if 'xG' in name:
                ht = f"{hv:.2f}"
                at = f"{av:.2f}"
            elif '%' in name:
                ht = f"{hv}%"
                at = f"{av}%"
            else:
                ht = str(int(hv))
                at = str(int(av))
            
            bg = '#16213e' if i % 2 == 0 else '#1a1a2e'
            
            tk.Label(parent, text=name, bg=bg, fg='#ccc',
                    font=('Segoe UI', 7), anchor='w', width=14).grid(row=i, column=0, padx=1, sticky='w')
            
            if lower_is_better:
                hc = '#2ecc71' if hv <= av else 'white'
                ac = '#2ecc71' if av <= hv else 'white'
            else:
                hc = '#2ecc71' if hv >= av else 'white'
                ac = '#2ecc71' if av >= hv else 'white'
            
            tk.Label(parent, text=ht, bg=bg, fg=hc,
                    font=('Segoe UI', 8, 'bold'), width=8).grid(row=i, column=1, padx=1)
            tk.Label(parent, text=at, bg=bg, fg=ac,
                    font=('Segoe UI', 8, 'bold'), width=8).grid(row=i, column=2, padx=1)
    
    def create_compact_events(self, parent, cursor):
        """Crea lista de eventos compacta con scroll"""
        canvas = tk.Canvas(parent, bg='#16213e', highlightthickness=0, height=200)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#16213e')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=240)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        cursor.execute('''
            SELECT minute, event_type, description FROM match_events
            WHERE match_id = ? ORDER BY minute
        ''', (self.match_id,))
        
        events = cursor.fetchall()
        
        if not events:
            tk.Label(scrollable_frame, text="Sin eventos",
                    bg='#16213e', fg='white', font=('Segoe UI', 8)).pack(pady=5)
        else:
            for minute, event_type, desc in events:
                if event_type == 'GOAL':
                    bg_color = '#1a472a'; icon = '⚽'
                elif event_type == 'RED_CARD':
                    bg_color = '#7b241c'; icon = '🟥'
                elif event_type == 'YELLOW_CARD':
                    bg_color = '#7d6608'; icon = '🟨'
                elif event_type == 'SUBSTITUTION':
                    bg_color = '#1a5276'; icon = '🔄'
                else:
                    bg_color = '#16213e'; icon = '•'
                
                ef = tk.Frame(scrollable_frame, bg=bg_color)
                ef.pack(fill='x', padx=2, pady=1)
                
                tk.Label(ef, text=f"{minute}' {icon} {desc}",
                        bg=bg_color, fg='white', font=('Segoe UI', 7),
                        anchor='w', justify='left', wraplength=230).pack(fill='x', padx=3, pady=1)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')


class StandingsWindow:
    """Ventana para mostrar la clasificación"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Tabla de Clasificación")
        self.window.geometry("950x450")
        self.window.configure(bg='#1a1a2e')
        
        # Título
        ttk.Label(self.window,
                 text="📊 TABLA DE CLASIFICACIÓN",
                 style='Custom.TLabel',
                 font=('Segoe UI', 16, 'bold')).pack(pady=20)
        
        # Crear tabla
        table_frame = tk.Frame(self.window, bg='#16213e')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Obtener datos
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                m.home_team_id, m.away_team_id, 
                m.home_score, m.away_score
            FROM matches m
            WHERE m.played = 1
        ''')
        
        matches = cursor.fetchall()
        
        if not matches:
            ttk.Label(self.window,
                     text="No hay partidos jugados",
                     style='Custom.TLabel').pack(pady=20)
            conn.close()
            ttk.Button(self.window,
                      text="Cerrar",
                      style='Custom.TButton',
                      command=self.window.destroy,
                      width=15).pack(pady=10)
            return
        
        # Calcular estadísticas
        stats = {}
        cursor.execute("SELECT id, name, short_name FROM teams")
        for team_id, name, short in cursor.fetchall():
            stats[team_id] = {
                'name': name,
                'short': short,
                'points': 0,
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'gf': 0,
                'ga': 0,
            }
        
        for match in matches:
            home_id, away_id, home_score, away_score = match
            
            if home_id in stats and away_id in stats:
                stats[home_id]['played'] += 1
                stats[home_id]['gf'] += home_score
                stats[home_id]['ga'] += away_score
                
                if home_score > away_score:
                    stats[home_id]['won'] += 1
                    stats[home_id]['points'] += 3
                elif home_score == away_score:
                    stats[home_id]['drawn'] += 1
                    stats[home_id]['points'] += 1
                else:
                    stats[home_id]['lost'] += 1
                
                stats[away_id]['played'] += 1
                stats[away_id]['gf'] += away_score
                stats[away_id]['ga'] += home_score
                
                if away_score > home_score:
                    stats[away_id]['won'] += 1
                    stats[away_id]['points'] += 3
                elif away_score == home_score:
                    stats[away_id]['drawn'] += 1
                    stats[away_id]['points'] += 1
                else:
                    stats[away_id]['lost'] += 1
        
        conn.close()
        
        sorted_stats = sorted(stats.items(),
                            key=lambda x: (x[1]['points'],
                                          x[1]['gf'] - x[1]['ga'],
                                          x[1]['gf']),
                            reverse=True)
        
        # Importar estilos de equipos
        from team_colors import get_team_style
        
        # Cabecera de la tabla
        headers = ['POS', 'EQUIPO', 'PJ', 'PG', 'PE', 'PP', 'GF', 'GC', 'DG', 'PTS']
        widths = [5, 28, 5, 5, 5, 5, 5, 5, 5, 5]
        
        for col, (header, width) in enumerate(zip(headers, widths)):
            tk.Label(table_frame,
                    text=header,
                    bg='#e94560',
                    fg='white',
                    font=('Segoe UI', 10, 'bold'),
                    width=width).grid(row=0, column=col, padx=1, pady=1)
        
        # Datos
        for pos, (team_id, data) in enumerate(sorted_stats, 1):
            dg = data['gf'] - data['ga']
            team_style = get_team_style(data['short'])
            
            values = [
                pos, 
                f"{team_style['emoji']} {data['name']}", 
                data['played'], 
                data['won'],
                data['drawn'], 
                data['lost'], 
                data['gf'], 
                data['ga'],
                f"+{dg}" if dg > 0 else str(dg), 
                data['points']
            ]
            
            for col, value in enumerate(values):
                if col == 1:
                    bg = team_style['color']
                else:
                    bg = '#16213e' if pos % 2 == 0 else '#1a1a2e'
                
                tk.Label(table_frame,
                        text=value,
                        bg=bg,
                        fg='white',
                        font=('Segoe UI', 10),
                        width=widths[col]).grid(row=pos, column=col, padx=1, pady=1)
        
        # Botón cerrar
        ttk.Button(self.window,
                  text="Cerrar",
                  style='Custom.TButton',
                  command=self.window.destroy,
                  width=15).pack(pady=10)


class StatsWindow:
    """Ventana para mostrar estadísticas de la temporada"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Estadísticas de la Temporada")
        self.window.geometry("700x600")
        self.window.configure(bg='#1a1a2e')
        
        stats = get_season_stats()
        
        if stats['total_matches'] == 0:
            ttk.Label(self.window,
                     text="No hay partidos jugados todavía",
                     style='Custom.TLabel',
                     font=('Segoe UI', 14)).pack(pady=50)
            ttk.Button(self.window,
                      text="Cerrar",
                      style='Custom.TButton',
                      command=self.window.destroy,
                      width=15).pack()
            return
        
        # Título
        ttk.Label(self.window,
                 text="📊 ESTADÍSTICAS DE LA TEMPORADA",
                 style='Custom.TLabel',
                 font=('Segoe UI', 16, 'bold')).pack(pady=15)
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Datos generales
        gen_frame = tk.Frame(main_frame, bg='#16213e', relief='ridge', bd=2)
        gen_frame.pack(fill='x', pady=10)
        
        ttk.Label(gen_frame,
                 text="📈 DATOS GENERALES",
                 style='Custom.TLabel',
                 font=('Segoe UI', 12, 'bold'),
                 background='#16213e').pack(pady=5)
        
        datos = [
            f"🏟️  Total de partidos jugados: {stats['total_matches']}",
            f"⚽ Total de goles: {stats['total_goals']}",
            f"📊 Media de goles por partido: {stats['avg_goals']}"
        ]
        
        for dato in datos:
            tk.Label(gen_frame,
                    text=dato,
                    bg='#16213e',
                    fg='white',
                    font=('Segoe UI', 10),
                    anchor='w').pack(fill='x', padx=20, pady=2)
        
        # Máximos goleadores
        goals_frame = tk.Frame(main_frame, bg='#16213e', relief='ridge', bd=2)
        goals_frame.pack(fill='x', pady=10)
        
        ttk.Label(goals_frame,
                 text="⚽ MÁXIMOS GOLEADORES",
                 style='Custom.TLabel',
                 font=('Segoe UI', 12, 'bold'),
                 background='#16213e').pack(pady=5)
        
        if stats['top_scorers']:
            for i, (name, team, goals) in enumerate(stats['top_scorers'], 1):
                emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][i-1]
                tk.Label(goals_frame,
                        text=f"  {emoji} {name} ({team}) - {goals} goles",
                        bg='#16213e',
                        fg='white',
                        font=('Segoe UI', 10),
                        anchor='w').pack(fill='x', padx=20, pady=2)
        
        # Récords
        records_frame = tk.Frame(main_frame, bg='#16213e', relief='ridge', bd=2)
        records_frame.pack(fill='x', pady=10)
        
        ttk.Label(records_frame,
                 text="🏆 RÉCORDS",
                 style='Custom.TLabel',
                 font=('Segoe UI', 12, 'bold'),
                 background='#16213e').pack(pady=5)
        
        if stats['most_goals_team']:
            tk.Label(records_frame,
                    text=f"  ⚽ Equipo más goleador: {stats['most_goals_team'][0]} ({stats['most_goals_team'][1]} goles)",
                    bg='#16213e',
                    fg='white',
                    font=('Segoe UI', 10),
                    anchor='w').pack(fill='x', padx=20, pady=2)
        
        if stats['biggest_win']:
            home, away, hs, aw, diff = stats['biggest_win']
            tk.Label(records_frame,
                    text=f"  🔥 Mayor goleada: {home} {hs}-{aw} {away}",
                    bg='#16213e',
                    fg='white',
                    font=('Segoe UI', 10),
                    anchor='w').pack(fill='x', padx=20, pady=2)
        
        if stats['most_cards']:
            name, team, cards = stats['most_cards']
            tk.Label(records_frame,
                    text=f"  🟨 Jugador con más tarjetas: {name} ({team}) - {cards} tarjetas",
                    bg='#16213e',
                    fg='white',
                    font=('Segoe UI', 10),
                    anchor='w').pack(fill='x', padx=20, pady=2)
        
        # Botón cerrar
        ttk.Button(self.window,
                  text="Cerrar",
                  style='Custom.TButton',
                  command=self.window.destroy,
                  width=15).pack(pady=10)


class FixtureWindow:
    """Ventana para mostrar y gestionar las jornadas"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📅 Calendario de Jornadas")
        self.window.geometry("700x600")
        self.window.configure(bg='#1a1a2e')
        
        from team_colors import get_team_style
        
        ttk.Label(self.window,
                 text="📅 CALENDARIO DE JORNADAS",
                 style='Custom.TLabel',
                 font=('Segoe UI', 16, 'bold')).pack(pady=15)
        
        # Obtener partidos jugados y pendientes
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        # Contar partidos jugados
        cursor.execute("SELECT COUNT(*) FROM matches WHERE played = 1")
        played_count = cursor.fetchone()[0]
        
        # Obtener equipos
        cursor.execute("SELECT id, name, short_name FROM teams")
        teams = cursor.fetchall()
        
        total_teams = len(teams)
        matches_per_round = total_teams // 2
        total_rounds = (total_teams - 1) * 2  # Ida y vuelta
        current_round = (played_count // matches_per_round) + 1 if played_count < total_rounds * matches_per_round else total_rounds
        
        # Info de progreso
        info_frame = tk.Frame(self.window, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(info_frame,
                text=f"📊 Progreso: Jornada {min(current_round, total_rounds)} de {total_rounds}",
                bg='#16213e',
                fg='white',
                font=('Segoe UI', 11)).pack(pady=5)
        
        tk.Label(info_frame,
                text=f"⚽ Partidos jugados: {played_count} de {total_rounds * matches_per_round}",
                bg='#16213e',
                fg='white',
                font=('Segoe UI', 10)).pack(pady=2)
        
        # Frame para partidos de la jornada actual
        matches_frame = tk.Frame(self.window, bg='#1a1a2e')
        matches_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        if played_count >= total_rounds * matches_per_round:
            # Temporada terminada
            tk.Label(matches_frame,
                    text="🏆 ¡Temporada completada!",
                    bg='#1a1a2e',
                    fg='#f1c40f',
                    font=('Segoe UI', 14, 'bold')).pack(pady=20)
            
            tk.Label(matches_frame,
                    text="Reinicia la base de datos para jugar otra temporada",
                    bg='#1a1a2e',
                    fg='white',
                    font=('Segoe UI', 10)).pack()
        else:
            # Mostrar partidos de las últimas jornadas jugadas
            tk.Label(matches_frame,
                    text="📋 ÚLTIMOS RESULTADOS",
                    bg='#1a1a2e',
                    fg='#e94560',
                    font=('Segoe UI', 12, 'bold')).pack(pady=5)
            
            cursor.execute('''
                SELECT th.short_name, ta.short_name, m.home_score, m.away_score, m.id
                FROM matches m
                JOIN teams th ON m.home_team_id = th.id
                JOIN teams ta ON m.away_team_id = ta.id
                WHERE m.played = 1
                ORDER BY m.id DESC
                LIMIT 10
            ''')
            
            recent_matches = cursor.fetchall()
            
            for home, away, hs, aw, mid in recent_matches:
                home_style = get_team_style(home)
                away_style = get_team_style(away)
                
                match_frame = tk.Frame(matches_frame, bg='#16213e', relief='groove', bd=1)
                match_frame.pack(fill='x', pady=2)
                
                tk.Label(match_frame,
                        text=f"{home_style['emoji']} {home}",
                        bg='#16213e',
                        fg=home_style['color'],
                        font=('Segoe UI', 10, 'bold'),
                        width=20, anchor='e').pack(side='left', padx=5)
                
                tk.Label(match_frame,
                        text=f"{hs} - {aw}",
                        bg='#16213e',
                        fg='white',
                        font=('Segoe UI', 11, 'bold'),
                        width=8).pack(side='left')
                
                tk.Label(match_frame,
                        text=f"{away} {away_style['emoji']}",
                        bg='#16213e',
                        fg=away_style['color'],
                        font=('Segoe UI', 10, 'bold'),
                        width=20, anchor='w').pack(side='left', padx=5)
        
        conn.close()
        
        # Botones
        btn_frame = tk.Frame(self.window, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame,
                  text="Cerrar",
                  style='Custom.TButton',
                  command=self.window.destroy,
                  width=15).pack(side='left', padx=5)


class TeamSelectorWindow:
    """Ventana para seleccionar un equipo"""
    def __init__(self, parent, title, callback):
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x300")
        self.window.configure(bg='#1a1a2e')
        
        self.teams = get_available_teams()
        
        ttk.Label(self.window,
                 text="Seleccionar Equipo",
                 style='Custom.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=20)
        
        listbox_frame = tk.Frame(self.window, bg='#16213e')
        listbox_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.listbox = tk.Listbox(listbox_frame,
                                 bg='#16213e',
                                 fg='white',
                                 font=('Segoe UI', 11),
                                 selectbackground='#e94560',
                                 height=8)
        self.listbox.pack(fill='both', expand=True)
        
        for team in self.teams:
            self.listbox.insert(tk.END, f"{team[2]} - {team[1]}")
        
        ttk.Button(self.window,
                  text="Seleccionar",
                  style='Custom.TButton',
                  command=self.select_team,
                  width=15).pack(pady=10)
    
    def select_team(self):
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            team_id = self.teams[idx][0]
            self.callback(team_id)
            self.window.destroy()


class LineupWindow:
    """Ventana para mostrar la plantilla de un equipo"""
    def __init__(self, parent, lineup):
        self.window = tk.Toplevel(parent)
        self.window.title(f"📋 {lineup['team_name']}")
        self.window.geometry("750x550")
        self.window.configure(bg='#1a1a2e')
        
        # Importar estilos de equipos
        from team_colors import get_team_style
        team_style = get_team_style(lineup['team_short'])
        
        # Título con color del equipo
        title_frame = tk.Frame(self.window, bg=team_style['color'], relief='raised', bd=2)
        title_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(title_frame,
                text=f"{team_style['emoji']} {lineup['team_name']} ({lineup['team_short']})",
                bg=team_style['color'],
                fg='white',
                font=('Segoe UI', 16, 'bold')).pack(pady=10)
        
        tk.Label(title_frame,
                text=f"🏟️ {team_style['stadium']}",
                bg=team_style['color'],
                fg='white',
                font=('Segoe UI', 10)).pack(pady=3)
        
        # Crear tabla de jugadores
        table_frame = tk.Frame(self.window, bg='#16213e')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        headers = ['Nº', 'Jugador', 'POS', 'ATQ', 'DEF', 'MED', 'POR', 'RES', 'VEL']
        widths = [4, 25, 5, 5, 5, 5, 5, 5, 5]
        
        for col, (header, width) in enumerate(zip(headers, widths)):
            tk.Label(table_frame,
                    text=header,
                    bg='#e94560',
                    fg='white',
                    font=('Segoe UI', 9, 'bold'),
                    width=width).grid(row=0, column=col, padx=1, pady=1)
        
        for row, player in enumerate(lineup['players'], 1):
            name, pos, num, att, df, mid, gk, sta, spd = player
            values = [num, name, pos, att, df, mid, gk, sta, spd]
            
            # Destacar según posición
            if pos == 'GK':
                bg_color = '#1a5276'
            elif pos == 'DEF':
                bg_color = '#196f3d'
            elif pos == 'MID':
                bg_color = '#935116'
            else:
                bg_color = '#922b21'
            
            # Alternar ligeramente el color para filas pares/impares
            if row % 2 == 0:
                bg_color = self._adjust_color(bg_color, -20)
            
            for col, value in enumerate(values):
                tk.Label(table_frame,
                        text=value,
                        bg=bg_color,
                        fg='white',
                        font=('Segoe UI', 9),
                        width=widths[col]).grid(row=row, column=col, padx=1, pady=1)
        
        # Leyenda
        legend_frame = tk.Frame(self.window, bg='#1a1a2e')
        legend_frame.pack(fill='x', padx=20, pady=5)
        
        legends = [
            ('GK - Portero', '#1a5276'),
            ('DEF - Defensa', '#196f3d'),
            ('MID - Centrocampista', '#935116'),
            ('FWD - Delantero', '#922b21')
        ]
        
        for text, color in legends:
            leg = tk.Frame(legend_frame, bg='#1a1a2e')
            leg.pack(side='left', padx=10)
            
            tk.Label(leg,
                    text="  ",
                    bg=color,
                    width=3).pack(side='left')
            
            tk.Label(leg,
                    text=text,
                    bg='#1a1a2e',
                    fg='white',
                    font=('Segoe UI', 8)).pack(side='left', padx=3)
        
        # Botón cerrar
        ttk.Button(self.window,
                  text="Cerrar",
                  style='Custom.TButton',
                  command=self.window.destroy,
                  width=15).pack(pady=10)
    
    def _adjust_color(self, hex_color, amount):
        """Ajusta un color hexadecimal haciéndolo más claro u oscuro"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        return f'#{r:02x}{g:02x}{b:02x}'


class SuspensionsWindow:
    """Ventana para mostrar jugadores sancionados"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("🟥 Jugadores Sancionados")
        self.window.geometry("600x400")
        self.window.configure(bg='#1a1a2e')
        
        ttk.Label(self.window,
                 text="🟥 JUGADORES SANCIONADOS",
                 style='Custom.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=15)
        
        # Obtener sanciones activas
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, t.short_name, s.suspension_type, 
                   s.matches_banned - s.matches_served as remaining,
                   s.matches_banned
            FROM suspensions s
            JOIN players p ON s.player_id = p.id
            JOIN teams t ON p.team_id = t.id
            WHERE s.active = 1
            ORDER BY remaining DESC
        ''')
        
        suspensions = cursor.fetchall()
        conn.close()
        
        if not suspensions:
            ttk.Label(self.window,
                     text="✅ No hay jugadores sancionados actualmente",
                     style='Custom.TLabel',
                     font=('Segoe UI', 12)).pack(pady=30)
        else:
            # Tabla de sanciones
            table_frame = tk.Frame(self.window, bg='#16213e')
            table_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            headers = ['Jugador', 'Equipo', 'Tipo', 'Partidos restantes']
            for col, header in enumerate(headers):
                tk.Label(table_frame,
                        text=header,
                        bg='#e94560',
                        fg='white',
                        font=('Segoe UI', 10, 'bold'),
                        width=20 if col == 0 else 15).grid(row=0, column=col, padx=1, pady=1)
            
            for row, (name, team, type_susp, remaining, total) in enumerate(suspensions, 1):
                if type_susp == 'RED_CARD':
                    tipo = '🟥 Roja'
                else:
                    tipo = '🟨 Acumulación'
                
                values = [name, team, tipo, f"{remaining} de {total}"]
                for col, value in enumerate(values):
                    tk.Label(table_frame,
                            text=value,
                            bg='#16213e' if row % 2 == 0 else '#1a1a2e',
                            fg='white',
                            font=('Segoe UI', 10),
                            width=20 if col == 0 else 15).grid(row=row, column=col, padx=1, pady=1)
        
        ttk.Button(self.window,
                  text="Cerrar",
                  style='Custom.TButton',
                  command=self.window.destroy,
                  width=15).pack(pady=10)

class LiveMatchWindow:
    """Ventana para simulación de partido en vivo con alineaciones visibles"""
    def __init__(self, parent, match_simulator, home_team_id, away_team_id):
        self.window = tk.Toplevel(parent)
        self.window.title("⚽ Partido en Vivo")
        self.window.geometry("1100x650")
        self.window.configure(bg='#1a1a2e')
        
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, short_name FROM teams WHERE id = ?", (home_team_id,))
        self.home_info = cursor.fetchone()
        cursor.execute("SELECT name, short_name FROM teams WHERE id = ?", (away_team_id,))
        self.away_info = cursor.fetchone()
        conn.close()
        
        from team_colors import get_team_style
        self.home_style = get_team_style(self.home_info[1])
        self.away_style = get_team_style(self.away_info[1])
        
        self.match_simulator = match_simulator
        self.live_match = None
        self.match_id = None
        
        self.create_widgets()
        self.start_match()
    
    def create_widgets(self):
        # ===== MARCADOR SUPERIOR =====
        score_frame = tk.Frame(self.window, bg='#1a1a2e')
        score_frame.pack(pady=8)
        
        # Local
        home_frame = tk.Frame(score_frame, bg=self.home_style['color'], relief='raised', bd=2)
        home_frame.pack(side='left', padx=10)
        tk.Label(home_frame, text=f"{self.home_style['emoji']} {self.home_info[1]}",
                bg=self.home_style['color'], fg='white', font=('Segoe UI', 11, 'bold')).pack(padx=15, pady=3)
        self.home_score_label = tk.Label(home_frame, text="0",
                bg=self.home_style['color'], fg='white', font=('Segoe UI', 30, 'bold'))
        self.home_score_label.pack(padx=15, pady=5)
        
        # Minuto + VS
        mid_frame = tk.Frame(score_frame, bg='#1a1a2e')
        mid_frame.pack(side='left', padx=10)
        self.minute_label = tk.Label(mid_frame, text="0'",
                bg='#1a1a2e', fg='#f1c40f', font=('Segoe UI', 14, 'bold'))
        self.minute_label.pack()
        tk.Label(mid_frame, text="VS", bg='#1a1a2e', fg='#e94560',
                font=('Segoe UI', 12, 'bold')).pack(pady=3)
        
        # Visitante
        away_frame = tk.Frame(score_frame, bg=self.away_style['color'], relief='raised', bd=2)
        away_frame.pack(side='left', padx=10)
        tk.Label(away_frame, text=f"{self.away_style['emoji']} {self.away_info[1]}",
                bg=self.away_style['color'], fg='white', font=('Segoe UI', 11, 'bold')).pack(padx=15, pady=3)
        self.away_score_label = tk.Label(away_frame, text="0",
                bg=self.away_style['color'], fg='white', font=('Segoe UI', 30, 'bold'))
        self.away_score_label.pack(padx=15, pady=5)
        
        # ===== PANEL PRINCIPAL (3 COLUMNAS) =====
        main_panel = tk.Frame(self.window, bg='#1a1a2e')
        main_panel.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Columna IZQUIERDA - Alineación local
        self.left_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=1, width=200)
        self.left_col.pack(side='left', fill='both', padx=3)
        self.left_col.pack_propagate(False)
        
        tk.Label(self.left_col, text=f"{self.home_style['emoji']} {self.home_info[1]}",
                bg=self.home_style['color'], fg='white', font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=2)
        
        self.home_lineup_frame = tk.Frame(self.left_col, bg='#16213e')
        self.home_lineup_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Columna CENTRAL - Eventos
        mid_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=1)
        mid_col.pack(side='left', fill='both', expand=True, padx=3)
        
        tk.Label(mid_col, text="📋 EVENTOS EN DIRECTO", bg='#e94560', fg='white',
                font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=2)
        
        self.events_canvas = tk.Canvas(mid_col, bg='#16213e', highlightthickness=0)
        events_scrollbar = ttk.Scrollbar(mid_col, orient='vertical', command=self.events_canvas.yview)
        self.events_frame = tk.Frame(self.events_canvas, bg='#16213e')
        
        self.events_frame.bind("<Configure>", 
            lambda e: self.events_canvas.configure(scrollregion=self.events_canvas.bbox("all")))
        self.events_canvas.create_window((0, 0), window=self.events_frame, anchor="nw", width=350)
        self.events_canvas.configure(yscrollcommand=events_scrollbar.set)
        
        self.events_canvas.pack(side='left', fill='both', expand=True)
        events_scrollbar.pack(side='right', fill='y')
        
        # Columna DERECHA - Alineación visitante
        self.right_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=1, width=200)
        self.right_col.pack(side='right', fill='both', padx=3)
        self.right_col.pack_propagate(False)
        
        tk.Label(self.right_col, text=f"{self.away_style['emoji']} {self.away_info[1]}",
                bg=self.away_style['color'], fg='white', font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=2)
        
        self.away_lineup_frame = tk.Frame(self.right_col, bg='#16213e')
        self.away_lineup_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        # ===== BOTONES INFERIORES =====
        btn_frame = tk.Frame(self.window, bg='#1a1a2e')
        btn_frame.pack(pady=8)
        
        self.pause_btn = ttk.Button(btn_frame, text="⏸️ Pausar", style='Custom.TButton',
                                   command=self.toggle_pause, width=12)
        self.pause_btn.pack(side='left', padx=3)
        
        ttk.Button(btn_frame, text="⏩ Saltar al final", style='Custom.TButton',
                  command=self.skip_to_end, width=15).pack(side='left', padx=3)
        
        ttk.Button(btn_frame, text="❌ Salir", style='Custom.TButton',
                  command=self.window.destroy, width=10).pack(side='left', padx=3)
    
    def start_match(self):
        """Inicia la simulación en vivo"""
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teams WHERE short_name = ?", (self.home_info[1],))
        home_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM teams WHERE short_name = ?", (self.away_info[1],))
        away_id = cursor.fetchone()[0]
        conn.close()
        
        self.live_match = LiveMatchSimulator(
            self.match_simulator, home_id, away_id,
            callback=self.on_match_update
        )
        self.live_match.simulate_in_thread()
        
        # Actualizar alineaciones después de que se generen
        self.window.after(100, self.update_lineups)
    
    def update_lineups(self):
        """Muestra las alineaciones en los paneles laterales"""
        if not self.live_match:
            return
        
        # Limpiar frames
        for widget in self.home_lineup_frame.winfo_children():
            widget.destroy()
        for widget in self.away_lineup_frame.winfo_children():
            widget.destroy()
        
        # Alineación local
        for i, player in enumerate(self.live_match.home_starting, 1):
            pos_emoji = {'GK': '🧤', 'DEF': '🛡️', 'MID': '⚡', 'FWD': '🎯'}.get(player['position'], '⚽')
            tk.Label(self.home_lineup_frame, 
                    text=f"{pos_emoji} {player['name']}",
                    bg='#16213e', fg='white', font=('Segoe UI', 8), anchor='w').pack(fill='x', pady=1)
        
        # Alineación visitante
        for i, player in enumerate(self.live_match.away_starting, 1):
            pos_emoji = {'GK': '🧤', 'DEF': '🛡️', 'MID': '⚡', 'FWD': '🎯'}.get(player['position'], '⚽')
            tk.Label(self.away_lineup_frame,
                    text=f"{pos_emoji} {player['name']}",
                    bg='#16213e', fg='white', font=('Segoe UI', 8), anchor='w').pack(fill='x', pady=1)
    
    def on_match_update(self, event_type, data):
        """Callback desde el hilo de simulación"""
        self.window.after(0, self._update_gui, event_type, data)
    
    def _update_gui(self, event_type, data):
        """Actualiza la GUI (hilo principal)"""
        if event_type == 'update':
            self.home_score_label.config(text=str(data['home_score']))
            self.away_score_label.config(text=str(data['away_score']))
            if data['minute'] > 90:
                self.minute_label.config(text=f"90'+{data['minute']-90}")
            else:
                self.minute_label.config(text=f"{data['minute']}'")
        
        elif event_type == 'event':
            event = data
            if event['type'] == 'GOAL':
                bg = '#1a472a'; icon = '⚽'
            elif event['type'] in ['YELLOW_CARD']:
                bg = '#7d6608'; icon = '🟨'
            elif event['type'] in ['RED_CARD']:
                bg = '#7b241c'; icon = '🟥'
            elif event['type'] == 'SUBSTITUTION':
                bg = '#1a5276'; icon = '🔄'
            elif event['type'] == 'SAVE':
                bg = '#1a1a2e'; icon = '🧤'
            elif event['type'] == 'SHOT':
                bg = '#16213e'; icon = '🎯'
            elif event['type'] == 'CORNER':
                bg = '#16213e'; icon = '🚩'
            elif event['type'] == 'FOUL':
                bg = '#16213e'; icon = '💢'
            elif event['type'] == 'OFFSIDE':
                bg = '#16213e'; icon = '🏁'
            else:
                bg = '#16213e'; icon = '•'
            
            ef = tk.Frame(self.events_frame, bg=bg)
            ef.pack(fill='x', padx=2, pady=1)
            
            minute = event['minute']
            minute_text = f"{minute}'" if minute <= 90 else f"90'+{minute-90}"
            
            tk.Label(ef, text=f"{minute_text} {icon} {event['description']}",
                    bg=bg, fg='white', font=('Segoe UI', 8),
                    anchor='w', wraplength=330).pack(fill='x', padx=4, pady=1)
            
            self.events_canvas.yview_moveto(1.0)
        
        elif event_type == 'halftime':
            ef = tk.Frame(self.events_frame, bg='#1a1a2e')
            ef.pack(fill='x', padx=2, pady=5)
            tk.Label(ef, text="⏸️  DESCANSO  ⏸️",
                    bg='#1a1a2e', fg='#f1c40f', font=('Segoe UI', 11, 'bold')).pack(pady=8)
            self.events_canvas.yview_moveto(1.0)
        
        elif event_type == 'final':
             self.match_id = self.live_match.saved_match_id
             
             ef = tk.Frame(self.events_frame, bg='#1a1a2e')
             ef.pack(fill='x', padx=2, pady=5)
             tk.Label(ef, text="🏁 FINAL DEL PARTIDO 🏁",
                     bg='#1a1a2e', fg='#f1c40f', font=('Segoe UI', 13, 'bold')).pack(pady=8)
             
             self.events_canvas.yview_moveto(1.0)
             self.pause_btn.config(text="Finalizado", state='disabled')
             
             # Abrir automáticamente la ventana de resultado
             self.window.after(1000, self.show_full_result)
    
    def show_full_result(self):
         """Abre la ventana de resultado detallado"""
         if not self.match_id and self.live_match:
             self.live_match.save_match_to_db()
             self.match_id = self.live_match.saved_match_id
         
         if self.match_id:
             ResultWindow(self.window, self.match_id)
    
    def toggle_pause(self):
        if self.live_match:
            self.live_match.is_paused = not self.live_match.is_paused
            if self.live_match.is_paused:
                self.pause_btn.config(text="▶️ Reanudar")
            else:
                self.pause_btn.config(text="⏸️ Pausar")

    def show_full_result(self):
        """Abre la ventana de resultado detallado y cierra la actual al cerrar resultado"""
        if not self.match_id and self.live_match:
            self.live_match.save_match_to_db()
            self.match_id = self.live_match.saved_match_id
        
        if self.match_id:
            result_win = ResultWindow(self.window, self.match_id)
            # Cuando se cierre la ventana de resultado, cerrar también la de simulación
            def on_result_close():
                if self.window.winfo_exists():
                    self.window.destroy()
            result_win.window.protocol("WM_DELETE_WINDOW", on_result_close)
    
    def skip_to_end(self):
        """Salta al final del partido simulando los eventos restantes"""
        if self.live_match and self.live_match.is_running:
            self.live_match.is_running = False
            
            # Actualizar marcador al resultado final
            self.live_match.home_score = self.live_match.final_home_score
            self.live_match.away_score = self.live_match.final_away_score
            
            self.home_score_label.config(text=str(self.live_match.home_score))
            self.away_score_label.config(text=str(self.live_match.away_score))
            self.minute_label.config(text=f"90'+{self.live_match.stoppage_time}")
            self.pause_btn.config(text="Finalizado", state='disabled')
            
            # Añadir eventos que no se llegaron a mostrar (minuto actual hasta el final)
            current_min = self.live_match.current_minute
            pending_events = [e for e in self.live_match.pregenerated_events 
                             if e['minute'] > current_min]
            
            for event in pending_events:
                # Añadir a la lista de eventos del partido
                self.live_match.match_events.append(event)
                
                # Mostrar en la GUI
                if event['type'] == 'GOAL':
                    bg = '#1a472a'; icon = '⚽'
                elif event['type'] in ['YELLOW_CARD']:
                    bg = '#7d6608'; icon = '🟨'
                elif event['type'] in ['RED_CARD']:
                    bg = '#7b241c'; icon = '🟥'
                elif event['type'] == 'SUBSTITUTION':
                    bg = '#1a5276'; icon = '🔄'
                elif event['type'] == 'SAVE':
                    bg = '#1a1a2e'; icon = '🧤'
                elif event['type'] == 'SHOT':
                    bg = '#16213e'; icon = '🎯'
                elif event['type'] == 'CORNER':
                    bg = '#16213e'; icon = '🚩'
                elif event['type'] == 'FOUL':
                    bg = '#16213e'; icon = '💢'
                elif event['type'] == 'OFFSIDE':
                    bg = '#16213e'; icon = '🏁'
                else:
                    bg = '#16213e'; icon = '•'
                
                ef = tk.Frame(self.events_frame, bg=bg)
                ef.pack(fill='x', padx=2, pady=1)
                
                minute = event['minute']
                minute_text = f"{minute}'" if minute <= 90 else f"90'+{minute-90}"
                
                tk.Label(ef, text=f"{minute_text} {icon} {event['description']}",
                        bg=bg, fg='white', font=('Segoe UI', 8),
                        anchor='w', wraplength=330).pack(fill='x', padx=4, pady=1)
            
            # Mostrar final
            ef = tk.Frame(self.events_frame, bg='#1a1a2e')
            ef.pack(fill='x', padx=2, pady=5)
            tk.Label(ef, text="🏁 FINAL DEL PARTIDO 🏁",
                    bg='#1a1a2e', fg='#f1c40f', font=('Segoe UI', 13, 'bold')).pack(pady=8)
            
            self.events_canvas.yview_moveto(1.0)
            
            # Guardar y abrir resultado
            self.live_match.save_match_to_db()
            self.match_id = self.live_match.saved_match_id
            
            # Abrir resultado automáticamente
            self.window.after(800, self.show_full_result)

class SeasonWindow:
    """Ventana para el modo temporada con jornadas"""
    def __init__(self, parent, match_simulator):
        self.window = tk.Toplevel(parent)
        self.window.title("🏆 Modo Temporada")
        self.window.geometry("950x700")
        self.window.configure(bg='#1a1a2e')
        
        self.ms = match_simulator
        self.season = SeasonManager()
        
        # Iniciar temporada
        num_teams, total_rounds = self.season.initialize_season()
        
        self.create_widgets()
        self.update_view()
    
    def create_widgets(self):
        # Título
        header = tk.Frame(self.window, bg='#1a1a2e')
        header.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(header, text="🏆 MODO TEMPORADA",
                 style='Custom.TLabel', font=('Segoe UI', 18, 'bold')).pack(side='left')
        
        self.progress_label = ttk.Label(header, text="",
                                        style='Custom.TLabel', font=('Segoe UI', 10))
        self.progress_label.pack(side='right')
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(self.window, length=900, mode='determinate')
        self.progress_bar.pack(padx=20, pady=5)
        
        # Navegación de jornadas
        nav_frame = tk.Frame(self.window, bg='#16213e', relief='ridge', bd=2)
        nav_frame.pack(fill='x', padx=20, pady=8)
        
        ttk.Button(nav_frame, text="◀◀ Primera", style='Custom.TButton',
                  command=lambda: self.go_to_round(1), width=12).pack(side='left', padx=5, pady=5)
        
        ttk.Button(nav_frame, text="◀ Anterior", style='Custom.TButton',
                  command=lambda: self.go_to_round(self.current_round - 1), width=12).pack(side='left', padx=5, pady=5)
        
        self.round_label = tk.Label(nav_frame, text="Jornada 1 de 10",
                                    bg='#16213e', fg='white', font=('Segoe UI', 14, 'bold'))
        self.round_label.pack(side='left', expand=True, pady=5)
        
        ttk.Button(nav_frame, text="Siguiente ▶", style='Custom.TButton',
                  command=lambda: self.go_to_round(self.current_round + 1), width=12).pack(side='right', padx=5, pady=5)
        
        ttk.Button(nav_frame, text="Última ▶▶", style='Custom.TButton',
                  command=lambda: self.go_to_round(self.season.total_rounds), width=12).pack(side='right', padx=5, pady=5)
        
        # Panel principal: partidos + clasificación
        main_panel = tk.Frame(self.window, bg='#1a1a2e')
        main_panel.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Columna izquierda: Partidos de la jornada
        left_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=2)
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(left_col, text="⚽ PARTIDOS DE LA JORNADA", bg='#16213e', fg='#e94560',
                font=('Segoe UI', 11, 'bold')).pack(fill='x', pady=5)
        
        self.matches_frame = tk.Frame(left_col, bg='#16213e')
        self.matches_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botón simular jornada
        btn_frame = tk.Frame(left_col, bg='#16213e')
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        self.sim_round_btn = ttk.Button(btn_frame, text="⚡ Simular Jornada Completa",
                                        style='Custom.TButton', command=self.simulate_round, width=25)
        self.sim_round_btn.pack(pady=3)
        
        # Columna derecha: Clasificación
        right_col = tk.Frame(main_panel, bg='#16213e', relief='ridge', bd=2)
        right_col.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(right_col, text="📊 CLASIFICACIÓN", bg='#16213e', fg='#e94560',
                font=('Segoe UI', 11, 'bold')).pack(fill='x', pady=5)
        
        self.standings_frame = tk.Frame(right_col, bg='#16213e')
        self.standings_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Botones inferiores
        bottom_frame = tk.Frame(self.window, bg='#1a1a2e')
        bottom_frame.pack(fill='x', padx=15, pady=8)
        
        ttk.Button(bottom_frame, text="🔄 Nueva Temporada", style='Custom.TButton',
                  command=self.new_season, width=18).pack(side='left', padx=3)
        
        ttk.Button(bottom_frame, text="📊 Ver Estadísticas", style='Custom.TButton',
                  command=self.show_stats, width=18).pack(side='left', padx=3)
        
        ttk.Button(bottom_frame, text="❌ Salir", style='Custom.TButton',
                  command=self.window.destroy, width=12).pack(side='right', padx=3)
        
        self.current_round = 1
    
    def update_view(self):
        """Actualiza toda la ventana"""
        progress = self.season.get_season_progress()
        
        # Actualizar barra de progreso
        self.progress_bar['value'] = progress['progress_percent']
        self.progress_label.config(text=f"Progreso: {progress['progress_percent']:.1f}% | "
                                    f"{progress['played']}/{progress['total']} partidos")
        
        # Actualizar etiqueta de jornada
        total = progress['total_rounds']
        self.round_label.config(text=f"Jornada {self.current_round} de {total}")
        
        # Actualizar partidos
        self.update_matches()
        
        # Actualizar clasificación
        self.update_standings()
        
        # Actualizar botón simular
        round_info = self.season.get_round_info(self.current_round)
        if round_info:
            all_played = all(m['played'] for m in round_info['matches'])
            self.sim_round_btn.config(state='disabled' if all_played else 'normal',
                                      text="✅ Jornada Completada" if all_played else "⚡ Simular Jornada Completa")
    
    def update_matches(self):
        """Actualiza el panel de partidos"""
        for widget in self.matches_frame.winfo_children():
            widget.destroy()
        
        round_info = self.season.get_round_info(self.current_round)
        if not round_info:
            return
        
        from team_colors import get_team_style
        
        for i, match in enumerate(round_info['matches']):
            home_style = get_team_style(match['home_name'])
            away_style = get_team_style(match['away_name'])
            
            match_frame = tk.Frame(self.matches_frame, bg='#1a1a2e' if i % 2 == 0 else '#16213e',
                                  relief='groove', bd=1)
            match_frame.pack(fill='x', pady=2)
            
            # Equipo local
            tk.Label(match_frame, text=f"{home_style['emoji']} {match['home_name']}",
                    bg=match_frame['bg'], fg=home_style['color'],
                    font=('Segoe UI', 10, 'bold'), width=12, anchor='e').pack(side='left', padx=5, pady=3)
            
            # Resultado o VS
            if match['played']:
                result_text = f"  {match['home_score']} - {match['away_score']}  "
                result_frame = tk.Frame(match_frame, bg=match_frame['bg'])
                result_frame.pack(side='left', padx=5)
                
                tk.Label(result_frame, text=result_text,
                        bg=match_frame['bg'], fg='white',
                        font=('Segoe UI', 11, 'bold')).pack()
                
                # Botón para ver detalle
                ttk.Button(result_frame, text="📋", width=3,
                          command=lambda mid=match['match_id']: ResultWindow(self.window, mid)).pack()
            else:
                tk.Label(match_frame, text="  VS  ",
                        bg=match_frame['bg'], fg='#e94560',
                        font=('Segoe UI', 10, 'bold')).pack(side='left', padx=5, pady=3)
                
                # Botón para simular este partido en vivo
                ttk.Button(match_frame, text="▶ Simular",
                          command=lambda hid=match['home_id'], aid=match['away_id']: 
                          self.simulate_live_match(hid, aid), width=10).pack(side='left', padx=3)
            
            # Equipo visitante
            tk.Label(match_frame, text=f"{match['away_name']} {away_style['emoji']}",
                    bg=match_frame['bg'], fg=away_style['color'],
                    font=('Segoe UI', 10, 'bold'), width=12, anchor='w').pack(side='right', padx=5, pady=3)
    
    def update_standings(self):
        """Actualiza la tabla de clasificación"""
        for widget in self.standings_frame.winfo_children():
            widget.destroy()
        
        standings = self.season.get_standings()
        from team_colors import get_team_style
        
        # Cabecera
        headers = ['POS', 'EQUIPO', 'PJ', 'PTS']
        widths = [4, 18, 4, 5]
        for col, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(self.standings_frame, text=h, bg='#e94560', fg='white',
                    font=('Segoe UI', 9, 'bold'), width=w).grid(row=0, column=col, padx=1, pady=1)
        
        for pos, (team_id, data) in enumerate(standings, 1):
            style = get_team_style(data['short'])
            bg = '#16213e' if pos % 2 == 0 else '#1a1a2e'
            
            tk.Label(self.standings_frame, text=str(pos),
                    bg=bg, fg='white', font=('Segoe UI', 9), width=4).grid(row=pos, column=0, padx=1, pady=1)
            
            tk.Label(self.standings_frame, text=f"{style['emoji']} {data['short']}",
                    bg=style['color'], fg='white', font=('Segoe UI', 9, 'bold'),
                    width=18, anchor='w').grid(row=pos, column=1, padx=1, pady=1)
            
            tk.Label(self.standings_frame, text=str(data['played']),
                    bg=bg, fg='white', font=('Segoe UI', 9), width=4).grid(row=pos, column=2, padx=1, pady=1)
            
            tk.Label(self.standings_frame, text=str(data['points']),
                    bg=bg, fg='#f1c40f' if pos == 1 else 'white',
                    font=('Segoe UI', 10, 'bold'), width=5).grid(row=pos, column=3, padx=1, pady=1)
    
    def go_to_round(self, round_num):
        """Navega a una jornada específica"""
        if 1 <= round_num <= self.season.total_rounds:
            self.current_round = round_num
            self.update_view()
    
    def simulate_round(self):
        """Simula todos los partidos pendientes de la jornada actual"""
        round_info = self.season.get_round_info(self.current_round)
        if not round_info:
            return
        
        pending = [m for m in round_info['matches'] if not m['played']]
        
        if not pending:
            messagebox.showinfo("Info", "Todos los partidos de esta jornada ya se han jugado.")
            return
        
        # Simular partidos pendientes (rápido, sin ventana en vivo)
        for match in pending:
            self.ms.simulate_match(match['home_id'], match['away_id'])
        
        self.update_view()
        
        # Mostrar resumen
        messagebox.showinfo("Jornada Completada", 
                          f"✅ Jornada {self.current_round} completada.\n"
                          f"📊 {len(pending)} partidos simulados.")
    
    def simulate_live_match(self, home_id, away_id):
        """Abre la simulación en vivo para un partido y actualiza al cerrar"""
        live_win = LiveMatchWindow(self.window, self.ms, home_id, away_id)
        # Esperar a que termine y actualizar
        self.window.after(500, lambda: self._check_and_update(live_win))

    def _check_and_update(self, live_win):
        """Comprueba si el partido terminó y actualiza"""
        if live_win.window.winfo_exists():
            # La ventana sigue abierta, volver a comprobar
            self.window.after(1000, lambda: self._check_and_update(live_win))
        else:
            # La ventana se cerró, actualizar
            self.update_view()
    
    def new_season(self):
        """Inicia una nueva temporada"""
        if messagebox.askyesno("⚠️ Confirmar", "¿Iniciar nueva temporada? Se borrarán todos los resultados."):
            self.season.initialize_season()
            self.current_round = 1
            self.update_view()
    
    def show_stats(self):
        """Muestra estadísticas de la temporada"""
        StatsWindow(self.window)

# ============ INICIO DE LA APLICACIÓN ============
if __name__ == "__main__":
    root = tk.Tk()
    app = FootballManagerGUI(root)
    root.mainloop()
    app.close()