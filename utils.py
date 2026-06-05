import sqlite3
import os

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Imprime un encabezado bonito"""
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)

def get_team_lineup(team_id):
    """Obtiene la alineación de un equipo ordenada por posición"""
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, short_name FROM teams WHERE id = ?", (team_id,))
    team_info = cursor.fetchone()
    
    cursor.execute('''
        SELECT name, position, number, attack, defense, midfield, goalkeeping, stamina, speed
        FROM players 
        WHERE team_id = ?
        ORDER BY 
            CASE position 
                WHEN 'GK' THEN 1 
                WHEN 'DEF' THEN 2 
                WHEN 'MID' THEN 3 
                WHEN 'FWD' THEN 4 
            END,
            CASE position 
                WHEN 'GK' THEN goalkeeping 
                WHEN 'DEF' THEN defense 
                WHEN 'MID' THEN midfield 
                WHEN 'FWD' THEN attack 
            END DESC
    ''', (team_id,))
    
    players = cursor.fetchall()
    conn.close()
    
    return {
        'team_name': team_info[0],
        'team_short': team_info[1],
        'players': players
    }

def print_lineup(lineup):
    """Imprime una alineación formateada"""
    print(f"\n  📋 {lineup['team_name']} ({lineup['team_short']})")
    print(f"  {'-' * 60}")
    print(f"  {'Nº':<4} {'Jugador':<25} {'POS':<5} {'ATQ':<5} {'DEF':<5} {'MED':<5} {'POR':<5} {'RES':<5} {'VEL':<5}")
    print(f"  {'-' * 60}")
    
    for player in lineup['players']:
        name, pos, num, att, df, mid, gk, sta, spd = player
        print(f"  {num:<4} {name:<25} {pos:<5} {att:<5} {df:<5} {mid:<5} {gk:<5} {sta:<5} {spd:<5}")

def get_available_teams():
    """Obtiene lista de equipos disponibles"""
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, short_name FROM teams ORDER BY name")
    teams = cursor.fetchall()
    conn.close()
    return teams

def print_match_result(match_id):
    """Imprime el resultado detallado de un partido"""
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT th.name, ta.name, m.home_score, m.away_score, m.match_date
        FROM matches m
        JOIN teams th ON m.home_team_id = th.id
        JOIN teams ta ON m.away_team_id = ta.id
        WHERE m.id = ?
    ''', (match_id,))
    
    match = cursor.fetchone()
    if not match:
        print("  Partido no encontrado")
        conn.close()
        return
    
    home_name, away_name, home_score, away_score, date = match
    
    print(f"\n  🏟️  {home_name} {home_score} - {away_score} {away_name}")
    print(f"  📅 {date}")
    print(f"  {'-' * 60}")
    print(f"  📋 Eventos:")
    
    cursor.execute('''
        SELECT minute, event_type, description
        FROM match_events
        WHERE match_id = ?
        ORDER BY minute
    ''', (match_id,))
    
    events = cursor.fetchall()
    
    if not events:
        print("  Sin eventos destacados")
    else:
        for minute, event_type, description in events:
            icon = {'GOAL': '⚽', 'YELLOW_CARD': '🟨', 'RED_CARD': '🟥', 'PENALTY': '⚡', 'SUBSTITUTION': '🔄'}
            print(f"  {minute:2d}' {icon.get(event_type, '•')} {description}")
    
    conn.close()

def get_season_stats():
    """Obtiene estadísticas completas de la temporada"""
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    
    stats = {}
    
    # Máximo goleador
    cursor.execute('''
        SELECT p.name, t.short_name, COUNT(*) as goals
        FROM match_events me
        JOIN players p ON me.player_id = p.id
        JOIN teams t ON p.team_id = t.id
        WHERE me.event_type = 'GOAL'
        GROUP BY p.id
        ORDER BY goals DESC
        LIMIT 5
    ''')
    stats['top_scorers'] = cursor.fetchall()
    
    # Equipo más goleador
    cursor.execute('''
        SELECT t.name, SUM(m.home_score) as goals
        FROM matches m
        JOIN teams t ON m.home_team_id = t.id
        WHERE m.played = 1
        GROUP BY t.id
        ORDER BY goals DESC
        LIMIT 1
    ''')
    stats['most_goals_team'] = cursor.fetchone()
    
    # Total de goles en la temporada
    cursor.execute('''
        SELECT SUM(home_score + away_score), COUNT(*)
        FROM matches
        WHERE played = 1
    ''')
    total_goals, total_matches = cursor.fetchone()
    stats['total_goals'] = total_goals or 0
    stats['total_matches'] = total_matches or 0
    stats['avg_goals'] = round(stats['total_goals'] / max(stats['total_matches'], 1), 2)
    
    # Jugador con más tarjetas
    cursor.execute('''
        SELECT p.name, t.short_name, COUNT(*) as cards
        FROM match_events me
        JOIN players p ON me.player_id = p.id
        JOIN teams t ON p.team_id = t.id
        WHERE me.event_type IN ('YELLOW_CARD', 'RED_CARD')
        GROUP BY p.id
        ORDER BY cards DESC
        LIMIT 1
    ''')
    stats['most_cards'] = cursor.fetchone()
    
    # Mayor goleada
    cursor.execute('''
        SELECT th.name, ta.name, m.home_score, m.away_score,
               ABS(m.home_score - m.away_score) as diff
        FROM matches m
        JOIN teams th ON m.home_team_id = th.id
        JOIN teams ta ON m.away_team_id = ta.id
        WHERE m.played = 1
        ORDER BY diff DESC
        LIMIT 1
    ''')
    stats['biggest_win'] = cursor.fetchone()
    
    conn.close()
    return stats

def get_head_to_head(team1_id, team2_id):
    """Obtiene el historial de enfrentamientos entre dos equipos"""
    conn = sqlite3.connect("football_manager.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            th.short_name, ta.short_name,
            m.home_score, m.away_score,
            m.match_date
        FROM matches m
        JOIN teams th ON m.home_team_id = th.id
        JOIN teams ta ON m.away_team_id = ta.id
        WHERE (m.home_team_id = ? AND m.away_team_id = ?)
           OR (m.home_team_id = ? AND m.away_team_id = ?)
        ORDER BY m.match_date DESC
        LIMIT 5
    ''', (team1_id, team2_id, team2_id, team1_id))
    
    matches = cursor.fetchall()
    conn.close()
    return matches
    