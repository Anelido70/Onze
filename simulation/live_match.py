import random
import time
import threading

class LiveMatchSimulator:
    def __init__(self, match_simulator, home_team_id, away_team_id, callback=None):
        self.ms = match_simulator
        self.home_id = home_team_id
        self.away_id = away_team_id
        self.callback = callback
        
        self.home_team = self.ms.get_team_stats(home_team_id)
        self.away_team = self.ms.get_team_stats(away_team_id)
        self.home_team = self.ms.filter_suspended_players(self.home_team, home_team_id)
        self.away_team = self.ms.filter_suspended_players(self.away_team, away_team_id)
        
        self.home_starting = self.ms.get_starting_eleven(self.home_team)
        self.away_starting = self.ms.get_starting_eleven(self.away_team)
        
        self.home_reds = 0
        self.away_reds = 0
        self.home_score = 0
        self.away_score = 0
        self.current_minute = 0
        self.stoppage_time = random.randint(1, 5)
        self.is_running = False
        self.is_paused = False
        self.match_events = []
        self.saved_match_id = None
        
        home_power = self.ms.calculate_team_power(self.home_team)
        away_power = self.ms.calculate_team_power(self.away_team)
        self.final_home_score, self.final_away_score = self.ms.simulate_score(home_power, away_power)
        
        self.pregenerated_events = self.generate_all_events()
    
    def generate_all_events(self):
        events = []
        used = set()

        # Contadores de expulsiones
        self.home_reds = 0
        self.away_reds = 0
        
        # ===== ROJA DIRECTA =====
        self.has_red_card = False
        self.red_card_team = None
        self.red_card_minute = None
        
        if random.random() < 0.15:
            self.has_red_card = True
            self.red_card_team = random.choice(['home', 'away'])
            self.red_card_minute = random.randint(20, 75)
            impact = (90 - self.red_card_minute) / 90
            
            if self.red_card_team == 'home':
                pen = int(impact * 3.5)
                self.final_home_score = max(0, self.final_home_score - pen)
                if random.random() < impact:
                    self.final_away_score += random.randint(0, 1)
            else:
                pen = int(impact * 3.5)
                self.final_away_score = max(0, self.final_away_score - pen)
                if random.random() < impact:
                    self.final_home_score += random.randint(0, 1)
        
                # ===== PENALTIS (generar solo minutos y tipo, no eventos aún) =====
        max_penalties = random.randint(0, 2)
        penalty_minutes = []
        penalty_types = []  # 'home' o 'away'
        penalty_goals_home = 0
        penalty_goals_away = 0
        
        for _ in range(max_penalties):
            minute = random.randint(10, 85)
            while minute in used:
                minute = random.randint(10, 85)
            used.add(minute)
            penalty_minutes.append(minute)
            
            if random.random() < 0.5:
                penalty_types.append(('home', 'away'))
            else:
                penalty_types.append(('away', 'home'))
        
        # ===== GOLES NORMALES =====
        normal_home = self.final_home_score - penalty_goals_home
        normal_away = self.final_away_score - penalty_goals_away
        total_normal = normal_home + normal_away
        
        # Secuencia de goles normales
        seq_normal = []
        h_left, a_left = normal_home, normal_away
        for _ in range(total_normal):
            if h_left > 0 and a_left > 0:
                if random.random() < h_left / (h_left + a_left):
                    seq_normal.append('home'); h_left -= 1
                else:
                    seq_normal.append('away'); a_left -= 1
            elif h_left > 0:
                seq_normal.append('home'); h_left -= 1
            else:
                seq_normal.append('away'); a_left -= 1
        
        # Minutos de goles normales
        goal_minutes = []
        if total_normal > 0:
            fh = max(0, int(total_normal * 0.4))
            sh = total_normal - fh
            p1 = list(set(range(1, 46)) - used)
            if fh > 0 and p1:
                goal_minutes.extend(sorted(random.sample(p1, min(fh, len(p1)))))
            p2 = list(set(range(46, 91)) - used)
            if sh > 0 and p2:
                goal_minutes.extend(sorted(random.sample(p2, min(sh, len(p2)))))
        
        # ===== JUNTAR PENALTIS Y GOLES POR MINUTO =====
        # Crear lista combinada: (minuto, tipo, equipo)
        all_goals = []
        for minute in penalty_minutes:
            all_goals.append((minute, 'penalty'))
        for i, minute in enumerate(goal_minutes):
            all_goals.append((minute, 'normal', seq_normal[i]))
        
        # Ordenar por minuto
        all_goals.sort(key=lambda x: x[0])
        
        # Contadores para narración
        h_sc = 0
        a_sc = 0
        pen_idx = 0  # Índice para penalty_types
        
        for item in all_goals:
            minute = item[0]
            
            if item[1] == 'penalty':
                # Es un penalti
                pen_team, def_team = penalty_types[pen_idx]
                pen_idx += 1
                
                if pen_team == 'home':
                    pen_tn = self.home_team['short_name']
                    def_tn = self.away_team['short_name']
                    shooter = random.choice([p for p in self.home_starting if p['position'] != 'GK'])
                    defender = random.choice([p for p in self.away_starting if p['position'] != 'GK'])
                    gk_pen = [p for p in self.away_starting if p['position'] == 'GK'][0]
                else:
                    pen_tn = self.away_team['short_name']
                    def_tn = self.home_team['short_name']
                    shooter = random.choice([p for p in self.away_starting if p['position'] != 'GK'])
                    defender = random.choice([p for p in self.home_starting if p['position'] != 'GK'])
                    gk_pen = [p for p in self.home_starting if p['position'] == 'GK'][0]
                
                # Tarjeta
                if random.random() < 0.3:
                    if def_team == 'home':
                        self.home_reds += 1
                        players_left = 11 - self.home_reds
                    else:
                        self.away_reds += 1
                        players_left = 11 - self.away_reds
                    events.append({'minute': minute, 'type': 'RED_CARD', 'icon': '🟥', 'team': def_team,
                        'description': f"¡ROJA! {defender['name']} ({def_tn}) por penalti. ¡Se queda con {players_left}!"})
                else:
                    events.append({'minute': minute, 'type': 'YELLOW_CARD', 'icon': '🟨', 'team': def_team,
                        'description': f"Amarilla para {defender['name']} ({def_tn}) por el penalti"})
                
                # ¿Gol o parada?
                if random.random() < 0.75:
                    if pen_team == 'home':
                        self.final_home_score += 1
                        h_sc += 1
                    else:
                        self.final_away_score += 1
                        a_sc += 1
                    events.append({'minute': minute, 'type': 'GOAL', 'icon': '⚽', 'team': pen_team,
                        'description': f"¡PENALTI! {shooter['name']} ({pen_tn}) marca. {h_sc}-{a_sc}"})
                else:
                    events.append({'minute': minute, 'type': 'SAVE', 'icon': '🧤', 'team': pen_team,
                        'description': f"¡PENALTI PARADO! {gk_pen['name']} ({def_tn}) a {shooter['name']}"})
            
            else:
                # Es un gol normal
                team = item[2]
                if team == 'home':
                    h_sc += 1
                    s = random.choice(self.home_starting)
                    events.append({'minute': minute, 'type': 'GOAL', 'icon': '⚽', 'team': 'home',
                        'description': f"¡GOOOL de {s['name']} ({self.home_team['short_name']})! {h_sc}-{a_sc}"})
                else:
                    a_sc += 1
                    s = random.choice(self.away_starting)
                    events.append({'minute': minute, 'type': 'GOAL', 'icon': '⚽', 'team': 'away',
                        'description': f"¡GOOOL de {s['name']} ({self.away_team['short_name']})! {h_sc}-{a_sc}"})
        
        # ===== TARJETAS AMARILLAS =====
        yellows = random.randint(3, 6)
        pool = list(set(range(1, 91)) - used)
        ymins = sorted(random.sample(pool, min(yellows, len(pool))))
        yt = {}
        for minute in ymins:
            used.add(minute)
            if random.random() < 0.5:
                tt, tn = 'home', self.home_team['short_name']
                p = random.choice(self.home_starting)
            else:
                tt, tn = 'away', self.away_team['short_name']
                p = random.choice(self.away_starting)
            key = (tt, p['id'])
            yt[key] = yt.get(key, 0) + 1
            if yt[key] >= 2:
                if tt == 'home':
                    self.home_reds += 1
                    players_left = 11 - self.home_reds
                else:
                    self.away_reds += 1
                    players_left = 11 - self.away_reds
                
                events.append({'minute': minute, 'type': 'RED_CARD', 'icon': '🟥', 'team': tt,
                    'description': f"¡EXPULSIÓN! {p['name']} ({tn}) - Doble amarilla. ¡Se queda con {players_left}!"})
            else:
                events.append({'minute': minute, 'type': 'YELLOW_CARD', 'icon': '🟨', 'team': tt,
                    'description': f"Amarilla para {p['name']} ({tn})"})
        
        # ===== ROJA DIRECTA (evento) =====
        if self.has_red_card:
            minute = self.red_card_minute
            while minute in used and minute < 90:
                minute += 1
            used.add(minute)
            self.red_card_minute = minute
            if self.red_card_team == 'home':
                tt, tn = 'home', self.home_team['short_name']
                p = random.choice(self.home_starting)
            else:
                tt, tn = 'away', self.away_team['short_name']
                p = random.choice(self.away_starting)
            if tt == 'home':
                self.home_reds += 1
                players_left = 11 - self.home_reds
            else:
                self.away_reds += 1
                players_left = 11 - self.away_reds
            
            events.append({'minute': minute, 'type': 'RED_CARD', 'icon': '🟥', 'team': tt,
                'description': f"¡ROJA DIRECTA! {p['name']} ({tn}) - ¡Se queda con {players_left}!"})
            for _ in range(random.randint(2, 4)):
                pm = random.randint(minute + 2, 88)
                if pm not in used:
                    used.add(pm)
                    if self.red_card_team == 'home':
                        opp = self.away_team['short_name']
                        op = random.choice(self.away_starting)
                        events.append({'minute': pm, 'type': 'SHOT', 'icon': '🎯', 'team': 'away',
                            'description': f"¡Ocasión! {op['name']} ({opp}) con superioridad"})
                    else:
                        opp = self.home_team['short_name']
                        op = random.choice(self.home_starting)
                        events.append({'minute': pm, 'type': 'SHOT', 'icon': '🎯', 'team': 'home',
                            'description': f"¡Ocasión! {op['name']} ({opp}) con superioridad"})
        
        # ===== SUSTITUCIONES =====
        num_subs = random.randint(2, 4)
        pool = [m for m in range(55, 88) if m not in used]
        smins = sorted(random.sample(pool, min(num_subs, len(pool))))
        for minute in smins:
            used.add(minute)
            if random.random() < 0.5:
                po = random.choice(self.home_starting[1:])
                events.append({'minute': minute, 'type': 'SUBSTITUTION', 'icon': '🔄', 'team': 'home',
                    'description': f"Cambio {self.home_team['short_name']}: Sale {po['name']}"})
            else:
                po = random.choice(self.away_starting[1:])
                events.append({'minute': minute, 'type': 'SUBSTITUTION', 'icon': '🔄', 'team': 'away',
                    'description': f"Cambio {self.away_team['short_name']}: Sale {po['name']}"})
        
        # ===== EVENTOS DE JUEGO =====
        pool = list(set(range(1, 91)) - used)
        num = random.randint(10, 18)
        gms = sorted(random.sample(pool, min(num, len(pool))))
        for minute in gms:
            if random.random() < 0.5:
                tt, tn = 'home', self.home_team['short_name']
                out_h = [p for p in self.home_starting if p['position'] != 'GK']
                out_a = [p for p in self.away_starting if p['position'] != 'GK']
                gk_h = [p for p in self.home_starting if p['position'] == 'GK']
                gk_a = [p for p in self.away_starting if p['position'] == 'GK']
                pl = random.choice(out_h) if out_h else random.choice(self.home_starting)
                on = self.away_team['short_name']
                gk = gk_a[0] if gk_a else random.choice(self.away_starting)
                op = random.choice(out_a) if out_a else random.choice(self.away_starting)
            else:
                tt, tn = 'away', self.away_team['short_name']
                out_h = [p for p in self.home_starting if p['position'] != 'GK']
                out_a = [p for p in self.away_starting if p['position'] != 'GK']
                gk_h = [p for p in self.home_starting if p['position'] == 'GK']
                gk_a = [p for p in self.away_starting if p['position'] == 'GK']
                pl = random.choice(out_a) if out_a else random.choice(self.away_starting)
                on = self.home_team['short_name']
                gk = gk_h[0] if gk_h else random.choice(self.home_starting)
                op = random.choice(out_h) if out_h else random.choice(self.home_starting)
            
            t = random.choice(['SHOT', 'SAVE', 'CORNER', 'FOUL', 'OFFSIDE', 'INJURY'])
            
            if t == 'SHOT':
                events.append({'minute': minute, 'type': 'SHOT', 'icon': '🎯', 'team': tt,
                    'description': f"Disparo de {pl['name']} ({tn})"})
            elif t == 'SAVE':
                events.append({'minute': minute, 'type': 'SAVE', 'icon': '🧤', 'team': tt,
                    'description': f"¡Parada de {gk['name']} ({on})! Disparo de {pl['name']}"})
            elif t == 'CORNER':
                events.append({'minute': minute, 'type': 'CORNER', 'icon': '🚩', 'team': tt,
                    'description': f"Córner a favor de {tn}"})
            elif t == 'FOUL':
                events.append({'minute': minute, 'type': 'FOUL', 'icon': '💢', 'team': tt,
                    'description': f"Falta de {pl['name']} ({tn}) sobre {op['name']}"})
            elif t == 'OFFSIDE':
                events.append({'minute': minute, 'type': 'OFFSIDE', 'icon': '🏁', 'team': tt,
                    'description': f"Fuera de juego de {pl['name']} ({tn})"})
            elif t == 'INJURY':
                if random.random() < 0.10:
                    injured = random.choice(out_h if tt == 'home' else out_a)
                    sev = random.choice(['leve', 'moderada', 'grave'])
                    if sev == 'leve':
                        desc = f"{injured['name']} ({tn}) se duele... Podrá continuar"
                        icon = '🤕'
                    elif sev == 'moderada':
                        desc = f"¡Lesión de {injured['name']} ({tn})! No puede seguir"
                        icon = '🚑'
                    else:
                        desc = f"¡GRAVE LESIÓN de {injured['name']} ({tn})! Se retira en camilla"
                        icon = '🏥'
                    events.append({'minute': minute, 'type': 'INJURY', 'icon': icon, 'team': tt,
                        'description': desc})
        
        events.sort(key=lambda x: x['minute'])
        return events
    
    def simulate_in_thread(self):
        self.is_running = True
        t = threading.Thread(target=self.run_simulation)
        t.daemon = True
        t.start()
    
    def run_simulation(self):
        for m in range(1, 46):
            if not self.is_running: return
            while self.is_paused: time.sleep(0.1)
            self.current_minute = m
            self.fire_events(m)
            if self.callback: self.callback('update', self.get_state())
            time.sleep(0.4)
        
        if self.is_running:
            if self.callback: self.callback('halftime', self.get_state())
            time.sleep(2)
        
        for m in range(46, 91):
            if not self.is_running: return
            while self.is_paused: time.sleep(0.1)
            self.current_minute = m
            self.fire_events(m)
            if self.callback: self.callback('update', self.get_state())
            time.sleep(0.4)
        
        for extra in range(1, self.stoppage_time + 1):
            if not self.is_running: return
            self.current_minute = 90 + extra
            self.fire_events(90 + extra)
            if self.callback: self.callback('update', self.get_state())
            time.sleep(0.2)
        
        self.save_match_to_db()
        self.is_running = False
        if self.callback:
            self.callback('final', self.get_state())
    
    def fire_events(self, minute):
        for ev in self.pregenerated_events:
            if ev['minute'] == minute:
                self.match_events.append(ev)
                if ev['type'] == 'GOAL':
                    if ev['team'] == 'home':
                        self.home_score += 1
                    else:
                        self.away_score += 1
                if self.callback:
                    self.callback('event', ev)
    
    def get_state(self):
        return {
            'minute': self.current_minute,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'home_short': self.home_team['short_name'],
            'away_short': self.away_team['short_name'],
            'home_starting': self.home_starting,
            'away_starting': self.away_starting
        }
    
    def save_match_to_db(self):
        import sqlite3
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO matches (home_team_id, away_team_id, home_score, away_score, match_date, played)
            VALUES (?, ?, ?, ?, datetime('now'), 1)
        ''', (self.home_id, self.away_id, self.final_home_score, self.final_away_score))
        match_id = cursor.lastrowid
        
        for i, player in enumerate(self.home_starting):
            cursor.execute('''
                INSERT INTO match_lineups (match_id, team_id, player_id, position_order, is_starter, side)
                VALUES (?, ?, ?, ?, 1, 'home')
            ''', (match_id, self.home_id, player['id'], i+1))
        
        for i, player in enumerate(self.away_starting):
            cursor.execute('''
                INSERT INTO match_lineups (match_id, team_id, player_id, position_order, is_starter, side)
                VALUES (?, ?, ?, ?, 1, 'away')
            ''', (match_id, self.away_id, player['id'], i+1))
        
        for ev in self.match_events:
            if ev['type'] in ['GOAL', 'YELLOW_CARD', 'RED_CARD', 'SUBSTITUTION']:
                is_sec = 1 if 'Segunda' in ev.get('description', '') or 'Doble' in ev.get('description', '') else 0
                cursor.execute('''
                    INSERT INTO match_events (match_id, minute, event_type, player_id, description, is_second_yellow)
                    VALUES (?, ?, ?, 0, ?, ?)
                ''', (match_id, ev['minute'], ev['type'], ev['description'], is_sec))
        
        self._save_stats(cursor, match_id)
        
        conn.commit()
        conn.close()
        self.saved_match_id = match_id
    
    def _save_stats(self, cursor, match_id):
        import random
        
        # Calcular posesión real (suma 100%)
        # Basado en poder de mediocampo y si hubo roja
        home_mid_power = sum(p.get('midfield', 50) for p in self.home_starting) / 11
        away_mid_power = sum(p.get('midfield', 50) for p in self.away_starting) / 11
        
        # Ajustar por roja (equipo con 10 pierde ~15% de posesión)
        if self.has_red_card:
            if self.red_card_team == 'home':
                home_mid_power *= 0.7
            else:
                away_mid_power *= 0.7
        
        total_mid = home_mid_power + away_mid_power
        if total_mid > 0:
            home_possession = round((home_mid_power / total_mid) * 100, 1)
        else:
            home_possession = 50.0
        away_possession = round(100 - home_possession, 1)
        
        # Precisión de pases (más realista: 78-92%)
        home_pass_acc = round(random.uniform(78, 92), 1)
        away_pass_acc = round(random.uniform(78, 92), 1)
        
        # El equipo con roja pierde precisión
        if self.has_red_card:
            if self.red_card_team == 'home':
                home_pass_acc = round(home_pass_acc - random.uniform(5, 10), 1)
            else:
                away_pass_acc = round(away_pass_acc - random.uniform(5, 10), 1)
        
        # Tiros (el equipo con roja tira menos)
        home_shots = random.randint(5, 15)
        away_shots = random.randint(5, 15)
        if self.has_red_card:
            if self.red_card_team == 'home':
                home_shots = max(2, home_shots - random.randint(3, 7))
                away_shots = min(20, away_shots + random.randint(2, 5))
            else:
                away_shots = max(2, away_shots - random.randint(3, 7))
                home_shots = min(20, home_shots + random.randint(2, 5))
        
        # Tiros a puerta
        home_shots_on = min(home_shots, random.randint(1, home_shots))
        away_shots_on = min(away_shots, random.randint(1, away_shots))
        
        # xG
        home_xg = round(random.uniform(0.3, 3.5), 2)
        away_xg = round(random.uniform(0.3, 3.5), 2)
        
        # Ajustar xG por roja
        if self.has_red_card:
            if self.red_card_team == 'home':
                home_xg = round(home_xg * random.uniform(0.4, 0.7), 2)
                away_xg = round(away_xg * random.uniform(1.2, 1.6), 2)
            else:
                away_xg = round(away_xg * random.uniform(0.4, 0.7), 2)
                home_xg = round(home_xg * random.uniform(1.2, 1.6), 2)
        
        # Córners
        home_corners = random.randint(1, 8)
        away_corners = random.randint(1, 8)
        if self.has_red_card:
            if self.red_card_team == 'home':
                home_corners = max(0, home_corners - random.randint(2, 4))
            else:
                away_corners = max(0, away_corners - random.randint(2, 4))
        
        # Faltas
        home_fouls = random.randint(5, 18)
        away_fouls = random.randint(5, 18)
        if self.has_red_card:
            if self.red_card_team == 'home':
                home_fouls = min(25, home_fouls + random.randint(3, 7))
            else:
                away_fouls = min(25, away_fouls + random.randint(3, 7))
        
        # Tarjetas desde eventos
        home_yellows = sum(1 for e in self.match_events if e['type'] == 'YELLOW_CARD' and e['team'] == 'home')
        away_yellows = sum(1 for e in self.match_events if e['type'] == 'YELLOW_CARD' and e['team'] == 'away')
        home_reds = sum(1 for e in self.match_events if e['type'] == 'RED_CARD' and e['team'] == 'home')
        away_reds = sum(1 for e in self.match_events if e['type'] == 'RED_CARD' and e['team'] == 'away')
        
        # Insertar stats home
        cursor.execute('''
            INSERT INTO match_stats (match_id, team_id, shots, shots_on_target, possession, corners, fouls,
                                    yellow_cards, red_cards, offsides, passes, tackles, xG, pass_accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, self.home_id,
              home_shots, home_shots_on, home_possession, home_corners, home_fouls,
              home_yellows, home_reds, random.randint(0, 4),
              random.randint(250, 550), random.randint(10, 25),
              home_xg, home_pass_acc))
        
        # Insertar stats away
        cursor.execute('''
            INSERT INTO match_stats (match_id, team_id, shots, shots_on_target, possession, corners, fouls,
                                    yellow_cards, red_cards, offsides, passes, tackles, xG, pass_accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, self.away_id,
              away_shots, away_shots_on, away_possession, away_corners, away_fouls,
              away_yellows, away_reds, random.randint(0, 4),
              random.randint(250, 550), random.randint(10, 25),
              away_xg, away_pass_acc))