import sqlite3
import random

def run_all_updates():
    """Ejecuta todas las actualizaciones de la base de datos"""
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    
    print("🔄 Ejecutando actualizaciones...")
    
    # ===== UPDATE 1: Tabla de sanciones =====
    print("  • Creando tabla suspensions...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suspensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            match_id INTEGER,
            suspension_type TEXT CHECK(suspension_type IN ('RED_CARD', 'YELLOW_ACCUMULATION')),
            matches_banned INTEGER DEFAULT 1,
            matches_served INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (match_id) REFERENCES matches(id)
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE match_events ADD COLUMN is_second_yellow INTEGER DEFAULT 0")
        print("  • Columna is_second_yellow añadida")
    except:
        print("  • Columna is_second_yellow ya existe")
    
    # ===== UPDATE 2: Tabla de alineaciones =====
    print("  • Creando tabla match_lineups...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_lineups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            team_id INTEGER,
            player_id INTEGER,
            position_order INTEGER,
            is_starter INTEGER DEFAULT 1,
            side TEXT CHECK(side IN ('home', 'away')),
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')
    
    # ===== UPDATE 3: Sistema táctico =====
    print("  • Creando tabla formations...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            style TEXT CHECK(style IN ('DEFENSIVE', 'BALANCED', 'OFFENSIVE', 'POSSESSION', 'COUNTER')),
            defense_bonus REAL DEFAULT 0,
            midfield_bonus REAL DEFAULT 0,
            attack_bonus REAL DEFAULT 0,
            possession_bonus REAL DEFAULT 0,
            counter_attack_chance REAL DEFAULT 0
        )
    ''')
    
    print("  • Creando tabla team_tactics...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_tactics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER UNIQUE,
            formation_id INTEGER DEFAULT 1,
            mentality TEXT CHECK(mentality IN ('VERY_DEFENSIVE', 'DEFENSIVE', 'BALANCED', 'OFFENSIVE', 'VERY_OFFENSIVE')) DEFAULT 'BALANCED',
            tempo TEXT CHECK(tempo IN ('SLOW', 'NORMAL', 'FAST')) DEFAULT 'NORMAL',
            pressing TEXT CHECK(pressing IN ('LOW', 'MEDIUM', 'HIGH')) DEFAULT 'MEDIUM',
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (formation_id) REFERENCES formations(id)
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN specific_position TEXT")
        print("  • Columna specific_position añadida")
    except:
        print("  • Columna specific_position ya existe")
    
    # Insertar formaciones si no existen
    cursor.execute("SELECT COUNT(*) FROM formations")
    if cursor.fetchone()[0] == 0:
        print("  • Insertando formaciones...")
        formaciones = [
            ("4-4-2 Clásico", "Formación equilibrada con dos delanteros", "BALANCED", 0, 5, 5, 0, 10),
            ("4-3-3 Ofensivo", "Ataque con extremos rápidos", "OFFENSIVE", -5, 5, 10, 5, 5),
            ("5-3-2 Defensivo", "Autobús defensivo con contragolpes", "DEFENSIVE", 15, -5, -5, -10, 20),
            ("4-2-3-1 Creativo", "Control del mediocampo con mediapunta", "POSSESSION", 0, 10, 5, 15, 0),
            ("3-5-2 Ofensivo", "Carrileros largos y presión alta", "OFFENSIVE", -5, 10, 5, 10, 0),
            ("4-1-4-1 Tiki-Taka", "Posesión y toque corto", "POSSESSION", 5, 10, 0, 20, -5),
            ("4-4-2 Contragolpe", "Defensa sólida y salida rápida", "COUNTER", 10, 0, 5, -5, 25),
            ("3-4-3 Ataque total", "Presión alta y muchos hombres al ataque", "OFFENSIVE", -10, 5, 15, 5, 0),
        ]
        cursor.executemany('''
            INSERT INTO formations (name, description, style, defense_bonus, midfield_bonus, attack_bonus, possession_bonus, counter_attack_chance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', formaciones)
        print("  • 8 formaciones insertadas")
        
        # Asignar tácticas a equipos
        print("  • Asignando tácticas a equipos...")
        random.seed(123)
        cursor.execute("SELECT id FROM teams")
        teams = cursor.fetchall()
        for team in teams:
            formation_id = random.randint(1, 8)
            mentalities = ['VERY_DEFENSIVE', 'DEFENSIVE', 'BALANCED', 'OFFENSIVE', 'VERY_OFFENSIVE']
            tempos = ['SLOW', 'NORMAL', 'FAST']
            pressings = ['LOW', 'MEDIUM', 'HIGH']
            cursor.execute('''
                INSERT OR REPLACE INTO team_tactics (team_id, formation_id, mentality, tempo, pressing)
                VALUES (?, ?, ?, ?, ?)
            ''', (team[0], formation_id, random.choice(mentalities), random.choice(tempos), random.choice(pressings)))
        
        # Asignar posiciones específicas
        print("  • Asignando posiciones específicas...")
        posiciones_especificas = {
            'GK': ['Portero'],
            'DEF': ['Lateral Derecho', 'Lateral Izquierdo', 'Defensa Central'],
            'MID': ['Mediocentro Defensivo', 'Mediocentro', 'Mediocentro Ofensivo', 'Extremo Derecho', 'Extremo Izquierdo', 'Mediapunta'],
            'FWD': ['Delantero Centro', 'Segundo Delantero', 'Extremo Derecho', 'Extremo Izquierdo']
        }
        cursor.execute("SELECT id, position FROM players")
        for player_id, position in cursor.fetchall():
            if position in posiciones_especificas:
                especifica = random.choice(posiciones_especificas[position])
                cursor.execute("UPDATE players SET specific_position = ? WHERE id = ?", (especifica, player_id))
    
    # ===== UPDATE 4: Estadísticas de partido =====
    print("  • Creando tabla match_stats...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            team_id INTEGER,
            shots INTEGER DEFAULT 0,
            shots_on_target INTEGER DEFAULT 0,
            possession REAL DEFAULT 50,
            corners INTEGER DEFAULT 0,
            fouls INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            offsides INTEGER DEFAULT 0,
            passes INTEGER DEFAULT 0,
            tackles INTEGER DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Todas las actualizaciones completadas!")

if __name__ == "__main__":
    run_all_updates()