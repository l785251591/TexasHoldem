#!/usr/bin/env python3
"""
德州扑克游戏主程序
演示人类玩家与不同智力水平的机器人对战
"""

import sys
import os
from poker_game import PokerGame, HumanPlayer, EasyBot, MediumBot, HardBot, RLBot

def create_game_setup():
    """创建游戏设置"""
    print("=" * 60)
    print("🎲 欢迎来到德州扑克游戏！ 🎲")
    print("=" * 60)
    
    # 创建游戏实例
    game = PokerGame(small_blind=10, big_blind=20)
    
    print("\n请选择游戏模式:")
    print("1. 快速游戏 (预设玩家)")
    print("2. 自定义游戏")
    
    while True:
        try:
            choice = int(input("请输入选择 (1-2): "))
            if choice in [1, 2]:
                break
            else:
                print("请输入有效的选择 (1-2)")
        except ValueError:
            print("请输入有效的数字")
    
    if choice == 1:
        # 快速游戏模式
        return setup_quick_game(game)
    else:
        # 自定义游戏模式
        return setup_custom_game(game)

def setup_quick_game(game):
    """设置快速游戏"""
    print("\n设置快速游戏...")
    
    # 添加人类玩家
    human_name = input("请输入你的姓名 (默认: 玩家): ").strip()
    if not human_name:
        human_name = "玩家"
    
    human_player = HumanPlayer("human_1", human_name, 1000)
    game.add_player(human_player)
    
    # 添加不同难度的机器人
    game.add_player(EasyBot("easy_bot", "简单机器人", 1000))
    game.add_player(MediumBot("medium_bot", "中等机器人", 1000))
    game.add_player(HardBot("hard_bot", "困难机器人", 1000))
    
    # 添加强化学习机器人
    rl_bot = RLBot("rl_bot", "学习机器人", 1000)
    game.add_player(rl_bot)
    
    return game

def setup_custom_game(game):
    """设置自定义游戏"""
    print("\n设置自定义游戏...")
    
    # 添加人类玩家
    while True:
        add_human = input("是否添加人类玩家? (y/n): ").lower()
        if add_human in ['y', 'yes', 'n', 'no']:
            break
        print("请输入 y 或 n")
    
    if add_human in ['y', 'yes']:
        human_name = input("请输入玩家姓名: ").strip()
        if not human_name:
            human_name = "人类玩家"
        
        chips = get_chips_input("请输入初始筹码 (默认: 1000): ", 1000)
        human_player = HumanPlayer("human_1", human_name, chips)
        game.add_player(human_player)
    
    # 添加机器人
    bot_types = {
        "1": ("简单机器人", EasyBot),
        "2": ("中等机器人", MediumBot),
        "3": ("困难机器人", HardBot),
        "4": ("强化学习机器人", RLBot)
    }
    
    print("\n机器人类型:")
    for key, (name, _) in bot_types.items():
        print(f"{key}. {name}")
    
    bot_count = 0
    while len(game.players) < 6:  # 最多6个玩家
        print(f"\n当前玩家数: {len(game.players)}")
        add_bot = input("是否添加机器人? (y/n): ").lower()
        
        if add_bot in ['n', 'no']:
            break
        
        if add_bot in ['y', 'yes']:
            while True:
                try:
                    bot_type = input("选择机器人类型 (1-4): ")
                    if bot_type in bot_types:
                        break
                    else:
                        print("请输入有效的选择 (1-4)")
                except:
                    print("请输入有效的数字")
            
            name, bot_class = bot_types[bot_type]
            bot_count += 1
            bot_name = f"{name}_{bot_count}"
            chips = get_chips_input(f"请输入{name}的初始筹码 (默认: 1000): ", 1000)
            
            if bot_class == RLBot:
                bot = bot_class(f"bot_{bot_count}", bot_name, chips)
            else:
                bot = bot_class(f"bot_{bot_count}", bot_name, chips)
            
            game.add_player(bot)
    
    if len(game.players) < 2:
        print("至少需要2个玩家，自动添加一个简单机器人...")
        game.add_player(EasyBot("auto_bot", "自动机器人", 1000))
    
    return game

def get_chips_input(prompt, default):
    """获取筹码输入"""
    while True:
        try:
            chips_input = input(prompt).strip()
            if not chips_input:
                return default
            chips = int(chips_input)
            if chips > 0:
                return chips
            else:
                print("筹码数量必须大于0")
        except ValueError:
            print("请输入有效的数字")

