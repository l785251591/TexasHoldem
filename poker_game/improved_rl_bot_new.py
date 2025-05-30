#!/usr/bin/env python3
"""
改进版强化学习机器人 - 基于抽象基类的新实现
使用先进的学习算法和激进的策略配置
"""

from .base_rl_bot import BaseRLBot, RLBotConfig
from .player import PlayerAction
from typing import Dict, Any, List, Tuple
import math

class ImprovedRLBot(BaseRLBot):
    """改进版强化学习机器人"""
    
    def get_default_config(self) -> RLBotConfig:
        """获取改进版机器人的默认配置"""
        return RLBotConfig(
            # 学习参数 (激进设置)
            epsilon=0.35,
            epsilon_decay=0.9997,
            epsilon_min=0.08,
            learning_rate=0.015,
            gamma=0.95,
            
            # 策略参数 (激进风格)
            aggression_threshold=0.55,
            max_bet_ratio=0.6,
            min_hand_strength_call=0.2,
            min_hand_strength_raise=0.5,
            all_in_threshold=0.8,
            
            # 高级功能 (全部启用)
            use_double_q_learning=True,
            use_experience_replay=True,
            use_enhanced_state=True,
            use_dynamic_actions=True,
            use_conservative_mode=False,
            
            # 经验回放参数 (增强版)
            memory_size=10000,
            replay_batch_size=32,
            
            # 其他参数
            snapshot_interval=50,
            model_name="improved_rl_bot"
        )
    
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """改进版机器人的动态动作集合"""
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
            actions.append((PlayerAction.CALL, call_amount))
        
        # 动态加注策略
        if self.chips > call_amount:
            remaining_chips = self.chips - call_amount
            
            if remaining_chips >= min_raise:
                # 多样化的加注大小
                pot_size_effective = max(pot_size, min_raise * 2)
                
                # 小加注 (0.3-0.5倍底池)
                small_raise_amount = int(pot_size_effective * 0.4)
                small_raise_total = call_amount + min(small_raise_amount, remaining_chips)
                if small_raise_total <= self.chips:
                    actions.append((PlayerAction.RAISE, small_raise_total))
                
                # 中等加注 (0.6-0.8倍底池)
                if remaining_chips >= min_raise * 2:
                    medium_raise_amount = int(pot_size_effective * 0.7)
                    medium_raise_total = call_amount + min(medium_raise_amount, remaining_chips)
                    if medium_raise_total <= self.chips and medium_raise_total > small_raise_total:
                        actions.append((PlayerAction.RAISE, medium_raise_total))
                
                # 大加注 (1.0-1.5倍底池)
                if remaining_chips >= min_raise * 3 and hand_strength > 0.4:
                    big_raise_amount = int(pot_size_effective * 1.2)
                    big_raise_total = call_amount + min(big_raise_amount, remaining_chips)
                    if big_raise_total <= self.chips and big_raise_total > medium_raise_total:
                        actions.append((PlayerAction.RAISE, big_raise_total))
                
                # 超大加注 (2.0+倍底池) - 只在强牌时
                if remaining_chips >= min_raise * 5 and hand_strength > 0.7:
                    huge_raise_amount = int(pot_size_effective * 2.5)
                    huge_raise_total = call_amount + min(huge_raise_amount, remaining_chips)
                    if huge_raise_total <= self.chips and huge_raise_total > big_raise_total:
                        actions.append((PlayerAction.RAISE, huge_raise_total))
        
        # 全押 (根据手牌强度决定)
        if self.chips > call_amount:
            # 降低全押阈值，更激进
            if hand_strength > self.all_in_threshold or (hand_strength > 0.6 and pot_odds > 2.0):
                actions.append((PlayerAction.ALL_IN, self.chips))
        
        # 确保至少有一个动作
        if not actions:
            if call_amount == 0:
                actions.append((PlayerAction.CHECK, 0))
            elif self.chips >= call_amount:
                actions.append((PlayerAction.CALL, call_amount))
            else:
                actions.append((PlayerAction.FOLD, 0))
        
        return actions
    
    def _calculate_reward(self, hand_result: Dict[str, Any]) -> float:
        """改进版机器人的增强奖励函数"""
        import math
        
        reward = 0.0
        
        # 基础胜负奖励
        if hand_result.get('winner_id') == self.player_id:
            winnings = hand_result.get('winnings', 0)
            # 适度鼓励胜利，但限制过度奖励
            roi_reward = winnings / max(self.total_bet_in_hand, 1)
            # 防止数值溢出并限制奖励范围
            if math.isinf(roi_reward) or math.isnan(roi_reward) or roi_reward > 5.0:
                reward += 5.0  # 设置合理上限
            else:
                reward += min(5.0, roi_reward)
        else:
            # 对失败的惩罚更温和，鼓励适度冒险
            loss_ratio = self.total_bet_in_hand / max(self.chips + self.total_bet_in_hand, 1)
            reward -= min(1.5, loss_ratio * 1.0)  # 适度惩罚
        
        # 决策质量奖励
        for i, step in enumerate(self.current_trajectory):
            game_state = step['game_state']
            action, amount = step['action']
            
            # 手牌强度相关奖励
            hand_strength = self.estimate_hand_strength(game_state)
            pot_odds = self.calculate_pot_odds(game_state)
            
            # 鼓励正确的激进决策
            if action == PlayerAction.RAISE and hand_strength > 0.6:
                reward += 0.1  # 强牌时加注
            elif action == PlayerAction.FOLD and hand_strength < 0.2 and pot_odds < 1.5:
                reward += 0.05  # 弱牌时正确弃牌
            elif action == PlayerAction.CALL and 0.3 < hand_strength < 0.6 and pot_odds > 2.0:
                reward += 0.05  # 边际牌时根据赔率跟注
            
            # 位置意识奖励
            opponents_count = len([p for p in game_state.get('other_players', []) 
                                  if not p.get('is_folded', False)])
            if opponents_count <= 2 and action == PlayerAction.RAISE:
                reward += 0.02  # 鼓励在少人时激进
        
        # 生存奖励 (避免过早全押)
        if not self.is_folded and self.chips > 0:
            reward += 0.05
        
        # 适应性学习奖励
        if hasattr(self, 'recent_performance'):
            if len(self.recent_performance) >= 5:
                recent_avg = sum(self.recent_performance[-5:]) / 5
                if recent_avg > 0:
                    reward += 0.1  # 连续表现好时的奖励
        
        return reward 