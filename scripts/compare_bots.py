#!/usr/bin/env python3
"""
德州扑克机器人对比训练脚本
用于比较原版和改进版强化学习机器人的性能
"""

import time
from datetime import datetime
from poker_game import PokerGame, EasyBot, MediumBot, HardBot, RLBot, ImprovedRLBot

def run_comparison_training(hands_count=1000):
    """运行对比训练"""
    print("🆚 开始强化学习机器人对比训练")
    print("=" * 60)
    
    # 创建游戏
    game = PokerGame(small_blind=10, big_blind=20)
    
    # 添加机器人
    game.add_player(RLBot("rl_bot_1", "原版机器人1", 1000))
    game.add_player(ImprovedRLBot("improved_rl_bot_1", "🚀改进机器人1", 1000))
    game.add_player(RLBot("rl_bot_2", "原版机器人2", 1000))
    game.add_player(ImprovedRLBot("improved_rl_bot_2", "🚀改进机器人2", 1000))
    game.add_player(MediumBot("medium_bot", "中等对手", 1000))
    game.add_player(HardBot("hard_bot", "困难对手", 1000))
    
    print(f"参与对比的机器人:")
    for player in game.players:
        if isinstance(player, ImprovedRLBot):
            print(f"  🚀 {player.name} (改进版)")
        elif isinstance(player, RLBot):
            print(f"  🤖 {player.name} (原版)")
        else:
            print(f"  🔧 {player.name} (规则机器人)")
    
    # 设置训练模式
    game.training_mode = True
    game.game_start_time = datetime.now()
    
    start_time = time.time()
    last_stats_hand = 0
    
    # 统计数据
    stats = {
        'original_wins': 0,
        'improved_wins': 0,
        'original_total_chips': 0,
        'improved_total_chips': 0,
        'original_hands_played': 0,
        'improved_hands_played': 0
    }
    
    print(f"\n🎯 开始训练 {hands_count} 手牌...")
    print(f"训练开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        while game.current_hand < hands_count:
            # 检查是否需要重新分配筹码
            active_players = [p for p in game.players if p.chips > 0]
            if len(active_players) < 2:
                _rebalance_chips(game.players)
            
            # 显示进度
            if game.current_hand % 100 == 0 and game.current_hand > 0:
                elapsed_time = time.time() - start_time
                progress = (game.current_hand / hands_count) * 100
                hands_per_second = game.current_hand / elapsed_time if elapsed_time > 0 else 0
                
                print(f"\n📊 训练进度: {game.current_hand}/{hands_count} "
                      f"({progress:.1f}%) - {hands_per_second:.1f} 手/秒")
                
                # 显示机器人状态对比
                original_bots = [p for p in game.players if isinstance(p, RLBot) and not isinstance(p, ImprovedRLBot)]
                improved_bots = [p for p in game.players if isinstance(p, ImprovedRLBot)]
                
                print(f"\n🤖 原版机器人状态:")
                for bot in original_bots:
                    stats_data = bot.get_learning_stats()
                    status = "✅活跃" if bot.chips > 0 else "❌淘汰"
                    print(f"  {bot.name}: Q表={stats_data['q_table_size']}状态, "
                          f"ε={stats_data['epsilon']:.3f}, 筹码={bot.chips} ({status})")
                
                print(f"\n🚀 改进版机器人状态:")
                for bot in improved_bots:
                    stats_data = bot.get_learning_stats()
                    status = "✅活跃" if bot.chips > 0 else "❌淘汰"
                    print(f"  {bot.name}: Q表={stats_data['q_table_size']}状态, "
                          f"ε={stats_data['epsilon']:.3f}, 胜率={stats_data['win_rate']:.1%}, "
                          f"筹码={bot.chips} ({status})")
                
                # 更新统计
                _update_stats(stats, original_bots, improved_bots)
                
                # 显示对比统计
                print(f"\n📈 对比统计 (截至第{game.current_hand}手):")
                if stats['original_hands_played'] > 0 and stats['improved_hands_played'] > 0:
                    orig_win_rate = stats['original_wins'] / stats['original_hands_played']
                    impr_win_rate = stats['improved_wins'] / stats['improved_hands_played']
                    
                    print(f"  原版机器人: 胜率 {orig_win_rate:.1%}, 平均筹码 {stats['original_total_chips']/len(original_bots):.0f}")
                    print(f"  改进版机器人: 胜率 {impr_win_rate:.1%}, 平均筹码 {stats['improved_total_chips']/len(improved_bots):.0f}")
                    
                    if impr_win_rate > orig_win_rate:
                        print(f"  🏆 改进版领先 {(impr_win_rate - orig_win_rate)*100:.1f}个百分点!")
                    elif orig_win_rate > impr_win_rate:
                        print(f"  📊 原版领先 {(orig_win_rate - impr_win_rate)*100:.1f}个百分点")
                    else:
                        print(f"  🤝 目前势均力敌")
            
            # 保存模型
            if game.current_hand % 200 == 0 and game.current_hand > 0:
                print(f"\n💾 保存模型... (第 {game.current_hand} 手)")
                for player in game.players:
                    if isinstance(player, (RLBot, ImprovedRLBot)):
                        player.save_model()
            
            # 继续下一手
            try:
                game._play_hand()
                game.current_hand += 1
                game._move_dealer_button()
            except Exception as e:
                print(f"手牌 {game.current_hand} 出现错误: {e}")
                # 重置状态继续
                for player in game.players:
                    player.reset_for_new_hand()
                game.current_hand += 1
                continue
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  训练被用户中断 (已完成 {game.current_hand} 手)")
    
    # 训练完成统计
    end_time = time.time()
    training_duration = end_time - start_time
    
    print(f"\n" + "🎉" * 20 + " 对比训练完成 " + "🎉" * 20)
    print(f"总用时: {training_duration:.2f} 秒")
    print(f"完成手牌: {game.current_hand}")
    if training_duration > 0:
        print(f"平均速度: {game.current_hand/training_duration:.2f} 手/秒")
    
    # 最终统计对比
    original_bots = [p for p in game.players if isinstance(p, RLBot) and not isinstance(p, ImprovedRLBot)]
    improved_bots = [p for p in game.players if isinstance(p, ImprovedRLBot)]
    
    _update_stats(stats, original_bots, improved_bots)
    
    print(f"\n📊 最终对比结果:")
    print(f"=" * 50)
    
    # 保存最终模型
    print(f"\n💾 保存最终模型...")
    for player in game.players:
        if isinstance(player, (RLBot, ImprovedRLBot)):
            player.save_model()
            stats_data = player.get_learning_stats()
            status = "✅存活" if player.chips > 0 else "❌被淘汰"
            
            if isinstance(player, ImprovedRLBot):
                print(f"🚀 {player.name}: Q表={stats_data['q_table_size']}状态, "
                      f"胜率={stats_data['win_rate']:.1%}, 筹码={player.chips} ({status})")
            else:
                print(f"🤖 {player.name}: Q表={stats_data['q_table_size']}状态, "
                      f"筹码={player.chips} ({status})")
    
    # 总体对比
    if stats['original_hands_played'] > 0 and stats['improved_hands_played'] > 0:
        orig_win_rate = stats['original_wins'] / stats['original_hands_played']
        impr_win_rate = stats['improved_wins'] / stats['improved_hands_played']
        orig_avg_chips = stats['original_total_chips'] / len(original_bots)
        impr_avg_chips = stats['improved_total_chips'] / len(improved_bots)
        
        print(f"\n🏆 最终对比结果:")
        print(f"  原版机器人: 胜率 {orig_win_rate:.1%}, 平均筹码 {orig_avg_chips:.0f}")
        print(f"  改进版机器人: 胜率 {impr_win_rate:.1%}, 平均筹码 {impr_avg_chips:.0f}")
        
        win_rate_diff = impr_win_rate - orig_win_rate
        chips_diff = impr_avg_chips - orig_avg_chips
        
        if win_rate_diff > 0.05 and chips_diff > 100:
            print(f"\n🎉 改进版机器人明显优于原版!")
            print(f"   胜率提升: +{win_rate_diff*100:.1f}个百分点")
            print(f"   筹码优势: +{chips_diff:.0f}")
        elif win_rate_diff > 0.02 or chips_diff > 50:
            print(f"\n📈 改进版机器人略胜一筹")
            print(f"   胜率差异: {win_rate_diff*100:+.1f}个百分点")
            print(f"   筹码差异: {chips_diff:+.0f}")
        elif abs(win_rate_diff) <= 0.02 and abs(chips_diff) <= 50:
            print(f"\n🤝 两种机器人表现接近")
        else:
            print(f"\n📉 原版机器人表现更好")
            print(f"   胜率差异: {win_rate_diff*100:+.1f}个百分点")
            print(f"   筹码差异: {chips_diff:+.0f}")
    
    print(f"\n✅ 对比训练完成！请查看上述统计数据来评估改进效果。")

def _rebalance_chips(players):
    """重新平衡筹码"""
    total_chips = sum(p.chips for p in players)
    target_chips = max(1000, total_chips // len(players))
    
    for player in players:
        if isinstance(player, (RLBot, ImprovedRLBot)):
            player.chips = int(target_chips * 1.1)  # 强化学习机器人多一点
        else:
            player.chips = target_chips

def _update_stats(stats, original_bots, improved_bots):
    """更新统计数据"""
    # 重置统计
    stats['original_total_chips'] = sum(bot.chips for bot in original_bots)
    stats['improved_total_chips'] = sum(bot.chips for bot in improved_bots)
    
    # 累计游戏和胜利次数
    for bot in original_bots:
        if hasattr(bot, 'get_learning_stats'):
            bot_stats = bot.get_learning_stats()
            # 这里可能需要根据实际的统计方法调整
    
    for bot in improved_bots:
        if hasattr(bot, 'get_learning_stats'):
            bot_stats = bot.get_learning_stats()
            stats['improved_hands_played'] = max(stats['improved_hands_played'], bot_stats.get('game_count', 0))
            stats['improved_wins'] = max(stats['improved_wins'], bot_stats.get('win_count', 0))

if __name__ == "__main__":
    print("🤖 德州扑克强化学习机器人对比训练")
    print("这个脚本将对比原版和改进版强化学习机器人的性能")
    
    try:
        hands = int(input("请输入训练手牌数 (默认: 1000): ") or "1000")
    except ValueError:
        hands = 1000
    
    print(f"\n开始对比训练 {hands} 手牌...")
    
    run_comparison_training(hands) 