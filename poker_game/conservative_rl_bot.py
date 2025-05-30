#!/usr/bin/env python3
"""
保守版强化学习机器人
针对训练初期优化，减少筹码损失
"""

from .improved_rl_bot import ImprovedRLBot
from .player import PlayerAction
from typing import Dict, Any, Tuple, List
import random
import math

class ConservativeRLBot(ImprovedRLBot):
    """保守版强化学习机器人，适合训练初期使用"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000, 
                 model_path: str = "models/conservative_rl_bot_model.pkl"):
        super().__init__(player_id, name, chips, model_path)
        
        # 调整后的学习参数：更平衡的保守策略
        self.epsilon = 0.15         # 适中的探索率 (从0.1到0.15)
        self.epsilon_decay = 0.9998 # 适中的衰减 (从0.999到0.9998)
        self.epsilon_min = 0.03     # 保持适度探索 (从0.02到0.03)
        self.learning_rate = 0.008  # 稍微提高学习率 (从0.005到0.008)
        
        # 调整后的保守策略参数
        self.conservative_mode = True
        self.aggression_threshold = 0.6  # 降低激进阈值 (从0.8到0.6)
        self.max_bet_ratio = 0.3         # 增加最大下注比例 (从0.2到0.3)
        self.min_hand_strength_call = 0.2  # 降低跟注阈值 (从0.3到0.2)
        self.min_hand_strength_raise = 0.65  # 新增：加注阈值
        self.all_in_threshold = 0.85     # 降低全押阈值 (从0.95到0.85)
        
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """获取保守的动作空间"""
        if not self.conservative_mode:
            return super()._get_enhanced_actions(game_state)
        
        try:
            actions = []
            call_amount = game_state.get('call_amount', 0)
            pot_size = max(1, game_state.get('pot', 1))
            min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
            
            # 评估手牌强度
            hand_strength = self.estimate_hand_strength(game_state)
            
            # 弃牌 (总是可用)
            if call_amount > 0:
                actions.append((PlayerAction.FOLD, 0))
            
            # 过牌或跟注
            if call_amount == 0:
                actions.append((PlayerAction.CHECK, 0))
            elif call_amount <= self.chips:
                # 保守的跟注策略：只有在合理情况下才跟注
                pot_odds = pot_size / call_amount if call_amount > 0 else float('inf')
                if hand_strength > self.min_hand_strength_call or pot_odds > 3:  # 手牌不错或赔率好
                    actions.append((PlayerAction.CALL, call_amount))
            
            # 保守的加注策略
            if self.chips > call_amount and hand_strength > self.aggression_threshold:
                remaining_chips = self.chips - call_amount
                max_bet = min(int(self.chips * self.max_bet_ratio), remaining_chips)
                
                # 只在手牌很强时才加注
                if max_bet >= min_raise:
                    # 小加注
                    small_bet = max(min_raise, min(int(pot_size * 0.3), max_bet))
                    if small_bet <= remaining_chips:
                        actions.append((PlayerAction.RAISE, call_amount + small_bet))
                    
                    # 中等加注 (只有在手牌特别强时)
                    if hand_strength > self.min_hand_strength_raise:
                        medium_bet = max(min_raise, min(int(pot_size * 0.5), max_bet))
                        if medium_bet <= remaining_chips and medium_bet != small_bet:
                            actions.append((PlayerAction.RAISE, call_amount + medium_bet))
            
            # 移除全押选项 (太危险)
            # 只在绝对确定时才全押
            if hand_strength > self.all_in_threshold and self.chips <= pot_size:
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
            
        except Exception as e:
            print(f"⚠️  {self.name} 保守动作生成失败: {e}")
            # 安全回退
            call_amount = game_state.get('call_amount', 0)
            if call_amount == 0:
                return [(PlayerAction.CHECK, 0)]
            elif self.chips >= call_amount:
                return [(PlayerAction.CALL, call_amount)]
            else:
                return [(PlayerAction.FOLD, 0)]
    
    def _should_explore(self, state_key: str) -> bool:
        """更保守的探索策略"""
        # 基础ε-贪婪，但探索率更低
        if random.random() < self.epsilon:
            return True
        
        # 对新状态的探索更谨慎
        if self.state_visit_count[state_key] < 2:  # 降低从3到2
            return True
        
        return False
    
    def _calculate_enhanced_reward(self, hand_result: Dict[str, Any]) -> float:
        """更平衡的奖励函数"""
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
        
        # 生存奖励
        if not self.is_folded and self.chips > 0:
            reward += 0.15  # 增加生存奖励
        
        # 策略平衡奖励
        for i, step in enumerate(self.current_trajectory):
            action_type, amount = step['action']
            game_state = step['game_state']
            hand_strength = self.estimate_hand_strength(game_state)
            
            # 鼓励合理的弃牌
            if action_type == PlayerAction.FOLD:
                if hand_strength < 0.3:  # 弱牌弃牌
                    reward += 0.1
                elif hand_strength > 0.7:  # 强牌弃牌轻微惩罚
                    reward -= 0.05
            
            # 鼓励合理的跟注和加注
            elif action_type in [PlayerAction.CALL, PlayerAction.RAISE]:
                bet_ratio = amount / max(self.chips, 1)
                
                # 根据手牌强度评估下注合理性
                if hand_strength > 0.6:  # 强牌
                    if bet_ratio > 0.1:  # 鼓励强牌下注
                        reward += 0.08
                elif hand_strength > 0.4:  # 中等手牌
                    if 0.05 <= bet_ratio <= 0.3:  # 鼓励适度下注
                        reward += 0.05
                else:  # 弱牌
                    if bet_ratio < 0.15:  # 弱牌小注可以接受
                        reward += 0.02
                    else:  # 弱牌大注惩罚
                        reward -= 0.08
            
            # 评估全押决策
            elif action_type == PlayerAction.ALL_IN:
                if hand_strength > 0.8:  # 强牌全押奖励
                    reward += 0.1
                elif hand_strength < 0.4:  # 弱牌全押严重惩罚
                    reward -= 0.3
                else:  # 中等牌全押轻微惩罚
                    reward -= 0.1
        
        # 限制总奖励范围，防止过度奖励或惩罚
        return max(-3.0, min(10.0, reward))
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息（保守版）"""
        stats = super().get_learning_stats()
        stats.update({
            'conservative_mode': self.conservative_mode,
            'aggression_threshold': self.aggression_threshold,
            'max_bet_ratio': self.max_bet_ratio,
            'min_hand_strength_call': self.min_hand_strength_call,
            'min_hand_strength_raise': self.min_hand_strength_raise,
            'all_in_threshold': self.all_in_threshold,
            'bot_type': 'Conservative'
        })
        return stats
    
    def enable_normal_mode(self):
        """切换到正常模式（训练后期使用）"""
        self.conservative_mode = False
        self.epsilon = min(0.2, self.epsilon * 2)  # 稍微提高探索率
        self.aggression_threshold = 0.6  # 降低激进阈值
        self.max_bet_ratio = 0.5  # 增加最大下注比例
        print(f"🚀 {self.name} 切换到正常模式")
    
    def auto_adjust_conservatism(self):
        """根据表现自动调整保守程度"""
        if self.game_count > 100:
            win_rate = self.win_count / self.game_count
            
            # 如果表现很好，逐渐减少保守程度
            if win_rate > 0.3:
                self.aggression_threshold = max(0.6, self.aggression_threshold - 0.01)
                self.max_bet_ratio = min(0.5, self.max_bet_ratio + 0.01)
            # 如果表现很差，增加保守程度
            elif win_rate < 0.1:
                self.aggression_threshold = min(0.9, self.aggression_threshold + 0.01)
                self.max_bet_ratio = max(0.1, self.max_bet_ratio - 0.01)
    
    def learn_from_hand_result(self, hand_result: Dict[str, Any]):
        """学习时自动调整保守程度"""
        super().learn_from_hand_result(hand_result)
        
        # 每100手自动调整一次
        if self.game_count % 100 == 0:
            self.auto_adjust_conservatism()
    
    def _record_training_progress(self):
        """记录训练进度到追踪器（保守版专用）"""
        try:
            from .training_tracker import TrainingTracker
            
            tracker = TrainingTracker()
            
            # 获取当前统计
            current_stats = self.get_learning_stats()
            
            # 添加额外信息
            additional_info = {
                'snapshot_interval': self.snapshot_interval,
                'model_path': self.model_path,
                'current_chips': self.chips,
                'conservative_mode': self.conservative_mode,
                'aggression_threshold': self.aggression_threshold,
                'max_bet_ratio': self.max_bet_ratio,
                'min_hand_strength_call': self.min_hand_strength_call,
                'min_hand_strength_raise': self.min_hand_strength_raise,
                'all_in_threshold': self.all_in_threshold
            }
            
            # 记录快照 - 确保使用正确的机器人类型
            tracker.record_snapshot('conservative_rl_bot', current_stats, additional_info)
            
        except Exception as e:
            # 静默处理错误，不影响训练
            pass 