#!/usr/bin/env python3
"""
原版强化学习机器人 - 基于抽象基类的新实现
使用基础配置和保守的学习策略
"""

from .base_rl_bot import BaseRLBot, RLBotConfig
from .player import PlayerAction
from typing import Dict, Any, List, Tuple
import math

class RLBot(BaseRLBot):
    """原版强化学习机器人"""
    
    def get_default_config(self) -> RLBotConfig:
        """获取原版机器人的默认配置"""
        return RLBotConfig(
            # 学习参数 (保守设置)
            epsilon=0.3,
            epsilon_decay=0.9995,
            epsilon_min=0.05,
            learning_rate=0.01,
            gamma=0.9,
            
            # 策略参数 (保守风格)
            aggression_threshold=0.7,
            max_bet_ratio=0.4,
            min_hand_strength_call=0.3,
            min_hand_strength_raise=0.65,
            all_in_threshold=0.9,
            
            # 高级功能 (基础功能)
            use_double_q_learning=False,
            use_experience_replay=False,
            use_enhanced_state=False,
            use_dynamic_actions=False,
            use_conservative_mode=False,
            
            # 经验回放参数
            memory_size=5000,
            replay_batch_size=16,
            
            # 其他参数
            snapshot_interval=50,
            model_name="rl_bot"
        )
    
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """原版机器人使用基础动作集合"""
        return self._get_basic_actions(game_state)
    
    def _calculate_reward(self, hand_result: Dict[str, Any]) -> float:
        """原版机器人的简单奖励函数"""
        import math
        
        # 基础胜负奖励
        if hand_result.get('winner_id') == self.player_id:
            # 获胜
            winnings = hand_result.get('winnings', 0)
            roi_reward = winnings / max(self.total_bet_in_hand, 1)
            # 防止数值溢出
            if math.isinf(roi_reward) or math.isnan(roi_reward) or roi_reward > 10.0:
                reward = 10.0  # 设置最大奖励上限
            else:
                reward = min(10.0, roi_reward)  # 限制在10.0以内
        else:
            # 失败
            reward = -self.total_bet_in_hand / max(self.chips + self.total_bet_in_hand, 1)
        
        # 如果弃牌了，给予小的负奖励
        if self.is_folded:
            reward = -0.1
        
        return reward 