def show_game_menu():
    """显示游戏菜单"""
    print("\n" + "=" * 40)
    print("🎯 游戏功能菜单")
    print("=" * 40)
    print("1. 开始新游戏")
    print("2. 🤖 自动训练模式 (机器人对战)")
    print("3. 🔄 永久自动训练模式 (无限循环)")
    print("4. 查看游戏统计")
    print("5. 查看强化学习机器人状态")
    print("6. 查看游戏历史")
    print("7. 🗃️  数据库管理")
    print("8. 退出")
    print("=" * 40)

def show_statistics(game):
    """显示游戏统计"""
    from poker_game import GameDatabase
    
    db = GameDatabase()
    
    print("\n" + "=" * 50)
    print("📊 游戏统计信息")
    print("=" * 50)
    
    # 显示当前游戏状态
    if game.players:
        stats = game.get_game_statistics()
        print(f"当前游戏已进行 {stats['hands_played']} 手牌")
        print("\n玩家状态:")
        for player_stat in stats['players']:
            status = "✅ 活跃" if player_stat['is_active'] else "❌ 淘汰"
            print(f"  {player_stat['name']}: {player_stat['chips']} 筹码 ({status})")
    
    # 显示历史统计
    print("\n📈 历史游戏记录:")
    history = db.get_game_history(limit=5)
    if history:
        for record in history:
            print(f"  游戏ID: {record['id']}, 获胜者: {record['winner_id']}, "
                  f"总奖池: {record['total_pot']}, 时间: {record['start_time']}")
    else:
        print("  暂无历史记录")

def show_rl_bot_status():
    """显示强化学习机器人状态"""
    print("\n" + "=" * 50)
    print("🤖 强化学习机器人状态")
    print("=" * 50)
    
    try:
        # 创建一个临时的RL机器人来查看状态
        temp_bot = RLBot("temp", "临时机器人", 1000)
        stats = temp_bot.get_learning_stats()
        
        print(f"Q表大小: {stats['q_table_size']} 个状态")
        print(f"总状态-动作对: {stats['total_states']}")
        print(f"当前探索率: {stats['epsilon']:.3f}")
        print(f"记忆大小: {stats['memory_size']} 条记录")
        
        # 显示学习数据
        from poker_game import GameDatabase
        db = GameDatabase()
        learning_data = db.get_bot_learning_data("rl_bot", limit=10)
        
        if learning_data:
            print(f"\n最近 {len(learning_data)} 条学习记录:")
            for i, data in enumerate(learning_data[:5], 1):
                print(f"  {i}. 动作: {data['action_taken']}, "
                      f"奖励: {data['reward']:.3f}, "
                      f"手牌强度: {data['hand_strength']:.3f}")
        else:
            print("\n暂无学习数据")
            
    except Exception as e:
        print(f"获取机器人状态失败: {e}")

def show_game_history():
    """显示游戏历史"""
    from poker_game import GameDatabase
    
    db = GameDatabase()
    
    print("\n" + "=" * 50)
    print("📚 游戏历史记录")
    print("=" * 50)
    
    history = db.get_game_history(limit=10)
    if history:
        for i, record in enumerate(history, 1):
            print(f"\n{i}. 游戏 #{record['id']}")
            print(f"   开始时间: {record['start_time']}")
            print(f"   结束时间: {record['end_time']}")
            print(f"   获胜者: {record['winner_id']}")
            print(f"   总奖池: {record['total_pot']}")
            print(f"   玩家数量: {record['players_count']}")
    else:
        print("暂无游戏历史记录")

