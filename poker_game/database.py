import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os

class GameDatabase:
    """游戏数据库管理类"""
    
    def __init__(self, db_path: str = "data/poker_game.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 游戏记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    winner_id TEXT,
                    total_pot INTEGER,
                    players_count INTEGER,
                    game_data TEXT  -- JSON格式的游戏详细数据
                )
            ''')
            
            # 游戏手数记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    hand_number INTEGER,
                    pot_size INTEGER,
                    winner_id TEXT,
                    showdown BOOLEAN,
                    community_cards TEXT,  -- JSON格式
                    hand_data TEXT,  -- JSON格式的手牌详细数据
                    timestamp TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
            ''')
            
            # 玩家动作记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hand_id INTEGER,
                    player_id TEXT,
                    action_type TEXT,  -- fold, call, raise, check, all_in
                    amount INTEGER,
                    position INTEGER,
                    betting_round TEXT,  -- preflop, flop, turn, river
                    hand_cards TEXT,  -- JSON格式的手牌
                    pot_odds REAL,
                    hand_strength REAL,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (hand_id) REFERENCES hands (id)
                )
            ''')
            
            # 机器人学习数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT,
                    game_state TEXT,  -- JSON格式的游戏状态
                    action_taken TEXT,
                    reward REAL,
                    hand_strength REAL,
                    pot_odds REAL,
                    position INTEGER,
                    opponents_count INTEGER,
                    timestamp TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_game(self, start_time: datetime, end_time: datetime, 
                  winner_id: str, total_pot: int, players_count: int, 
                  game_data: Dict[str, Any]) -> int:
        """保存游戏记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO games (start_time, end_time, winner_id, total_pot, players_count, game_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (start_time, end_time, winner_id, total_pot, players_count, json.dumps(game_data)))
            
            return cursor.lastrowid
    
    def save_hand(self, game_id: int, hand_number: int, pot_size: int, 
                  winner_id: str, showdown: bool, community_cards: List[str], 
                  hand_data: Dict[str, Any]) -> int:
        """保存手牌记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hands (game_id, hand_number, pot_size, winner_id, showdown, 
                                 community_cards, hand_data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (game_id, hand_number, pot_size, winner_id, showdown, 
                  json.dumps(community_cards), json.dumps(hand_data), datetime.now()))
            
            return cursor.lastrowid
    
    def save_player_action(self, hand_id: int, player_id: str, action_type: str, 
                          amount: int, position: int, betting_round: str, 
                          hand_cards: List[str], pot_odds: float, hand_strength: float):
        """保存玩家动作记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO player_actions (hand_id, player_id, action_type, amount, position,
                                          betting_round, hand_cards, pot_odds, hand_strength, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hand_id, player_id, action_type, amount, position, betting_round,
                  json.dumps(hand_cards), pot_odds, hand_strength, datetime.now()))
    
    def save_bot_learning_data(self, bot_id: str, game_state: Dict[str, Any], 
                              action_taken: str, reward: float, hand_strength: float,
                              pot_odds: float, position: int, opponents_count: int):
        """保存机器人学习数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bot_learning_data (bot_id, game_state, action_taken, reward,
                                             hand_strength, pot_odds, position, opponents_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bot_id, json.dumps(game_state), action_taken, reward, hand_strength,
                  pot_odds, position, opponents_count, datetime.now()))
    
    def get_bot_learning_data(self, bot_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取机器人学习数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bot_learning_data 
                WHERE bot_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (bot_id, limit))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
    
    def get_game_history(self, player_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """获取游戏历史记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if player_id:
                cursor.execute('''
                    SELECT * FROM games 
                    WHERE game_data LIKE ? 
                    ORDER BY start_time DESC 
                    LIMIT ?
                ''', (f'%{player_id}%', limit))
            else:
                cursor.execute('''
                    SELECT * FROM games 
                    ORDER BY start_time DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
    
    def get_player_statistics(self, player_id: str) -> Dict[str, Any]:
        """获取玩家统计数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 游戏总数
            cursor.execute('''
                SELECT COUNT(*) FROM games 
                WHERE game_data LIKE ?
            ''', (f'%{player_id}%',))
            total_games = cursor.fetchone()[0]
            
            # 胜利次数
            cursor.execute('''
                SELECT COUNT(*) FROM games 
                WHERE winner_id = ?
            ''', (player_id,))
            wins = cursor.fetchone()[0]
            
            # 获取最近的动作统计
            cursor.execute('''
                SELECT action_type, COUNT(*) as count, AVG(amount) as avg_amount
                FROM player_actions 
                WHERE player_id = ?
                GROUP BY action_type
            ''', (player_id,))
            actions_stats = cursor.fetchall()
            
            return {
                'total_games': total_games,
                'wins': wins,
                'win_rate': wins / max(total_games, 1),
                'actions_stats': {action[0]: {'count': action[1], 'avg_amount': action[2]} 
                                for action in actions_stats}
            }
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 删除旧的游戏记录
            cursor.execute('DELETE FROM games WHERE start_time < ?', (cutoff_date,))
            cursor.execute('DELETE FROM bot_learning_data WHERE timestamp < ?', (cutoff_date,))
            
            conn.commit() 