#!/usr/bin/env python3
"""
强化学习机器人抽象基类
提供可配置的参数系统，支持不同策略的实现
"""

from abc import ABC, abstractmethod
from .player import Player, PlayerAction
from typing import Dict, Any, Tuple, List
import pickle
import os
import random
from collections import defaultdict, deque
import math

class RLBotConfig:
    """强化学习机器人配置类"""
    
    def __init__(self, 
                 # 学习参数
                 epsilon: float = 0.3,
                 epsilon_decay: float = 0.9995,
                 epsilon_min: float = 0.05,
                 learning_rate: float = 0.01,
                 gamma: float = 0.9,
                 
                 # 策略参数
                 aggression_threshold: float = 0.7,
                 max_bet_ratio: float = 0.5,
                 min_hand_strength_call: float = 0.25,
                 min_hand_strength_raise: float = 0.6,
                 all_in_threshold: float = 0.9,
                 
                 # 高级功能开关
                 use_double_q_learning: bool = True,
                 use_experience_replay: bool = True,
                 use_enhanced_state: bool = True,
                 use_dynamic_actions: bool = True,
                 use_conservative_mode: bool = False,
                 
                 # 经验回放参数
                 memory_size: int = 10000,
                 replay_batch_size: int = 32,
                 
                 # 其他参数
                 snapshot_interval: int = 50,
                 model_name: str = "base_rl_bot"
                 ):
        
        # 学习参数
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.learning_rate = learning_rate
        self.gamma = gamma
        
        # 策略参数
        self.aggression_threshold = aggression_threshold
        self.max_bet_ratio = max_bet_ratio
        self.min_hand_strength_call = min_hand_strength_call
        self.min_hand_strength_raise = min_hand_strength_raise
        self.all_in_threshold = all_in_threshold
        
        # 高级功能
        self.use_double_q_learning = use_double_q_learning
        self.use_experience_replay = use_experience_replay
        self.use_enhanced_state = use_enhanced_state
        self.use_dynamic_actions = use_dynamic_actions
        self.use_conservative_mode = use_conservative_mode
        
        # 经验回放参数
        self.memory_size = memory_size
        self.replay_batch_size = replay_batch_size
        
        # 其他参数
        self.snapshot_interval = snapshot_interval
        self.model_name = model_name

