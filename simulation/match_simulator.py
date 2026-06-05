import sqlite3
import random
from datetime import datetime

class MatchSimulator:
    def __init__(self):
        self.conn = sqlite3.connect("football_manager.db")
        self.cursor = self.conn.cursor()
        random.seed()
        
    def simulate_match(self, home_team_id, away_team_id):
        """Simula un partido completo entre dos equipos"""
        
        home_team = self.get_team_stats(home_team_id)
        away_team = self.get_team_stats(away_team_id)
        
        # Filtrar jugadores sancionados
        home_team = self.filter_suspended_players(home_team, home_team_id)
        away_team = self.filter_suspended_players(away_team, away_team_id)
        
        home_power = self.calculate_team_power(home_team)
        away_power = self.calculate_team_power(away_team)
        
        home_score, away_score = self.simulate_score(home_power, away_power)
        
        self.cursor.execute('''
            INSERT INTO matches (home_team_id, away_team_id, home_score, away_score, match_date, played)
            VALUES (?, ?, ?, ?, datetime('now'), 1)
        ''', (home_team_id, away_team_id, home_score, away_score))
        match_id = self.cursor.lastrowid
        
        self.generate_match_events(match_id, home_team_id, away_team_id, 
                                   home_score, away_score, home_team, away_team)
        
        # Generar estadísticas del partido
        self.generate_match_stats(match_id, home_team_id, away_team_id, home_team, away_team, home_score, away_score)
        
        self.conn.commit()
        
        return {
            'match_id': match_id,
            'home_team': home_team['name'],
            'away_team': away_team['name'],
            'home_score': home_score,
            'away_score': away_score,
            'home_power': home_power,
            'away_power': away_power
        }
    
    def filter_suspended_players(self, team, team_id):
        """Filtra los jugadores sancionados del equipo"""
        suspended = self.get_suspended_player_ids(team_id)
        
        if suspended:
            # Guardar los sancionados para mostrarlos
            team['suspended_players'] = [p for p in team['players'] if p['id'] in suspended]
            # Filtrar jugadores disponibles
            team['players'] = [p for p in team['players'] if p['id'] not in suspended]
        else:
            team['suspended_players'] = []
        
        return team
    
    def get_suspended_player_ids(self, team_id):
        """Obtiene IDs de jugadores sancionados de un equipo"""
        self.cursor.execute('''
            SELECT DISTINCT s.player_id
            FROM suspensions s
            JOIN players p ON s.player_id = p.id
            WHERE p.team_id = ? AND s.active = 1
        ''', (team_id,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_team_stats(self, team_id):
        """Obtiene todos los jugadores de un equipo con sus stats"""
        self.cursor.execute('''
            SELECT t.name, t.short_name, p.id, p.name, p.position, 
                   p.attack, p.defense, p.midfield, p.goalkeeping, p.stamina, p.speed
            FROM teams t
            JOIN players p ON t.id = p.team_id
            WHERE t.id = ?
        ''', (team_id,))
        
        team_data = {
            'name': '',
            'short_name': '',
            'players': []
        }
        
        for row in self.cursor.fetchall():
            team_data['name'] = row[0]
            team_data['short_name'] = row[1]
            team_data['players'].append({
                'id': row[2],
                'name': row[3],
                'position': row[4],
                'attack': row[5],
                'defense': row[6],
                'midfield': row[7],
                'goalkeeping': row[8],
                'stamina': row[9],
                'speed': row[10]
            })
        
        return team_data
    
    def calculate_team_power(self, team):
        """Calcula la fuerza general del equipo basado en sus jugadores"""
        if not team['players']:
            return 50
        
        gk = [p for p in team['players'] if p['position'] == 'GK']
        defs = [p for p in team['players'] if p['position'] == 'DEF']
        mids = [p for p in team['players'] if p['position'] == 'MID']
        fwds = [p for p in team['players'] if p['position'] == 'FWD']
        
        gk_avg = sum(p['goalkeeping'] for p in gk) / max(len(gk), 1)
        def_avg = sum(p['defense'] for p in defs) / max(len(defs), 1)
        mid_avg = sum(p['midfield'] for p in mids) / max(len(mids), 1)
        att_avg = sum(p['attack'] for p in fwds) / max(len(fwds), 1)
        
        power = (def_avg * 0.25 + mid_avg * 0.30 + att_avg * 0.30 + gk_avg * 0.15)
        
        return int(power)
    
    def simulate_score(self, home_power, away_power):
        """Simula el marcador basado en la diferencia de poder"""
        home_advantage = home_power * 1.05
        power_diff = home_advantage - away_power
        base_goals = 1.5
        
        if power_diff > 10:
            home_expected = base_goals + 1.0
            away_expected = base_goals - 0.5
        elif power_diff > 5:
            home_expected = base_goals + 0.5
            away_expected = base_goals - 0.2
        elif power_diff < -10:
            home_expected = base_goals - 0.5
            away_expected = base_goals + 1.0
        elif power_diff < -5:
            home_expected = base_goals - 0.2
            away_expected = base_goals + 0.5
        else:
            home_expected = base_goals
            away_expected = base_goals
        
        home_score = max(0, int(round(random.gauss(home_expected, 0.8))))
        away_score = max(0, int(round(random.gauss(away_expected, 0.8))))
        
        home_score = min(home_score, 6)
        away_score = min(away_score, 6)
        
        return home_score, away_score
    
    def get_starting_eleven(self, team):
        """Selecciona el 11 titular usando la formación táctica del equipo"""
        # Obtener el team_id del primer jugador
        if not team['players']:
            return []
        
        team_id = None
        self.cursor.execute("SELECT team_id FROM players WHERE id = ?", (team['players'][0]['id'],))
        result = self.cursor.fetchone()
        if result:
            team_id = result[0]
        
        if team_id:
            from simulation.tactics import TacticsManager
            tm = TacticsManager()
            tactics = tm.get_team_tactics(team_id)
            formation_name = tactics['formation_name']
            positioned = tm.get_starting_eleven_with_positions(team['players'], formation_name)
            tm.close()
            return positioned
        
        # Fallback: selección manual
        gk = sorted([p for p in team['players'] if p['position'] == 'GK'], 
                   key=lambda x: x['goalkeeping'], reverse=True)
        defs = sorted([p for p in team['players'] if p['position'] == 'DEF'], 
                     key=lambda x: x['defense'], reverse=True)
        mids = sorted([p for p in team['players'] if p['position'] == 'MID'], 
                     key=lambda x: x['midfield'], reverse=True)
        fwds = sorted([p for p in team['players'] if p['position'] == 'FWD'], 
                     key=lambda x: x['attack'], reverse=True)
        
        starting = []
        if gk: starting.append(gk[0])
        starting.extend(defs[:4])
        starting.extend(mids[:4])
        starting.extend(fwds[:2])
        
        all_players = team['players'].copy()
        for p in starting:
            if p in all_players:
                all_players.remove(p)
        while len(starting) < 11 and all_players:
            starting.append(all_players.pop(0))
        
        return starting[:11]
    
    def get_substitutes(self, team, starting_eleven):
        """Obtiene los suplentes (jugadores no titulares)"""
        starting_ids = [p['id'] for p in starting_eleven]
        return [p for p in team['players'] if p['id'] not in starting_ids][:7]
    
    def generate_match_events(self, match_id, home_id, away_id, home_score, away_score, home_team, away_team):
        """Genera los eventos detallados del partido con sistema de tarjetas"""
        events = []
        
        # Procesar sanciones de partidos anteriores
        self.process_suspensions()
        
        # Seleccionar alineaciones
        home_starting = self.get_starting_eleven(home_team)
        away_starting = self.get_starting_eleven(away_team)
        home_subs = self.get_substitutes(home_team, home_starting)
        away_subs = self.get_substitutes(away_team, away_starting)
        
        # Guardar alineaciones en la BD
        self.save_lineup(match_id, home_id, home_starting, 'home')
        self.save_lineup(match_id, away_id, away_starting, 'away')
        
        # Simular sustituciones (2-4 por partido)
        substitutions = []
        num_subs = random.randint(2, 4)
        sub_minutes = sorted(random.sample(range(60, 90), min(num_subs, 30)))
        
        for minute in sub_minutes:
            if random.random() < 0.5 and home_subs:
                player_out = random.choice(home_starting[1:])  # No cambiar portero
                player_in = home_subs.pop(0) if home_subs else None
                if player_in:
                    events.append((match_id, minute, 'SUBSTITUTION', player_out['id'],
                                 f"🔄 Cambio en {home_team['short_name']}: Sale {player_out['name']}, entra {player_in['name']}", 0))
                    substitutions.append((player_out, player_in, 'home'))
                    # Actualizar alineación
                    home_starting.remove(player_out)
                    home_starting.append(player_in)
            elif away_subs:
                player_out = random.choice(away_starting[1:])
                player_in = away_subs.pop(0) if away_subs else None
                if player_in:
                    events.append((match_id, minute, 'SUBSTITUTION', player_out['id'],
                                 f"🔄 Cambio en {away_team['short_name']}: Sale {player_out['name']}, entra {player_in['name']}", 0))
                    substitutions.append((player_out, player_in, 'away'))
                    away_starting.remove(player_out)
                    away_starting.append(player_in)
        
        # Calcular goles totales
        total_goals = home_score + away_score
        
        # Distribuir goles en el tiempo
        goal_minutes = []
        if total_goals > 0:
            possible_minutes = list(range(1, 91))
            goal_minutes = sorted(random.sample(possible_minutes, min(total_goals, len(possible_minutes))))
        
        home_goals_to_score = home_score
        away_goals_to_score = away_score
        home_goals_scored = 0
        away_goals_scored = 0
        
        goal_sequence = []
        for _ in range(total_goals):
            if home_goals_to_score > 0 and away_goals_to_score > 0:
                if random.random() < (home_goals_to_score / (home_goals_to_score + away_goals_to_score)):
                    goal_sequence.append('home')
                    home_goals_to_score -= 1
                else:
                    goal_sequence.append('away')
                    away_goals_to_score -= 1
            elif home_goals_to_score > 0:
                goal_sequence.append('home')
                home_goals_to_score -= 1
            else:
                goal_sequence.append('away')
                away_goals_to_score -= 1
        
        for i, minute in enumerate(goal_minutes):
            if goal_sequence[i] == 'home':
                scorer = random.choice(home_starting)
                home_goals_scored += 1
                events.append((match_id, minute, 'GOAL', scorer['id'], 
                             f"¡GOL de {scorer['name']} ({home_team['short_name']})! {home_goals_scored}-{away_goals_scored}", 0))
            else:
                scorer = random.choice(away_starting)
                away_goals_scored += 1
                events.append((match_id, minute, 'GOAL', scorer['id'], 
                             f"¡GOL de {scorer['name']} ({away_team['short_name']})! {home_goals_scored}-{away_goals_scored}", 0))
        
        # Tarjetas
        yellow_cards_this_match = {}
        num_yellows = random.randint(2, 5)
        available_minutes = [m for m in range(1, 91) if m not in goal_minutes]
        yellow_minutes = sorted(random.sample(available_minutes, min(num_yellows, len(available_minutes))))
        
        for minute in yellow_minutes:
            if random.random() < 0.5:
                team = home_starting
                team_short = home_team['short_name']
            else:
                team = away_starting
                team_short = away_team['short_name']
            
            player = random.choice(team)
            player_id = player['id']
            player_name = player['name']
            
            if player_id in yellow_cards_this_match:
                yellow_cards_this_match[player_id] += 1
                events.append((match_id, minute, 'YELLOW_CARD', player_id, 
                             f"🟨 Segunda amarilla para {player_name} ({team_short}) ¡ES EXPULSIÓN!", 1))
                events.append((match_id, minute, 'RED_CARD', player_id,
                             f"🟥 {player_name} ({team_short}) expulsado por doble amarilla", 0))
                self.create_suspension(player_id, match_id, 'RED_CARD', 1)
            else:
                yellow_cards_this_match[player_id] = 1
                events.append((match_id, minute, 'YELLOW_CARD', player_id,
                             f"Tarjeta amarilla para {player_name} ({team_short})", 0))
                
                if self.check_yellow_accumulation(player_id):
                    events.append((match_id, minute, 'YELLOW_CARD', player_id,
                                 f"⚠️ {player_name} ({team_short}) acumula 3 amarillas y será sancionado", 0))
                    self.create_suspension(player_id, match_id, 'YELLOW_ACCUMULATION', 1)
        
        # Roja directa (8% de probabilidad)
        if random.random() < 0.08:
            available_for_red = [m for m in range(1, 91) if m not in goal_minutes and m not in yellow_minutes]
            if available_for_red:
                minute = random.choice(available_for_red)
                if random.random() < 0.5:
                    team = home_starting
                    team_short = home_team['short_name']
                else:
                    team = away_starting
                    team_short = away_team['short_name']
                
                player = random.choice(team)
                events.append((match_id, minute, 'RED_CARD', player['id'],
                             f"🟥 ¡ROJA DIRECTA! {player['name']} ({team_short}) expulsado", 0))
                self.create_suspension(player['id'], match_id, 'RED_CARD', 2)
        
        # Ordenar eventos por minuto
        events.sort(key=lambda x: x[1])
        
        # Insertar todos los eventos
        for event in events:
            self.cursor.execute('''
                INSERT INTO match_events (match_id, minute, event_type, player_id, description, is_second_yellow)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', event)
    
    def save_lineup(self, match_id, team_id, players, side):
        """Guarda la alineación en la BD - exactamente los 11 que recibe"""
        for i, player in enumerate(players):
            self.cursor.execute('''
                INSERT INTO match_lineups (match_id, team_id, player_id, position_order, is_starter, side)
                VALUES (?, ?, ?, ?, 1, ?)
            ''', (match_id, team_id, player['id'], i+1, side))
    
    def check_yellow_accumulation(self, player_id):
        """Verifica si un jugador acumula 3 amarillas en la temporada"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM match_events
            WHERE player_id = ? AND event_type = 'YELLOW_CARD' AND is_second_yellow = 0
        ''', (player_id,))
        
        count = self.cursor.fetchone()[0]
        return count >= 3
    
    def create_suspension(self, player_id, match_id, suspension_type, matches_banned):
        """Crea una sanción para un jugador"""
        self.cursor.execute('''
            INSERT INTO suspensions (player_id, match_id, suspension_type, matches_banned, matches_served, active)
            VALUES (?, ?, ?, ?, 0, 1)
        ''', (player_id, match_id, suspension_type, matches_banned))
    
    def process_suspensions(self):
        """Actualiza las sanciones - descuenta 1 partido a las sanciones activas"""
        self.cursor.execute('''
            UPDATE suspensions 
            SET matches_served = matches_served + 1
            WHERE active = 1
        ''')
        
        self.cursor.execute('''
            UPDATE suspensions 
            SET active = 0
            WHERE matches_served >= matches_banned
        ''')
    
    def get_random_scorer(self, team):
        """Selecciona un goleador aleatorio"""
        weights = []
        for player in team['players']:
            if player['position'] == 'FWD':
                weights.append(0.60)
            elif player['position'] == 'MID':
                weights.append(0.25)
            elif player['position'] == 'DEF':
                weights.append(0.10)
            else:
                weights.append(0.05)
        
        adjusted_weights = []
        for i, player in enumerate(team['players']):
            attack_factor = player['attack'] / 100
            adjusted_weights.append(weights[i] * attack_factor)
        
        scorer = random.choices(team['players'], weights=adjusted_weights, k=1)[0]
        return (scorer['id'], scorer['name'])
    
    def get_random_player(self, team, avoid_gk=False):
        """Selecciona un jugador aleatorio del equipo"""
        available = [p for p in team['players'] if not (avoid_gk and p['position'] == 'GK')]
        player = random.choice(available)
        return (player['id'], player['name'])
    
    def get_match_events_by_type(self, match_id, event_type):
        """Obtiene eventos de un tipo específico del partido"""
        self.cursor.execute('''
        SELECT player_id FROM match_events
        WHERE match_id = ? AND event_type = ?
        ''', (match_id, event_type))
        return [row[0] for row in self.cursor.fetchall()]

    def is_home_event(self, player_id, home_team_id):
        """Verifica si un evento pertenece al equipo local"""
        self.cursor.execute('''
        SELECT team_id FROM players WHERE id = ?
        ''', (player_id,))
        result = self.cursor.fetchone()
        return result and result[0] == home_team_id

    def generate_match_stats(self, match_id, home_team_id, away_team_id, home_team, away_team, 
                         home_score, away_score):
         """Genera estadísticas detalladas del partido"""
    
         # Calcular poder de mediocampo para posesión
         home_mids = [p for p in home_team['players'] if p['position'] == 'MID']
         away_mids = [p for p in away_team['players'] if p['position'] == 'MID']
    
         home_mid_power = sum(p['midfield'] for p in home_mids) / max(len(home_mids), 1)
         away_mid_power = sum(p['midfield'] for p in away_mids) / max(len(away_mids), 1)
    
         total_mid = home_mid_power + away_mid_power
         if total_mid > 0:
             home_possession = round((home_mid_power / total_mid) * 100, 1)
             away_possession = round(100 - home_possession, 1)
         else:
             home_possession = 50
             away_possession = 50
    

         # Tiros
         home_att = [p for p in home_team['players'] if p['position'] in ['FWD', 'MID']]
         away_att = [p for p in away_team['players'] if p['position'] in ['FWD', 'MID']]
    
         home_att_power = sum(p['attack'] for p in home_att) / max(len(home_att), 1)
         away_att_power = sum(p['attack'] for p in away_att) / max(len(away_att), 1)
    
         home_shots = max(1, int(home_score * 4 + (home_att_power / 20) + random.randint(-2, 3)))
         away_shots = max(1, int(away_score * 4 + (away_att_power / 20) + random.randint(-2, 3)))
    
         # Tiros a puerta
         home_shots_on = min(home_shots, max(0, int(home_shots * (0.3 + home_score * 0.1 + random.uniform(-0.1, 0.1)))))
         away_shots_on = min(away_shots, max(0, int(away_shots * (0.3 + away_score * 0.1 + random.uniform(-0.1, 0.1)))))
    
         # xG (Goles Esperados) - basado en tiros a puerta y poder de ataque
         home_xg = round(home_shots_on * (home_att_power / 200) * random.uniform(0.8, 1.2), 2)
         away_xg = round(away_shots_on * (away_att_power / 200) * random.uniform(0.8, 1.2), 2)
    
         # Asegurar que xG no sea menor que los goles reales
         home_xg = max(home_xg, home_score * 0.7)
         away_xg = max(away_xg, away_score * 0.7)
    
         # Precisión de pases (basado en mediocampo y posesión)
         home_pass_acc = round(min(95, 70 + (home_mid_power / 3) + (home_possession / 5) + random.uniform(-5, 5)), 1)
         away_pass_acc = round(min(95, 70 + (away_mid_power / 3) + (away_possession / 5) + random.uniform(-5, 5)), 1)
    
         # Contar tarjetas
         home_yellows = len([e for e in self.get_match_events_by_type(match_id, 'YELLOW_CARD') 
                            if self.is_home_event(e, home_team_id)])
         away_yellows = len([e for e in self.get_match_events_by_type(match_id, 'YELLOW_CARD') 
                                if not self.is_home_event(e, home_team_id)])
         home_reds = len([e for e in self.get_match_events_by_type(match_id, 'RED_CARD') 
                         if self.is_home_event(e, home_team_id)])
         away_reds = len([e for e in self.get_match_events_by_type(match_id, 'RED_CARD') 
                         if not self.is_home_event(e, home_team_id)])
    
         # Insertar estadísticas local
         self.cursor.execute('''
             INSERT INTO match_stats (match_id, team_id, shots, shots_on_target, possession, corners, 
                                     fouls, yellow_cards, red_cards, offsides, passes, tackles, xG, pass_accuracy)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         ''', (match_id, home_team_id, home_shots, home_shots_on, home_possession, 
               random.randint(1, 8), random.randint(5, 18), home_yellows, home_reds,
               random.randint(0, 4), int(home_possession * 5 + random.randint(-20, 20)), 
               random.randint(10, 25), home_xg, home_pass_acc))
        
         # Insertar estadísticas visitante
         self.cursor.execute('''
             INSERT INTO match_stats (match_id, team_id, shots, shots_on_target, possession, corners, 
                                     fouls, yellow_cards, red_cards, offsides, passes, tackles, xG, pass_accuracy)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         ''', (match_id, away_team_id, away_shots, away_shots_on, away_possession, 
               random.randint(1, 8), random.randint(5, 18), away_yellows, away_reds,
               random.randint(0, 4), int(away_possession * 5 + random.randint(-20, 20)), 
               random.randint(10, 25), away_xg, away_pass_acc))
        
    def close(self):
            self.conn.close()