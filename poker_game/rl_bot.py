import numpy as np
import pickle
import os
import random
from typing import List, Dict, Any, Tuple
from .player import Player, PlayerAction
from .hand_evaluator import HandEvaluator
from .database import GameDatabase
from .card import Card
import math

class RLBot(Player):
    """强化学习机器人，具有学习和记忆能力"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000, 
                 model_path: str = "models/rl_bot_model.pkl"):
        super().__init__(player_id, name, chips)
        self.model_path = model_path
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # 探索率
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Q表：状态 -> 动作 -> 价值
        self.q_table = {}
        
        # 记忆系统
        self.memory = []
        self.memory_size = 1000
        
        # 训练进度追踪
        self.last_snapshot_game_count = 0
        self.snapshot_interval = 100  # 每100手记录一次进度
        self.total_reward = 0
        self.game_count = 0
        self.win_count = 0
        
        # 加载已保存的模型
        self.load_model()
        
        # 数据库连接用于学习
        self.db = GameDatabase()
        
        # 当前回合的状态-动作对
        self.current_state = None
        self.current_action = None
        
    def load_model(self):
        """加载已保存的模型"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.q_table = data.get('q_table', {})
                    self.epsilon = data.get('epsilon', self.epsilon)
                print(f"已加载模型: {self.model_path}")
            except Exception as e:
                print(f"加载模型失败: {e}")
                self.q_table = {}
    
    def save_model(self):
        """保存模型到磁盘"""
        try:
            data = {
                'q_table': self.q_table,
                'epsilon': self.epsilon
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"模型已保存: {self.model_path}")
        except Exception as e:
            print(f"保存模型失败: {e}")
    
    def get_state_key(self, game_state: Dict[str, Any]) -> str:
        """将游戏状态转换为状态键"""
        # 简化的状态表示
        hand_strength = self.estimate_hand_strength(game_state)
        pot_odds = self.calculate_pot_odds(game_state)
        position = self.position
        opponents_count = len([p for p in game_state.get('other_players', []) 
                              if not p.get('is_folded', False)])
        betting_round = game_state.get('betting_round', 'preflop')
        
        # 将连续值离散化
        hand_strength_bucket = int(hand_strength * 10)
        # 处理无穷大的pot_odds
        if pot_odds == float('inf'):
            pot_odds_bucket = 10  # 设置一个最大值
        else:
            pot_odds_bucket = min(int(pot_odds), 10)
        
        return f"{hand_strength_bucket}_{pot_odds_bucket}_{position}_{opponents_count}_{betting_round}"
    
    def get_action(self, game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """获取动作，结合探索和利用"""
        state_key = self.get_state_key(game_state)
        self.current_state = state_key
        
        # 获取可用动作
        available_actions = self._get_available_actions(game_state)
        
        # ε-贪婪策略
        if random.random() < self.epsilon:
            # 探索：随机选择动作
            action_type, amount = random.choice(available_actions)
        else:
            # 利用：选择Q值最高的动作
            action_type, amount = self._get_best_action(state_key, available_actions, game_state)
        
        self.current_action = (action_type, amount)
        return action_type, amount
    
    def _get_available_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """获取可用动作列表"""
        actions = []
        call_amount = game_state.get('call_amount', 0)
        min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
        
        # 弃牌
        actions.append((PlayerAction.FOLD, 0))
        
        # 过牌或跟注
        if call_amount == 0:
            actions.append((PlayerAction.CHECK, 0))
        elif call_amount <= self.chips:
            actions.append((PlayerAction.CALL, call_amount))
        
        # 加注
        if self.chips >= min_raise:
            # 小加注
            small_raise = min(min_raise, self.chips)
            actions.append((PlayerAction.RAISE, small_raise))
            
            # 中等加注
            if self.chips >= min_raise * 2:
                medium_raise = min(min_raise * 2, self.chips)
                actions.append((PlayerAction.RAISE, medium_raise))
            
            # 大加注
            if self.chips >= min_raise * 3:
                big_raise = min(min_raise * 3, self.chips)
                actions.append((PlayerAction.RAISE, big_raise))
        
        # 全押
        if self.chips > 0:
            actions.append((PlayerAction.ALL_IN, self.chips))
        
        return actions
    
    def _get_best_action(self, state_key: str, available_actions: List[Tuple[PlayerAction, int]], 
                        game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """选择Q值最高的动作"""
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        
        best_action = None
        best_q_value = float('-inf')
        
        for action_type, amount in available_actions:
            action_key = f"{action_type.value}_{self._discretize_amount(amount, game_state)}"
            
            if action_key not in self.q_table[state_key]:
                # 如果没有该动作的Q值，初始化为0
                self.q_table[state_key][action_key] = 0
            
            q_value = self.q_table[state_key][action_key]
            
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = (action_type, amount)
        
        return best_action if best_action else available_actions[0]
    
    def _discretize_amount(self, amount: int, game_state: Dict[str, Any]) -> str:
        """将下注金额离散化"""
        if amount == 0:
            return "none"
        elif amount == self.chips:
            return "all_in"
        else:
            pot_size = game_state.get('pot', 1)
            ratio = amount / pot_size
            if ratio < 0.5:
                return "small"
            elif ratio < 1.0:
                return "medium"
            else:
                return "large"
    
    def update_q_value(self, reward: float, next_state_key: str = None):
        """更新Q值"""
        if self.current_state is None or self.current_action is None:
            return
        
        action_type, amount = self.current_action
        # 这里需要game_state来离散化amount，但我们可以简化处理
        action_key = f"{action_type.value}_{amount}"
        
        if self.current_state not in self.q_table:
            self.q_table[self.current_state] = {}
        
        if action_key not in self.q_table[self.current_state]:
            self.q_table[self.current_state][action_key] = 0
        
        # Q-learning更新公式
        current_q = self.q_table[self.current_state][action_key]
        
        if next_state_key and next_state_key in self.q_table:
            max_next_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
        else:
            max_next_q = 0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[self.current_state][action_key] = new_q
        
        # 保存到记忆中
        self.memory.append({
            'state': self.current_state,
            'action': action_key,
            'reward': reward,
            'next_state': next_state_key
        })
        
        # 限制记忆大小
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)
    
    def learn_from_hand_result(self, hand_result: Dict[str, Any]):
        """从手牌结果中学习"""
        # 计算奖励
        if hand_result.get('winner_id') == self.player_id:
            # 获胜
            winnings = hand_result.get('winnings', 0)
            roi_reward = winnings / max(self.total_bet_in_hand, 1)
            # 防止数值溢出
            if math.isinf(roi_reward) or math.isnan(roi_reward) or roi_reward > 10.0:
                reward = 10.0  # 设置最大奖励上限
            else:
                reward = min(10.0, roi_reward)  # 限制在10.0以内
            self.win_count += 1
        else:
            # 失败
            reward = -self.total_bet_in_hand / max(self.chips + self.total_bet_in_hand, 1)
        
        # 如果弃牌了，给予小的负奖励
        if self.is_folded:
            reward = -0.1
        
        # 更新统计
        self.total_reward += reward
        self.game_count += 1
        
        self.update_q_value(reward)
        
        # 记录训练进度 (每N手记录一次)
        if (self.game_count - self.last_snapshot_game_count) >= self.snapshot_interval:
            self._record_training_progress()
            self.last_snapshot_game_count = self.game_count
        
        # 保存学习数据到数据库
        if hasattr(self, 'db'):
            game_state = hand_result.get('game_state', {})
            pot_odds = self.calculate_pot_odds(game_state)
            # 处理无穷大的pot_odds，数据库不能存储无穷大
            if pot_odds == float('inf'):
                pot_odds = 999.0  # 用一个大数值代替无穷大
            
            self.db.save_bot_learning_data(
                bot_id=self.player_id,
                game_state=game_state,
                action_taken=f"{self.current_action[0].value}_{self.current_action[1]}" if self.current_action else "none",
                reward=reward,
                hand_strength=self.estimate_hand_strength(game_state),
                pot_odds=pot_odds,
                position=self.position,
                opponents_count=len([p for p in game_state.get('other_players', []) 
                                   if not p.get('is_folded', False)])
            )
    
    def _record_training_progress(self):
        """记录训练进度到追踪器"""
        try:
            from .training_tracker import TrainingTracker
            
            tracker = TrainingTracker()
            
            # 获取当前统计
            current_stats = self.get_learning_stats()
            current_stats.update({
                'game_count': self.game_count,
                'win_count': self.win_count,
                'total_reward': self.total_reward,
                'win_rate': self.win_count / max(1, self.game_count),
                'avg_reward': self.total_reward / max(1, self.game_count)
            })
            
            # 添加额外信息
            additional_info = {
                'snapshot_interval': self.snapshot_interval,
                'model_path': self.model_path,
                'current_chips': self.chips
            }
            
            # 记录快照
            tracker.record_snapshot('rl_bot', current_stats, additional_info)
            
        except Exception as e:
            # 静默处理错误，不影响训练
            pass
    
    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def estimate_hand_strength(self, game_state: Dict[str, Any]) -> float:
        """评估手牌强度"""
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
            return self._evaluate_preflop_strength()
    
    def _evaluate_preflop_strength(self) -> float:
        """评估翻牌前手牌强度"""
        if len(self.hole_cards) != 2:
            return 0.0
        
        card1, card2 = self.hole_cards
        
        # 口袋对子
        if card1.rank_value == card2.rank_value:
            if card1.rank_value >= 10:
                return 0.9
            elif card1.rank_value >= 7:
                return 0.7
            else:
                return 0.5
        
        # 同花连张
        if card1.suit == card2.suit:
            if abs(card1.rank_value - card2.rank_value) == 1:
                return 0.8
        
        # 高牌组合
        high_card = max(card1.rank_value, card2.rank_value)
        low_card = min(card1.rank_value, card2.rank_value)
        
        if high_card == 14:  # A
            if low_card >= 11:
                return 0.85
            elif low_card >= 9:
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
    
    def _evaluate_partial_hand_strength(self, all_cards) -> float:
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
    
    def calculate_pot_odds(self, game_state: Dict[str, Any]) -> float:
        """计算底池赔率"""
        call_amount = game_state.get('call_amount', 0)
        pot_size = game_state.get('pot', 0)
        
        if call_amount == 0:
            return float('inf')
        
        return pot_size / call_amount if call_amount > 0 else float('inf')
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        return {
            'q_table_size': len(self.q_table),
            'total_states': sum(len(actions) for actions in self.q_table.values()),
            'epsilon': self.epsilon,
            'memory_size': len(self.memory)
        } 