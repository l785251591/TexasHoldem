#!/usr/bin/env python3
"""
强化学习机器人工厂
提供便捷的方法来创建各种配置的强化学习机器人
"""

from .base_rl_bot import BaseRLBot, RLBotConfig
from .rl_bot_configs import get_config_by_name, create_custom_config, PREDEFINED_CONFIGS
from .player import PlayerAction
from typing import Dict, Any, List, Tuple, Optional
import random

class GenericRLBot(BaseRLBot):
    """通用强化学习机器人 - 可配置各种策略"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000, 
                 config: RLBotConfig = None, model_path: str = None):
        super().__init__(player_id, name, chips, config, model_path)
    
    def get_default_config(self) -> RLBotConfig:
        """默认使用平衡配置"""
        return RLBotConfig(
            epsilon=0.25,
            epsilon_decay=0.9996,
            epsilon_min=0.05,
            learning_rate=0.012,
            gamma=0.93,
            
            aggression_threshold=0.6,
            max_bet_ratio=0.5,
            min_hand_strength_call=0.25,
            min_hand_strength_raise=0.6,
            all_in_threshold=0.85,
            
            use_double_q_learning=True,
            use_experience_replay=True,
            use_enhanced_state=True,
            use_dynamic_actions=True,
            
            memory_size=8000,
            replay_batch_size=32,
            model_name="generic_rl_bot"
        )
    
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """根据配置动态生成动作集合"""
        actions = []
        call_amount = game_state.get('call_amount', 0)
        min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
        pot_size = game_state.get('pot', 0)
        
        # 获取手牌强度和位置信息
        hand_strength = self.estimate_hand_strength(game_state)
        pot_odds = self.calculate_pot_odds(game_state)
        
        # 弃牌 (如果需要跟注)
        if call_amount > 0:
            actions.append((PlayerAction.FOLD, 0))
        
        # 过牌或跟注
        if call_amount == 0:
            actions.append((PlayerAction.CHECK, 0))
        elif call_amount <= self.chips:
            # 根据配置决定跟注条件
            should_call = (
                hand_strength >= self.min_hand_strength_call or
                pot_odds >= (3.0 if self.conservative_mode else 2.0) or
                call_amount <= self.chips * (0.05 if self.conservative_mode else 0.1)
            )
            if should_call:
                actions.append((PlayerAction.CALL, call_amount))
        
        # 加注策略
        if (self.chips > call_amount and 
            hand_strength >= self.min_hand_strength_raise):
            
            remaining_chips = self.chips - call_amount
            
            if remaining_chips >= min_raise:
                pot_size_effective = max(pot_size, min_raise * 2)
                max_bet_amount = int(self.chips * self.max_bet_ratio)
                
                # 动态调整加注大小
                if self.conservative_mode:
                    # 保守模式：较小的加注
                    if hand_strength >= 0.6:
                        raise_amount = int(pot_size_effective * 0.4)
                        raise_total = call_amount + min(raise_amount, remaining_chips, max_bet_amount)
                        if raise_total <= self.chips:
                            actions.append((PlayerAction.RAISE, raise_total))
                    
                    if hand_strength >= 0.8 and remaining_chips >= min_raise * 2:
                        raise_amount = int(pot_size_effective * 0.7)
                        raise_total = call_amount + min(raise_amount, remaining_chips, max_bet_amount)
                        if raise_total <= self.chips:
                            actions.append((PlayerAction.RAISE, raise_total))
                
                else:
                    # 正常/激进模式：多样化加注
                    if hand_strength >= self.min_hand_strength_raise:
                        # 小加注
                        small_raise = int(pot_size_effective * 0.5)
                        small_total = call_amount + min(small_raise, remaining_chips, max_bet_amount)
                        if small_total <= self.chips:
                            actions.append((PlayerAction.RAISE, small_total))
                    
                    if hand_strength >= 0.7 and remaining_chips >= min_raise * 2:
                        # 大加注
                        big_raise = int(pot_size_effective * 1.0)
                        big_total = call_amount + min(big_raise, remaining_chips, max_bet_amount)
                        if big_total <= self.chips and big_total > small_total:
                            actions.append((PlayerAction.RAISE, big_total))
                    
                    # 激进模式额外的超大加注
                    if (self.aggression_threshold < 0.5 and 
                        hand_strength >= 0.8 and 
                        remaining_chips >= min_raise * 3):
                        huge_raise = int(pot_size_effective * 1.8)
                        huge_total = call_amount + min(huge_raise, remaining_chips, max_bet_amount)
                        if huge_total <= self.chips and huge_total > big_total:
                            actions.append((PlayerAction.RAISE, huge_total))
        
        # 全押策略
        if self.chips > call_amount:
            should_all_in = False
            
            if self.conservative_mode:
                # 保守全押条件
                opponents_count = len([p for p in game_state.get('other_players', []) 
                                      if not p.get('is_folded', False)])
                should_all_in = (
                    hand_strength >= self.all_in_threshold and
                    (opponents_count <= 2 or hand_strength >= 0.9)
                )
            else:
                # 正常全押条件
                should_all_in = (
                    hand_strength >= self.all_in_threshold or
                    (hand_strength >= 0.6 and pot_odds >= 3.0)
                )
            
            if should_all_in:
                actions.append((PlayerAction.ALL_IN, self.chips))
        
        # 确保至少有一个动作
        if not actions:
            if call_amount == 0:
                actions.append((PlayerAction.CHECK, 0))
            elif call_amount <= self.chips * 0.1:
                actions.append((PlayerAction.CALL, call_amount))
            else:
                actions.append((PlayerAction.FOLD, 0))
        
        return actions
    
    def _calculate_reward(self, hand_result: Dict[str, Any]) -> float:
        """根据配置动态计算奖励"""
        import math
        
        reward = 0.0
        
        # 基础胜负奖励
        if hand_result.get('winner_id') == self.player_id:
            winnings = hand_result.get('winnings', 0)
            roi_reward = winnings / max(self.total_bet_in_hand, 1)
            
            # 防止数值溢出
            if math.isinf(roi_reward) or math.isnan(roi_reward) or roi_reward > 8.0:
                reward += 8.0
            else:
                reward += min(8.0, roi_reward)
        else:
            # 失败惩罚
            loss_ratio = self.total_bet_in_hand / max(self.chips + self.total_bet_in_hand, 1)
            penalty_factor = 1.5 if self.conservative_mode else 1.0
            reward -= min(penalty_factor, loss_ratio * penalty_factor)
        
        # 生存奖励
        if not self.is_folded and self.chips > 0:
            survival_bonus = 0.15 if self.conservative_mode else 0.08
            reward += survival_bonus
        
        # 决策质量奖励
        for step in self.current_trajectory:
            game_state = step['game_state']
            action, amount = step['action']
            
            hand_strength = self.estimate_hand_strength(game_state)
            pot_odds = self.calculate_pot_odds(game_state)
            
            # 根据配置调整奖励权重
            fold_bonus = 0.1 if self.conservative_mode else 0.05
            raise_bonus = 0.08 if not self.conservative_mode else 0.12
            
            # 正确决策奖励
            if action == PlayerAction.FOLD and hand_strength < 0.25:
                reward += fold_bonus
            elif action == PlayerAction.RAISE and hand_strength >= 0.7:
                reward += raise_bonus
            elif action == PlayerAction.CALL and 0.2 <= hand_strength <= 0.6 and pot_odds >= 2.5:
                reward += 0.06
            
            # 错误决策惩罚
            if self.conservative_mode:
                if action == PlayerAction.RAISE and hand_strength < 0.4:
                    reward -= 0.12
                elif action == PlayerAction.ALL_IN and hand_strength < 0.85:
                    reward -= 0.2
            else:
                if action == PlayerAction.FOLD and hand_strength > 0.8:
                    reward -= 0.1
        
        return reward

class RLBotFactory:
    """强化学习机器人工厂"""
    
    @staticmethod
    def create_bot(config_name: str, player_id: str, name: str, 
                   chips: int = 1000, model_path: Optional[str] = None) -> GenericRLBot:
        """根据配置名称创建机器人"""
        config = get_config_by_name(config_name)
        return GenericRLBot(player_id, name, chips, config, model_path)
    
    @staticmethod
    def create_custom_bot(player_id: str, name: str, chips: int = 1000, 
                         model_path: Optional[str] = None, **config_kwargs) -> GenericRLBot:
        """创建自定义配置的机器人"""
        config = create_custom_config(**config_kwargs)
        return GenericRLBot(player_id, name, chips, config, model_path)
    
    @staticmethod
    def create_team(team_configs: List[Dict], base_chips: int = 1000) -> List[GenericRLBot]:
        """创建一队机器人
        
        参数:
            team_configs: 配置列表，每个配置包含 {'config_name': str, 'name': str, 'player_id': str}
            base_chips: 基础筹码数量
        
        返回:
            机器人列表
        """
        bots = []
        for i, config_info in enumerate(team_configs):
            config_name = config_info.get('config_name', 'improved')
            name = config_info.get('name', f"机器人{i+1}")
            player_id = config_info.get('player_id', f"bot_{i+1}")
            chips = config_info.get('chips', base_chips)
            
            bot = RLBotFactory.create_bot(config_name, player_id, name, chips)
            bots.append(bot)
        
        return bots
    
    @staticmethod
    def create_diverse_team(count: int, base_chips: int = 1000) -> List[GenericRLBot]:
        """创建多样化的机器人队伍"""
        configs = list(PREDEFINED_CONFIGS.keys())
        bots = []
        
        for i in range(count):
            config_name = configs[i % len(configs)]
            player_id = f"diverse_bot_{i+1}"
            name = f"{config_name.title()}机器人{i+1}"
            
            bot = RLBotFactory.create_bot(config_name, player_id, name, base_chips)
            bots.append(bot)
        
        return bots
    
    @staticmethod
    def create_tournament_lineup() -> List[GenericRLBot]:
        """创建锦标赛阵容 - 各种风格的机器人"""
        lineup_configs = [
            {'config_name': 'conservative', 'name': '🛡️稳健派', 'player_id': 'conservative_1'},
            {'config_name': 'aggressive', 'name': '⚡激进派', 'player_id': 'aggressive_1'},
            {'config_name': 'bluff', 'name': '🎭诈唬大师', 'player_id': 'bluff_1'},
            {'config_name': 'tight', 'name': '🔒紧凶型', 'player_id': 'tight_1'},
            {'config_name': 'adaptive', 'name': '🧠适应者', 'player_id': 'adaptive_1'},
        ]
        
        return RLBotFactory.create_team(lineup_configs)
    
    @staticmethod
    def get_available_configs() -> List[str]:
        """获取可用的配置名称列表"""
        return list(PREDEFINED_CONFIGS.keys())
    
    @staticmethod
    def print_config_info(config_name: str):
        """打印配置信息"""
        try:
            config = get_config_by_name(config_name)
            from .rl_bot_configs import print_config_summary
            print_config_summary(config)
        except ValueError as e:
            print(f"❌ {e}")

# ===== 便捷函数 =====

def quick_create_bot(style: str, name: str, player_id: str = None, chips: int = 1000) -> GenericRLBot:
    """快速创建机器人的便捷函数
    
    参数:
        style: 机器人风格 ('conservative', 'aggressive', 'bluff', 等)
        name: 机器人名称
        player_id: 玩家ID (可选，默认基于名称生成)
        chips: 初始筹码
    """
    if player_id is None:
        player_id = name.lower().replace(' ', '_')
    
    return RLBotFactory.create_bot(style, player_id, name, chips)

def create_balanced_trio() -> List[GenericRLBot]:
    """创建平衡的三人组"""
    return [
        quick_create_bot('conservative', '🛡️保守派', 'conservative_1'),
        quick_create_bot('improved', '🚀平衡派', 'improved_1'),
        quick_create_bot('aggressive', '⚡激进派', 'aggressive_1'),
    ]

def create_experimental_group() -> List[GenericRLBot]:
    """创建实验组"""
    return [
        quick_create_bot('experimental', '🧪实验者', 'experimental_1'),
        quick_create_bot('adaptive', '🧠适应者', 'adaptive_1'),
        quick_create_bot('bluff', '🎭诈唬师', 'bluff_1'),
    ]

# ===== 使用示例 =====

if __name__ == "__main__":
    print("🏭 强化学习机器人工厂")
    print("=" * 50)
    
    # 展示可用配置
    print("📋 可用配置:")
    for config_name in RLBotFactory.get_available_configs():
        print(f"   • {config_name}")
    
    # 创建示例机器人
    print("\n🤖 创建示例机器人:")
    
    # 单个机器人
    conservative_bot = RLBotFactory.create_bot('conservative', 'c1', '保守派机器人')
    print(f"   ✅ {conservative_bot.name} - {conservative_bot.config.model_name}")
    
    # 自定义机器人
    custom_bot = RLBotFactory.create_custom_bot(
        'custom1', '自定义机器人',
        epsilon=0.2,
        aggression_threshold=0.4,
        model_name="my_custom_bot"
    )
    print(f"   ✅ {custom_bot.name} - {custom_bot.config.model_name}")
    
    # 团队
    print("\n👥 创建机器人团队:")
    tournament_bots = RLBotFactory.create_tournament_lineup()
    for bot in tournament_bots:
        print(f"   🏆 {bot.name} - {bot.config.model_name}")
    
    print("\n✨ 工厂系统就绪！") 