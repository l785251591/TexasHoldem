import random
import math
from typing import List, Dict, Any, Tuple
from .player import Player, PlayerAction
from .hand_evaluator import HandEvaluator
from .card import Card

class BotPlayer(Player):
    """机器人玩家基础类"""
    
    def __init__(self, player_id: str, name: str, difficulty: str, chips: int = 1000):
        super().__init__(player_id, name, chips)
        self.difficulty = difficulty
        self.aggression_factor = self._get_aggression_factor()
        self.bluff_frequency = self._get_bluff_frequency()
        
    def _get_aggression_factor(self) -> float:
        """根据难度获取攻击性因子"""
        if self.difficulty == "easy":
            return random.uniform(0.1, 0.3)
        elif self.difficulty == "medium":
            return random.uniform(0.3, 0.6)
        else:  # hard
            return random.uniform(0.6, 0.9)
    
    def _get_bluff_frequency(self) -> float:
        """根据难度获取虚张声势频率"""
        if self.difficulty == "easy":
            return random.uniform(0.05, 0.15)
        elif self.difficulty == "medium":
            return random.uniform(0.15, 0.25)
        else:  # hard
            return random.uniform(0.25, 0.35)

    def calculate_pot_odds(self, game_state: Dict[str, Any]) -> float:
        """计算底池赔率"""
        call_amount = game_state.get('call_amount', 0)
        pot_size = game_state.get('pot', 0)
        
        if call_amount == 0:
            return float('inf')  # 无需跟注时，赔率无限大
        
        return pot_size / call_amount

    def estimate_hand_strength(self, game_state: Dict[str, Any]) -> float:
        """评估手牌强度"""
        from .card import Card, Suit, Rank
        
        community_cards = game_state.get('community_cards', [])
        
        # 如果community_cards是字符串格式，需要转换回Card对象
        if community_cards and isinstance(community_cards[0], str):
            # 将字符串转换回Card对象
            card_objects = []
            for card_str in community_cards:
                # 解析字符串格式的牌，例如 "A♠"
                try:
                    card_objects.append(Card.from_string(card_str))
                except:
                    # 如果解析失败，跳过这张牌
                    continue
            community_cards = card_objects
        
        all_cards = self.hole_cards + community_cards
        
        # 只有当牌数达到5张或7张时才使用HandEvaluator
        if len(all_cards) == 5 or len(all_cards) == 7:
            return HandEvaluator.get_hand_strength(all_cards)
        elif len(all_cards) >= 3:
            # 翻牌或转牌阶段的简化评估
            return self._evaluate_partial_hand_strength(all_cards)
        else:
            # 翻牌前的简单评估
            return self._evaluate_preflop_strength()
    
    def _evaluate_preflop_strength(self) -> float:
        """评估翻牌前手牌强度"""
        if not self.hole_cards or len(self.hole_cards) != 2:
            return 0.2
        
        card1, card2 = self.hole_cards
        
        # 口袋对子
        if card1.rank_value == card2.rank_value:
            if card1.rank_value >= 10:  # TT+
                return 0.9
            elif card1.rank_value >= 7:  # 77-99
                return 0.7
            else:  # 22-66
                return 0.5
        
        # 同花连张
        if card1.suit == card2.suit:
            if abs(card1.rank_value - card2.rank_value) == 1:
                return 0.8
        
        # 高牌组合
        high_card = max(card1.rank_value, card2.rank_value)
        low_card = min(card1.rank_value, card2.rank_value)
        
        if high_card == 14:  # A
            if low_card >= 11:  # AK, AQ, AJ
                return 0.85
            elif low_card >= 9:  # AT, A9
                return 0.6
            else:
                return 0.4
        elif high_card >= 13:  # K, Q
            if low_card >= 11:
                return 0.7
            elif low_card >= 9:
                return 0.5
            else:
                return 0.3
        
        return 0.2

    def _evaluate_partial_hand_strength(self, all_cards: List) -> float:
        """评估部分手牌强度（用于翻牌和转牌阶段）"""
        if len(all_cards) < 3:
            return self._evaluate_preflop_strength()
        
        # 简化的评估逻辑
        values = [card.rank_value for card in all_cards]
        suits = [card.suit for card in all_cards]
        
        from collections import Counter
        value_counts = Counter(values)
        suit_counts = Counter(suits)
        
        # 基础分数
        base_score = 0.3
        
        # 检查对子、三条等
        counts = sorted(value_counts.values(), reverse=True)
        if counts[0] >= 3:  # 三条或更好
            base_score = 0.8
        elif counts[0] == 2:  # 一对
            pair_value = max([v for v, c in value_counts.items() if c == 2])
            if pair_value >= 10:  # 高对
                base_score = 0.6
            else:
                base_score = 0.5
        
        # 检查同花可能性
        max_suit_count = max(suit_counts.values())
        if max_suit_count >= 3:  # 有同花可能
            base_score += 0.1
        
        # 检查顺子可能性
        unique_values = sorted(set(values))
        if len(unique_values) >= 3:
            # 简单的连续性检查
            consecutive_count = 1
            max_consecutive = 1
            for i in range(1, len(unique_values)):
                if unique_values[i] - unique_values[i-1] == 1:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1
            
            if max_consecutive >= 3:  # 有顺子可能
                base_score += 0.1
        
        return min(0.9, base_score)

    def calculate_kelly_criterion(self, win_probability: float, pot_odds: float) -> float:
        """使用凯利公式计算最优下注比例"""
        if pot_odds <= 1:
            return 0.0
        
        # 凯利公式: f = (bp - q) / b
        # 其中 b = 赔率, p = 胜率, q = 败率 = 1-p
        b = pot_odds - 1  # 净赔率
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # 限制最大下注比例，避免过度激进
        return max(0, min(kelly_fraction, 0.25))

