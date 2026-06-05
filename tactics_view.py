import tkinter as tk
from tkinter import ttk
import sqlite3
from team_colors import get_team_style

class TacticsViewer:
    """Ventana para mostrar la formación táctica"""
    def __init__(self, parent, match_id=None, team_id=None):
        self.window = tk.Toplevel(parent)
        self.window.title("🎯 Visor Táctico")
        self.window.geometry("900x700")
        self.window.configure(bg='#1a1a2e')
        
        self.match_id = match_id
        self.team_id = team_id
        
        if match_id:
            self.show_match_tactics()
        elif team_id:
            self.show_team_tactics()
    
    def show_match_tactics(self):
        """Muestra las tácticas de un partido"""
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        # Obtener datos del partido
        cursor.execute('''
            SELECT th.id, th.short_name, ta.id, ta.short_name
            FROM matches m
            JOIN teams th ON m.home_team_id = th.id
            JOIN teams ta ON m.away_team_id = ta.id
            WHERE m.id = ?
        ''', (self.match_id,))
        
        match_data = cursor.fetchone()
        if not match_data:
            conn.close()
            return
        
        home_id, home_short, away_id, away_short = match_data
        conn.close()
        
        # Título
        from team_colors import get_team_style
        home_style = get_team_style(home_short)
        away_style = get_team_style(away_short)
        
        ttk.Label(self.window,
                 text=f"🎯 FORMACIONES DEL PARTIDO",
                 style='Custom.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Frame para dos campos
        fields_frame = tk.Frame(self.window, bg='#1a1a2e')
        fields_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Campo local
        self.draw_field(fields_frame, home_id, home_short, home_style, 'left')
        
        # Separador
        tk.Frame(fields_frame, bg='#e94560', width=2).pack(side='left', fill='y', padx=10)
        
        # Campo visitante
        self.draw_field(fields_frame, away_id, away_short, away_style, 'right')
        
        ttk.Button(self.window,
                  text="Cerrar",
                  style='Custom.TButton',
                  command=self.window.destroy,
                  width=15).pack(pady=10)
    
    def draw_field(self, parent, team_id, team_short, team_style, side):
        """Dibuja un campo de fútbol con la formación"""
        from simulation.tactics import TacticsManager
        tm = TacticsManager()
        
        tactics = tm.get_team_tactics(team_id)
        players = tm.get_team_players_with_positions(team_id)
        formation_positions = tm.get_formation_positions(tactics['formation_name'])
        
        # Frame del campo
        field_frame = tk.Frame(parent, bg=team_style['color'], relief='raised', bd=2)
        field_frame.pack(side=side, fill='both', expand=True, padx=5)
        
        # Nombre del equipo y formación
        tk.Label(field_frame,
                text=f"{team_style['emoji']} {team_short}",
                bg=team_style['color'],
                fg='white',
                font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        tk.Label(field_frame,
                text=tactics['formation_name'],
                bg=team_style['color'],
                fg='#f1c40f',
                font=('Segoe UI', 10, 'bold')).pack()
        
        tk.Label(field_frame,
                text=f"Estilo: {tactics['style']} | Mentalidad: {tactics['mentality']}",
                bg=team_style['color'],
                fg='white',
                font=('Segoe UI', 8)).pack()
        
        # Canvas para dibujar el campo
        canvas = tk.Canvas(field_frame, bg='#27ae60', height=400, width=350, highlightthickness=0)
        canvas.pack(pady=10)
        
        # Dibujar líneas del campo
        self.draw_pitch(canvas, 350, 400)
        
        # Filtrar jugadores no sancionados
        from simulation.match_simulator import MatchSimulator
        ms = MatchSimulator()
        suspended_ids = ms.get_suspended_player_ids(team_id)
        ms.close()
        
        available_players = [p for p in players if p['id'] not in suspended_ids]
        
        # Seleccionar 11 titulares
        starting = tm.get_starting_eleven_with_positions(available_players, tactics['formation_name'])
        
        # Dibujar jugadores en el campo
        for player in starting:
            x = player.get('field_x', 50) * 3.3 + 10
            y = player.get('field_y', 50) * 3.8 + 10
            
            # Color según posición
            if player['position'] == 'GK':
                color = '#f1c40f'
            elif player['position'] == 'DEF':
                color = '#3498db'
            elif player['position'] == 'MID':
                color = '#2ecc71'
            else:
                color = '#e74c3c'
            
            # Dibujar círculo del jugador
            canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, outline='white', width=2)
            canvas.create_text(x, y-18, text=player['number'], fill='white', font=('Arial', 8, 'bold'))
            canvas.create_text(x, y+18, text=player['name'].split()[-1][:8], fill='white', font=('Arial', 7))
        
        tm.close()
    
    def draw_pitch(self, canvas, width, height):
        """Dibuja un campo de fútbol"""
        # Césped
        canvas.create_rectangle(5, 5, width-5, height-5, outline='white', width=2)
        
        # Línea de medio campo
        canvas.create_line(5, height//2, width-5, height//2, fill='white', width=2)
        
        # Círculo central
        canvas.create_oval(width//2-30, height//2-30, width//2+30, height//2+30, outline='white', width=2)
        
        # Áreas
        canvas.create_rectangle(30, 10, width-30, 80, outline='white', width=2)
        canvas.create_rectangle(30, height-80, width-30, height-10, outline='white', width=2)
        
        # Áreas pequeñas
        canvas.create_rectangle(80, 10, width-80, 40, outline='white', width=1)
        canvas.create_rectangle(80, height-40, width-80, height-10, outline='white', width=1)
        
        # Porterías
        canvas.create_rectangle(100, 2, width-100, 10, outline='white', width=2)
        canvas.create_rectangle(100, height-10, width-100, height-2, outline='white', width=2)
    
    def show_team_tactics(self):
        """Muestra la táctica de un equipo"""
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        cursor.execute("SELECT short_name FROM teams WHERE id = ?", (self.team_id,))
        team_short = cursor.fetchone()[0]
        conn.close()
        
        team_style = get_team_style(team_short)
        
        ttk.Label(self.window,
                 text=f"🎯 TÁCTICA DE {team_short}",
                 style='Custom.TLabel',
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        self.draw_field(self.window, self.team_id, team_short, team_style, 'left')