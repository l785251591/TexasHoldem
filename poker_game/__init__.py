"""
德州扑克游戏包
包含完整的德州扑克游戏实现，支持人类玩家和不同智力水平的机器人
"""

from .card import Card, Deck, Suit, Rank
from .hand_evaluator import HandEvaluator, HandRank
from .player import Player, PlayerAction, HumanPlayer
from .bot_players import BotPlayer, EasyBot, MediumBot, HardBot

# 新的抽象基类架构
from .base_rl_bot import BaseRLBot, RLBotConfig

# 新的机器人实现 (推荐使用)
try:
    from .rl_bot_new import RLBot as RLBotNew
    from .improved_rl_bot_new import ImprovedRLBot as ImprovedRLBotNew
    from .conservative_rl_bot_new import ConservativeRLBot as ConservativeRLBotNew
    
    # 使用新实现
    RLBot = RLBotNew
    ImprovedRLBot = ImprovedRLBotNew
    ConservativeRLBot = ConservativeRLBotNew
    
    print("✅ 使用新的抽象基类架构的强化学习机器人")
    
except ImportError as e:
    # 回退到旧实现 (向后兼容)
    try:
        from .rl_bot import RLBot
        from .improved_rl_bot import ImprovedRLBot
        from .conservative_rl_bot import ConservativeRLBot
        print("⚠️  回退到旧的强化学习机器人实现")
    except ImportError:
        print("❌ 无法加载强化学习机器人模块")
        RLBot = None
        ImprovedRLBot = None
        ConservativeRLBot = None

from .training_tracker import TrainingTracker
from .game_engine import PokerGame
from .database import GameDatabase

__all__ = [
    'Card', 'Deck', 'Suit', 'Rank',
    'HandEvaluator', 'HandRank',
    'Player', 'PlayerAction', 'HumanPlayer',
    'BotPlayer', 'EasyBot', 'MediumBot', 'HardBot',
    'BaseRLBot', 'RLBotConfig',  # 新增抽象基类
    'RLBot', 'ImprovedRLBot', 'ConservativeRLBot',
    'TrainingTracker',
    'PokerGame',
    'GameDatabase'
]

__version__ = "2.0.0"  # 更新版本号以反映架构改进
__author__ = "AI Assistant"
__description__ = "完整的德州扑克游戏实现，支持人类玩家和AI机器人 - 现在使用抽象基类架构" 