class BaseRLBot(Player, ABC):
    """强化学习机器人抽象基类"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000, 
                 config: RLBotConfig = None, model_path: str = None):
        super().__init__(player_id, name, chips)
        
        # 使用配置
        self.config = config or self.get_default_config()
        
        # 设置模型路径
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = f"models/{self.config.model_name}_model.pkl"
        
        # 应用配置参数
        self._apply_config()
        
        # 初始化学习组件
        self._initialize_learning_components()
        
        # 加载模型
        self.load_model()
    
    @abstractmethod
    def get_default_config(self) -> RLBotConfig:
        """获取默认配置，子类必须实现"""
        pass
    
    def _apply_config(self):
        """应用配置参数"""
        config = self.config
        
        # 学习参数
        self.epsilon = config.epsilon
        self.epsilon_decay = config.epsilon_decay
        self.epsilon_min = config.epsilon_min
        self.learning_rate = config.learning_rate
        self.gamma = config.gamma
        
        # 策略参数
        self.aggression_threshold = config.aggression_threshold
        self.max_bet_ratio = config.max_bet_ratio
        self.min_hand_strength_call = config.min_hand_strength_call
        self.min_hand_strength_raise = config.min_hand_strength_raise
        self.all_in_threshold = config.all_in_threshold
        
        # 功能开关
        self.use_double_q_learning = config.use_double_q_learning
        self.use_experience_replay = config.use_experience_replay
        self.use_enhanced_state = config.use_enhanced_state
        self.use_dynamic_actions = config.use_dynamic_actions
        self.conservative_mode = config.use_conservative_mode
        
        # 经验回放参数
        self.memory_size = config.memory_size
        self.replay_batch_size = config.replay_batch_size
        
        # 其他参数
        self.snapshot_interval = config.snapshot_interval
    
    def _initialize_learning_components(self):
        """初始化学习组件"""
        # Q表 (根据配置决定是否使用双Q学习)
        if self.use_double_q_learning:
            self.q_table_1 = defaultdict(lambda: defaultdict(float))
            self.q_table_2 = defaultdict(lambda: defaultdict(float))
        else:
            self.q_table = defaultdict(lambda: defaultdict(float))
        
        # 统计信息
        self.total_reward = 0.0
        self.game_count = 0
        self.win_count = 0
        
        # 状态访问计数
        self.state_visit_count = defaultdict(int)
        self.action_count = defaultdict(lambda: defaultdict(int))
        
        # 经验回放缓冲区
        if self.use_experience_replay:
            self.experience_memory = deque(maxlen=self.memory_size)
        
        # 训练轨迹
        self.current_trajectory = []
        self.last_state_key = None
        self.last_action_key = None
        
        # 当前手牌信息
        self.total_bet_in_hand = 0
        self.is_folded = False
        
        print(f"📝 创建新的{self.config.model_name}: {self.model_path}")
    
    def get_state_key(self, game_state: Dict[str, Any]) -> str:
        """获取状态键值"""
        if self.use_enhanced_state:
            return self._get_enhanced_state_key(game_state)
        else:
            return self._get_basic_state_key(game_state)
    
    def _get_basic_state_key(self, game_state: Dict[str, Any]) -> str:
        """获取基础状态表示"""
        try:
            hand_strength = self.estimate_hand_strength(game_state)
            pot_odds = self.calculate_pot_odds(game_state)
            
            # 离散化
            hand_str_bucket = min(4, int(hand_strength * 5))
            pot_odds_bucket = min(3, int(pot_odds * 2)) if pot_odds < float('inf') else 3
            
            opponents_count = len([p for p in game_state.get('other_players', []) 
                                  if not p.get('is_folded', False)])
            opponents_count = max(1, min(opponents_count, 5))
            
            return f"h{hand_str_bucket}_p{pot_odds_bucket}_o{opponents_count}"
        except:
            return "default_state"
    
    def _get_enhanced_state_key(self, game_state: Dict[str, Any]) -> str:
        """获取增强状态表示"""
        try:
            # 基础信息
            hand_strength = self.estimate_hand_strength(game_state)
            pot_odds = self.calculate_pot_odds(game_state)
            
            # 对手信息
            opponents_count = len([p for p in game_state.get('other_players', []) 
                                  if not p.get('is_folded', False)])
            opponents_count = max(1, min(opponents_count, 8))
            
            # 下注信息
            call_amount = game_state.get('call_amount', 0)
            pot_size = game_state.get('pot', 0)
            
            # 位置信息
            position_type = self._get_position_type(opponents_count)
            
            # 游戏阶段
            community_cards = game_state.get('community_cards', [])
            stage = len(community_cards)  # 0=preflop, 3=flop, 4=turn, 5=river
            
            # 离散化各个维度
            hand_bucket = min(4, int(hand_strength * 5))
            pot_odds_bucket = min(3, int(pot_odds * 2)) if pot_odds < float('inf') else 3
            
            # 下注压力
            bet_pressure = call_amount / max(self.chips, 1)
            pressure_bucket = min(3, int(bet_pressure * 4))
            
            # 底池相对大小
            pot_ratio = pot_size / max(self.chips + pot_size, 1)
            pot_bucket = min(3, int(pot_ratio * 4))
            
            return (f"h{hand_bucket}_p{pot_odds_bucket}_o{opponents_count}_"
                   f"pos{position_type}_s{stage}_pr{pressure_bucket}_pb{pot_bucket}")
        except:
            return "enhanced_default"
    
    def _get_position_type(self, opponents_count: int) -> str:
        """获取位置类型"""
        if opponents_count <= 2:
            return "hu"  # heads-up
        elif opponents_count <= 4:
            return "sh"  # short-handed
        else:
            return "fu"  # full table
    
    def get_action(self, game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """获取动作"""
        try:
            state_key = self.get_state_key(game_state)
            self.state_visit_count[state_key] += 1
            
            # 获取可用动作
            if self.use_dynamic_actions:
                available_actions = self._get_enhanced_actions(game_state)
            else:
                available_actions = self._get_basic_actions(game_state)
            
            # 选择动作
            if self._should_explore(state_key):
                # 探索：随机选择
                action, amount = random.choice(available_actions)
            else:
                # 利用：选择最佳动作
                action, amount = self._get_best_action(state_key, available_actions, game_state)
            
            # 记录动作
            action_key = self._get_action_key(action, amount, game_state)
            self.action_count[state_key][action_key] += 1
            
            # 保存状态和动作
            self.last_state_key = state_key
            self.last_action_key = action_key
            
            # 记录轨迹
            self.current_trajectory.append({
                'state': state_key,
                'action': (action, amount),
                'game_state': game_state.copy()
            })
            
            return action, amount
            
        except Exception as e:
            print(f"⚠️  {self.name}: 内部计算异常 (已自动处理)")
            # 安全回退
            call_amount = game_state.get('call_amount', 0)
            if call_amount == 0:
                return PlayerAction.CHECK, 0
            elif self.chips >= call_amount:
                return PlayerAction.CALL, call_amount
            else:
                return PlayerAction.FOLD, 0
    
    def _should_explore(self, state_key: str) -> bool:
        """是否应该探索"""
        return random.random() < self.epsilon
    
    def _get_best_action(self, state_key: str, available_actions: List[Tuple[PlayerAction, int]], 
                        game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """获取最佳动作"""
        if self.use_double_q_learning:
            return self._double_q_action_selection(state_key, available_actions, game_state)
        else:
            return self._single_q_action_selection(state_key, available_actions, game_state)
    
    def _single_q_action_selection(self, state_key: str, available_actions: List[Tuple[PlayerAction, int]], 
                                  game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """单Q表动作选择"""
        best_q_value = float('-inf')
        best_action = available_actions[0]
        
        for action, amount in available_actions:
            action_key = self._get_action_key(action, amount, game_state)
            q_value = self.q_table[state_key][action_key]
            
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = (action, amount)
        
        return best_action
    
    def _double_q_action_selection(self, state_key: str, available_actions: List[Tuple[PlayerAction, int]], 
                                  game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """双Q表动作选择"""
        best_q_value = float('-inf')
        best_action = available_actions[0]
        
        for action, amount in available_actions:
            action_key = self._get_action_key(action, amount, game_state)
            # 取两个Q表的平均值
            q_value = (self.q_table_1[state_key][action_key] + 
                      self.q_table_2[state_key][action_key]) / 2
            
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = (action, amount)
        
        return best_action
    
    def _get_basic_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """获取基础动作集合"""
        actions = []
        call_amount = game_state.get('call_amount', 0)
        min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
        
        # 弃牌 (如果需要跟注)
        if call_amount > 0:
            actions.append((PlayerAction.FOLD, 0))
        
        # 过牌或跟注
        if call_amount == 0:
            actions.append((PlayerAction.CHECK, 0))
        elif call_amount <= self.chips:
            actions.append((PlayerAction.CALL, call_amount))
        
        # 加注
        if self.chips > call_amount:
            remaining_chips = self.chips - call_amount
            if remaining_chips >= min_raise:
                # 小加注
                small_raise = min(min_raise, remaining_chips)
                actions.append((PlayerAction.RAISE, call_amount + small_raise))
                
                # 大加注
                if remaining_chips >= min_raise * 3:
                    big_raise = min(min_raise * 3, remaining_chips)
                    actions.append((PlayerAction.RAISE, call_amount + big_raise))
        
        # 全押
        if self.chips > call_amount:
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
    
    @abstractmethod
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """获取增强动作集合，子类需要实现"""
        pass
    
    def _get_action_key(self, action_type: PlayerAction, amount: int, game_state: Dict[str, Any]) -> str:
        """获取动作键值"""
        if action_type in [PlayerAction.FOLD, PlayerAction.CHECK]:
            return action_type.value
        elif action_type == PlayerAction.CALL:
            return f"call_{self._discretize_amount(amount, game_state)}"
        elif action_type == PlayerAction.RAISE:
            return f"raise_{self._discretize_amount(amount, game_state)}"
        elif action_type == PlayerAction.ALL_IN:
            return "all_in"
        else:
            return str(action_type.value)
    
    def _discretize_amount(self, amount: int, game_state: Dict[str, Any]) -> str:
        """离散化金额"""
        pot_size = max(1, game_state.get('pot', 1))
        ratio = amount / pot_size
        
        if ratio <= 0.5:
            return "small"
        elif ratio <= 1.5:
            return "medium"
        elif ratio <= 3.0:
            return "large"
        else:
            return "huge"
    
    def learn_from_hand_result(self, hand_result: Dict[str, Any]):
        """从手牌结果学习"""
        if not self.current_trajectory:
            return
        
        # 计算奖励
        reward = self._calculate_reward(hand_result)
        self.total_reward += reward
        self.game_count += 1
        
        if hand_result.get('winner_id') == self.player_id:
            self.win_count += 1
        
        # 更新Q值
        self._update_q_values(reward)
        
        # 经验回放
        if self.use_experience_replay:
            self._add_experience_and_learn(reward)
        
        # 衰减探索率
        self.decay_epsilon()
        
        # 重置轨迹
        self.current_trajectory = []
        self.last_state_key = None
        self.last_action_key = None
        
        # 定期记录训练进度
        if self.game_count % self.snapshot_interval == 0:
            self._record_training_progress()
    
    @abstractmethod
    def _calculate_reward(self, hand_result: Dict[str, Any]) -> float:
        """计算奖励，子类需要实现"""
        pass
    
    def _update_q_values(self, final_reward: float):
        """更新Q值"""
        if self.use_double_q_learning:
            self._update_double_q_values(final_reward)
        else:
            self._update_single_q_values(final_reward)
    
    def _update_single_q_values(self, final_reward: float):
        """更新单Q表"""
        reward = final_reward
        for i in reversed(range(len(self.current_trajectory))):
            step = self.current_trajectory[i]
            state = step['state']
            action_key = self._get_action_key(step['action'][0], step['action'][1], step['game_state'])
            
            # 获取下一状态的最大Q值
            next_max_q = 0
            if i < len(self.current_trajectory) - 1:
                next_step = self.current_trajectory[i + 1]
                next_state = next_step['state']
                next_max_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
            
            # 更新Q值
            old_q = self.q_table[state][action_key]
            target_q = reward + self.gamma * next_max_q
            self.q_table[state][action_key] = old_q + self.learning_rate * (target_q - old_q)
            
            # 折扣奖励
            reward *= self.gamma
    
    def _update_double_q_values(self, final_reward: float):
        """更新双Q表"""
        reward = final_reward
        for i in reversed(range(len(self.current_trajectory))):
            step = self.current_trajectory[i]
            state = step['state']
            action_key = self._get_action_key(step['action'][0], step['action'][1], step['game_state'])
            
            # 随机选择更新哪个Q表
            if random.random() < 0.5:
                primary_q, secondary_q = self.q_table_1, self.q_table_2
            else:
                primary_q, secondary_q = self.q_table_2, self.q_table_1
            
            # 获取下一状态
            next_state = None
            if i < len(self.current_trajectory) - 1:
                next_step = self.current_trajectory[i + 1]
                next_state = next_step['state']
            
            # 更新Q值
            self._update_q_table(primary_q, secondary_q, state, action_key, reward, next_state)
            
            # 折扣奖励
            reward *= self.gamma
    
    def _update_q_table(self, primary_q: dict, secondary_q: dict, state: str, action: str, 
                       reward: float, next_state: str):
        """更新Q表"""
        if next_state:
            # 使用primary_q选择动作，secondary_q评估价值
            best_next_action = max(primary_q[next_state], key=primary_q[next_state].get) if primary_q[next_state] else None
            next_q_value = secondary_q[next_state][best_next_action] if best_next_action else 0
        else:
            next_q_value = 0
        
        # TD更新
        old_q = primary_q[state][action]
        target_q = reward + self.gamma * next_q_value
        primary_q[state][action] = old_q + self.learning_rate * (target_q - old_q)
    
    def _add_experience_and_learn(self, final_reward: float):
        """添加经验并进行经验回放学习"""
        # 添加经验到缓冲区
        for step in self.current_trajectory:
            experience = {
                'state': step['state'],
                'action': step['action'],
                'reward': final_reward,
                'game_state': step['game_state']
            }
            self.experience_memory.append(experience)
        
        # 经验回放
        if len(self.experience_memory) >= self.replay_batch_size:
            self._replay_experience()
    
    def _replay_experience(self):
        """经验回放"""
        batch_size = min(self.replay_batch_size, len(self.experience_memory))
        batch = random.sample(list(self.experience_memory), batch_size)
        
        for experience in batch:
            state = experience['state']
            action = experience['action']
            reward = experience['reward']
            game_state = experience['game_state']
            
            action_key = self._get_action_key(action[0], action[1], game_state)
            
            if self.use_double_q_learning:
                # 随机选择Q表
                if random.random() < 0.5:
                    primary_q, secondary_q = self.q_table_1, self.q_table_2
                else:
                    primary_q, secondary_q = self.q_table_2, self.q_table_1
                
                old_q = primary_q[state][action_key]
                target_q = reward
                primary_q[state][action_key] = old_q + self.learning_rate * (target_q - old_q)
            else:
                old_q = self.q_table[state][action_key]
                target_q = reward
                self.q_table[state][action_key] = old_q + self.learning_rate * (target_q - old_q)
    
    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def estimate_hand_strength(self, game_state: Dict[str, Any]) -> float:
        """估算手牌强度 (0-1)"""
        try:
            if not self.hole_cards or len(self.hole_cards) != 2:
                return 0.3
            
            community_cards = game_state.get('community_cards', [])
            
            if not community_cards:
                return self._evaluate_preflop_strength()
            else:
                all_cards = self.hole_cards + community_cards
                return self._evaluate_partial_hand_strength(all_cards)
        except:
            return 0.3
    
    def _evaluate_preflop_strength(self) -> float:
        """评估翻牌前手牌强度"""
        if len(self.hole_cards) != 2:
            return 0.3
        
        card1, card2 = self.hole_cards
        rank1, suit1 = card1.rank, card1.suit
        rank2, suit2 = card2.rank, card2.suit
        
        # 定义牌面值
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        val1 = rank_values.get(rank1, 7)
        val2 = rank_values.get(rank2, 7)
        
        # 基础分数
        high_card = max(val1, val2)
        low_card = min(val1, val2)
        
        # 对子
        if val1 == val2:
            if val1 >= 10:  # TT+
                return 0.9
            elif val1 >= 7:  # 77-99
                return 0.75
            else:  # 22-66
                return 0.6
        
        # 同花
        suited = (suit1 == suit2)
        
        # 连牌
        connected = abs(val1 - val2) == 1 or (val1 == 14 and val2 == 2)
        
        # AK, AQ类似的高牌
        if high_card == 14:  # A
            if low_card >= 10:  # AK, AQ, AJ, AT
                return 0.85 if suited else 0.75
            elif low_card >= 7:  # A9-A7
                return 0.65 if suited else 0.5
            else:  # A6-A2
                return 0.55 if suited else 0.4
        
        # 高牌组合
        if high_card >= 12:  # K+
            if low_card >= 10:  # KQ, KJ, QJ
                return 0.7 if suited else 0.6
            elif low_card >= 8:  # K9-K8, Q9-Q8
                return 0.55 if suited else 0.45
        
        # 同花连牌奖励
        if suited and connected:
            if high_card >= 8:
                return 0.65
            else:
                return 0.55
        
        # 连牌
        if connected and high_card >= 8:
            return 0.5
        
        # 同花
        if suited:
            return 0.45
        
        # 默认
        return 0.3
    
    def _evaluate_partial_hand_strength(self, all_cards) -> float:
        """评估部分公共牌情况下的手牌强度"""
        # 简化实现
        return min(0.9, 0.3 + len(all_cards) * 0.1)
    
    def calculate_pot_odds(self, game_state: Dict[str, Any]) -> float:
        """计算底池赔率"""
        call_amount = game_state.get('call_amount', 0)
        pot_size = game_state.get('pot', 0)
        
        if call_amount <= 0 or pot_size <= 0:
            return float('inf')
        
        return pot_size / call_amount
    
    def save_model(self):
        """保存模型"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            data = {
                'total_reward': self.total_reward,
                'game_count': self.game_count,
                'win_count': self.win_count,
                'epsilon': self.epsilon,
                'state_visit_count': dict(self.state_visit_count),
                'action_count': {k: dict(v) for k, v in self.action_count.items()},
                'config': self.config.__dict__
            }
            
            # 保存Q表
            if self.use_double_q_learning:
                data['q_table_1'] = dict(self.q_table_1)
                data['q_table_2'] = dict(self.q_table_2)
            else:
                data['q_table'] = dict(self.q_table)
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 {self.config.model_name}模型已保存: {self.model_path}")
        except Exception as e:
            print(f"❌ 保存模型失败: {e}")
    
    def load_model(self):
        """加载模型"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                
                self.total_reward = data.get('total_reward', 0.0)
                self.game_count = data.get('game_count', 0)
                self.win_count = data.get('win_count', 0)
                self.epsilon = data.get('epsilon', self.config.epsilon)
                self.state_visit_count = defaultdict(int, data.get('state_visit_count', {}))
                
                action_count_data = data.get('action_count', {})
                self.action_count = defaultdict(lambda: defaultdict(int))
                for state, actions in action_count_data.items():
                    for action, count in actions.items():
                        self.action_count[state][action] = count
                
                # 加载Q表
                if self.use_double_q_learning:
                    q1_data = data.get('q_table_1', {})
                    q2_data = data.get('q_table_2', {})
                    self.q_table_1 = defaultdict(lambda: defaultdict(float))
                    self.q_table_2 = defaultdict(lambda: defaultdict(float))
                    
                    for state, actions in q1_data.items():
                        for action, value in actions.items():
                            self.q_table_1[state][action] = value
                    
                    for state, actions in q2_data.items():
                        for action, value in actions.items():
                            self.q_table_2[state][action] = value
                else:
                    q_data = data.get('q_table', {})
                    self.q_table = defaultdict(lambda: defaultdict(float))
                    for state, actions in q_data.items():
                        for action, value in actions.items():
                            self.q_table[state][action] = value
                
                print(f"✅ 已加载{self.config.model_name}: {self.model_path}")
                print(f"   游戏次数: {self.game_count}, 胜率: {(self.win_count/max(1,self.game_count))*100:.1f}%")
            else:
                self._initialize_empty_model()
        except Exception as e:
            print(f"⚠️  加载模型失败 ({e})，创建新模型")
            self._initialize_empty_model()
    
    def _initialize_empty_model(self):
        """初始化空模型"""
        print(f"📝 创建新的{self.config.model_name}: {self.model_path}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        if self.use_double_q_learning:
            q_table_size = len(self.q_table_1) + len(self.q_table_2)
        else:
            q_table_size = len(getattr(self, 'q_table', {}))
        
        stats = {
            'q_table_size': q_table_size,
            'epsilon': self.epsilon,
            'total_reward': self.total_reward,
            'game_count': self.game_count,
            'win_count': self.win_count,
            'win_rate': (self.win_count / max(1, self.game_count)) * 100,
            'avg_reward': self.total_reward / max(1, self.game_count),
            'memory_size': len(getattr(self, 'experience_memory', [])),
            'total_states': len(self.state_visit_count),
            'model_name': self.config.model_name
        }
        
        # 添加配置信息
        stats.update(self.config.__dict__)
        
        return stats
    
    def _record_training_progress(self):
        """记录训练进度"""
        try:
            from .training_tracker import TrainingTracker
            
            tracker = TrainingTracker()
            current_stats = self.get_learning_stats()
            
            additional_info = {
                'snapshot_interval': self.snapshot_interval,
                'model_path': self.model_path,
                'current_chips': self.chips
            }
            
            tracker.record_snapshot(self.config.model_name, current_stats, additional_info)
        except Exception as e:
            # 静默处理错误，不影响训练
            pass 