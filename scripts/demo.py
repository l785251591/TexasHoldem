#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
德州扑克游戏演示脚本
展示游戏的主要功能和特性
"""

from poker_game import *
import time

def demo_card_system():
    """演示扑克牌系统"""
    print("🎴 扑克牌系统演示")
    print("=" * 50)
    
    # 创建牌堆
    deck = Deck()
    print(f"牌堆总数: {deck.cards_remaining()}")
    
    # 发几张牌
    cards = deck.deal_cards(5)
    print("发出的5张牌:")
    for i, card in enumerate(cards, 1):
        print(f"  {i}. {card} (数值: {card.rank_value})")
    
    print()

def demo_hand_evaluation():
    """演示牌型评估"""
    print("🃏 牌型评估演示")
    print("=" * 50)
    
    # 创建一个皇家同花顺
    royal_flush = [
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.HEARTS, Rank.JACK),
        Card(Suit.HEARTS, Rank.QUEEN),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.HEARTS, Rank.ACE)
    ]
    
    rank, kickers = HandEvaluator.evaluate_hand(royal_flush)
    strength = HandEvaluator.get_hand_strength(royal_flush)
    
    print("皇家同花顺:")
    print(f"  牌: {' '.join(str(card) for card in royal_flush)}")
    print(f"  牌型: {rank.hand_name}")
    print(f"  强度: {strength:.3f}")
    
    # 创建一个对子
    pair = [
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.QUEEN),
        Card(Suit.HEARTS, Rank.JACK)
    ]
    
    rank, kickers = HandEvaluator.evaluate_hand(pair)
    strength = HandEvaluator.get_hand_strength(pair)
    
    print("\n一对A:")
    print(f"  牌: {' '.join(str(card) for card in pair)}")
    print(f"  牌型: {rank.hand_name}")
    print(f"  强度: {strength:.3f}")
    
    print()

def demo_bot_intelligence():
    """演示机器人智能"""
    print("🤖 机器人智能演示")
    print("=" * 50)
    
    # 创建不同难度的机器人
    easy_bot = EasyBot("easy_1", "简单机器人", 1000)
    medium_bot = MediumBot("medium_1", "中等机器人", 1000)
    hard_bot = HardBot("hard_1", "困难机器人", 1000)
    rl_bot = RLBot("rl_1", "学习机器人", 1000)
    
    # 给机器人发手牌
    deck = Deck()
    for bot in [easy_bot, medium_bot, hard_bot, rl_bot]:
        bot.hole_cards = deck.deal_cards(2)
    
    # 模拟游戏状态
    game_state = {
        'call_amount': 50,
        'pot': 200,
        'min_raise': 50,
        'community_cards': deck.deal_cards(3),  # 翻牌
        'other_players': []
    }
    
    print("游戏状态:")
    print(f"  跟注金额: {game_state['call_amount']}")
    print(f"  底池大小: {game_state['pot']}")
    print(f"  公共牌: {' '.join(str(card) for card in game_state['community_cards'])}")
    
    print("\n各机器人的决策:")
    for bot in [easy_bot, medium_bot, hard_bot, rl_bot]:
        hand_strength = bot.estimate_hand_strength(game_state)
        action, amount = bot.get_action(game_state)
        
        print(f"  {bot.name}:")
        print(f"    手牌: {' '.join(str(card) for card in bot.hole_cards)}")
        print(f"    牌力: {hand_strength:.3f}")
        print(f"    决策: {action.value} {amount if amount > 0 else ''}")
    
    print()

def demo_rl_bot_learning():
    """演示强化学习机器人"""
    print("🧠 强化学习机器人演示")
    print("=" * 50)
    
    rl_bot = RLBot("rl_demo", "学习机器人", 1000)
    
    print(f"初始状态:")
    stats = rl_bot.get_learning_stats()
    print(f"  Q表大小: {stats['q_table_size']}")
    print(f"  总状态数: {stats['total_states']}")
    print(f"  探索率: {stats['epsilon']:.3f}")
    
    # 模拟一些学习
    print("\n模拟学习过程...")
    for i in range(5):
        # 模拟手牌结果
        hand_result = {
            'winner_id': rl_bot.player_id if i % 2 == 0 else 'other',
            'winnings': 100 if i % 2 == 0 else 0,
            'game_state': {'pot': 200, 'call_amount': 50}
        }
        
        rl_bot.total_bet_in_hand = 50
        rl_bot.learn_from_hand_result(hand_result)
        rl_bot.decay_epsilon()
        
        if i % 2 == 0:
            print(f"  第{i+1}局: 获胜 (+100)")
        else:
            print(f"  第{i+1}局: 失败 (-50)")
    
    print(f"\n学习后状态:")
    stats = rl_bot.get_learning_stats()
    print(f"  Q表大小: {stats['q_table_size']}")
    print(f"  总状态数: {stats['total_states']}")
    print(f"  探索率: {stats['epsilon']:.3f}")
    print(f"  记忆大小: {stats['memory_size']}")
    
    print()

def demo_kelly_criterion():
    """演示凯利公式"""
    print("📊 凯利公式演示")
    print("=" * 50)
    
    hard_bot = HardBot("hard_demo", "困难机器人", 1000)
    
    scenarios = [
        (0.6, 3.0, "胜率60%, 赔率3:1"),
        (0.4, 2.0, "胜率40%, 赔率2:1"),
        (0.8, 4.0, "胜率80%, 赔率4:1"),
        (0.3, 1.5, "胜率30%, 赔率1.5:1")
    ]
    
    print("不同情况下的凯利公式计算:")
    for win_prob, pot_odds, description in scenarios:
        kelly = hard_bot.calculate_kelly_criterion(win_prob, pot_odds)
        print(f"  {description}")
        print(f"    凯利比例: {kelly:.3f} ({kelly*100:.1f}%)")
        print(f"    建议下注: {int(1000 * kelly)} (筹码总数1000)")
        print()

def main():
    """主演示函数"""
    print("🎯 德州扑克游戏功能演示")
    print("=" * 60)
    print()
    
    try:
        demo_card_system()
        time.sleep(1)
        
        demo_hand_evaluation()
        time.sleep(1)
        
        demo_bot_intelligence()
        time.sleep(1)
        
        demo_rl_bot_learning()
        time.sleep(1)
        
        demo_kelly_criterion()
        
        print("✅ 演示完成！")
        print("\n要开始完整游戏，请运行: python main.py")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 