from typing import List, Tuple, Optional
from collections import Counter
from enum import Enum
from .card import Card, Rank

class HandRank(Enum):
    """牌型排名"""
    HIGH_CARD = (1, "高牌")
    PAIR = (2, "一对")
    TWO_PAIR = (3, "两对")
    THREE_OF_KIND = (4, "三条")
    STRAIGHT = (5, "顺子")
    FLUSH = (6, "同花")
    FULL_HOUSE = (7, "葫芦")
    FOUR_OF_KIND = (8, "四条")
    STRAIGHT_FLUSH = (9, "同花顺")
    ROYAL_FLUSH = (10, "皇家同花顺")
    
    def __init__(self, rank_value, hand_name):
        self.rank_value = rank_value
        self.hand_name = hand_name

class HandEvaluator:
    """德州扑克牌型评估器"""
    
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        评估牌型
        返回 (牌型, 比较用的数值列表)
        """
        if len(cards) != 7 and len(cards) != 5:
            raise ValueError("德州扑克需要7张牌（2张手牌+5张公共牌）或5张牌进行评估")
        
        # 找出最好的5张牌组合
        if len(cards) == 7:
            best_hand = HandEvaluator._find_best_hand(cards)
        else:
            best_hand = cards
        
        return HandEvaluator._evaluate_five_cards(best_hand)
    
    @staticmethod
    def _find_best_hand(cards: List[Card]) -> List[Card]:
        """从7张牌中找出最好的5张牌组合"""
        from itertools import combinations
        
        best_hand = None
        best_rank = None
        best_kickers = None
        
        for five_cards in combinations(cards, 5):
            rank, kickers = HandEvaluator._evaluate_five_cards(list(five_cards))
            
            if best_hand is None or HandEvaluator._compare_hands(
                (rank, kickers), (best_rank, best_kickers)) > 0:
                best_hand = list(five_cards)
                best_rank = rank
                best_kickers = kickers
        
        return best_hand
    
    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """评估5张牌的牌型"""
        values = [card.rank_value for card in cards]
        suits = [card.suit for card in cards]
        
        value_counts = Counter(values)
        suit_counts = Counter(suits)
        
        # 检查是否为同花
        is_flush = len(suit_counts) == 1
        
        # 检查是否为顺子
        is_straight, straight_high = HandEvaluator._check_straight(values)
        
        # 检查牌型
        counts = sorted(value_counts.values(), reverse=True)
        unique_values = sorted(value_counts.keys(), reverse=True)
        
        if is_straight and is_flush:
            if straight_high == 14:  # A高顺子同花
                return HandRank.ROYAL_FLUSH, [14]
            else:
                return HandRank.STRAIGHT_FLUSH, [straight_high]
        
        if counts == [4, 1]:
            # 四条
            four_kind = [v for v, c in value_counts.items() if c == 4][0]
            kicker = [v for v, c in value_counts.items() if c == 1][0]
            return HandRank.FOUR_OF_KIND, [four_kind, kicker]
        
        if counts == [3, 2]:
            # 葫芦
            three_kind = [v for v, c in value_counts.items() if c == 3][0]
            pair = [v for v, c in value_counts.items() if c == 2][0]
            return HandRank.FULL_HOUSE, [three_kind, pair]
        
        if is_flush:
            return HandRank.FLUSH, sorted(values, reverse=True)
        
        if is_straight:
            return HandRank.STRAIGHT, [straight_high]
        
        if counts == [3, 1, 1]:
            # 三条
            three_kind = [v for v, c in value_counts.items() if c == 3][0]
            kickers = sorted([v for v, c in value_counts.items() if c == 1], reverse=True)
            return HandRank.THREE_OF_KIND, [three_kind] + kickers
        
        if counts == [2, 2, 1]:
            # 两对
            pairs = sorted([v for v, c in value_counts.items() if c == 2], reverse=True)
            kicker = [v for v, c in value_counts.items() if c == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        
        if counts == [2, 1, 1, 1]:
            # 一对
            pair = [v for v, c in value_counts.items() if c == 2][0]
            kickers = sorted([v for v, c in value_counts.items() if c == 1], reverse=True)
            return HandRank.PAIR, [pair] + kickers
        
        # 高牌
        return HandRank.HIGH_CARD, sorted(values, reverse=True)
    
    @staticmethod
    def _check_straight(values: List[int]) -> Tuple[bool, int]:
        """检查是否为顺子，返回(是否为顺子, 最高牌)"""
        unique_values = sorted(set(values))
        
        # 检查A-2-3-4-5的特殊顺子
        if unique_values == [2, 3, 4, 5, 14]:
            return True, 5
        
        # 检查普通顺子
        if len(unique_values) == 5:
            if unique_values[-1] - unique_values[0] == 4:
                return True, unique_values[-1]
        
        return False, 0
    
    @staticmethod
    def _compare_hands(hand1: Tuple[HandRank, List[int]], 
                      hand2: Tuple[HandRank, List[int]]) -> int:
        """
        比较两手牌的大小
        返回: 1 if hand1 > hand2, -1 if hand1 < hand2, 0 if equal
        """
        rank1, kickers1 = hand1
        rank2, kickers2 = hand2
        
        # 首先比较牌型
        if rank1.rank_value > rank2.rank_value:
            return 1
        elif rank1.rank_value < rank2.rank_value:
            return -1
        
        # 牌型相同，比较kicker
        for k1, k2 in zip(kickers1, kickers2):
            if k1 > k2:
                return 1
            elif k1 < k2:
                return -1
        
        return 0
    
    @staticmethod
    def compare_hands(cards1: List[Card], cards2: List[Card]) -> int:
        """比较两手牌，返回1表示cards1更大，-1表示cards2更大，0表示平手"""
        hand1 = HandEvaluator.evaluate_hand(cards1)
        hand2 = HandEvaluator.evaluate_hand(cards2)
        return HandEvaluator._compare_hands(hand1, hand2)
    
    @staticmethod
    def get_hand_strength(cards: List[Card]) -> float:
        """获取牌力强度(0-1之间的值)"""
        rank, kickers = HandEvaluator.evaluate_hand(cards)
        
        # 基础分数
        base_score = rank.rank_value / 10.0
        
        # 根据kicker调整分数
        kicker_bonus = 0
        if kickers:
            # 将kicker归一化到0-1之间
            max_kicker = max(kickers)
            kicker_bonus = (max_kicker - 2) / 12.0 * 0.1  # 最多增加0.1
        
        return min(1.0, base_score + kicker_bonus) 