class EasyBot(BotPlayer):
    """简单机器人 - 基础逻辑，较少虚张声势"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        super().__init__(player_id, name, "easy", chips)
    
    def get_action(self, game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """简单机器人的决策逻辑"""
        hand_strength = self.estimate_hand_strength(game_state)
        call_amount = game_state.get('call_amount', 0)
        pot_size = game_state.get('pot', 0)
        
        # 非常简单的决策逻辑
        if hand_strength < 0.3:
            if call_amount == 0:
                return PlayerAction.CHECK, 0
            else:
                return PlayerAction.FOLD, 0
        
        elif hand_strength < 0.6:
            if call_amount == 0:
                return PlayerAction.CHECK, 0
            elif call_amount <= self.chips * 0.1:  # 只愿意跟小注
                return PlayerAction.CALL, call_amount
            else:
                return PlayerAction.FOLD, 0
        
        else:  # 强牌
            if call_amount == 0:
                # 有机会下注
                bet_amount = min(int(pot_size * 0.5), int(self.chips * 0.2))
                if bet_amount > 0:
                    return PlayerAction.RAISE, bet_amount
                else:
                    return PlayerAction.CHECK, 0
            else:
                return PlayerAction.CALL, call_amount

class MediumBot(BotPlayer):
    """中等机器人 - 考虑底池赔率和位置"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        super().__init__(player_id, name, "medium", chips)
    
    def get_action(self, game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """中等机器人的决策逻辑"""
        hand_strength = self.estimate_hand_strength(game_state)
        pot_odds = self.calculate_pot_odds(game_state)
        call_amount = game_state.get('call_amount', 0)
        pot_size = game_state.get('pot', 0)
        
        # 考虑底池赔率的决策
        if hand_strength < 0.3:
            # 弱牌
            if call_amount == 0:
                # 偶尔虚张声势
                if random.random() < self.bluff_frequency:
                    bet_amount = min(int(pot_size * 0.3), int(self.chips * 0.1))
                    return PlayerAction.RAISE, bet_amount
                else:
                    return PlayerAction.CHECK, 0
            else:
                # 根据底池赔率决定是否跟注
                if pot_odds > 4 and call_amount <= self.chips * 0.05:
                    return PlayerAction.CALL, call_amount
                else:
                    return PlayerAction.FOLD, 0
        
        elif hand_strength < 0.7:
            # 中等牌力
            if call_amount == 0:
                return PlayerAction.CHECK, 0
            elif pot_odds >= 2:
                return PlayerAction.CALL, call_amount
            else:
                return PlayerAction.FOLD, 0
        
        else:
            # 强牌
            if call_amount == 0:
                bet_amount = min(int(pot_size * 0.7), int(self.chips * 0.3))
                return PlayerAction.RAISE, bet_amount
            else:
                # 考虑加注
                if hand_strength > 0.85 and self.chips > call_amount * 2:
                    raise_amount = call_amount + min(int(pot_size * 0.5), int(self.chips * 0.4))
                    return PlayerAction.RAISE, raise_amount
                else:
                    return PlayerAction.CALL, call_amount

class HardBot(BotPlayer):
    """困难机器人 - 使用凯利公式和高级策略"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        super().__init__(player_id, name, "hard", chips)
    
    def get_action(self, game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """困难机器人的决策逻辑"""
        hand_strength = self.estimate_hand_strength(game_state)
        pot_odds = self.calculate_pot_odds(game_state)
        call_amount = game_state.get('call_amount', 0)
        pot_size = game_state.get('pot', 0)
        
        # 估计胜率（简化版本）
        win_probability = self._estimate_win_probability(hand_strength, game_state)
        
        # 使用凯利公式计算最优下注比例
        kelly_fraction = self.calculate_kelly_criterion(win_probability, pot_odds)
        
        # 考虑位置和对手行为
        position_factor = self._get_position_factor(game_state)
        adjusted_strength = hand_strength * position_factor
        
        if adjusted_strength < 0.25:
            # 很弱的牌
            if call_amount == 0:
                # 偶尔虚张声势，特别是在好位置
                if random.random() < self.bluff_frequency * position_factor:
                    bet_amount = min(int(pot_size * 0.4), int(self.chips * 0.15))
                    return PlayerAction.RAISE, bet_amount
                else:
                    return PlayerAction.CHECK, 0
            else:
                # 根据赔率和凯利公式决定
                if kelly_fraction > 0.05 and pot_odds > 5:
                    return PlayerAction.CALL, call_amount
                else:
                    return PlayerAction.FOLD, 0
        
        elif adjusted_strength < 0.6:
            # 中等牌力
            if call_amount == 0:
                # 根据牌力和位置决定是否下注
                if adjusted_strength > 0.45:
                    bet_amount = min(int(pot_size * 0.5), int(self.chips * kelly_fraction))
                    return PlayerAction.RAISE, max(bet_amount, game_state.get('min_raise', 20))
                else:
                    return PlayerAction.CHECK, 0
            else:
                # 根据凯利公式和赔率
                if kelly_fraction > 0.1 or pot_odds > 3:
                    return PlayerAction.CALL, call_amount
                else:
                    return PlayerAction.FOLD, 0
        
        else:
            # 强牌
            if call_amount == 0:
                # 价值下注
                bet_amount = min(int(pot_size * 0.8), int(self.chips * min(kelly_fraction * 2, 0.4)))
                return PlayerAction.RAISE, max(bet_amount, game_state.get('min_raise', 20))
            else:
                # 考虑加注获取更多价值
                if adjusted_strength > 0.8:
                    raise_amount = call_amount + min(int(pot_size * 0.6), int(self.chips * kelly_fraction))
                    return PlayerAction.RAISE, raise_amount
                else:
                    return PlayerAction.CALL, call_amount
    
    def _estimate_win_probability(self, hand_strength: float, game_state: Dict[str, Any]) -> float:
        """估计获胜概率"""
        # 简化的胜率估计，考虑对手数量
        opponents_count = len([p for p in game_state.get('other_players', []) 
                              if not p.get('is_folded', False)])
        
        # 基础胜率基于手牌强度
        base_win_rate = hand_strength
        
        # 根据对手数量调整胜率
        if opponents_count > 1:
            # 对手越多，获胜概率越低
            adjusted_win_rate = base_win_rate ** (1 + (opponents_count - 1) * 0.2)
        else:
            adjusted_win_rate = base_win_rate
        
        return max(0.1, min(0.9, adjusted_win_rate))
    
    def _get_position_factor(self, game_state: Dict[str, Any]) -> float:
        """获取位置因子"""
        # 简化的位置评估
        # 在实际游戏中，这应该基于真实的位置信息
        total_players = len(game_state.get('other_players', [])) + 1
        if total_players <= 2:
            return 1.0
        
        # 假设后面的位置更有优势
        position_ratio = self.position / (total_players - 1)
        return 0.8 + 0.4 * position_ratio  # 0.8 到 1.2 的范围 