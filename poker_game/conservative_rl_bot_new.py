#!/usr/bin/env python3
"""
保守版强化学习机器人 - 基于抽象基类的新实现
使用稳健的学习策略和保守的游戏风格
"""

from .base_rl_bot import BaseRLBot, RLBotConfig
from .player import PlayerAction
from typing import Dict, Any, List, Tuple
import math

class ConservativeRLBot(BaseRLBot):
    """保守版强化学习机器人"""
    
    def get_default_config(self) -> RLBotConfig:
        """获取保守版机器人的默认配置"""
        return RLBotConfig(
            # 学习参数 (更平衡的保守策略)
            epsilon=0.15,
            epsilon_decay=0.9998,
            epsilon_min=0.03,
            learning_rate=0.008,
            gamma=0.92,
            
            # 策略参数 (调整后的保守参数)
            aggression_threshold=0.6,
            max_bet_ratio=0.3,
            min_hand_strength_call=0.2,
            min_hand_strength_raise=0.65,
            all_in_threshold=0.85,
            
            # 高级功能 (选择性启用)
            use_double_q_learning=True,
            use_experience_replay=True,
            use_enhanced_state=True,
            use_dynamic_actions=True,
            use_conservative_mode=True,
            
            # 经验回放参数 (适中配置)
            memory_size=8000,
            replay_batch_size=24,
            
            # 其他参数
            snapshot_interval=50,
            model_name="conservative_rl_bot"
        )
    
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """保守版机器人的稳健动作集合"""
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
        
        # 过牌或跟注 (保守策略优先)
        if call_amount == 0:
            actions.append((PlayerAction.CHECK, 0))
        elif call_amount <= self.chips:
            # 保守跟注条件：手牌强度或赔率足够好
            if (hand_strength >= self.min_hand_strength_call or 
                pot_odds >= 3.0 or 
                call_amount <= self.chips * 0.05):  # 小额跟注
                actions.append((PlayerAction.CALL, call_amount))
        
        # 保守加注策略
        if (self.chips > call_amount and 
            hand_strength >= self.min_hand_strength_raise):
            
            remaining_chips = self.chips - call_amount
            
            if remaining_chips >= min_raise:
                pot_size_effective = max(pot_size, min_raise * 2)
                max_bet_amount = int(self.chips * self.max_bet_ratio)
                
                # 小加注 (0.2-0.4倍底池，保守)
                if hand_strength >= 0.6:
                    small_raise_amount = int(pot_size_effective * 0.3)
                    small_raise_total = call_amount + min(small_raise_amount, remaining_chips, max_bet_amount)
                    if small_raise_total <= self.chips:
                        actions.append((PlayerAction.RAISE, small_raise_total))
                
                # 中等加注 (0.5-0.7倍底池，需要更强牌)
                if (hand_strength >= 0.75 and 
                    remaining_chips >= min_raise * 2):
                    medium_raise_amount = int(pot_size_effective * 0.6)
                    medium_raise_total = call_amount + min(medium_raise_amount, remaining_chips, max_bet_amount)
                    if medium_raise_total <= self.chips and medium_raise_total > call_amount + small_raise_amount:
                        actions.append((PlayerAction.RAISE, medium_raise_total))
                
                # 大加注 (只在非常强的牌时)
                if (hand_strength >= 0.85 and 
                    remaining_chips >= min_raise * 3):
                    big_raise_amount = int(pot_size_effective * 0.8)
                    big_raise_total = call_amount + min(big_raise_amount, remaining_chips, max_bet_amount)
                    if big_raise_total <= self.chips and big_raise_total > medium_raise_total:
                        actions.append((PlayerAction.RAISE, big_raise_total))
        
        # 全押 (非常保守的条件)
        if (self.chips > call_amount and 
            hand_strength >= self.all_in_threshold):
            
            # 额外的保守检查
            opponents_count = len([p for p in game_state.get('other_players', []) 
                                  if not p.get('is_folded', False)])
            
            # 只在少对手或极强牌时全押
            if (opponents_count <= 2 or 
                hand_strength >= 0.9 or 
                (hand_strength >= 0.8 and pot_odds >= 4.0)):
                actions.append((PlayerAction.ALL_IN, self.chips))
        
        # 确保至少有一个动作
        if not actions:
            if call_amount == 0:
                actions.append((PlayerAction.CHECK, 0))
            elif call_amount <= self.chips * 0.1:  # 如果跟注金额很小，可以跟注
                actions.append((PlayerAction.CALL, call_amount))
            else:
                actions.append((PlayerAction.FOLD, 0))
        
        return actions
    
    def _calculate_reward(self, hand_result: Dict[str, Any]) -> float:
        """保守版机器人的平衡奖励函数"""
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
        
        # 生存奖励 (保守策略重视生存)
        if not self.is_folded and self.chips > 0:
            reward += 0.1  # 比其他机器人更高的生存奖励
        
        # 保守决策质量奖励
        for i, step in enumerate(self.current_trajectory):
            game_state = step['game_state']
            action, amount = step['action']
            
            hand_strength = self.estimate_hand_strength(game_state)
            pot_odds = self.calculate_pot_odds(game_state)
            
            # 鼓励正确的保守决策
            if action == PlayerAction.FOLD and hand_strength < 0.25:
                reward += 0.08  # 弱牌时正确弃牌 (比其他机器人更高奖励)
            elif action == PlayerAction.CHECK and hand_strength < 0.4:
                reward += 0.05  # 边际牌时过牌
            elif action == PlayerAction.CALL and 0.2 <= hand_strength <= 0.6 and pot_odds >= 2.5:
                reward += 0.06  # 根据赔率正确跟注
            elif action == PlayerAction.RAISE and hand_strength >= 0.7:
                reward += 0.12  # 强牌时加注 (鼓励价值下注)
            
            # 惩罚过度激进
            if action == PlayerAction.RAISE and hand_strength < 0.4:
                reward -= 0.1  # 弱牌时加注 (保守策略不鼓励)
            elif action == PlayerAction.ALL_IN and hand_strength < 0.8:
                reward -= 0.15  # 非强牌时全押
        
        # 筹码管理奖励
        if hasattr(self, 'initial_chips'):
            chips_ratio = self.chips / max(self.initial_chips, 1)
            if chips_ratio > 1.1:  # 筹码增长
                reward += 0.05
            elif chips_ratio < 0.5:  # 筹码损失过多
                reward -= 0.1
        
        # 一致性奖励 (保守风格的一致性)
        conservative_actions = [PlayerAction.FOLD, PlayerAction.CHECK, PlayerAction.CALL]
        conservative_count = sum(1 for step in self.current_trajectory 
                               if step['action'][0] in conservative_actions)
        
        if len(self.current_trajectory) > 0:
            conservative_ratio = conservative_count / len(self.current_trajectory)
            if conservative_ratio >= 0.7:  # 70%以上保守动作
                reward += 0.05
        
        return reward 