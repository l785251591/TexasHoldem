import numpy as np
import pickle
import os
import random
import math
from typing import List, Dict, Any, Tuple
from collections import defaultdict, deque
from .player import Player, PlayerAction
from .hand_evaluator import HandEvaluator
from .database import GameDatabase
from .card import Card

class ImprovedRLBot(Player):
    """改进的强化学习机器人，具有更好的学习和决策能力"""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000, 
                 model_path: str = "models/improved_rl_bot_model.pkl"):
        super().__init__(player_id, name, chips)
        self.model_path = model_path
        
        # 改进的学习参数
        self.learning_rate = 0.01  # 降低学习率，避免过度学习
        self.discount_factor = 0.99  # 提高折扣因子，更重视长期奖励
        self.epsilon = 0.3  # 提高初始探索率
        self.epsilon_decay = 0.9995  # 更慢的衰减
        self.epsilon_min = 0.05  # 保持一定的探索
        
        # 双Q网络（Double Q-Learning）
        self.q_table_1 = defaultdict(lambda: defaultdict(float))
        self.q_table_2 = defaultdict(lambda: defaultdict(float))
        
        # 经验回放
        self.experience_buffer = deque(maxlen=10000)
        self.batch_size = 32
        
        # 状态-动作价值记录
        self.state_visit_count = defaultdict(int)
        self.action_count = defaultdict(lambda: defaultdict(int))
        
        # 性能追踪
        self.total_reward = 0
        self.game_count = 0
        self.win_count = 0
        
        # 训练进度追踪
        self.last_snapshot_game_count = 0
        self.snapshot_interval = 100  # 每100手记录一次进度
        
        # 加载已保存的模型
        self.load_model()
        
        # 数据库连接
        self.db = GameDatabase()
        
        # 当前轨迹
        self.current_trajectory = []
        self.hand_history = []
        
    def load_model(self):
        """加载已保存的模型"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.q_table_1 = data.get('q_table_1', defaultdict(lambda: defaultdict(float)))
                    self.q_table_2 = data.get('q_table_2', defaultdict(lambda: defaultdict(float)))
                    self.epsilon = data.get('epsilon', self.epsilon)
                    self.total_reward = data.get('total_reward', 0)
                    self.game_count = data.get('game_count', 0)
                    self.win_count = data.get('win_count', 0)
                    self.state_visit_count = data.get('state_visit_count', defaultdict(int))
                    self.action_count = data.get('action_count', defaultdict(lambda: defaultdict(int)))
                    print(f"✅ 已加载改进模型: {self.model_path}")
                    print(f"   游戏次数: {self.game_count}, 胜率: {self.win_count/max(1,self.game_count):.1%}")
            except Exception as e:
                print(f"❌ 加载模型失败: {e}")
                self._initialize_empty_model()
        else:
            print(f"📝 创建新的改进模型: {self.model_path}")
            self._initialize_empty_model()
    
    def _initialize_empty_model(self):
        """初始化空模型"""
        self.q_table_1 = defaultdict(lambda: defaultdict(float))
        self.q_table_2 = defaultdict(lambda: defaultdict(float))
        self.state_visit_count = defaultdict(int)
        self.action_count = defaultdict(lambda: defaultdict(int))
    
    def save_model(self):
        """保存模型到磁盘"""
        try:
            data = {
                'q_table_1': dict(self.q_table_1),
                'q_table_2': dict(self.q_table_2),
                'epsilon': self.epsilon,
                'total_reward': self.total_reward,
                'game_count': self.game_count,
                'win_count': self.win_count,
                'state_visit_count': dict(self.state_visit_count),
                'action_count': {k: dict(v) for k, v in self.action_count.items()}
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 改进模型已保存: {self.model_path}")
        except Exception as e:
            print(f"❌ 保存模型失败: {e}")
    
    def get_enhanced_state_key(self, game_state: Dict[str, Any]) -> str:
        """获取增强的状态表示"""
        try:
            # 基础信息
            hand_strength = self.estimate_hand_strength(game_state)
            pot_odds = self.calculate_pot_odds(game_state)
            
            # 对手信息
            opponents_count = len([p for p in game_state.get('other_players', []) 
                                  if not p.get('is_folded', False)])
            opponents_count = max(1, min(opponents_count, 8))  # 限制范围 1-8
            
            # 下注信息
            call_amount = max(0, game_state.get('call_amount', 0))
            pot_size = max(1, game_state.get('pot', 1))  # 确保至少为1
            big_blind = max(1, game_state.get('big_blind', 20))  # 确保至少为1
            
            # 游戏阶段
            betting_round = str(game_state.get('betting_round', 'preflop'))
            
            # 筹码信息
            stack_ratio = max(0, self.chips) / max(big_blind * 20, 1)  # 相对于起始筹码的比例
            
            # 位置信息（简化）
            position_type = self._get_position_type(opponents_count)
            
            # 下注压力
            bet_pressure = call_amount / pot_size
            
            # 离散化各个维度，确保值在合理范围内
            hand_bucket = max(0, min(int(hand_strength * 10), 9))
            
            if pot_odds == float('inf'):
                pot_odds_bucket = 10
            elif pot_odds < 0:
                pot_odds_bucket = 0
            else:
                pot_odds_bucket = min(int(pot_odds), 10)
            
            stack_bucket = max(0, min(int(stack_ratio), 10))
            pressure_bucket = max(0, min(int(bet_pressure * 5), 5))
            
            return f"{hand_bucket}_{pot_odds_bucket}_{opponents_count}_{betting_round}_{position_type}_{stack_bucket}_{pressure_bucket}"
            
        except Exception as e:
            print(f"⚠️  {self.name} 生成状态键出现错误: {e}, 使用默认状态")
            # 返回默认状态键
            return "0_0_2_preflop_early_5_0"
    
    def _get_position_type(self, opponents_count: int) -> str:
        """获取位置类型"""
        try:
            opponents_count = max(1, opponents_count)  # 确保至少为1
            position = getattr(self, 'position', 0)  # 安全获取位置
            
            if opponents_count <= 2:
                return "heads_up"
            elif position <= opponents_count // 3:
                return "early"
            elif position <= 2 * opponents_count // 3:
                return "middle"
            else:
                return "late"
        except (AttributeError, TypeError, ValueError):
            # 出现错误时返回默认位置
            return "early"
    
    def get_action(self, game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """获取动作，使用改进的策略"""
        try:
            state_key = self.get_enhanced_state_key(game_state)
            available_actions = self._get_enhanced_actions(game_state)
            
            # 确保至少有一个可用动作
            if not available_actions:
                # 如果没有可用动作，返回弃牌
                print(f"⚠️  {self.name}: 没有可用动作，默认弃牌")
                return PlayerAction.FOLD, 0
            
            # 记录状态访问
            self.state_visit_count[state_key] += 1
            
            # UCB（Upper Confidence Bound）探索策略
            if self._should_explore(state_key):
                action_type, amount = self._ucb_action_selection(state_key, available_actions, game_state)
            else:
                # 双Q网络选择
                action_type, amount = self._double_q_action_selection(state_key, available_actions, game_state)
            
            # 验证动作有效性
            if (action_type, amount) not in available_actions:
                print(f"⚠️  {self.name}: 选择的动作无效，使用默认动作")
                action_type, amount = available_actions[0]
            
            # 记录轨迹
            try:
                # 安全地复制游戏状态
                if isinstance(game_state, dict):
                    game_state_copy = game_state.copy()
                else:
                    game_state_copy = dict(game_state) if game_state else {}
                
                self.current_trajectory.append({
                    'state': state_key,
                    'action': (action_type, amount),
                    'game_state': game_state_copy
                })
            except Exception as trajectory_error:
                # 如果轨迹记录失败，至少记录基本信息
                print(f"⚠️  {self.name}: 轨迹记录失败: {trajectory_error}")
                self.current_trajectory.append({
                    'state': state_key,
                    'action': (action_type, amount),
                    'game_state': {}
                })
            
            # 记录动作选择
            try:
                action_key = self._get_action_key(action_type, amount, game_state)
                self.action_count[state_key][action_key] += 1
            except Exception as action_key_error:
                print(f"⚠️  {self.name}: 动作键记录失败: {action_key_error}")
                # 使用默认动作键
                self.action_count[state_key]["default_action"] += 1
            
            return action_type, amount
            
        except Exception as e:
            # 改进错误信息显示
            error_type = type(e).__name__
            error_msg = str(e)
            
            # 如果错误信息看起来像状态键，简化显示
            if '_' in error_msg and len(error_msg.split('_')) >= 6:
                print(f"⚠️  {self.name}: 内部计算异常 (已自动处理)")
            else:
                print(f"⚠️  {self.name}: 动作选择异常 - {error_msg} (已自动处理)")
            
            # 出现错误时的安全回退
            call_amount = game_state.get('call_amount', 0)
            
            # 尝试安全的默认动作
            if call_amount == 0:
                return PlayerAction.CHECK, 0
            elif call_amount > 0 and self.chips >= call_amount:
                return PlayerAction.CALL, call_amount
            else:
                return PlayerAction.FOLD, 0
    
    def _should_explore(self, state_key: str) -> bool:
        """改进的探索决策"""
        # 基础ε-贪婪
        if random.random() < self.epsilon:
            return True
        
        # 对新状态增加探索
        if self.state_visit_count[state_key] < 3:
            return True
        
        return False
    
    def _ucb_action_selection(self, state_key: str, available_actions: List[Tuple[PlayerAction, int]], 
                             game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """UCB动作选择"""
        try:
            best_action = None
            best_ucb = float('-inf')
            
            total_visits = sum(self.action_count[state_key].values())
            
            for action_type, amount in available_actions:
                action_key = self._get_action_key(action_type, amount, game_state)
                
                # Q值（双Q网络平均）
                q1 = self.q_table_1[state_key][action_key]
                q2 = self.q_table_2[state_key][action_key]
                q_value = (q1 + q2) / 2
                
                # UCB探索奖励
                action_visits = self.action_count[state_key][action_key]
                if action_visits == 0:
                    ucb_bonus = float('inf')
                else:
                    ucb_bonus = math.sqrt(2 * math.log(total_visits + 1) / action_visits)
                
                ucb_value = q_value + 0.1 * ucb_bonus
                
                if ucb_value > best_ucb:
                    best_ucb = ucb_value
                    best_action = (action_type, amount)
            
            return best_action if best_action else random.choice(available_actions)
            
        except Exception as e:
            print(f"⚠️  {self.name} UCB选择出现错误: {e}, 使用随机选择")
            return random.choice(available_actions) if available_actions else (PlayerAction.FOLD, 0)
    
    def _double_q_action_selection(self, state_key: str, available_actions: List[Tuple[PlayerAction, int]], 
                                  game_state: Dict[str, Any]) -> Tuple[PlayerAction, int]:
        """双Q网络动作选择"""
        try:
            best_action = None
            best_q = float('-inf')
            
            for action_type, amount in available_actions:
                action_key = self._get_action_key(action_type, amount, game_state)
                
                # 双Q网络的平均Q值
                q1 = self.q_table_1[state_key][action_key]
                q2 = self.q_table_2[state_key][action_key]
                avg_q = (q1 + q2) / 2
                
                if avg_q > best_q:
                    best_q = avg_q
                    best_action = (action_type, amount)
            
            return best_action if best_action else random.choice(available_actions)
            
        except Exception as e:
            print(f"⚠️  {self.name} 双Q选择出现错误: {e}, 使用随机选择")
            return random.choice(available_actions) if available_actions else (PlayerAction.FOLD, 0)
    
    def _get_enhanced_actions(self, game_state: Dict[str, Any]) -> List[Tuple[PlayerAction, int]]:
        """获取增强的动作空间"""
        try:
            actions = []
            call_amount = game_state.get('call_amount', 0)
            pot_size = game_state.get('pot', 1)
            min_raise = game_state.get('min_raise', game_state.get('big_blind', 20))
            
            # 弃牌（除非已经无需跟注）
            if call_amount > 0:
                actions.append((PlayerAction.FOLD, 0))
            
            # 过牌或跟注
            if call_amount == 0:
                actions.append((PlayerAction.CHECK, 0))
            elif call_amount <= self.chips:
                actions.append((PlayerAction.CALL, call_amount))
            
            # 各种大小的加注
            if self.chips > call_amount:
                remaining_chips = self.chips - call_amount
                
                # 小加注 (0.3-0.5 pot)
                small_bet = max(min_raise, min(int(pot_size * 0.4), remaining_chips))
                if small_bet <= remaining_chips:
                    actions.append((PlayerAction.RAISE, call_amount + small_bet))
                
                # 中等加注 (0.6-0.8 pot)
                medium_bet = max(min_raise, min(int(pot_size * 0.7), remaining_chips))
                if medium_bet <= remaining_chips and medium_bet != small_bet:
                    actions.append((PlayerAction.RAISE, call_amount + medium_bet))
                
                # 大加注 (1.0-1.5 pot)
                large_bet = max(min_raise, min(int(pot_size * 1.2), remaining_chips))
                if large_bet <= remaining_chips and large_bet != medium_bet:
                    actions.append((PlayerAction.RAISE, call_amount + large_bet))
                
                # 全押
                if remaining_chips > min_raise:
                    actions.append((PlayerAction.ALL_IN, self.chips))
            
            # 确保至少有一个动作
            if not actions:
                # 如果没有生成任何动作，添加安全的默认动作
                if call_amount == 0:
                    actions.append((PlayerAction.CHECK, 0))
                elif self.chips >= call_amount:
                    actions.append((PlayerAction.CALL, call_amount))
                else:
                    actions.append((PlayerAction.FOLD, 0))
            
            return actions
            
        except Exception as e:
            print(f"⚠️  {self.name} 生成动作出现错误: {e}, 使用默认动作")
            # 出现错误时的安全回退
            call_amount = game_state.get('call_amount', 0)
            if call_amount == 0:
                return [(PlayerAction.CHECK, 0)]
            elif self.chips >= call_amount:
                return [(PlayerAction.CALL, call_amount)]
            else:
                return [(PlayerAction.FOLD, 0)]
    
    def _get_action_key(self, action_type: PlayerAction, amount: int, game_state: Dict[str, Any]) -> str:
        """获取动作键"""
        try:
            if action_type == PlayerAction.FOLD:
                return "fold"
            elif action_type == PlayerAction.CHECK:
                return "check"
            elif action_type == PlayerAction.CALL:
                return "call"
            elif action_type == PlayerAction.ALL_IN:
                return "all_in"
            else:  # RAISE
                pot_size = max(1, game_state.get('pot', 1))  # 确保至少为1
                call_amount = max(0, game_state.get('call_amount', 0))
                bet_size = max(0, amount - call_amount)
                
                if pot_size <= 0:
                    return "small_raise"  # 默认返回
                
                bet_ratio = bet_size / pot_size
                
                if bet_ratio < 0.5:
                    return "small_raise"
                elif bet_ratio < 1.0:
                    return "medium_raise"
                else:
                    return "large_raise"
                    
        except (TypeError, ValueError, ZeroDivisionError):
            # 出现错误时返回默认动作键
            return "call"
    
    def learn_from_hand_result(self, hand_result: Dict[str, Any]):
        """从手牌结果中学习（改进版）"""
        if not self.current_trajectory:
            return
        
        # 计算改进的奖励
        reward = self._calculate_enhanced_reward(hand_result)
        
        # 经验回放学习
        self._add_experience_and_learn(reward)
        
        # 更新统计
        self.total_reward += reward
        self.game_count += 1
        if hand_result.get('winner_id') == self.player_id:
            self.win_count += 1
        
        # 衰减探索率
        self.decay_epsilon()
        
        # 记录训练进度 (每N手记录一次)
        if (self.game_count - self.last_snapshot_game_count) >= self.snapshot_interval:
            self._record_training_progress()
            self.last_snapshot_game_count = self.game_count
        
        # 清空当前轨迹
        self.current_trajectory = []
    
    def _record_training_progress(self):
        """记录训练进度到追踪器"""
        try:
            from .training_tracker import TrainingTracker
            
            tracker = TrainingTracker()
            
            # 确定机器人类型
            bot_type = 'improved_rl_bot'
            if hasattr(self, 'conservative_mode') and self.conservative_mode:
                bot_type = 'conservative_rl_bot'
            elif 'improved' not in self.model_path.lower():
                bot_type = 'rl_bot'
            
            # 获取当前统计
            current_stats = self.get_learning_stats()
            
            # 添加额外信息
            additional_info = {
                'snapshot_interval': self.snapshot_interval,
                'model_path': self.model_path,
                'current_chips': self.chips
            }
            
            # 记录快照
            tracker.record_snapshot(bot_type, current_stats, additional_info)
            
        except Exception as e:
            # 静默处理错误，不影响训练
            pass
    
    def _calculate_enhanced_reward(self, hand_result: Dict[str, Any]) -> float:
        """计算增强的奖励函数"""
        reward = 0.0
        
        # 基础胜负奖励
        if hand_result.get('winner_id') == self.player_id:
            winnings = hand_result.get('winnings', 0)
            # 限制奖励的最大值，防止数值溢出
            roi_reward = winnings / max(self.total_bet_in_hand, 1)
            # 确保奖励是有限的，并限制最大值
            if math.isinf(roi_reward) or math.isnan(roi_reward) or roi_reward > 10.0:
                reward += 10.0  # 设置最大奖励上限
            else:
                reward += min(10.0, roi_reward)  # ROI奖励，限制在10.0以内
        else:
            # 失败惩罚，但不过度惩罚
            reward -= min(1.0, self.total_bet_in_hand / max(self.chips + self.total_bet_in_hand, 1))
        
        # 决策质量奖励
        for i, step in enumerate(self.current_trajectory):
            action_type, amount = step['action']
            game_state = step['game_state']
            
            # 奖励合理的下注大小
            if action_type in [PlayerAction.RAISE, PlayerAction.CALL]:
                hand_strength = self.estimate_hand_strength(game_state)
                pot_odds = self.calculate_pot_odds(game_state)
                
                # 强牌时加注获得奖励
                if hand_strength > 0.7 and action_type == PlayerAction.RAISE:
                    reward += 0.1
                
                # 弱牌时弃牌获得奖励
                elif hand_strength < 0.3 and action_type == PlayerAction.FOLD:
                    reward += 0.05
                
                # 合理的底池赔率决策
                if pot_odds > 3 and hand_strength > 0.4 and action_type == PlayerAction.CALL:
                    reward += 0.05
        
        # 生存奖励（避免过早全押）
        if not self.is_folded and self.chips > 0:
            reward += 0.02
        
        return reward
    
    def _add_experience_and_learn(self, final_reward: float):
        """添加经验并进行学习"""
        # 计算每步的奖励（时间差分）
        for i, step in enumerate(self.current_trajectory):
            state = step['state']
            action_type, amount = step['action']
            action_key = self._get_action_key(action_type, amount, step['game_state'])
            
            # 计算折扣奖励
            steps_to_end = len(self.current_trajectory) - i - 1
            discounted_reward = final_reward * (self.discount_factor ** steps_to_end)
            
            # 添加到经验缓冲
            experience = {
                'state': state,
                'action': action_key,
                'reward': discounted_reward,
                'next_state': self.current_trajectory[i+1]['state'] if i+1 < len(self.current_trajectory) else None
            }
            self.experience_buffer.append(experience)
        
        # 经验回放学习
        self._replay_experience()
    
    def _replay_experience(self):
        """经验回放学习"""
        if len(self.experience_buffer) < self.batch_size:
            return
        
        # 随机采样经验
        batch = random.sample(self.experience_buffer, min(self.batch_size, len(self.experience_buffer)))
        
        for experience in batch:
            state = experience['state']
            action = experience['action']
            reward = experience['reward']
            next_state = experience['next_state']
            
            # 双Q学习更新
            if random.random() < 0.5:
                self._update_q_table(self.q_table_1, self.q_table_2, state, action, reward, next_state)
            else:
                self._update_q_table(self.q_table_2, self.q_table_1, state, action, reward, next_state)
    
    def _update_q_table(self, primary_q: dict, secondary_q: dict, state: str, action: str, 
                       reward: float, next_state: str):
        """更新Q表（双Q学习）"""
        current_q = primary_q[state][action]
        
        if next_state:
            # 使用primary_q选择动作，secondary_q评估价值
            best_next_action = max(primary_q[next_state].items(), 
                                 key=lambda x: x[1], default=(None, 0))[0]
            if best_next_action:
                max_next_q = secondary_q[next_state][best_next_action]
            else:
                max_next_q = 0
        else:
            max_next_q = 0
        
        # Q学习更新
        target_q = reward + self.discount_factor * max_next_q
        new_q = current_q + self.learning_rate * (target_q - current_q)
        primary_q[state][action] = new_q
    
    def decay_epsilon(self):
        """衰减探索率"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def estimate_hand_strength(self, game_state: Dict[str, Any]) -> float:
        """评估手牌强度（复用原有逻辑）"""
        community_cards = game_state.get('community_cards', [])
        
        # 转换字符串格式的牌
        if community_cards and isinstance(community_cards[0], str):
            card_objects = []
            for card_str in community_cards:
                try:
                    card_objects.append(Card.from_string(card_str))
                except:
                    continue
            community_cards = card_objects
        
        all_cards = self.hole_cards + community_cards
        
        # 使用HandEvaluator或简化评估
        if len(all_cards) == 5 or len(all_cards) == 7:
            return HandEvaluator.get_hand_strength(all_cards)
        elif len(all_cards) >= 3:
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
        """评估部分手牌强度"""
        if len(all_cards) < 3:
            return self._evaluate_preflop_strength()
        
        from collections import Counter
        values = [card.rank_value for card in all_cards]
        suits = [card.suit for card in all_cards]
        
        value_counts = Counter(values)
        suit_counts = Counter(suits)
        
        base_score = 0.3
        
        # 检查成牌
        counts = sorted(value_counts.values(), reverse=True)
        if counts[0] >= 3:
            base_score = 0.8
        elif counts[0] == 2:
            pair_value = max([v for v, c in value_counts.items() if c == 2])
            if pair_value >= 10:
                base_score = 0.6
            else:
                base_score = 0.5
        
        # 同花可能性
        max_suit_count = max(suit_counts.values())
        if max_suit_count >= 3:
            base_score += 0.1
        
        # 顺子可能性
        unique_values = sorted(set(values))
        if len(unique_values) >= 3:
            consecutive_count = 1
            max_consecutive = 1
            for i in range(1, len(unique_values)):
                if unique_values[i] - unique_values[i-1] == 1:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1
            
            if max_consecutive >= 3:
                base_score += 0.1
        
        return min(0.9, base_score)
    
    def calculate_pot_odds(self, game_state: Dict[str, Any]) -> float:
        """计算底池赔率"""
        try:
            call_amount = game_state.get('call_amount', 0)
            pot_size = game_state.get('pot', 0)
            
            if call_amount <= 0:
                return float('inf')
            
            if pot_size <= 0:
                return 0.0
            
            return pot_size / call_amount
            
        except (ZeroDivisionError, TypeError, ValueError):
            # 计算失败时返回默认值
            return 2.0  # 默认的合理底池赔率
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        total_states = len(self.q_table_1) + len(self.q_table_2)
        total_state_actions = sum(len(actions) for actions in self.q_table_1.values())
        total_state_actions += sum(len(actions) for actions in self.q_table_2.values())
        
        return {
            'q_table_size': total_states // 2,  # 双Q网络，除以2
            'total_states': total_state_actions // 2,
            'epsilon': self.epsilon,
            'memory_size': len(self.experience_buffer),
            'total_reward': self.total_reward,
            'game_count': self.game_count,
            'win_rate': self.win_count / max(1, self.game_count),
            'avg_reward': self.total_reward / max(1, self.game_count)
        } 