def setup_auto_training_mode():
    """设置自动训练模式"""
    print("\n" + "=" * 60)
    print("🤖 强化学习机器人自动训练模式")
    print("=" * 60)
    
    print("在此模式下，多个机器人将自动对战来训练强化学习机器人")
    print("游戏将快速进行，无需人工干预")
    
    # 获取训练参数
    training_hands = get_training_hands_input()
    save_interval = get_save_interval_input()
    
    # 创建训练游戏
    game = PokerGame(small_blind=10, big_blind=20)
    
    # 添加强化学习机器人
    rl_bot_count = get_rl_bot_count_input()
    for i in range(rl_bot_count):
        rl_bot = RLBot(f"rl_bot_{i+1}", f"学习机器人{i+1}", 1000)
        game.add_player(rl_bot)
    
    # 添加其他机器人
    remaining_slots = 6 - rl_bot_count  # 最多6个玩家
    if remaining_slots > 0:
        print(f"\n添加 {remaining_slots} 个训练对手:")
        
        # 默认配置：平衡的对手组合
        bots_to_add = []
        if remaining_slots >= 1:
            bots_to_add.append(("简单机器人", EasyBot))
        if remaining_slots >= 2:
            bots_to_add.append(("中等机器人", MediumBot))
        if remaining_slots >= 3:
            bots_to_add.append(("困难机器人", HardBot))
        
        # 如果还有空位，添加更多不同难度的机器人
        while len(bots_to_add) < remaining_slots:
            bot_types = [("简单机器人", EasyBot), ("中等机器人", MediumBot), ("困难机器人", HardBot)]
            bots_to_add.append(bot_types[len(bots_to_add) % 3])
        
        # 只添加需要的数量
        for i, (name, bot_class) in enumerate(bots_to_add[:remaining_slots]):
            bot = bot_class(f"opponent_{i+1}", f"{name}{i+1}", 1000)
            game.add_player(bot)
            print(f"  添加: {name}{i+1}")
    
    print(f"\n🎯 训练配置:")
    print(f"  目标手牌数: {training_hands}")
    print(f"  模型保存间隔: 每 {save_interval} 手")
    print(f"  强化学习机器人数量: {rl_bot_count}")
    print(f"  总玩家数: {len(game.players)}")
    
    confirm = input(f"\n开始训练? (y/n): ").lower()
    if confirm in ['y', 'yes']:
        start_auto_training(game, training_hands, save_interval)
    else:
        print("训练已取消")

def setup_permanent_training_mode():
    """设置永久自动训练模式"""
    print("\n" + "=" * 60)
    print("🔄 永久自动训练模式")
    print("=" * 60)
    
    print("在此模式下，强化学习机器人将进行无限循环训练：")
    print("• 🔄 自动重开新局：当所有强化学习机器人没有筹码时自动重开")
    print("• 🗃️  自动数据清理：定期清理历史数据防止数据库过大")
    print("• 💾 定期模型保存：自动保存学习进度")
    print("• ⚡ 快速训练：无人工干预，最大化训练效率")
    print("• 📊 实时监控：显示训练进度和机器人状态")
    
    print("\n⚠️  注意：此模式将持续运行直到手动停止 (Ctrl+C)")
    
    # 获取训练参数
    save_interval = get_permanent_save_interval_input()
    cleanup_interval = get_cleanup_interval_input()
    rl_bot_count = get_rl_bot_count_input()
    
    print(f"\n🎯 永久训练配置:")
    print(f"  模型保存间隔: 每 {save_interval} 手")
    print(f"  数据清理间隔: 每 {cleanup_interval} 手")
    print(f"  强化学习机器人数量: {rl_bot_count}")
    print(f"  训练对手: 自动配置平衡组合")
    
    confirm = input(f"\n开始永久训练? (y/n): ").lower()
    if confirm in ['y', 'yes']:
        start_permanent_training(rl_bot_count, save_interval, cleanup_interval)
    else:
        print("永久训练已取消")

def get_training_hands_input():
    """获取训练手牌数输入"""
    while True:
        try:
            hands_input = input("目标训练手牌数 (默认: 1000): ").strip()
            if not hands_input:
                return 1000
            hands = int(hands_input)
            if hands > 0:
                return hands
            else:
                print("手牌数必须大于0")
        except ValueError:
            print("请输入有效的数字")

def get_save_interval_input():
    """获取模型保存间隔输入"""
    while True:
        try:
            interval_input = input("模型保存间隔 (每N手保存一次，默认: 10): ").strip()
            if not interval_input:
                return 10
            interval = int(interval_input)
            if interval > 0:
                return interval
            else:
                print("保存间隔必须大于0")
        except ValueError:
            print("请输入有效的数字")

def get_rl_bot_count_input():
    """获取强化学习机器人数量输入"""
    while True:
        try:
            count_input = input("强化学习机器人数量 (1-4，默认: 2): ").strip()
            if not count_input:
                return 2
            count = int(count_input)
            if 1 <= count <= 4:
                return count
            else:
                print("机器人数量必须在1-4之间")
        except ValueError:
            print("请输入有效的数字")

