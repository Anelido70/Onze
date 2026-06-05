from simulation.match_simulator import MatchSimulator
from simulation.league_simulator import LeagueSimulator
from utils import *
import sqlite3

class GameManager:
    def __init__(self):
        self.match_simulator = MatchSimulator()
        self.league_simulator = LeagueSimulator()
        
    def main_menu(self):
        """Menú principal del juego"""
        while True:
            clear_screen()
            print_header("⚽ FOOTBALL MANAGER v1.0 ⚽")
            print("\n  📋 MENÚ PRINCIPAL")
            print("  " + "-" * 40)
            print("  1. ⚽ Simular partido entre dos equipos")
            print("  2. 🏆 Simular temporada completa")
            print("  3. 📊 Ver tabla de clasificación")
            print("  4. 📋 Ver alineación de un equipo")
            print("  5. 📜 Ver último resultado")
            print("  6. 🗑️  Limpiar base de datos (reiniciar)")
            print("  7. 🚪 Salir")
            print("  " + "-" * 40)
            
            option = input("\n  🎮 Elige una opción (1-7): ").strip()
            
            if option == '1':
                self.simulate_single_match()
            elif option == '2':
                self.simulate_full_season()
            elif option == '3':
                self.show_current_standings()
            elif option == '4':
                self.show_team_lineup()
            elif option == '5':
                self.show_last_match()
            elif option == '6':
                self.reset_database()
            elif option == '7':
                print("\n  👋 ¡Hasta pronto!")
                break
            else:
                print("\n  ❌ Opción no válida. Presiona Enter para continuar...")
                input()
    
    def simulate_single_match(self):
        """Simula un partido entre dos equipos seleccionados"""
        clear_screen()
        print_header("⚽ SIMULAR PARTIDO")
        
        # Mostrar equipos disponibles
        teams = get_available_teams()
        print("\n  📋 Equipos disponibles:")
        for i, team in enumerate(teams, 1):
            print(f"  {i}. {team[2]} - {team[1]}")
        
        # Seleccionar equipo local
        try:
            home_idx = int(input(f"\n  🏠 Elige equipo LOCAL (1-{len(teams)}): ")) - 1
            away_idx = int(input(f"  🚌 Elige equipo VISITANTE (1-{len(teams)}): ")) - 1
            
            if home_idx == away_idx:
                print("\n  ❌ No pueden ser el mismo equipo!")
                input("\n  Presiona Enter para continuar...")
                return
            
            home_team = teams[home_idx]
            away_team = teams[away_idx]
            
            # Mostrar alineaciones
            print(f"\n  📋 ALINEACIONES:")
            home_lineup = get_team_lineup(home_team[0])
            away_lineup = get_team_lineup(away_team[0])
            
            print_lineup(home_lineup)
            print_lineup(away_lineup)
            
            input(f"\n  ⚡ Presiona Enter para SIMULAR el partido...")
            
            # Simular partido
            clear_screen()
            print_header(f"⚽ {home_team[2]} vs {away_team[2]}")
            
            result = self.match_simulator.simulate_match(home_team[0], away_team[0])
            
            # Mostrar resultado y eventos
            print_match_result(result['match_id'])
            
            input(f"\n  Presiona Enter para continuar...")
            
        except (ValueError, IndexError):
            print("\n  ❌ Selección no válida!")
            input("\n  Presiona Enter para continuar...")
    
    def simulate_full_season(self):
        """Simula una temporada completa"""
        clear_screen()
        print_header("🏆 SIMULAR TEMPORADA")
        
        confirm = input("\n  ⚠️  ¿Estás seguro? Esto borrará la temporada anterior (s/n): ").lower()
        
        if confirm == 's':
            # Limpiar partidos anteriores
            conn = sqlite3.connect("football_manager.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM match_events")
            cursor.execute("DELETE FROM matches")
            conn.commit()
            conn.close()
            
            # Reiniciar simuladores
            self.match_simulator = MatchSimulator()
            self.league_simulator = LeagueSimulator()
            
            # Simular temporada
            self.league_simulator.simulate_season()
            
            input("\n  Presiona Enter para continuar...")
        else:
            print("\n  👍 Temporada cancelada.")
            input("\n  Presiona Enter para continuar...")
    
    def show_current_standings(self):
        """Muestra la tabla de clasificación actual"""
        clear_screen()
        self.league_simulator.show_standings()
        input("\n  Presiona Enter para continuar...")
    
    def show_team_lineup(self):
        """Muestra la alineación de un equipo"""
        clear_screen()
        print_header("📋 VER ALINEACIÓN")
        
        teams = get_available_teams()
        print("\n  📋 Equipos disponibles:")
        for i, team in enumerate(teams, 1):
            print(f"  {i}. {team[2]} - {team[1]}")
        
        try:
            idx = int(input(f"\n  🎯 Elige equipo (1-{len(teams)}): ")) - 1
            lineup = get_team_lineup(teams[idx][0])
            print_lineup(lineup)
            input("\n  Presiona Enter para continuar...")
        except (ValueError, IndexError):
            print("\n  ❌ Selección no válida!")
            input("\n  Presiona Enter para continuar...")
    
    def show_last_match(self):
        """Muestra el último partido jugado"""
        clear_screen()
        print_header("📜 ÚLTIMO RESULTADO")
        
        conn = sqlite3.connect("football_manager.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM matches 
            WHERE played = 1 
            ORDER BY id DESC 
            LIMIT 1
        ''')
        
        last_match = cursor.fetchone()
        conn.close()
        
        if last_match:
            print_match_result(last_match[0])
        else:
            print("\n  📭 No hay partidos jugados todavía.")
        
        input("\n  Presiona Enter para continuar...")
    
    def reset_database(self):
        """Reinicia la base de datos a su estado original"""
        clear_screen()
        print_header("🗑️  REINICIAR BASE DE DATOS")
        
        confirm = input("\n  ⚠️  ¿Estás seguro? Se perderán todos los datos (s/n): ").lower()
        
        if confirm == 's':
            self.match_simulator.close()
            self.league_simulator.close()
            
            import subprocess
            subprocess.run(["python", "init_database.py"])
            
            self.match_simulator = MatchSimulator()
            self.league_simulator = LeagueSimulator()
            
            print("\n  ✅ Base de datos reiniciada correctamente!")
            input("\n  Presiona Enter para continuar...")
        else:
            print("\n  👍 Reinicio cancelado.")
            input("\n  Presiona Enter para continuar...")
    
    def close(self):
        self.match_simulator.close()
        self.league_simulator.close()

if __name__ == "__main__":
    game = GameManager()
    try:
        game.main_menu()
    finally:
        game.close()