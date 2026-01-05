import pyodbc
import json
import datetime

class DatabaseManager:
    def __init__(self):
        self.driver = '{ODBC Driver 17 for SQL Server}'
        
        self.server = r'DESKTOP-FPJ715K\SQLEXPRESS' 
        
        self.database = 'TowerDefenseDB'
        
        self.conn_str = (
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'Trusted_Connection=yes;'
        )

        try:
            self.create_tables()
        except Exception as e:
            print(f"⚠️ ПОМИЛКА БД ПРИ СТАРТІ: {e}")
            print("Перевір: 1) Чи створена БД 'TowerDefenseDB' в SSMS? 2) Чи встановлений ODBC Driver 17?")

    def get_connection(self):
        try:
            return pyodbc.connect(self.conn_str)
        except pyodbc.Error as e:
            print(f"❌ Не вдалося підключитися до SQL Server: {e}")
            return None

    def create_tables(self):
        conn = self.get_connection()
        if not conn: return
        
        cursor = conn.cursor()
        
        if not cursor.tables(table='players', tableType='TABLE').fetchone():
            cursor.execute('''
                CREATE TABLE players (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(50) UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT GETDATE()
                )
            ''')
            print("✅ БД: Таблиця 'players' створена.")

        if not cursor.tables(table='maps', tableType='TABLE').fetchone():
            cursor.execute('''
                CREATE TABLE maps (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    seed NVARCHAR(50),
                    map_data NVARCHAR(MAX), 
                    difficulty INT,
                    created_at DATETIME DEFAULT GETDATE()
                )
            ''')
            print("✅ БД: Таблиця 'maps' створена.")

        if not cursor.tables(table='scores_survival', tableType='TABLE').fetchone():
            cursor.execute('''
                CREATE TABLE scores_survival (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    player_id INT FOREIGN KEY REFERENCES players(id),
                    max_wave INT,
                    time_played FLOAT,
                    date_played DATETIME DEFAULT GETDATE()
                )
            ''')
            print("✅ БД: Таблиця 'scores_survival' створена.")

        if not cursor.tables(table='scores_campaign', tableType='TABLE').fetchone():
            cursor.execute('''
                CREATE TABLE scores_campaign (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    player_id INT FOREIGN KEY REFERENCES players(id),
                    max_level INT,
                    time_total FLOAT,
                    date_played DATETIME DEFAULT GETDATE()
                )
            ''')
            print("✅ БД: Таблиця 'scores_campaign' створена.")

        conn.commit()
        conn.close()

    def get_player_id(self, name):
        conn = self.get_connection()
        if not conn: return None
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                player_id = row[0]
            else:
                cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
                conn.commit()
                cursor.execute("SELECT @@IDENTITY")
                player_id = int(cursor.fetchone()[0])
                print(f"👤 Новий гравець: {name} (ID: {player_id})")
            return player_id
        except pyodbc.Error as e:
            print(f"Помилка гравця: {e}")
            return None
        finally:
            conn.close()

    def save_survival_score(self, player_id, wave, time_played):
        conn = self.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scores_survival (player_id, max_wave, time_played)
                VALUES (?, ?, ?)
            ''', (player_id, wave, time_played))
            conn.commit()
            print(f"💾 Рекорд збережено: Хвиля {wave}")
        finally:
            conn.close()

    def save_campaign_progress(self, player_id, level, time_total):
        conn = self.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scores_campaign (player_id, max_level, time_total)
                VALUES (?, ?, ?)
            ''', (player_id, level, time_total))
            conn.commit()
            print(f"💾 Прогрес збережено: Рівень {level}")
        finally:
            conn.close()

    def get_campaign_stats(self, player_id):
        """Повертає (max_level, total_time_played) для гравця"""
        conn = self.get_connection()
        if not conn: return (1, 0)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(max_level), SUM(time_total) 
                FROM scores_campaign 
                WHERE player_id = ?
            ''', (player_id,))
            
            row = cursor.fetchone()
            if row and row[0] is not None:
                return (row[0], int(row[1]))
            return (1, 0)
        except Exception as e:
            print(f"Помилка отримання статистики кампанії: {e}")
            return (1, 0)
        finally:
            conn.close()

    def get_survival_stats(self, player_id):
        """Повертає (max_wave, best_time) для гравця"""
        conn = self.get_connection()
        if not conn: return (0, 0)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(max_wave), MAX(time_played) 
                FROM scores_survival 
                WHERE player_id = ?
            ''', (player_id,))
            
            row = cursor.fetchone()
            if row and row[0] is not None:
                return (row[0], int(row[1]))
            return (0, 0)
        except Exception as e:
            print(f"Помилка отримання статистики виживання: {e}")
            return (0, 0)
        finally:
            conn.close()

    def get_top_survival(self, limit=10):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = f'''
                SELECT TOP {limit} p.name, s.max_wave, s.time_played
                FROM scores_survival s
                JOIN players p ON s.player_id = p.id
                ORDER BY s.max_wave DESC, s.time_played DESC
            '''
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_top_campaign(self, limit=10):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = f'''
                SELECT TOP {limit} p.name, c.max_level, c.time_total
                FROM scores_campaign c
                JOIN players p ON c.player_id = p.id
                ORDER BY c.max_level DESC, c.time_total ASC
            '''
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def save_generated_map(self, map_data_dict, seed, difficulty):
        conn = self.get_connection()
        if not conn: return None
        try:
            json_str = json.dumps(map_data_dict)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO maps (seed, map_data, difficulty)
                VALUES (?, ?, ?)
            ''', (str(seed), json_str, difficulty))
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            return int(cursor.fetchone()[0])
        except Exception as e:
            print(f"Помилка карти: {e}")
            return None
        finally:
            conn.close()

    def load_map(self, map_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT map_data FROM maps WHERE id = ?", (map_id,))
            row = cursor.fetchone()
            if row: return json.loads(row[0])
            return None
        finally:
            conn.close()