import os
import re
import psycopg2
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
        }
        # Если есть DATABASE_URL, используем его (для Railway)
        if os.getenv("DATABASE_URL"):
            self.conn_params = {
                "dsn": os.getenv("DATABASE_URL")
            }
        self.create_tables()

    @contextmanager
    def get_cursor(self):
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def create_tables(self):
        with self.get_cursor() as cur:
            # Таблица аниме
            cur.execute("""
                CREATE TABLE IF NOT EXISTS anime (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    voiceover TEXT NOT NULL DEFAULT 'VexeraDubbing',
                    poster_url TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Таблица серий
            cur.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id SERIAL PRIMARY KEY,
                    anime_id INTEGER NOT NULL REFERENCES anime(id) ON DELETE CASCADE,
                    episode_number INTEGER NOT NULL,
                    vk_video_url TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT unique_episode UNIQUE (anime_id, episode_number)
                )
            """)
            
            # Индексы для быстрого поиска
            cur.execute("CREATE INDEX IF NOT EXISTS idx_anime_title ON anime(title)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_episodes_anime ON episodes(anime_id)")

    def search_anime(self, query: str):
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id, title, description, voiceover, poster_url 
                FROM anime 
                WHERE title ILIKE %s 
                LIMIT 10
            """, (f"%{query}%",))
            return self.dictfetchall(cur)

    def get_anime_by_id(self, anime_id: int):
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id, title, description, voiceover, poster_url 
                FROM anime 
                WHERE id = %s
            """, (anime_id,))
            return self.dictfetchone(cur)

    def get_episodes(self, anime_id: int):
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT episode_number, vk_video_url 
                FROM episodes 
                WHERE anime_id = %s 
                ORDER BY episode_number
            """, (anime_id,))
            return self.dictfetchall(cur)

    def get_episode_url(self, anime_id: int, episode_number: int):
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT vk_video_url 
                FROM episodes 
                WHERE anime_id = %s AND episode_number = %s
            """, (anime_id, episode_number))
            result = cur.fetchone()
            return result[0] if result else None

    def add_anime(self, title: str, voiceover: str, description: str = "", poster_url: str = None):
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO anime (title, description, voiceover, poster_url) 
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (title, description, voiceover, poster_url))
            return cur.fetchone()[0]

    def add_episode(self, anime_id: int, episode_number: int, vk_url: str):
        if not self.is_valid_vk_url(vk_url):
            raise ValueError("Некорректная ссылка VK")
        
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO episodes (anime_id, episode_number, vk_video_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (anime_id, episode_number) DO UPDATE
                SET vk_video_url = EXCLUDED.vk_video_url
            """, (anime_id, episode_number, vk_url))

    def get_all_anime(self):
        with self.get_cursor() as cur:
            cur.execute("SELECT id, title FROM anime ORDER BY title")
            return self.dictfetchall(cur)

    @staticmethod
    def is_valid_vk_url(url: str) -> bool:
        patterns = [
            r'https?://vk\.com/video[-\w]+_\d+',
            r'https?://vk\.com/video_ext\.php\?.*'
        ]
        return any(re.match(pattern, url) for pattern in patterns)

    @staticmethod
    def dictfetchall(cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def dictfetchone(cursor):
        row = cursor.fetchone()
        if not row:
            return None
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
