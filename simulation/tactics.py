import sqlite3

class TacticsManager:
    def __init__(self):
        self.conn = sqlite3.connect("football_manager.db")
        self.cursor = self.conn.cursor()
    
    def get_team_tactics(self, team_id):
        """Obtiene la táctica y formación de un equipo"""
        self.cursor.execute('''
            SELECT f.name, f.description, f.style, f.defense_bonus, f.midfield_bonus, 
                   f.attack_bonus, f.possession_bonus, f.counter_attack_chance,
                   tt.mentality, tt.tempo, tt.pressing
            FROM team_tactics tt
            JOIN formations f ON tt.formation_id = f.id
            WHERE tt.team_id = ?
        ''', (team_id,))
        
        result = self.cursor.fetchone()
        if result:
            return {
                'formation_name': result[0],
                'formation_desc': result[1],
                'style': result[2],
                'defense_bonus': result[3],
                'midfield_bonus': result[4],
                'attack_bonus': result[5],
                'possession_bonus': result[6],
                'counter_attack_chance': result[7],
                'mentality': result[8],
                'tempo': result[9],
                'pressing': result[10]
            }
        return None
    
    def get_formation_positions(self, formation_name):
        """Obtiene las posiciones en el campo según la formación"""
        formations_map = {
            "4-4-2 Clásico": {
                'GK': [(50, 90)],
                'DEF': [(20, 70), (40, 70), (60, 70), (80, 70)],
                'MID': [(15, 45), (35, 45), (65, 45), (85, 45)],
                'FWD': [(35, 20), (65, 20)]
            },
            "4-3-3 Ofensivo": {
                'GK': [(50, 90)],
                'DEF': [(20, 70), (40, 70), (60, 70), (80, 70)],
                'MID': [(30, 45), (50, 40), (70, 45)],
                'FWD': [(20, 20), (50, 15), (80, 20)]
            },
            "5-3-2 Defensivo": {
                'GK': [(50, 90)],
                'DEF': [(10, 70), (30, 75), (50, 75), (70, 75), (90, 70)],
                'MID': [(25, 40), (50, 45), (75, 40)],
                'FWD': [(35, 20), (65, 20)]
            },
            "4-2-3-1 Creativo": {
                'GK': [(50, 90)],
                'DEF': [(20, 70), (40, 70), (60, 70), (80, 70)],
                'MID': [(35, 50), (65, 50), (20, 35), (50, 30), (80, 35)],
                'FWD': [(50, 15)]
            },
            "3-5-2 Ofensivo": {
                'GK': [(50, 90)],
                'DEF': [(30, 75), (50, 75), (70, 75)],
                'MID': [(10, 50), (30, 40), (50, 35), (70, 40), (90, 50)],
                'FWD': [(35, 20), (65, 20)]
            },
            "4-1-4-1 Tiki-Taka": {
                'GK': [(50, 90)],
                'DEF': [(20, 70), (40, 70), (60, 70), (80, 70)],
                'MID': [(50, 55), (15, 40), (35, 40), (65, 40), (85, 40)],
                'FWD': [(50, 15)]
            },
            "4-4-2 Contragolpe": {
                'GK': [(50, 90)],
                'DEF': [(20, 65), (40, 65), (60, 65), (80, 65)],
                'MID': [(15, 40), (35, 40), (65, 40), (85, 40)],
                'FWD': [(35, 20), (65, 20)]
            },
            "3-4-3 Ataque total": {
                'GK': [(50, 90)],
                'DEF': [(30, 70), (50, 75), (70, 70)],
                'MID': [(15, 45), (35, 40), (65, 40), (85, 45)],
                'FWD': [(20, 15), (50, 10), (80, 15)]
            }
        }
        return formations_map.get(formation_name, formations_map["4-4-2 Clásico"])
    
    def get_starting_eleven_with_positions(self, team_players, formation_name):
        """Asigna posiciones del campo a una lista de jugadores según la formación"""
        positions = self.get_formation_positions(formation_name)
        
        # Contar cuántos jugadores hay de cada posición
        gk = [p for p in team_players if p['position'] == 'GK']
        defs = [p for p in team_players if p['position'] == 'DEF']
        mids = [p for p in team_players if p['position'] == 'MID']
        fwds = [p for p in team_players if p['position'] == 'FWD']
        
        result = []
        used_ids = set()
        
        def add_player(player, x, y):
            if player['id'] not in used_ids:
                p = player.copy()
                p['field_x'] = x
                p['field_y'] = y
                result.append(p)
                used_ids.add(player['id'])
        
        # Asignar GK
        for i in range(len(positions.get('GK', []))):
            if i < len(gk):
                add_player(gk[i], positions['GK'][i][0], positions['GK'][i][1])
        
        # Asignar DEF
        for i in range(len(positions.get('DEF', []))):
            if i < len(defs):
                add_player(defs[i], positions['DEF'][i][0], positions['DEF'][i][1])
        
        # Asignar MID
        for i in range(len(positions.get('MID', []))):
            if i < len(mids):
                add_player(mids[i], positions['MID'][i][0], positions['MID'][i][1])
        
        # Asignar FWD
        for i in range(len(positions.get('FWD', []))):
            if i < len(fwds):
                add_player(fwds[i], positions['FWD'][i][0], positions['FWD'][i][1])
        
        # Si faltan jugadores para llegar a 11, completar con los mejores no usados
        if len(result) < 11:
            remaining = [p for p in team_players if p['id'] not in used_ids]
            # Ordenar por mejor media de stats
            remaining.sort(key=lambda p: (p.get('attack',0) + p.get('defense',0) + p.get('midfield',0) + p.get('goalkeeping',0)) / 4, reverse=True)
            
            # Posiciones de reserva (banquillo o posiciones libres)
            backup_spots = [(50, 80), (30, 80), (70, 80), (15, 75), (85, 75), (50, 10), (30, 15), (70, 15)]
            spot_idx = 0
            
            for player in remaining:
                if len(result) >= 11:
                    break
                if spot_idx < len(backup_spots):
                    x, y = backup_spots[spot_idx]
                else:
                    x, y = 50, 85
                add_player(player, x, y)
                spot_idx += 1
        
        return result[:11]
    
    def get_specific_position_name(self, general_pos, index, total):
        """Obtiene el nombre específico de la posición"""
        names = {
            'GK': ['POR'],
            'DEF': ['DFC', 'DFC', 'LI', 'LD', 'DFC'][:total],
            'MID': ['MC', 'MCD', 'MCO', 'ED', 'EI', 'MP'][:total],
            'FWD': ['DC', 'SD', 'ED', 'EI'][:total]
        }
        return names.get(general_pos, ['-'])[index] if index < len(names.get(general_pos, ['-'])) else '-'
    
    def calculate_match_modifiers(self, home_tactics, away_tactics):
        """Calcula modificadores para la simulación según tácticas"""
        modifiers = {
            'home_possession': 50,
            'away_possession': 50,
            'home_attack_boost': 0,
            'away_attack_boost': 0,
            'home_defense_boost': 0,
            'away_defense_boost': 0,
            'counter_chance': 0
        }
        
        # Posesión base según formación
        modifiers['home_possession'] = 50 + home_tactics['possession_bonus'] - away_tactics['possession_bonus']
        modifiers['away_possession'] = 100 - modifiers['home_possession']
        
        # Bonificaciones de ataque/defensa
        modifiers['home_attack_boost'] = home_tactics['attack_bonus'] / 100
        modifiers['away_attack_boost'] = away_tactics['attack_bonus'] / 100
        modifiers['home_defense_boost'] = home_tactics['defense_bonus'] / 100
        modifiers['away_defense_boost'] = away_tactics['defense_bonus'] / 100
        
        # Probabilidad de contragolpe
        modifiers['counter_chance'] = (home_tactics['counter_attack_chance'] + away_tactics['counter_attack_chance']) / 200
        
        # Ajustar por mentalidad
        mentality_multipliers = {
            'VERY_DEFENSIVE': (0.7, 1.3, 0.3),
            'DEFENSIVE': (0.8, 1.2, 0.5),
            'BALANCED': (1.0, 1.0, 1.0),
            'OFFENSIVE': (1.2, 0.8, 0.5),
            'VERY_OFFENSIVE': (1.4, 0.6, 0.2)
        }
        
        home_mult = mentality_multipliers[home_tactics['mentality']]
        away_mult = mentality_multipliers[away_tactics['mentality']]
        
        modifiers['home_attack_boost'] *= home_mult[0]
        modifiers['home_defense_boost'] *= home_mult[1]
        modifiers['away_attack_boost'] *= away_mult[0]
        modifiers['away_defense_boost'] *= away_mult[1]
        
        return modifiers
    
    def get_team_players_with_positions(self, team_id):
        """Obtiene jugadores del equipo con sus posiciones específicas"""
        self.cursor.execute('''
            SELECT p.id, p.name, p.position, p.specific_position, p.number,
                   p.attack, p.defense, p.midfield, p.goalkeeping, p.stamina, p.speed
            FROM players p
            WHERE p.team_id = ?
            ORDER BY 
                CASE p.position 
                    WHEN 'GK' THEN 1 
                    WHEN 'DEF' THEN 2 
                    WHEN 'MID' THEN 3 
                    WHEN 'FWD' THEN 4 
                END
        ''', (team_id,))
        
        players = []
        for row in self.cursor.fetchall():
            players.append({
                'id': row[0],
                'name': row[1],
                'position': row[2],
                'specific_position': row[3] or row[2],
                'number': row[4],
                'attack': row[5],
                'defense': row[6],
                'midfield': row[7],
                'goalkeeping': row[8],
                'stamina': row[9],
                'speed': row[10]
            })
        
        return players
    
    def close(self):
        self.conn.close()