def start_auto_training(game, target_hands, save_interval):
    """开始自动训练"""
    import time
    from datetime import datetime
    from poker_game.database_cleaner import DatabaseCleaner
    
    print("\n" + "🚀" * 20 + " 开始自动训练 " + "🚀" * 20)
    print(f"训练开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查数据库大小，必要时自动清理
    print("\n🗃️  检查数据库状态...")
    cleaner = DatabaseCleaner()
    status = cleaner.check_database_status()
    
    if status.get('exists', False):
        print(f"📄 当前数据库: {status['file_size_mb']:.1f}MB, {status['total_records']:,}条记录")
        
        if status.get('needs_cleaning', False):
            print(f"⚠️  数据库需要清理，开始自动清理...")
            clean_result = cleaner.auto_clean_if_needed()
            
            if clean_result.get('cleaned', False):
                print(f"✅ 清理完成! 保留{clean_result['days_kept']}天数据")
                print(f"   清理了 {clean_result['total_cleaned']:,} 条记录")
                print(f"   清理后: {clean_result['after_size_mb']:.1f}MB, {clean_result['after_records']:,}条记录")
            else:
                print(f"ℹ️  {clean_result.get('reason', '无需清理')}")
        else:
            print(f"✅ 数据库状态良好，开始训练")
    
    # 设置游戏为训练模式（快速模式，无等待）
    game.training_mode = True
    game.game_start_time = datetime.now()
    
    start_time = time.time()
    last_rebalance_hand = 0
    
    try:
        while game.current_hand < target_hands:
            # 检查强化学习机器人是否还有筹码
            rl_bots_with_chips = [p for p in game.players if isinstance(p, RLBot) and p.chips > 0]
            if not rl_bots_with_chips:
                print(f"\n🚫 所有强化学习机器人都没有筹码了，训练结束 (第{game.current_hand}手)")
                print("   这表明当前训练策略可能需要调整")
                break
            
            # 检查是否还有足够的玩家继续游戏
            active_players = [p for p in game.players if p.chips > 0]
            if len(active_players) < 2:
                print(f"\n⚠️  玩家数量不足，重新分配筹码继续训练... (第{game.current_hand}手)")
                _rebalance_chips_for_training(game.players)
                active_players = game.players
                last_rebalance_hand = game.current_hand
            
            # 定期平衡筹码，防止筹码过度集中
            elif (game.current_hand - last_rebalance_hand) >= 50:
                total_chips = sum(p.chips for p in game.players)
                avg_chips = total_chips / len(game.players)
                max_chips = max(p.chips for p in game.players)
                min_chips = min(p.chips for p in game.players)
                
                # 如果筹码分配极不均衡，进行平衡
                if max_chips > avg_chips * 3 and min_chips < avg_chips * 0.3:
                    print(f"\n⚖️  筹码过度集中，进行平衡调整... (第{game.current_hand}手)")
                    print(f"   调整前 - 最高: {max_chips}, 最低: {min_chips}, 平均: {avg_chips:.0f}")
                    _rebalance_chips_for_training(game.players, partial_rebalance=True)
                    last_rebalance_hand = game.current_hand
            
            # 显示训练进度
            if game.current_hand % 10 == 0 and game.current_hand > 0:
                elapsed_time = time.time() - start_time
                progress = (game.current_hand / target_hands) * 100
                hands_per_second = game.current_hand / elapsed_time if elapsed_time > 0 else 0
                
                print(f"\n📊 训练进度: {game.current_hand}/{target_hands} "
                      f"({progress:.1f}%) - {hands_per_second:.2f} 手/秒")
                
                # 显示强化学习机器人状态
                rl_bots_active = 0
                for player in game.players:
                    if isinstance(player, RLBot):
                        stats = player.get_learning_stats()
                        status = "✅活跃" if player.chips > 0 else "❌淘汰"
                        print(f"  🤖 {player.name}: Q表={stats['q_table_size']}状态, "
                              f"ε={stats['epsilon']:.3f}, 筹码={player.chips} ({status})")
                        if player.chips > 0:
                            rl_bots_active += 1
                
                # 显示筹码分布情况
                total_chips = sum(p.chips for p in game.players)
                avg_chips = total_chips / len(game.players)
                print(f"  💰 筹码分布 - 总计: {total_chips}, 平均: {avg_chips:.0f}")
                print(f"  🤖 活跃强化学习机器人: {rl_bots_active}/{len([p for p in game.players if isinstance(p, RLBot)])}")
            
            # 保存模型
            if game.current_hand % save_interval == 0 and game.current_hand > 0:
                print(f"\n💾 保存模型... (第 {game.current_hand} 手)")
                for player in game.players:
                    if isinstance(player, RLBot):
                        player.save_model()
            
            # 如果达到目标，提前退出
            if game.current_hand >= target_hands:
                break
                
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
    
    # 训练完成
    end_time = time.time()
    training_duration = end_time - start_time
    
    print(f"\n" + "🎉" * 20 + " 训练完成 " + "🎉" * 20)
    print(f"总用时: {training_duration:.2f} 秒")
    print(f"完成手牌: {game.current_hand}")
    if training_duration > 0:
        print(f"平均速度: {game.current_hand/training_duration:.2f} 手/秒")
    
    # 最终保存所有模型
    print(f"\n💾 保存最终模型...")
    for player in game.players:
        if isinstance(player, RLBot):
            player.save_model()
            stats = player.get_learning_stats()
            status = "✅存活" if player.chips > 0 else "❌被淘汰"
            print(f"🤖 {player.name} 最终状态:")
            print(f"   Q表大小: {stats['q_table_size']} 状态")
            print(f"   探索率: {stats['epsilon']:.4f}")
            print(f"   最终筹码: {player.chips} ({status})")
    
    # 检查训练结果
    rl_bots_survived = len([p for p in game.players if isinstance(p, RLBot) and p.chips > 0])
    total_rl_bots = len([p for p in game.players if isinstance(p, RLBot)])
    
    if rl_bots_survived == 0:
        print(f"\n⚠️  训练结果: 所有强化学习机器人都被淘汰")
        print(f"   建议: 可能需要调整学习参数或增加训练数据")
    elif rl_bots_survived == total_rl_bots:
        print(f"\n🎉 训练结果: 所有强化学习机器人都存活下来！")
        print(f"   表现优秀: 学习策略有效")
    else:
        print(f"\n📊 训练结果: {rl_bots_survived}/{total_rl_bots} 强化学习机器人存活")
        print(f"   表现中等: 学习策略部分有效")
    
    print(f"\n✅ 训练完成！强化学习机器人已获得大量实战经验。")
    
    # 删除训练模式标记
    if hasattr(game, 'training_mode'):
        delattr(game, 'training_mode')

def _rebalance_chips_for_training(players, partial_rebalance=False):
    """为训练模式重新平衡筹码"""
    
    total_chips = sum(p.chips for p in players)
    target_chips_per_player = max(1000, total_chips // len(players))
    
    if partial_rebalance:
        # 部分平衡：只调整极端情况
        avg_chips = total_chips / len(players)
        for player in players:
            if player.chips > avg_chips * 2.5:
                # 过多筹码的玩家，减少到平均值的1.5倍
                excess = player.chips - int(avg_chips * 1.5)
                player.chips = int(avg_chips * 1.5)
                # 将多余筹码分配给筹码不足的玩家
                poor_players = [p for p in players if p.chips < avg_chips * 0.5]
                if poor_players:
                    bonus_per_player = excess // len(poor_players)
                    for poor_player in poor_players:
                        poor_player.chips += bonus_per_player
            elif player.chips < avg_chips * 0.3:
                # 筹码不足的玩家，补充到平均值的0.8倍
                player.chips = int(avg_chips * 0.8)
    else:
        # 完全重新分配
        print(f"   💰 筹码重新分配: 每人 {target_chips_per_player} 筹码")
        for player in players:
            # 强化学习机器人保留稍多筹码以继续学习
            if isinstance(player, RLBot):
                player.chips = int(target_chips_per_player * 1.2)
            else:
                player.chips = target_chips_per_player
    
    # 显示重分配后的状态
    print(f"   ✅ 重分配完成:")
    for player in players:
        player_type = "🤖" if isinstance(player, RLBot) else "🔧"
        print(f"      {player_type} {player.name}: {player.chips} 筹码")

def main():
    """主程序"""
    print("正在初始化德州扑克游戏...")
    
    current_game = None
    
    while True:
        show_game_menu()
        
        try:
            choice = int(input("\n请选择功能 (1-8): "))
            
            if choice == 1:
                # 开始新游戏
                try:
                    current_game = create_game_setup()
                    print("\n🎮 游戏即将开始...")
                    input("按回车键继续...")
                    current_game.start_game()
                except KeyboardInterrupt:
                    print("\n\n游戏被用户中断")
                except Exception as e:
                    print(f"\n游戏出现错误: {e}")
                    
            elif choice == 2:
                # 自动训练模式
                try:
                    setup_auto_training_mode()
                    input("\n按回车键继续...")
                except KeyboardInterrupt:
                    print("\n\n训练被用户中断")
                except Exception as e:
                    print(f"\n训练出现错误: {e}")
                    
            elif choice == 3:
                # 永久自动训练模式
                try:
                    setup_permanent_training_mode()
                    input("\n按回车键继续...")
                except KeyboardInterrupt:
                    print("\n\n训练被用户中断")
                except Exception as e:
                    print(f"\n训练出现错误: {e}")
                    
            elif choice == 4:
                # 查看游戏统计
                show_statistics(current_game if current_game else PokerGame())
                input("\n按回车键继续...")
                
            elif choice == 5:
                # 查看强化学习机器人状态
                show_rl_bot_status()
                input("\n按回车键继续...")
                
            elif choice == 6:
                # 查看游戏历史
                show_game_history()
                input("\n按回车键继续...")
                
            elif choice == 7:
                # 数据库管理
                try:
                    show_database_management()
                    input("\n按回车键继续...")
                except Exception as e:
                    print(f"\n数据库管理出现错误: {e}")
                    input("\n按回车键继续...")
                
            elif choice == 8:
                # 退出
                print("\n👋 感谢游玩德州扑克！再见！")
                break
                
            else:
                print("请输入有效的选择 (1-8)")
                
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n👋 游戏被中断，再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")

def show_database_management():
    """显示数据库管理界面"""
    from poker_game.database_cleaner import DatabaseCleaner
    
    cleaner = DatabaseCleaner()
    
    while True:
        print("\n" + "=" * 50)
        print("🗃️  数据库管理中心")
        print("=" * 50)
        print("1. 查看数据库状态")
        print("2. 清理旧数据")
        print("3. 自动清理（如果需要）")
        print("4. 设置清理阈值")
        print("5. 返回主菜单")
        print("=" * 50)
        
        try:
            choice = int(input("请选择操作 (1-5): "))
            
            if choice == 1:
                # 查看数据库状态
                print("\n正在检查数据库状态...")
                cleaner.print_status_report()
                
            elif choice == 2:
                # 手动清理数据
                days = get_cleanup_days_input()
                print(f"\n正在清理 {days} 天之前的数据...")
                result = cleaner.clean_old_data(days)
                
                if result['success']:
                    print(f"✅ 清理完成!")
                    print(f"清理的记录数:")
                    for table, count in result['cleaned_counts'].items():
                        if count > 0:
                            print(f"  {table}: {count:,} 条")
                    print(f"总计清理: {result['total_cleaned']:,} 条记录")
                    print(f"清理后大小: {result['after_size_mb']:.2f} MB")
                    print(f"清理后记录数: {result['after_records']:,}")
                else:
                    print(f"❌ 清理失败: {result.get('error', '未知错误')}")
                
            elif choice == 3:
                # 自动清理
                print("\n正在检查是否需要清理...")
                result = cleaner.auto_clean_if_needed()
                
                if result.get('cleaned', False):
                    print(f"✅ 自动清理完成!")
                    print(f"保留天数: {result['days_kept']}")
                    print(f"清理记录数: {result['total_cleaned']:,}")
                    print(f"清理后大小: {result['after_size_mb']:.2f} MB")
                    print(f"清理后记录数: {result['after_records']:,}")
                else:
                    print(f"ℹ️  {result.get('reason', '无需清理')}")
                
            elif choice == 4:
                # 设置清理阈值
                show_threshold_settings(cleaner)
                
            elif choice == 5:
                # 返回主菜单
                break
                
            else:
                print("请输入有效的选择 (1-5)")
                
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"操作失败: {e}")

def get_cleanup_days_input():
    """获取清理天数输入"""
    while True:
        try:
            days_input = input("保留最近多少天的数据? (默认: 30): ").strip()
            if not days_input:
                return 30
            days = int(days_input)
            if days > 0:
                return days
            else:
                print("天数必须大于0")
        except ValueError:
            print("请输入有效的数字")

def show_threshold_settings(cleaner):
    """显示阈值设置"""
    print("\n" + "=" * 50)
    print("⚙️  当前清理阈值设置")
    print("=" * 50)
    
    print("📄 文件大小阈值:")
    for level, size in cleaner.SIZE_THRESHOLDS.items():
        size_mb = size / (1024 * 1024)
        print(f"  {level}: {size_mb:.0f} MB")
    
    print("\n📊 记录数阈值:")
    for level, count in cleaner.RECORD_THRESHOLDS.items():
        print(f"  {level}: {count:,} 条")
    
    print(f"\n💡 清理策略 (针对强化学习训练优化):")
    print(f"  critical: 保留最近 3 天")
    print(f"  large: 保留最近 7 天")
    print(f"  medium: 保留最近 14 天")
    print(f"  small: 无需清理")
    
    print(f"\n注: 阈值已针对强化学习训练优化，数据库超过10MB时自动清理")

def get_permanent_save_interval_input():
    """获取永久训练模式的模型保存间隔输入"""
    while True:
        try:
            interval_input = input("模型保存间隔 (每N手保存一次，默认: 50): ").strip()
            if not interval_input:
                return 50
            interval = int(interval_input)
            if interval > 0:
                return interval
            else:
                print("保存间隔必须大于0")
        except ValueError:
            print("请输入有效的数字")

def get_cleanup_interval_input():
    """获取数据清理间隔输入"""
    while True:
        try:
            interval_input = input("数据清理间隔 (每N手清理一次，默认: 1000): ").strip()
            if not interval_input:
                return 1000
            interval = int(interval_input)
            if interval > 0:
                return interval
            else:
                print("清理间隔必须大于0")
        except ValueError:
            print("请输入有效的数字")

def start_permanent_training(rl_bot_count, save_interval, cleanup_interval):
    """开始永久自动训练"""
    import time
    from datetime import datetime
    from poker_game.database_cleaner import DatabaseCleaner
    
    print("\n" + "🚀" * 20 + " 开始永久自动训练 " + "🚀" * 20)
    print(f"训练开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("按 Ctrl+C 停止训练")
    
    # 初始化统计数据
    total_hands_played = 0
    total_games_played = 0
    training_start_time = time.time()
    last_cleanup_hand = 0
    
    # 数据库清理器
    cleaner = DatabaseCleaner()
    
    try:
        while True:  # 永久循环
            total_games_played += 1
            print(f"\n{'🎮' * 15} 第 {total_games_played} 局游戏开始 {'🎮' * 15}")
            
            # 创建新游戏
            game = _create_training_game(rl_bot_count)
            game.training_mode = True
            game.game_start_time = datetime.now()
            
            # 游戏循环
            game_hands = 0
            while True:
                # 检查强化学习机器人是否还有筹码
                rl_bots_with_chips = [p for p in game.players if isinstance(p, RLBot) and p.chips > 0]
                if not rl_bots_with_chips:
                    print(f"\n🔄 所有强化学习机器人没有筹码，准备重开新局...")
                    print(f"   本局完成 {game_hands} 手牌")
                    break
                
                # 检查是否还有足够的玩家继续游戏
                active_players = [p for p in game.players if p.chips > 0]
                if len(active_players) < 2:
                    print(f"\n⚖️  玩家数量不足，重新分配筹码...")
                    _rebalance_chips_for_training(game.players)
                
                # 显示训练进度
                if total_hands_played % 100 == 0 and total_hands_played > 0:
                    elapsed_time = time.time() - training_start_time
                    hands_per_second = total_hands_played / elapsed_time if elapsed_time > 0 else 0
                    
                    print(f"\n📊 永久训练进度:")
                    print(f"   总手牌数: {total_hands_played:,}")
                    print(f"   总游戏局数: {total_games_played}")
                    print(f"   当前局手牌: {game_hands}")
                    print(f"   训练速度: {hands_per_second:.2f} 手/秒")
                    print(f"   运行时长: {elapsed_time/3600:.1f} 小时")
                    
                    # 显示强化学习机器人状态
                    rl_bots_active = 0
                    for player in game.players:
                        if isinstance(player, RLBot):
                            stats = player.get_learning_stats()
                            status = "✅" if player.chips > 0 else "❌"
                            print(f"   🤖 {player.name}: Q表={stats['q_table_size']}, "
                                  f"ε={stats['epsilon']:.3f}, 筹码={player.chips} {status}")
                            if player.chips > 0:
                                rl_bots_active += 1
                    
                    print(f"   🤖 活跃RL机器人: {rl_bots_active}/{rl_bot_count}")
                
                # 保存模型
                if total_hands_played % save_interval == 0 and total_hands_played > 0:
                    print(f"\n💾 保存模型... (总计 {total_hands_played:,} 手)")
                    for player in game.players:
                        if isinstance(player, RLBot):
                            player.save_model()
                
                # 定期清理数据库
                if (total_hands_played - last_cleanup_hand) >= cleanup_interval and total_hands_played > 0:
                    print(f"\n🗃️  执行数据库清理... (总计 {total_hands_played:,} 手)")
                    try:
                        result = cleaner.auto_clean_for_training(target_size_mb=10.0)
                        if result.get('cleaned', False):
                            print(f"   ✅ 清理完成: 清理了 {result['total_cleaned']:,} 条记录")
                            print(f"   📄 清理前: {result['before_size_mb']:.1f}MB → 清理后: {result['after_size_mb']:.1f}MB")
                            print(f"   📊 记录数: {result['before_records']:,} → {result['after_records']:,}")
                        else:
                            print(f"   ℹ️  {result.get('reason', '无需清理')}")
                        last_cleanup_hand = total_hands_played
                    except Exception as e:
                        print(f"   ⚠️  数据库清理失败: {e}")
                
                # 额外检查：如果数据库超过10MB，立即清理（不等清理间隔）
                if total_hands_played % 50 == 0:  # 每50手检查一次
                    try:
                        status = cleaner.check_database_status()
                        if status.get('exists', False) and status['file_size_mb'] > 10.0:
                            print(f"\n🚨 数据库超过10MB ({status['file_size_mb']:.1f}MB)，立即清理...")
                            result = cleaner.auto_clean_for_training(target_size_mb=10.0)
                            if result.get('cleaned', False):
                                print(f"   ✅ 紧急清理完成: {result['before_size_mb']:.1f}MB → {result['after_size_mb']:.1f}MB")
                                print(f"   📊 清理了 {result['total_cleaned']:,} 条记录")
                                last_cleanup_hand = total_hands_played  # 更新清理时间
                    except Exception as e:
                        print(f"   ⚠️  紧急清理失败: {e}")
                
                # 继续下一手
                try:
                    game._play_hand()
                    game.current_hand += 1
                    game_hands += 1
                    total_hands_played += 1
                    game._move_dealer_button()
                except Exception as e:
                    print(f"手牌 {game_hands} 出现错误: {e}")
                    # 重置状态继续
                    for player in game.players:
                        player.reset_for_new_hand()
                    game.current_hand += 1
                    game_hands += 1
                    total_hands_played += 1
                    continue
            
            # 本局结束，保存模型
            print(f"\n💾 第 {total_games_played} 局结束，保存模型...")
            for player in game.players:
                if isinstance(player, RLBot):
                    player.save_model()
            
            # 短暂休息，防止CPU过载
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  永久训练被用户中断")
        print(f"📊 训练统计:")
        print(f"   总手牌数: {total_hands_played:,}")
        print(f"   总游戏局数: {total_games_played}")
        elapsed_time = time.time() - training_start_time
        print(f"   总训练时长: {elapsed_time/3600:.1f} 小时")
        if elapsed_time > 0:
            print(f"   平均速度: {total_hands_played/elapsed_time:.2f} 手/秒")
        
        # 最终保存所有模型
        print(f"\n💾 保存最终模型...")
        # 由于游戏可能已经结束，我们需要创建临时机器人来保存模型
        for i in range(rl_bot_count):
            temp_bot = RLBot(f"rl_bot_{i+1}", f"学习机器人{i+1}", 1000)
            temp_bot.save_model()
            stats = temp_bot.get_learning_stats()
            print(f"🤖 学习机器人{i+1} 最终状态:")
            print(f"   Q表大小: {stats['q_table_size']} 状态")
            print(f"   探索率: {stats['epsilon']:.4f}")
    
    except Exception as e:
        print(f"\n❌ 永久训练出现错误: {e}")
        print(f"📊 训练统计 (错误前):")
        print(f"   总手牌数: {total_hands_played:,}")
        print(f"   总游戏局数: {total_games_played}")
    
    print(f"\n✅ 永久训练结束！")

def _create_training_game(rl_bot_count):
    """创建训练游戏"""
    game = PokerGame(small_blind=10, big_blind=20)
    
    # 添加强化学习机器人
    for i in range(rl_bot_count):
        rl_bot = RLBot(f"rl_bot_{i+1}", f"学习机器人{i+1}", 1000)
        game.add_player(rl_bot)
    
    # 添加其他机器人
    remaining_slots = 6 - rl_bot_count  # 最多6个玩家
    if remaining_slots > 0:
        # 默认配置：平衡的对手组合
        bots_to_add = []
        if remaining_slots >= 1:
            bots_to_add.append(("简单机器人", EasyBot))
        if remaining_slots >= 2:
            bots_to_add.append(("中等机器人", MediumBot))
        if remaining_slots >= 3:
            bots_to_add.append(("困难机器人", HardBot))
        
        # 如果还有空位，添加更多不同难度的机器人
        while len(bots_to_add) < remaining_slots:
            bot_types = [("简单机器人", EasyBot), ("中等机器人", MediumBot), ("困难机器人", HardBot)]
            bots_to_add.append(bot_types[len(bots_to_add) % 3])
        
        # 只添加需要的数量
        for i, (name, bot_class) in enumerate(bots_to_add[:remaining_slots]):
            bot = bot_class(f"opponent_{i+1}", f"{name}{i+1}", 1000)
            game.add_player(bot)
    
    return game

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序出现严重错误: {e}")
        sys.exit(1) 