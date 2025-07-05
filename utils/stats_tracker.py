import sqlite3
import time
import os
from utils.logger import log

DB_PATH = os.path.join('models', 'trivia_knowledge_base.db')

class StatsTracker:
    def __init__(self):
        self.start_time = time.time()
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        log.info("Statistics Tracker initialized.")

    def _update_stat(self, key, value):
        """Helper to update a stat in the database."""
        self.cursor.execute("INSERT OR REPLACE INTO learning_stats (stat_key, stat_value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def increment_stat(self, key, increment_by=1):
        """Increments a numerical stat in the database."""
        self.cursor.execute("SELECT stat_value FROM learning_stats WHERE stat_key = ?", (key,))
        result = self.cursor.fetchone()
        current_value = int(result[0]) if result else 0
        self._update_stat(key, current_value + increment_by)

    def track_latency(self, component, duration_ms):
        """Logs the latency of a specific component."""
        log.debug(f"Performance Metric: {component} took {duration_ms:.2f} ms.")
        # In a more advanced system, you could average these values in the DB.

    def track_api_cost(self, tokens_used):
        """Tracks the estimated cost of API usage."""
        # This is a simplified model. Pricing depends on the specific API.
        cost_per_1k_tokens = 0.002 # Example cost
        cost = (tokens_used / 1000) * cost_per_1k_tokens
        self.increment_stat("total_api_cost", cost)
        log.info(f"Tracked API usage: {tokens_used} tokens, estimated cost: ${cost:.6f}")

    def generate_dashboard_data(self):
        """Generates a dictionary of key stats for a dashboard."""
        self.cursor.execute("SELECT stat_key, stat_value FROM learning_stats")
        stats = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        try:
            total_q = int(stats.get('total_questions_answered', 0))
            correct_q = int(stats.get('total_correct_answers', 0))
            accuracy = (correct_q / total_q) * 100 if total_q > 0 else 0
            stats['accuracy'] = f"{accuracy:.2f}%"
        except (ValueError, TypeError):
            stats['accuracy'] = "N/A"

        return stats

# Global instance
stats_tracker = StatsTracker()
