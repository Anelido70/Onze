# Colores y emojis para cada equipo
TEAM_STYLES = {
    'ADP': {
        'name': 'Atlético del Puerto',
        'color': '#1a5276',      # Azul marino
        'secondary': '#2e86c1',   # Azul claro
        'emoji': '⚓',
        'stadium': 'Estadio Marítimo'
    },
    'RCD': {
        'name': 'Real Club Deportivo',
        'color': '#922b21',      # Rojo oscuro
        'secondary': '#c0392b',   # Rojo
        'emoji': '👑',
        'stadium': 'Estadio Real'
    },
    'SVI': {
        'name': 'Sporting Victoria',
        'color': '#196f3d',      # Verde oscuro
        'secondary': '#27ae60',   # Verde
        'emoji': '🏆',
        'stadium': 'Victoria Arena'
    },
    'UAT': {
        'name': 'Unión Atlética',
        'color': '#935116',      # Marrón
        'secondary': '#e67e22',   # Naranja
        'emoji': '🤝',
        'stadium': 'Estadio Central'
    },
    'CDA': {
        'name': 'Club Deportivo Alameda',
        'color': '#6c3483',      # Púrpura
        'secondary': '#a569bd',   # Lila
        'emoji': '🌳',
        'stadium': 'Parque Alameda'
    },
    'RNO': {
        'name': 'Racing del Norte',
        'color': '#1b4f72',      # Azul oscuro
        'secondary': '#3498db',   # Azul brillante
        'emoji': '🚂',
        'stadium': 'Estadio del Norte'
    }
}

def get_team_style(short_name):
    """Obtiene el estilo de un equipo por su nombre corto"""
    return TEAM_STYLES.get(short_name, {
        'color': '#95a5a6',
        'secondary': '#bdc3c7',
        'emoji': '⚽',
        'stadium': 'Desconocido'
    })