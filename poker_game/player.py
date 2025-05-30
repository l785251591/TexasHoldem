from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum
from .card import Card

class PlayerAction(Enum):
    """玩家动作枚举"""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"

class Player(ABC):
    """玩家基础抽象类"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        self.player_id = player_id
        self.name = name
        self.chips = chips
        self.hole_cards: List[Card] = []
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
        self.total_bet_in_hand = 0
        self.position = 0
    
    def reset_for_new_hand(self):
        """为新手牌重置状态"""
        self.hole_cards = []
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
        self.total_bet_in_hand = 0
    
    def deal_hole_cards(self, cards: List[Card]):
        """发手牌"""
        self.hole_cards = cards
    
    def can_act(self) -> bool:
        """检查玩家是否可以行动"""
        return not self.is_folded and not self.is_all_in and self.chips > 0
    
    def bet(self, amount: int) -> int:
        """下注，返回实际下注金额"""
        if amount >= self.chips:
            # 全押
            actual_bet = self.chips
            self.chips = 0
            self.is_all_in = True
        else:
            actual_bet = amount
            self.chips -= amount
        
        self.current_bet += actual_bet  # 累加到当前下注
        self.total_bet_in_hand += actual_bet
        return actual_bet
    
    def fold(self):
        """弃牌"""
        self.is_folded = True
    
    def win_chips(self, amount: int):
        """赢得筹码"""
        import math
        
        # 安全检查：防止数值溢出
        MAX_SAFE_CHIPS = 10**12  # 1万亿筹码上限
        
        if not isinstance(amount, (int, float)) or math.isinf(amount) or math.isnan(amount):
            print(f"⚠️ 异常奖金数值: {amount}，忽略此次赢得")
            return
        
        if amount < 0:
            print(f"⚠️ 负数奖金: {amount}，忽略此次赢得")
            return
        
        # 限制单次赢得的最大金额
        amount = min(amount, MAX_SAFE_CHIPS)
        
        # 确保总筹码不超过安全上限
        if self.chips + amount > MAX_SAFE_CHIPS:
            amount = MAX_SAFE_CHIPS - self.chips
            if amount < 0:
                amount = 0
        
        self.chips += amount
        
        # 最终检查
        if self.chips > MAX_SAFE_CHIPS:
            self.chips = MAX_SAFE_CHIPS
    
    @abstractmethod
    def get_action(self, game_state: Dict[str, Any]) -> tuple[PlayerAction, int]:
        """获取玩家动作，返回(动作类型, 金额)"""
        pass
    
    def __str__(self):
        return f"{self.name} (筹码: {self.chips})"

class HumanPlayer(Player):
    """人类玩家类"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        super().__init__(player_id, name, chips)
    
    def get_action(self, game_state: Dict[str, Any]) -> tuple[PlayerAction, int]:
        """获取人类玩家的动作"""
        # 显示游戏状态
        self._display_game_state(game_state)
        
        # 获取可用动作
        available_actions = self._get_available_actions(game_state)
        
        # 显示选项
        print(f"\n{self.name}，轮到你行动了！")
        print(f"你的手牌: {' '.join(str(card) for card in self.hole_cards)}")
        print(f"当前筹码: {self.chips}")
        print(f"当前下注: {self.current_bet}")
        
        print("\n可用动作:")
        for i, (action, description) in enumerate(available_actions, 1):
            print(f"{i}. {description}")
        
        # 获取用户输入
        while True:
            try:
                choice = int(input("\n请选择动作 (输入数字): ")) - 1
                if 0 <= choice < len(available_actions):
                    action_type = available_actions[choice][0]
                    
                    if action_type == PlayerAction.RAISE:
                        # 如果是加注，需要输入金额
                        min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
                        max_raise = self.chips
                        
                        while True:
                            try:
                                amount = int(input(f"输入加注金额 ({min_raise}-{max_raise}): "))
                                if min_raise <= amount <= max_raise:
                                    return action_type, amount
                                else:
                                    print(f"金额必须在 {min_raise} 到 {max_raise} 之间")
                            except ValueError:
                                print("请输入有效的数字")
                    else:
                        # 其他动作不需要额外输入
                        amount = 0
                        if action_type == PlayerAction.CALL:
                            amount = game_state.get('call_amount', 0)
                        elif action_type == PlayerAction.ALL_IN:
                            amount = self.chips
                        
                        return action_type, amount
                else:
                    print("无效选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
    
    def _display_game_state(self, game_state: Dict[str, Any]):
        """显示游戏状态"""
        print("\n" + "="*50)
        print(f"当前阶段: {game_state.get('betting_round', '翻牌前')}")
        print(f"底池: {game_state.get('pot', 0)}")
        
        # 显示公共牌
        community_cards = game_state.get('community_cards', [])
        if community_cards:
            print(f"公共牌: {' '.join(str(card) for card in community_cards)}")
        
        # 显示其他玩家信息
        other_players = game_state.get('other_players', [])
        if other_players:
            print("\n其他玩家:")
            for player_info in other_players:
                status = ""
                if player_info.get('is_folded'):
                    status = "(已弃牌)"
                elif player_info.get('is_all_in'):
                    status = "(全押)"
                
                print(f"  {player_info.get('name')}: {player_info.get('chips')}筹码, "
                      f"当前下注: {player_info.get('current_bet', 0)} {status}")
        
        print("="*50)
    
    def _get_available_actions(self, game_state: Dict[str, Any]) -> List[tuple[PlayerAction, str]]:
        """获取可用动作列表"""
        actions = []
        
        call_amount = game_state.get('call_amount', 0)
        min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
        
        # 弃牌总是可用的
        actions.append((PlayerAction.FOLD, "弃牌"))
        
        # 检查是否可以过牌
        if call_amount == 0:
            actions.append((PlayerAction.CHECK, "过牌"))
        
        # 检查是否可以跟注
        if call_amount > 0 and call_amount <= self.chips:
            actions.append((PlayerAction.CALL, f"跟注 {call_amount}"))
        
        # 检查是否可以加注
        if self.chips >= min_raise:
            actions.append((PlayerAction.RAISE, f"加注 (最少{min_raise})"))
        
        # 全押
        if self.chips > 0:
            actions.append((PlayerAction.ALL_IN, f"全押 ({self.chips})"))
        
        return actions 