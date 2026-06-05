import sqlite3
import random

class SeasonManager:
    def __init__(self):
        self.conn = sqlite3.connect("football_manager.db")
        self.cursor = self.conn.cursor()
        self.fixtures = []  # Lista de jornadas, cada jornada = lista de partidos
        self.current_round = 0
        self.total_rounds = 0
        self.played_matches = 0
        
    def initialize_season(self):
        """Inicia una nueva temporada generando el calendario"""
        # Limpiar partidos anteriores
        self.cursor.execute("DELETE FROM match_events")
        self.cursor.execute("DELETE FROM match_lineups")
        self.cursor.execute("DELETE FROM match_stats")
        self.cursor.execute("DELETE FROM matches")
        self.cursor.execute("DELETE FROM suspensions")
        self.conn.commit()
        
        # Obtener equipos
        self.cursor.execute("SELECT id, name, short_name FROM teams ORDER BY id")
        teams = self.cursor.fetchall()
        n = len(teams)
        
        # Generar calendario: sistema round-robin ida y vuelta
        self.fixtures = []
        self.total_rounds = (n - 1) * 2  # Ida y vuelta
        
        # Crear lista de equipos para round-robin
        team_ids = [t[0] for t in teams]
        
        # Primera vuelta
        first_half = self._generate_round_robin(team_ids)
        # Segunda vuelta (invertir local/visitante)
        second_half = [[(away, home) for home, away in round_matches] for round_matches in first_half]
        
        self.fixtures = first_half + second_half
        self.current_round = 0
        self.played_matches = 0
        
        return len(teams), self.total_rounds
    
    def _generate_round_robin(self, teams):
        """Algoritmo round-robin para generar emparejamientos"""
        if len(teams) % 2 != 0:
            teams = teams + [None]  # Descanso si número impar
        
        n = len(teams)
        rounds = []
        
        for r in range(n - 1):
            round_matches = []
            for i in range(n // 2):
                home = teams[i]
                away = teams[n - 1 - i]
                if home is not None and away is not None:
                    round_matches.append((home, away))
            rounds.append(round_matches)
            
            # Rotar equipos (excepto el primero)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]
        
        return rounds
    
    def get_round_info(self, round_number):
        """Obtiene información de una jornada específica"""
        if round_number < 1 or round_number > self.total_rounds:
            return None
        
        round_index = round_number - 1
        matches = self.fixtures[round_index]
        
        result = {
            'round': round_number,
            'is_first_half': round_number <= self.total_rounds // 2,
            'matches': []
        }
        
        for home_id, away_id in matches:
            # Ver si el partido ya se jugó
            self.cursor.execute('''
                SELECT id, home_score, away_score, played FROM matches
                WHERE home_team_id = ? AND away_team_id = ? 
                AND match_date LIKE ?
            ''', (home_id, away_id, '%'))
            
            match_data = self.cursor.fetchone()
            
            match_info = {
                'home_id': home_id,
                'away_id': away_id,
                'played': False,
                'match_id': None,
                'home_score': None,
                'away_score': None
            }
            
            if match_data:
                match_info['played'] = match_data[3] == 1
                match_info['match_id'] = match_data[0]
                match_info['home_score'] = match_data[1]
                match_info['away_score'] = match_data[2]
            
            # Obtener nombres
            self.cursor.execute("SELECT short_name FROM teams WHERE id = ?", (home_id,))
            match_info['home_name'] = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT short_name FROM teams WHERE id = ?", (away_id,))
            match_info['away_name'] = self.cursor.fetchone()[0]
            
            result['matches'].append(match_info)
        
        return result
    
    def get_season_progress(self):
        """Obtiene el progreso de la temporada"""
        self.cursor.execute("SELECT COUNT(*) FROM matches WHERE played = 1")
        self.played_matches = self.cursor.fetchone()[0]
        
        total_matches = (len(self.fixtures[0]) if self.fixtures else 0) * self.total_rounds
        
        return {
            'played': self.played_matches,
            'total': total_matches,
            'current_round': (self.played_matches // len(self.fixtures[0])) + 1 if self.fixtures else 0,
            'total_rounds': self.total_rounds,
            'progress_percent': (self.played_matches / total_matches * 100) if total_matches > 0 else 0
        }
    
    def get_standings(self):
        """Calcula la clasificación actual"""
        self.cursor.execute('''
            SELECT m.home_team_id, m.away_team_id, m.home_score, m.away_score
            FROM matches m WHERE m.played = 1
        ''')
        matches = self.cursor.fetchall()
        
        stats = {}
        self.cursor.execute("SELECT id, name, short_name FROM teams")
        for team_id, name, short in self.cursor.fetchall():
            stats[team_id] = {
                'name': name, 'short': short,
                'points': 0, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
                'gf': 0, 'ga': 0
            }
        
        for home_id, away_id, hs, aw in matches:
            if home_id in stats:
                stats[home_id]['played'] += 1
                stats[home_id]['gf'] += hs
                stats[home_id]['ga'] += aw
                if hs > aw:
                    stats[home_id]['won'] += 1
                    stats[home_id]['points'] += 3
                elif hs == aw:
                    stats[home_id]['drawn'] += 1
                    stats[home_id]['points'] += 1
                else:
                    stats[home_id]['lost'] += 1
            
            if away_id in stats:
                stats[away_id]['played'] += 1
                stats[away_id]['gf'] += aw
                stats[away_id]['ga'] += hs
                if aw > hs:
                    stats[away_id]['won'] += 1
                    stats[away_id]['points'] += 3
                elif aw == hs:
                    stats[away_id]['drawn'] += 1
                    stats[away_id]['points'] += 1
                else:
                    stats[away_id]['lost'] += 1
        
        sorted_stats = sorted(stats.items(),
                            key=lambda x: (x[1]['points'], x[1]['gf'] - x[1]['ga'], x[1]['gf']),
                            reverse=True)
        return sorted_stats
    
    def close(self):
        self.conn.close()