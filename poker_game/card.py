import random
from enum import Enum
from typing import List, Optional

class Suit(Enum):
    """花色枚举"""
    HEARTS = "♥"    # 红桃
    DIAMONDS = "♦"  # 方块
    CLUBS = "♣"     # 梅花
    SPADES = "♠"    # 黑桃

class Rank(Enum):
    """牌面大小枚举"""
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "T")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")
    
    def __init__(self, rank_value, symbol):
        self.rank_value = rank_value
        self.symbol = symbol

class Card:
    """扑克牌类"""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.symbol}{self.suit.value}"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self):
        return hash((self.suit, self.rank))
    
    @property
    def value(self):
        """返回牌的数值"""
        return self.rank.rank_value
    
    @property
    def rank_value(self):
        """返回牌的数值（与value相同，为了兼容性）"""
        return self.rank.rank_value
    
    @classmethod
    def from_string(cls, card_str: str):
        """从字符串创建Card对象，例如 'A♠' -> Card(Spades, Ace)"""
        if len(card_str) != 2:
            raise ValueError(f"无效的牌字符串格式: {card_str}")
        
        rank_symbol = card_str[0]
        suit_symbol = card_str[1]
        
        # 查找rank
        rank = None
        for r in Rank:
            if r.symbol == rank_symbol:
                rank = r
                break
        
        if rank is None:
            raise ValueError(f"无效的牌面符号: {rank_symbol}")
        
        # 查找suit
        suit = None
        for s in Suit:
            if s.value == suit_symbol:
                suit = s
                break
        
        if suit is None:
            raise ValueError(f"无效的花色符号: {suit_symbol}")
        
        return cls(suit, rank)

class Deck:
    """牌堆类"""
    
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self):
        """重置牌堆，包含所有52张牌"""
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))
        self.shuffle()
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def deal_card(self) -> Optional[Card]:
        """发一张牌"""
        if self.cards:
            return self.cards.pop()
        return None
    
    def deal_cards(self, num_cards: int) -> List[Card]:
        """发多张牌"""
        dealt_cards = []
        for _ in range(num_cards):
            card = self.deal_card()
            if card:
                dealt_cards.append(card)
        return dealt_cards
    
    def cards_remaining(self) -> int:
        """剩余牌数"""
        return len(self.cards) 