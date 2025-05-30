from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import time
from .card import Deck, Card
from .player import Player, PlayerAction
from .hand_evaluator import HandEvaluator
from .database import GameDatabase

class PokerGame:
    """德州扑克游戏引擎"""
    
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.side_pots: List[Dict[str, Any]] = []
        
        # 盲注设置
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        # 游戏状态
        self.current_hand = 0
        self.dealer_position = 0
        self.current_player_index = 0
        self.current_bet = 0
        self.min_raise = big_blind
        self.betting_round = "preflop"  # preflop, flop, turn, river
        
        # 数据库
        self.db = GameDatabase()
        self.game_id = None
        self.hand_id = None
        self.game_start_time = None
        
        # 游戏历史
        self.hand_history: List[Dict[str, Any]] = []
        
    def _has_human_players(self) -> bool:
        """检查游戏中是否有真实玩家参与"""
        from .player import HumanPlayer
        return any(isinstance(player, HumanPlayer) for player in self.players)
    
    def _wait_for_human_observation(self, duration: float = 2.0):
        """如果有真实玩家参与，等待一段时间让玩家观察"""
        # 如果是训练模式，跳过所有等待
        if hasattr(self, 'training_mode') and self.training_mode:
            return
        
        if self._has_human_players():
            time.sleep(duration)
        
    def add_player(self, player: Player):
        """添加玩家到游戏中"""
        player.position = len(self.players)
        self.players.append(player)
        print(f"玩家 {player.name} 已加入游戏")
    
    def start_game(self):
        """开始游戏"""
        if len(self.players) < 2:
            raise ValueError("至少需要2个玩家才能开始游戏")
        
        self.game_start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"🎰 德州扑克游戏开始！🎰")
        print(f"{'='*60}")
        print(f"💰 小盲注: {self.small_blind} | 大盲注: {self.big_blind}")
        print(f"👥 参与玩家: {', '.join(p.name for p in self.players)}")
        for player in self.players:
            print(f"   {player.name}: {player.chips} 筹码")
        print(f"{'='*60}\n")
        
        # 游戏主循环
        while self._should_continue_game():
            self._play_hand()
            self.current_hand += 1
            self._move_dealer_button()
        
        self._end_game()
    
    def _should_continue_game(self) -> bool:
        """检查是否应该继续游戏"""
        active_players = [p for p in self.players if p.chips > 0]
        return len(active_players) > 1
    
    def _play_hand(self):
        """玩一手牌"""
        print(f"\n{'█'*50}")
        print(f"🃏 第 {self.current_hand + 1} 手牌开始 🃏")
        print(f"🎯 庄家位置: {self.players[self.dealer_position].name}")
        print(f"{'█'*50}")
        
        # 等待玩家观察
        self._wait_for_human_observation(1.5)
        
        # 重置手牌状态
        self._reset_hand()
        
        # 发手牌
        self._deal_hole_cards()
        
        # 下盲注
        self._post_blinds()
        
        # 翻牌前下注轮
        self.betting_round = "preflop"
        if not self._betting_round():
            self._end_hand()
            return
        
        # 翻牌
        if self._get_active_players_count() > 1:
            self._deal_flop()
            self.betting_round = "flop"
            if not self._betting_round():
                self._end_hand()
                return
        
        # 转牌
        if self._get_active_players_count() > 1:
            self._deal_turn()
            self.betting_round = "turn"
            if not self._betting_round():
                self._end_hand()
                return
        
        # 河牌
        if self._get_active_players_count() > 1:
            self._deal_river()
            self.betting_round = "river"
            if not self._betting_round():
                self._end_hand()
                return
        
        # 摊牌
        if self._get_active_players_count() > 1:
            self._showdown()
        
        self._end_hand()
    
    def _reset_hand(self):
        """重置手牌状态"""
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.side_pots = []
        self.current_bet = 0
        self.min_raise = self.big_blind
        
        # 重置玩家状态
        for player in self.players:
            player.reset_for_new_hand()
    
    def _deal_hole_cards(self):
        """发手牌"""
        for player in self.players:
            if player.chips > 0:
                hole_cards = self.deck.deal_cards(2)
                player.deal_hole_cards(hole_cards)
    
    def _post_blinds(self):
        """下盲注"""
        active_players = [p for p in self.players if p.chips > 0]
        if len(active_players) < 2:
            return
        
        # 确定小盲注和大盲注位置
        if len(active_players) == 2:
            # 只有两个玩家时，庄家下小盲注
            sb_pos = self.dealer_position
            bb_pos = (self.dealer_position + 1) % len(self.players)
        else:
            sb_pos = (self.dealer_position + 1) % len(self.players)
            bb_pos = (self.dealer_position + 2) % len(self.players)
        
        # 下小盲注
        sb_player = self.players[sb_pos]
        sb_amount = sb_player.bet(min(self.small_blind, sb_player.chips))
        self.pot += sb_amount
        print(f"💸 {sb_player.name} 下小盲注 {sb_amount}")
        
        # 下大盲注
        bb_player = self.players[bb_pos]
        bb_amount = bb_player.bet(min(self.big_blind, bb_player.chips))
        self.pot += bb_amount
        self.current_bet = bb_amount
        print(f"💸 {bb_player.name} 下大盲注 {bb_amount}")
        print(f"💰 底池: {self.pot}")
        
        # 等待玩家观察盲注情况
        self._wait_for_human_observation(1.0)
        
        # 设置第一个行动的玩家
        if len(active_players) == 2:
            self.current_player_index = sb_pos
        else:
            self.current_player_index = (bb_pos + 1) % len(self.players)
    
    def _betting_round(self) -> bool:
        """进行一轮下注，返回是否继续游戏"""
        if self._get_active_players_count() <= 1:
            return False
        
        print(f"\n┌{'─'*40}┐")
        print(f"│ 📊 {self.betting_round.upper()} 下注轮")
        if self.community_cards:
            print(f"│ 🎴 公共牌: {' '.join(str(card) for card in self.community_cards)}")
        print(f"│ 💰 底池: {self.pot}")
        print(f"│ 💵 当前下注: {self.current_bet}")
        print(f"└{'─'*40}┘")
        
        # 等待玩家观察下注轮信息
        self._wait_for_human_observation(1.0)
        
        # 添加循环计数器防止无限循环
        max_rounds = len(self.players) * 3  # 最多循环次数
        round_count = 0
        
        # 记录每个玩家是否已经行动过
        players_acted = {i: False for i in range(len(self.players))}
        last_raiser_index = None
        action_count = 0  # 总行动计数
        
        while round_count < max_rounds:
            round_count += 1
            
            # 检查是否所有需要行动的玩家都已行动
            all_players_acted = True
            for i, player in enumerate(self.players):
                if (player.can_act() and not players_acted.get(i, False)):
                    # 如果玩家还没有行动过，或者需要跟注
                    if (not players_acted.get(i, False) or 
                        player.current_bet < self.current_bet):
                        all_players_acted = False
                        break
            
            if all_players_acted:
                break
            
            current_player = self.players[self.current_player_index]
            
            # 跳过无法行动的玩家
            if not current_player.can_act():
                self._next_player()
                continue
            
            # 检查玩家是否需要行动
            needs_action = (
                not players_acted.get(self.current_player_index, False) or
                current_player.current_bet < self.current_bet
            )
            
            if not needs_action and self.current_player_index != last_raiser_index:
                players_acted[self.current_player_index] = True
                self._next_player()
                continue
            
            # 获取玩家动作
            game_state = self._get_game_state(current_player)
            action, amount = current_player.get_action(game_state)
            
            # 处理动作
            is_raise = self._process_action(current_player, action, amount)
            if is_raise:
                last_raiser_index = self.current_player_index
                # 重置其他玩家的行动状态
                players_acted = {i: False for i in range(len(self.players))}
            
            # 标记当前玩家已行动
            players_acted[self.current_player_index] = True
            action_count += 1
            
            # 等待玩家观察动作结果
            self._wait_for_human_observation(1.0)
            
            # 保存动作到数据库
            self._save_player_action(current_player, action, amount, game_state)
            
            # 检查是否还有玩家需要行动
            if self._get_active_players_count() <= 1:
                return False
            
            self._next_player()
        
        # 如果循环次数超限，输出调试信息
        if round_count >= max_rounds:
            print(f"警告：下注轮循环次数超限 ({max_rounds})，强制结束")
            print(f"当前下注: {self.current_bet}")
            for i, player in enumerate(self.players):
                print(f"  {player.name}: 下注={player.current_bet}, 可行动={player.can_act()}, 已行动={players_acted.get(i, False)}")
        
        # 重置当前下注
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        
        return True
    
    def _process_action(self, player: Player, action: PlayerAction, amount: int) -> bool:
        """处理玩家动作，返回是否是加注"""
        is_raise = False
        
        if action == PlayerAction.FOLD:
            player.fold()
            print(f"❌ {player.name} 弃牌")
            
        elif action == PlayerAction.CHECK:
            print(f"✋ {player.name} 过牌")
            
        elif action == PlayerAction.CALL:
            call_amount = self.current_bet - player.current_bet
            actual_amount = player.bet(call_amount)
            self.pot += actual_amount
            print(f"📞 {player.name} 跟注 {actual_amount} (总下注: {player.current_bet})")
            
        elif action == PlayerAction.RAISE:
            # 计算加注金额
            call_amount = self.current_bet - player.current_bet
            total_amount = call_amount + amount
            actual_amount = player.bet(total_amount)
            self.pot += actual_amount
            
            # 更新当前下注和最小加注
            new_bet = player.current_bet
            raise_amount = new_bet - self.current_bet
            self.current_bet = new_bet
            self.min_raise = max(self.min_raise, raise_amount)
            
            print(f"🚀 {player.name} 加注到 {new_bet} (加注 {raise_amount})")
            is_raise = True
            
        elif action == PlayerAction.ALL_IN:
            actual_amount = player.bet(player.chips)
            self.pot += actual_amount
            
            if player.current_bet > self.current_bet:
                # 全押且超过当前下注，算作加注
                raise_amount = player.current_bet - self.current_bet
                self.current_bet = player.current_bet
                self.min_raise = max(self.min_raise, raise_amount)
                is_raise = True
                print(f"💥 {player.name} 全押 {actual_amount} (加注到 {player.current_bet}) ⚡")
            else:
                print(f"💥 {player.name} 全押 {actual_amount} ⚡")
        
        return is_raise
    
    def _next_player(self):
        """移动到下一个玩家"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def _get_active_players_count(self) -> int:
        """获取仍在游戏中的玩家数量"""
        return len([p for p in self.players if not p.is_folded])
    
    def _deal_flop(self):
        """发翻牌"""
        self.deck.deal_card()  # 烧牌
        flop_cards = self.deck.deal_cards(3)
        self.community_cards.extend(flop_cards)
        print(f"\n🎯 翻牌: {' '.join(str(card) for card in flop_cards)}")
        
        # 等待玩家观察翻牌
        self._wait_for_human_observation(2.0)
    
    def _deal_turn(self):
        """发转牌"""
        self.deck.deal_card()  # 烧牌
        turn_card = self.deck.deal_card()
        self.community_cards.append(turn_card)
        print(f"\n🎯 转牌: {turn_card}")
        
        # 等待玩家观察转牌
        self._wait_for_human_observation(2.0)
    
    def _deal_river(self):
        """发河牌"""
        self.deck.deal_card()  # 烧牌
        river_card = self.deck.deal_card()
        self.community_cards.append(river_card)
        print(f"\n🎯 河牌: {river_card}")
        
        # 等待玩家观察河牌
        self._wait_for_human_observation(2.0)
    
    def _showdown(self):
        """摊牌"""
        print(f"\n{'🎊'*20} 摊牌时刻 {'🎊'*20}")
        active_players = [p for p in self.players if not p.is_folded]
        
        # 评估所有玩家的牌型
        player_hands = []
        for player in active_players:
            all_cards = player.hole_cards + self.community_cards
            hand_rank, kickers = HandEvaluator.evaluate_hand(all_cards)
            player_hands.append((player, hand_rank, kickers, all_cards))
            print(f"🎴 {player.name}: {' '.join(str(card) for card in player.hole_cards)} "
                  f"-> 🏆 {hand_rank.name}")
        
        # 排序找出获胜者
        player_hands.sort(key=lambda x: (x[1].rank_value, x[2]), reverse=True)
        
        # 分配奖池
        winners = [player_hands[0]]
        for i in range(1, len(player_hands)):
            if (player_hands[i][1].rank_value == winners[0][1].rank_value and 
                player_hands[i][2] == winners[0][2]):
                winners.append(player_hands[i])
            else:
                break
        
        winnings_per_player = self.pot // len(winners)
        remainder = self.pot % len(winners)
        
        print(f"\n{'🏆'*15} 获胜结果 {'🏆'*15}")
        for i, (winner, hand_rank, _, _) in enumerate(winners):
            amount = winnings_per_player + (1 if i < remainder else 0)
            winner.win_chips(amount)
            print(f"🎉 {winner.name} 获胜！赢得 {amount} 筹码 ({hand_rank.name})")
        print(f"{'🏆'*44}")
        
        # 等待玩家观察摊牌结果
        self._wait_for_human_observation(3.0)
    
    def _end_hand(self):
        """结束当前手牌"""
        # 找出获胜者
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            winner.win_chips(self.pot)
            print(f"\n{'🎊'*15} 手牌结束 {'🎊'*15}")
            print(f"🎉 {winner.name} 获胜！赢得 {self.pot} 筹码 (其他玩家弃牌)")
            print(f"{'🎊'*44}")
            
            # 等待玩家观察获胜结果
            self._wait_for_human_observation(2.0)
        
        # 保存手牌数据
        self._save_hand_data()
        
        # 学习（针对强化学习机器人）
        self._update_learning_bots()
        
        # 显示筹码情况
        print(f"\n{'💰'*20} 筹码统计 {'💰'*20}")
        for player in self.players:
            status = "🔥" if player.chips > 1000 else "💧" if player.chips < 500 else "💚"
            print(f"{status} {player.name}: {player.chips} 筹码")
        print(f"{'💰'*62}")
        
        # 淘汰没有筹码的玩家
        eliminated_players = [p for p in self.players if p.chips <= 0]
        if eliminated_players:
            print(f"\n{'💀'*10} 玩家淘汰 {'💀'*10}")
            for player in eliminated_players:
                print(f"💀 {player.name} 被淘汰！")
            print(f"{'💀'*32}")
        
        # 等待玩家观察手牌结束统计
        self._wait_for_human_observation(2.0)
        
        self.players = [p for p in self.players if p.chips > 0]
    
    def _move_dealer_button(self):
        """移动庄家按钮"""
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
    
    def _get_game_state(self, current_player: Player) -> Dict[str, Any]:
        """获取当前游戏状态"""
        other_players = []
        for player in self.players:
            if player != current_player:
                other_players.append({
                    'name': player.name,
                    'chips': player.chips,
                    'current_bet': player.current_bet,
                    'is_folded': player.is_folded,
                    'is_all_in': player.is_all_in
                })
        
        call_amount = max(0, self.current_bet - current_player.current_bet)
        
        return {
            'pot': self.pot,
            'community_cards': [str(card) for card in self.community_cards],
            'betting_round': self.betting_round,
            'current_bet': self.current_bet,
            'call_amount': call_amount,
            'min_raise': self.min_raise,
            'big_blind': self.big_blind,
            'small_blind': self.small_blind,
            'other_players': other_players,
            'hand_number': self.current_hand
        }
    
    def _save_player_action(self, player: Player, action: PlayerAction, 
                           amount: int, game_state: Dict[str, Any]):
        """保存玩家动作到数据库"""
        if self.hand_id:
            hand_strength = 0.0
            if hasattr(player, 'estimate_hand_strength'):
                hand_strength = player.estimate_hand_strength(game_state)
            
            pot_odds = 0.0
            if hasattr(player, 'calculate_pot_odds'):
                pot_odds = player.calculate_pot_odds(game_state)
                # 处理无穷大的pot_odds，数据库不能存储无穷大
                if pot_odds == float('inf'):
                    pot_odds = 999.0  # 用一个大数值代替无穷大
            
            self.db.save_player_action(
                hand_id=self.hand_id,
                player_id=player.player_id,
                action_type=action.value,
                amount=amount,
                position=player.position,
                betting_round=self.betting_round,
                hand_cards=[str(card) for card in player.hole_cards],
                pot_odds=pot_odds,
                hand_strength=hand_strength
            )
    
    def _save_hand_data(self):
        """保存手牌数据到数据库"""
        winner_id = ""
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) == 1:
            winner_id = active_players[0].player_id
        
        hand_data = {
            'players': [{'id': p.player_id, 'name': p.name, 'chips': p.chips} 
                       for p in self.players],
            'final_pot': self.pot,
            'community_cards': [str(card) for card in self.community_cards]
        }
        
        self.hand_id = self.db.save_hand(
            game_id=self.game_id or 0,
            hand_number=self.current_hand,
            pot_size=self.pot,
            winner_id=winner_id,
            showdown=len(active_players) > 1,
            community_cards=[str(card) for card in self.community_cards],
            hand_data=hand_data
        )
    
    def _update_learning_bots(self):
        """更新强化学习机器人"""
        from .rl_bot import RLBot
        
        for player in self.players:
            if isinstance(player, RLBot):
                hand_result = {
                    'winner_id': self._get_hand_winner_id(),
                    'winnings': self._get_player_winnings(player),
                    'game_state': self._get_game_state(player)
                }
                player.learn_from_hand_result(hand_result)
                player.decay_epsilon()
                
                # 定期保存模型
                if self.current_hand % 10 == 0:
                    player.save_model()
    
    def _get_hand_winner_id(self) -> str:
        """获取手牌获胜者ID"""
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) == 1:
            return active_players[0].player_id
        return ""
    
    def _get_player_winnings(self, player: Player) -> int:
        """获取玩家在本手牌的奖金"""
        # 简化计算，实际应该更复杂
        if not player.is_folded:
            active_players = [p for p in self.players if not p.is_folded]
            if len(active_players) == 1:
                return self.pot
        return 0
    
    def _end_game(self):
        """结束游戏"""
        print(f"\n{'🎯'*25}")
        print(f"{'🎯'*10} 游戏结束！ {'🎯'*10}")
        print(f"{'🎯'*25}")
        
        # 找出获胜者
        remaining_players = [p for p in self.players if p.chips > 0]
        if remaining_players:
            winner = max(remaining_players, key=lambda p: p.chips)
            print(f"\n{'👑'*20} 最终获胜者 {'👑'*20}")
            print(f"🏆 恭喜 {winner.name} 获得最终胜利！")
            print(f"💰 最终筹码: {winner.chips}")
            print(f"{'👑'*62}")
            
            # 显示所有玩家的最终排名
            all_players_sorted = sorted(self.players, key=lambda p: p.chips, reverse=True)
            print(f"\n{'📊'*20} 最终排名 {'📊'*20}")
            for i, player in enumerate(all_players_sorted, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                print(f"{medal} 第{i}名: {player.name} - {player.chips} 筹码")
            print(f"{'📊'*62}")
        
        # 显示游戏统计
        print(f"\n{'📈'*20} 游戏统计 {'📈'*20}")
        print(f"🎮 总手牌数: {self.current_hand}")
        if self.game_start_time:
            duration = datetime.now() - self.game_start_time
            print(f"⏱️  游戏时长: {duration}")
        print(f"{'📈'*62}")
        
        # 保存游戏数据
        if self.game_start_time:
            game_data = {
                'players': [{'id': p.player_id, 'name': p.name, 'final_chips': p.chips} 
                           for p in self.players],
                'hands_played': self.current_hand
            }
            
            self.game_id = self.db.save_game(
                start_time=self.game_start_time,
                end_time=datetime.now(),
                winner_id=winner.player_id if remaining_players else "",
                total_pot=sum(p.chips for p in self.players),
                players_count=len(self.players),
                game_data=game_data
            )
        
        # 保存强化学习机器人的模型
        from .rl_bot import RLBot
        for player in self.players:
            if isinstance(player, RLBot):
                player.save_model()
        
        print(f"\n感谢您的游戏！再见！👋")
        print(f"{'🎯'*25}")
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """获取游戏统计信息"""
        return {
            'hands_played': self.current_hand,
            'players': [
                {
                    'name': p.name,
                    'chips': p.chips,
                    'is_active': p.chips > 0
                }
                for p in self.players
            ]
        } 