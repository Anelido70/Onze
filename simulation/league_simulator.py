import sqlite3
from simulation.match_simulator import MatchSimulator

class LeagueSimulator:
    def __init__(self):
        self.conn = sqlite3.connect("football_manager.db")
        self.cursor = self.conn.cursor()
        self.simulator = MatchSimulator()
    
    def simulate_season(self):
        """Simula una temporada completa: todos contra todos ida y vuelta"""
        
        # Obtener todos los equipos
        self.cursor.execute("SELECT id, name, short_name FROM teams")
        teams = self.cursor.fetchall()
        
        print("=" * 70)
        print("🏆 LIGA TEMPORADA 2024-2025")
        print("=" * 70)
        print(f"\n📊 {len(teams)} equipos participantes:")
        for team in teams:
            print(f"  • {team[2]} - {team[1]}")
        
        # Generar calendario: todos contra todos ida y vuelta
        fixtures = self.generate_fixtures(teams)
        
        total_matches = len(fixtures)
        print(f"\n⚽ Comenzando temporada ({total_matches} partidos)...\n")
        
        # Simular primera vuelta
        print("📅 PRIMERA VUELTA:")
        print("-" * 70)
        mid_point = total_matches // 2
        
        for i, (home, away) in enumerate(fixtures[:mid_point], 1):
            result = self.simulator.simulate_match(home[0], away[0])
            self.print_result(i, result, home[2], away[2])
        
        # Simular segunda vuelta
        print(f"\n📅 SEGUNDA VUELTA:")
        print("-" * 70)
        
        for i, (home, away) in enumerate(fixtures[mid_point:], mid_point + 1):
            result = self.simulator.simulate_match(home[0], away[0])
            self.print_result(i, result, home[2], away[2])
        
        print("\n" + "=" * 70)
        print("✅ TEMPORADA COMPLETADA!")
        print(f"📊 {total_matches} partidos jugados")
        
        # Mostrar tabla de clasificación
        self.show_standings()
    
    def generate_fixtures(self, teams):
        """Genera el calendario completo: ida y vuelta"""
        fixtures = []
        n = len(teams)
        
        # Primera vuelta: todos contra todos
        for i in range(n):
            for j in range(n):
                if i != j:
                    fixtures.append(teams[i])  # equipo local
                    fixtures.append(teams[j])  # equipo visitante
                    # Pero necesitamos pares, así que reestructuramos
        
        # Mejor hacerlo así:
        fixtures = []
        for i in range(n):
            for j in range(n):
                if i != j:
                    fixtures.append((teams[i], teams[j]))
        
        return fixtures
    
    def print_result(self, match_num, result, home_short, away_short):
        """Imprime resultado de un partido"""
        print(f"  J{match_num:2d}: {home_short} {result['home_score']} - "
              f"{result['away_score']} {away_short} "
              f"(Poder: {result['home_power']} vs {result['away_power']})")
    
    def show_standings(self):
        """Calcula y muestra la tabla de clasificación"""
        
        print("\n" + "=" * 70)
        print("📊 TABLA DE CLASIFICACIÓN")
        print("=" * 70)
        
        # Obtener todos los partidos jugados
        self.cursor.execute('''
            SELECT 
                m.home_team_id, m.away_team_id, 
                m.home_score, m.away_score
            FROM matches m
            WHERE m.played = 1
        ''')
        
        matches = self.cursor.fetchall()
        
        # Calcular estadísticas por equipo
        stats = {}
        self.cursor.execute("SELECT id, short_name, name FROM teams")
        for team_id, short_name, name in self.cursor.fetchall():
            stats[team_id] = {
                'name': name,
                'short': short_name,
                'points': 0,
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'gf': 0,
                'ga': 0,
            }
        
        # Procesar cada partido
        for match in matches:
            home_id, away_id, home_score, away_score = match
            
            if home_id in stats and away_id in stats:
                # Actualizar estadísticas local
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
                
                # Actualizar estadísticas visitante
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
        
        # Ordenar por puntos, diferencia de goles, goles a favor
        sorted_stats = sorted(stats.items(), 
                             key=lambda x: (x[1]['points'], 
                                           x[1]['gf'] - x[1]['ga'],
                                           x[1]['gf']), 
                             reverse=True)
        
        # Mostrar tabla
        print(f"\n{'POS':<4} {'EQUIPO':<25} {'PJ':<4} {'PG':<4} {'PE':<4} {'PP':<4} {'GF':<4} {'GC':<4} {'DG':<5} {'PTS':<4}")
        print("-" * 75)
        
        for pos, (team_id, data) in enumerate(sorted_stats, 1):
            dg = data['gf'] - data['ga']
            print(f"{pos:<4} {data['name']:<25} {data['played']:<4} {data['won']:<4} "
                  f"{data['drawn']:<4} {data['lost']:<4} {data['gf']:<4} {data['ga']:<4} "
                  f"{dg:+<5} {data['points']:<4}")
    
    def close(self):
        self.simulator.close()
        self.conn.close()