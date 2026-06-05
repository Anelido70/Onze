import sqlite3
import os

def create_database():
    # Eliminar BD anterior si existe (para pruebas limpias)
    if os.path.exists("football_manager.db"):
        os.remove("football_manager.db")
    
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    
    # Crear tabla de equipos
    cursor.execute('''
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_name TEXT NOT NULL,
            stadium TEXT,
            city TEXT
        )
    ''')
    
    # Crear tabla de jugadores
    cursor.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            name TEXT NOT NULL,
            position TEXT CHECK(position IN ('GK', 'DEF', 'MID', 'FWD')),
            number INTEGER,
            age INTEGER,
            attack INTEGER DEFAULT 50,
            defense INTEGER DEFAULT 50,
            midfield INTEGER DEFAULT 50,
            goalkeeping INTEGER DEFAULT 50,
            stamina INTEGER DEFAULT 50,
            speed INTEGER DEFAULT 50,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')
    
    # Crear tabla de partidos
    cursor.execute('''
        CREATE TABLE matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            match_date TEXT,
            played INTEGER DEFAULT 0,
            FOREIGN KEY (home_team_id) REFERENCES teams(id),
            FOREIGN KEY (away_team_id) REFERENCES teams(id)
        )
    ''')
    
    # Crear tabla de eventos de partido
    cursor.execute('''
        CREATE TABLE match_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            minute INTEGER,
            event_type TEXT CHECK(event_type IN ('GOAL', 'YELLOW_CARD', 'RED_CARD', 'PENALTY', 'SUBSTITUTION')),
            player_id INTEGER,
            description TEXT,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')

    # Crear tabla de sanciones (jugadores suspendidos)
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
    
    # ============ INSERTAR DATOS ============
    
    # Equipos
    teams = [
        ("Atlético del Puerto", "ADP", "Estadio Marítimo", "Puerto Real"),
        ("Real Club Deportivo", "RCD", "Estadio Real", "Ciudad Jardín"),
        ("Sporting Victoria", "SVI", "Victoria Arena", "San Martín"),
        ("Unión Atlética", "UAT", "Estadio Central", "Valle Hermoso"),
        ("Club Deportivo Alameda", "CDA", "Parque Alameda", "Los Álamos"),
        ("Racing del Norte", "RNO", "Estadio del Norte", "Puerta Norte")
    ]
    cursor.executemany("INSERT INTO teams (name, short_name, stadium, city) VALUES (?, ?, ?, ?)", teams)
    
    # Jugadores - 18 por equipo (voy a crearlos con datos variados)
    players = []
    
    # Jugadores base - nombres variados para dar realismo
    first_names = ["Carlos", "Miguel", "Andrés", "Javier", "Diego", "Raúl", "Sergio", "Pablo", 
                   "Fernando", "Roberto", "Daniel", "Alberto", "Marcos", "David", "Alejandro", "Luis",
                   "Hugo", "Martín", "Lucas", "Mateo", "Nicolás", "Gabriel", "Adrián", "Iker"]
    last_names = ["García", "Martínez", "López", "Rodríguez", "Torres", "Ramírez", "Flores", "Morales",
                  "Sánchez", "Vargas", "Castro", "Ortega", "Medina", "Ruiz", "Álvarez", "Navarro",
                  "Silva", "Moreno", "Romero", "Domínguez", "Mendoza", "Ibáñez", "Paredes", "Cruz"]
    
    import random
    random.seed(42)  # Para consistencia en los datos
    
    positions = ["GK"]*2 + ["DEF"]*6 + ["MID"]*6 + ["FWD"]*4  # 18 jugadores: 2 porteros, 6 defensas, 6 medios, 4 delanteros
    
    for team_id in range(1, 7):
        team_positions = positions.copy()
        random.shuffle(team_positions)  # Mezclar posiciones para variedad
        
        for i in range(18):
            pos = team_positions[i]
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # Generar stats según posición
            if pos == "GK":
                att, df, mid, gk = random.randint(20,40), random.randint(40,60), random.randint(20,40), random.randint(70,90)
            elif pos == "DEF":
                att, df, mid, gk = random.randint(40,60), random.randint(70,90), random.randint(50,70), random.randint(20,40)
            elif pos == "MID":
                att, df, mid, gk = random.randint(50,70), random.randint(50,70), random.randint(70,90), random.randint(20,40)
            else:  # FWD
                att, df, mid, gk = random.randint(70,90), random.randint(30,50), random.randint(50,70), random.randint(10,30)
            
            players.append((
                team_id, name, pos, i+1, random.randint(19, 34),
                att, df, mid, gk,
                random.randint(50, 85),  # stamina
                random.randint(50, 90)   # speed
            ))
    
    cursor.executemany('''
        INSERT INTO players (team_id, name, position, number, age, attack, defense, midfield, goalkeeping, stamina, speed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', players)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos creada exitosamente!")
    print(f"📊 6 equipos y {len(players)} jugadores cargados.")
    
    # Mostrar resumen
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    cursor.execute("SELECT short_name, COUNT(*) FROM teams t JOIN players p ON t.id = p.team_id GROUP BY t.id")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} jugadores")
    conn.close()

if __name__ == "__main__":
    create_database()