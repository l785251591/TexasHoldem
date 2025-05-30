#!/usr/bin/env python3
"""
德州扑克游戏主程序
演示人类玩家与不同智力水平的机器人对战

目录结构:
- poker_game/: 核心游戏引擎
- models/: 强化学习模型文件
- data/: 数据库和历史数据
- docs/: 文档文件
- tests/: 测试文件
- scripts/: 工具脚本
"""

import sys
import os
from poker_game import PokerGame, HumanPlayer, EasyBot, MediumBot, HardBot, RLBot, ImprovedRLBot, ConservativeRLBot, TrainingTracker

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
    
    # 询问使用哪种强化学习机器人
    print("\n选择强化学习机器人类型:")
    print("1. 原版强化学习机器人")
    print("2. 🚀 改进版强化学习机器人")
    print("3. 🛡️  保守版强化学习机器人 (训练专用，推荐)")
    
    while True:
        try:
            rl_choice = int(input("请选择 (1-3, 默认: 3): ") or "3")
            if rl_choice in [1, 2, 3]:
                break
            else:
                print("请输入有效的选择 (1-3)")
        except ValueError:
            print("请输入有效的数字")
    
    if rl_choice == 1:
        rl_bot = RLBot("rl_bot", "原版学习机器人", 1000)
    elif rl_choice == 2:
        rl_bot = ImprovedRLBot("improved_rl_bot", "🚀改进学习机器人", 1000)
    else:
        rl_bot = ConservativeRLBot("conservative_rl_bot", "🛡️保守学习机器人", 1000)
    
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
        "4": ("原版强化学习机器人", RLBot),
        "5": ("🚀改进强化学习机器人", ImprovedRLBot),
        "6": ("🛡️保守强化学习机器人", ConservativeRLBot)
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
                    bot_type = input("选择机器人类型 (1-6): ")
                    if bot_type in bot_types:
                        break
                    else:
                        print("请输入有效的选择 (1-6)")
                except:
                    print("请输入有效的数字")
            
            name, bot_class = bot_types[bot_type]
            bot_count += 1
            bot_name = f"{name}_{bot_count}"
            chips = get_chips_input(f"请输入{name}的初始筹码 (默认: 1000): ", 1000)
            
            if bot_class in [RLBot, ImprovedRLBot, ConservativeRLBot]:
                bot = bot_class(f"bot_{bot_count}", bot_name, chips)
            else:
                bot = bot_class(f"bot_{bot_count}", bot_name, chips)
            
            game.add_player(bot)
    
    if len(game.players) < 2:
        print("至少需要2个玩家，自动添加一个保守的强化学习机器人...")
        game.add_player(ConservativeRLBot("auto_bot", "🛡️自动保守机器人", 1000))
    
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
    print("6. 📈 查看训练进步过程 (新功能)")
    print("7. 查看游戏历史")
    print("8. 🗃️  数据库管理")
    print("9. 退出")
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
        # 检查原版机器人
        print("📊 原版强化学习机器人:")
        temp_bot = RLBot("temp", "临时机器人", 1000)
        stats = temp_bot.get_learning_stats()
        
        print(f"  Q表大小: {stats['q_table_size']} 个状态")
        print(f"  总状态-动作对: {stats['total_states']}")
        print(f"  当前探索率: {stats['epsilon']:.3f}")
        print(f"  记忆大小: {stats['memory_size']} 条记录")
        
        # 检查改进版机器人
        print("\n🚀 改进版强化学习机器人:")
        improved_bot = ImprovedRLBot("temp_improved", "临时改进机器人", 1000)
        improved_stats = improved_bot.get_learning_stats()
        
        print(f"  Q表大小: {improved_stats['q_table_size']} 个状态")
        print(f"  总状态-动作对: {improved_stats['total_states']}")
        print(f"  当前探索率: {improved_stats['epsilon']:.3f}")
        print(f"  经验缓冲: {improved_stats['memory_size']} 条记录")
        print(f"  游戏次数: {improved_stats['game_count']}")
        print(f"  胜率: {improved_stats['win_rate']:.1%}")
        print(f"  平均奖励: {improved_stats['avg_reward']:.3f}")
        
        # 检查保守版机器人
        print("\n🛡️  保守版强化学习机器人:")
        conservative_bot = ConservativeRLBot("temp_conservative", "临时保守机器人", 1000)
        conservative_stats = conservative_bot.get_learning_stats()
        
        print(f"  Q表大小: {conservative_stats['q_table_size']} 个状态")
        print(f"  总状态-动作对: {conservative_stats['total_states']}")
        print(f"  当前探索率: {conservative_stats['epsilon']:.3f}")
        print(f"  经验缓冲: {conservative_stats['memory_size']} 条记录")
        print(f"  游戏次数: {conservative_stats['game_count']}")
        print(f"  胜率: {conservative_stats['win_rate']:.1%}")
        print(f"  平均奖励: {conservative_stats['avg_reward']:.3f}")
        print(f"  保守模式: {'开启' if conservative_stats.get('conservative_mode', False) else '关闭'}")
        print(f"  激进阈值: {conservative_stats.get('aggression_threshold', 0.8)}")
        print(f"  最大下注比例: {conservative_stats.get('max_bet_ratio', 0.2)*100:.0f}%")
        
        # 显示学习数据
        from poker_game import GameDatabase
        db = GameDatabase()
        learning_data = db.get_bot_learning_data("rl_bot", limit=5)
        improved_learning_data = db.get_bot_learning_data("improved_rl_bot", limit=5)
        
        if learning_data:
            print(f"\n原版机器人最近 {len(learning_data)} 条学习记录:")
            for i, data in enumerate(learning_data, 1):
                print(f"  {i}. 动作: {data['action_taken']}, "
                      f"奖励: {data['reward']:.3f}, "
                      f"手牌强度: {data['hand_strength']:.3f}")
        
        if improved_learning_data:
            print(f"\n改进版机器人最近 {len(improved_learning_data)} 条学习记录:")
            for i, data in enumerate(improved_learning_data, 1):
                print(f"  {i}. 动作: {data['action_taken']}, "
                      f"奖励: {data['reward']:.3f}, "
                      f"手牌强度: {data['hand_strength']:.3f}")
        
        if not learning_data and not improved_learning_data:
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
    
    # 选择训练的机器人类型
    print("\n选择要训练的强化学习机器人类型:")
    print("1. 原版强化学习机器人")
    print("2. 🚀 改进版强化学习机器人 (推荐)")
    print("3. 🛡️ 保守版强化学习机器人 (稳健训练)")
    print("4. 对比学习 (原版 vs 改进版)")
    print("5. 混合训练 (原版+改进版+保守版)")
    
    while True:
        try:
            rl_type = int(input("请选择 (1-5, 默认: 2): ") or "2")
            if rl_type in [1, 2, 3, 4, 5]:
                break
            else:
                print("请输入有效的选择 (1-5)")
        except ValueError:
            print("请输入有效的数字")
    
    # 获取训练参数
    training_hands = get_training_hands_input()
    save_interval = get_save_interval_input()
    
    # 创建训练游戏
    game = PokerGame(small_blind=10, big_blind=20)
    
    # 添加强化学习机器人
    rl_bot_count = get_rl_bot_count_input()
    for i in range(rl_bot_count):
        if rl_type == 1:
            rl_bot = RLBot(f"rl_bot_{i+1}", f"原版学习机器人{i+1}", 1000)
        elif rl_type == 2:
            rl_bot = ImprovedRLBot(f"improved_rl_bot_{i+1}", f"🚀改进学习机器人{i+1}", 1000)
        elif rl_type == 3:
            rl_bot = ConservativeRLBot(f"conservative_rl_bot_{i+1}", f"🛡️保守学习机器人{i+1}", 1000)
        elif rl_type == 4:  # 对比学习 (原版 vs 改进版)
            if i % 2 == 0:
                rl_bot = ImprovedRLBot(f"improved_rl_bot_{i+1}", f"🚀改进学习机器人{i+1}", 1000)
            else:
                rl_bot = RLBot(f"rl_bot_{i+1}", f"原版学习机器人{i+1}", 1000)
        else:  # rl_type == 5, 混合训练 (三种都训练)
            if i % 3 == 0:
                rl_bot = ImprovedRLBot(f"improved_rl_bot_{i+1}", f"🚀改进学习机器人{i+1}", 1000)
            elif i % 3 == 1:
                rl_bot = RLBot(f"rl_bot_{i+1}", f"原版学习机器人{i+1}", 1000)
            else:
                rl_bot = ConservativeRLBot(f"conservative_rl_bot_{i+1}", f"🛡️保守学习机器人{i+1}", 1000)
        
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
    if rl_type == 1:
        print(f"  训练类型: 原版强化学习机器人")
    elif rl_type == 2:
        print(f"  训练类型: 🚀 改进版强化学习机器人")
    elif rl_type == 3:
        print(f"  训练类型: 🛡️ 保守版强化学习机器人")
    elif rl_type == 4:
        print(f"  训练类型: 对比训练 (原版 vs 改进版)")
    else:
        print(f"  训练类型: 混合训练 (三种机器人)")
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
    
    # 选择机器人类型
    print("\n选择要训练的强化学习机器人类型:")
    print("1. 🤖 原版强化学习机器人")
    print("2. 🚀 改进版强化学习机器人 (推荐)")
    print("3. 🛡️  保守版强化学习机器人 (稳健训练)")
    print("4. 🔄 混合训练 (原版+改进版)")
    print("5. 🎯 全类型训练 (三种机器人同时)")
    
    while True:
        try:
            bot_type_choice = int(input("\n请选择机器人类型 (1-5): "))
            if 1 <= bot_type_choice <= 5:
                break
            else:
                print("请输入 1-5 之间的数字")
        except ValueError:
            print("请输入有效的数字")
    
    # 获取其他训练参数
    save_interval = get_permanent_save_interval_input()
    cleanup_interval = get_cleanup_interval_input()
    rl_bot_count = get_rl_bot_count_input()
    
    # 显示配置信息
    bot_type_names = {
        1: "原版强化学习机器人",
        2: "改进版强化学习机器人",
        3: "保守版强化学习机器人",
        4: "混合训练 (原版+改进版)",
        5: "全类型训练 (三种机器人)"
    }
    
    print(f"\n🎯 永久训练配置:")
    print(f"  机器人类型: {bot_type_names[bot_type_choice]}")
    print(f"  强化学习机器人数量: {rl_bot_count}")
    print(f"  模型保存间隔: 每 {save_interval} 手")
    print(f"  数据清理间隔: 每 {cleanup_interval} 手")
    print(f"  训练对手: 自动配置平衡组合")
    
    confirm = input(f"\n开始永久训练? (y/n): ").lower()
    if confirm in ['y', 'yes']:
        start_permanent_training(rl_bot_count, save_interval, cleanup_interval, bot_type_choice)
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
            rl_bots_with_chips = [p for p in game.players if isinstance(p, (RLBot, ImprovedRLBot, ConservativeRLBot)) and p.chips > 0]
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
                    if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
                        stats = player.get_learning_stats()
                        status = "✅活跃" if player.chips > 0 else "❌淘汰"
                        
                        if isinstance(player, ConservativeRLBot):
                            bot_type = "🛡️保守"
                            print(f"  🛡️ {player.name}: Q表={stats['q_table_size']}状态, "
                                  f"ε={stats['epsilon']:.3f}, 胜率={stats['win_rate']:.1%}, "
                                  f"筹码={player.chips} ({status})")
                        elif isinstance(player, ImprovedRLBot):
                            bot_type = "🚀改进"
                            print(f"  🚀 {player.name}: Q表={stats['q_table_size']}状态, "
                                  f"ε={stats['epsilon']:.3f}, 胜率={stats['win_rate']:.1%}, "
                                  f"筹码={player.chips} ({status})")
                        else:
                            bot_type = "🤖原版"
                            print(f"  🤖 {player.name}: Q表={stats['q_table_size']}状态, "
                                  f"ε={stats['epsilon']:.3f}, 筹码={player.chips} ({status})")
                        
                        if player.chips > 0:
                            rl_bots_active += 1
                
                # 显示筹码分布情况
                total_chips = sum(p.chips for p in game.players)
                avg_chips = total_chips / len(game.players)
                print(f"  💰 筹码分布 - 总计: {total_chips}, 平均: {avg_chips:.0f}")
                print(f"  🤖 活跃强化学习机器人: {rl_bots_active}/{len([p for p in game.players if isinstance(p, (RLBot, ImprovedRLBot, ConservativeRLBot))])}")
            
            # 保存模型
            if game.current_hand % save_interval == 0 and game.current_hand > 0:
                print(f"\n💾 保存模型... (第 {game.current_hand} 手)")
                for player in game.players:
                    if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
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
    
    # 最终保存所有模型和显示统计
    print(f"\n💾 保存最终模型...")
    # 如果游戏还在进行，直接保存当前玩家的模型
    if 'game' in locals() and hasattr(game, 'players'):
        for player in game.players:
            if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
                try:
                    player.save_model()
                    stats = player.get_learning_stats()
                    if isinstance(player, ConservativeRLBot):
                        bot_type = "🛡️保守版"
                    elif isinstance(player, ImprovedRLBot):
                        bot_type = "🚀改进版"
                    else:
                        bot_type = "🤖原版"
                    print(f"{bot_type} {player.name} 最终状态:")
                    print(f"   Q表大小: {stats['q_table_size']} 状态")
                    print(f"   探索率: {stats['epsilon']:.4f}")
                except Exception as save_error:
                    print(f"   ⚠️  保存 {player.name} 失败: {save_error}")
    else:
        # 游戏已经结束，根据机器人类型创建临时机器人来保存最新状态
        bot_types_to_save = []
        if bot_type_choice == 1:  # 原版
            bot_types_to_save = [('rl_bot', RLBot, '🤖原版')]
        elif bot_type_choice == 2:  # 改进版
            bot_types_to_save = [('improved_rl_bot', ImprovedRLBot, '🚀改进版')]
        elif bot_type_choice == 3:  # 保守版
            bot_types_to_save = [('conservative_rl_bot', ConservativeRLBot, '🛡️保守版')]
        elif bot_type_choice == 4:  # 混合训练 (原版+改进版)
            bot_types_to_save = [('rl_bot', RLBot, '🤖原版'), ('improved_rl_bot', ImprovedRLBot, '🚀改进版')]
        elif bot_type_choice == 5:  # 全类型训练
            bot_types_to_save = [('rl_bot', RLBot, '🤖原版'), ('improved_rl_bot', ImprovedRLBot, '🚀改进版'), ('conservative_rl_bot', ConservativeRLBot, '🛡️保守版')]
        
        for bot_id, bot_class, bot_name in bot_types_to_save:
            try:
                temp_bot = bot_class(f"{bot_id}_temp", f"临时{bot_name}机器人", 1000)
                temp_bot.save_model()
                stats = temp_bot.get_learning_stats()
                print(f"{bot_name} 最终状态:")
                print(f"   Q表大小: {stats['q_table_size']} 状态")
                print(f"   探索率: {stats['epsilon']:.4f}")
            except Exception as save_error:
                print(f"   ⚠️  保存{bot_name}失败: {save_error}")
    
    # 检查训练结果
    rl_bots_survived = len([p for p in game.players if isinstance(p, (RLBot, ImprovedRLBot, ConservativeRLBot)) and p.chips > 0])
    total_rl_bots = len([p for p in game.players if isinstance(p, (RLBot, ImprovedRLBot, ConservativeRLBot))])
    
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
    import math
    
    # 安全检查：防止数值溢出
    MAX_SAFE_CHIPS = 10**12  # 1万亿筹码上限
    
    # 检查和修复异常筹码值
    for player in players:
        if not isinstance(player.chips, (int, float)) or math.isinf(player.chips) or math.isnan(player.chips):
            print(f"   ⚠️ 检测到异常筹码值: {player.name} = {player.chips}，重置为1000")
            player.chips = 1000
        elif player.chips > MAX_SAFE_CHIPS:
            print(f"   ⚠️ 检测到过大筹码值: {player.name} = {player.chips}，限制到{MAX_SAFE_CHIPS}")
            player.chips = MAX_SAFE_CHIPS
        elif player.chips < 0:
            print(f"   ⚠️ 检测到负筹码值: {player.name} = {player.chips}，重置为1000")
            player.chips = 1000
    
    # 重新计算总筹码
    total_chips = sum(p.chips for p in players)
    
    # 防止总筹码异常
    if total_chips <= 0 or total_chips > MAX_SAFE_CHIPS * len(players):
        print(f"   ⚠️ 总筹码异常 ({total_chips})，重置所有玩家筹码")
        for player in players:
            player.chips = 1000
        total_chips = 1000 * len(players)
    
    target_chips_per_player = max(1000, min(total_chips // len(players), MAX_SAFE_CHIPS))
    
    if partial_rebalance:
        # 部分平衡：只调整极端情况
        avg_chips = total_chips / len(players)
        
        # 确保平均筹码是合理的
        if avg_chips > MAX_SAFE_CHIPS or avg_chips <= 0:
            avg_chips = 1000
        
        for player in players:
            if player.chips > avg_chips * 2.5:
                # 过多筹码的玩家，减少到平均值的1.5倍
                excess = player.chips - int(avg_chips * 1.5)
                player.chips = int(avg_chips * 1.5)
                # 将多余筹码分配给筹码不足的玩家
                poor_players = [p for p in players if p.chips < avg_chips * 0.5]
                if poor_players and excess > 0:
                    bonus_per_player = min(excess // len(poor_players), int(avg_chips * 0.5))
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
            if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
                player.chips = int(target_chips_per_player * 1.2)
            else:
                player.chips = target_chips_per_player
    
    # 最终安全检查
    for player in players:
        if player.chips > MAX_SAFE_CHIPS:
            player.chips = MAX_SAFE_CHIPS
        elif player.chips < 0:
            player.chips = 1000
    
    # 显示重分配后的状态
    print(f"   ✅ 重分配完成:")
    for player in players:
        if isinstance(player, ConservativeRLBot):
            player_type = "🛡️"
        elif isinstance(player, ImprovedRLBot):
            player_type = "🚀"
        elif isinstance(player, RLBot):
            player_type = "🤖"
        else:
            player_type = "🔧"
        print(f"      {player_type} {player.name}: {player.chips:,} 筹码")

def main():
    """主程序"""
    print("正在初始化德州扑克游戏...")
    
    current_game = None
    
    while True:
        show_game_menu()
        
        try:
            choice = int(input("\n请选择功能 (1-9): "))
            
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
                # 查看训练进步过程
                show_training_progress()
                input("\n按回车键继续...")
                
            elif choice == 7:
                # 查看游戏历史
                show_game_history()
                input("\n按回车键继续...")
                
            elif choice == 8:
                # 数据库管理
                try:
                    show_database_management()
                    input("\n按回车键继续...")
                except Exception as e:
                    print(f"\n数据库管理出现错误: {e}")
                    input("\n按回车键继续...")
                
            elif choice == 9:
                # 退出
                print("\n👋 感谢游玩德州扑克！再见！")
                break
                
            else:
                print("请输入有效的选择 (1-9)")
                
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

def start_permanent_training(rl_bot_count, save_interval, cleanup_interval, bot_type_choice):
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
            game = _create_training_game(rl_bot_count, bot_type_choice)
            game.training_mode = True
            game.game_start_time = datetime.now()
            
            # 游戏循环
            game_hands = 0
            while True:
                # 检查强化学习机器人是否还有筹码
                rl_bots_with_chips = [p for p in game.players 
                                    if isinstance(p, (RLBot, ImprovedRLBot, ConservativeRLBot)) and p.chips > 0]
                if not rl_bots_with_chips:
                    print(f"\n🔄 所有强化学习机器人没有筹码，准备重开新局...")
                    print(f"   本局完成 {game_hands} 手牌")
                    break
                
                # 检查是否还有足够的玩家继续游戏
                active_players = [p for p in game.players if p.chips > 0]
                if len(active_players) < 2:
                    print(f"\n⚖️  玩家数量不足，重新分配筹码...")
                    _rebalance_chips_for_training(game.players)
                
                # 显示训练状态（每1000手显示一次详细状态）
                if total_hands_played % 1000 == 0:
                    print(f"\n📊 训练状态报告 (累计 {total_hands_played:,} 手牌):")
                    rl_bots_active = 0
                    for player in game.players:
                        if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
                            stats = player.get_learning_stats()
                            status = "✅" if player.chips > 0 else "❌"
                            
                            # 根据机器人类型显示不同图标
                            if isinstance(player, ConservativeRLBot):
                                bot_icon = "🛡️"
                            elif isinstance(player, ImprovedRLBot):
                                bot_icon = "🚀"
                            else:  # RLBot
                                bot_icon = "🤖"
                            
                            print(f"   {bot_icon} {player.name}: Q表={stats['q_table_size']}, "
                                  f"ε={stats['epsilon']:.3f}, 筹码={player.chips} {status}")
                            if player.chips > 0:
                                rl_bots_active += 1
                    
                    print(f"   🤖 活跃RL机器人: {rl_bots_active}/{rl_bot_count}")
                
                # 保存模型
                if total_hands_played % save_interval == 0 and total_hands_played > 0:
                    print(f"\n💾 保存模型... (总计 {total_hands_played:,} 手)")
                    for player in game.players:
                        if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
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
                if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
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
        # 如果游戏还在进行，直接保存当前玩家的模型
        if 'game' in locals() and hasattr(game, 'players'):
            for player in game.players:
                if isinstance(player, (RLBot, ImprovedRLBot, ConservativeRLBot)):
                    try:
                        player.save_model()
                        stats = player.get_learning_stats()
                        if isinstance(player, ConservativeRLBot):
                            bot_type = "🛡️保守版"
                        elif isinstance(player, ImprovedRLBot):
                            bot_type = "🚀改进版"
                        else:
                            bot_type = "🤖原版"
                        print(f"{bot_type} {player.name} 最终状态:")
                        print(f"   Q表大小: {stats['q_table_size']} 状态")
                        print(f"   探索率: {stats['epsilon']:.4f}")
                    except Exception as save_error:
                        print(f"   ⚠️  保存 {player.name} 失败: {save_error}")
        else:
            # 游戏已经结束，根据机器人类型创建临时机器人来保存最新状态
            bot_types_to_save = []
            if bot_type_choice == 1:  # 原版
                bot_types_to_save = [('rl_bot', RLBot, '🤖原版')]
            elif bot_type_choice == 2:  # 改进版
                bot_types_to_save = [('improved_rl_bot', ImprovedRLBot, '🚀改进版')]
            elif bot_type_choice == 3:  # 保守版
                bot_types_to_save = [('conservative_rl_bot', ConservativeRLBot, '🛡️保守版')]
            elif bot_type_choice == 4:  # 混合训练 (原版+改进版)
                bot_types_to_save = [('rl_bot', RLBot, '🤖原版'), ('improved_rl_bot', ImprovedRLBot, '🚀改进版')]
            elif bot_type_choice == 5:  # 全类型训练
                bot_types_to_save = [('rl_bot', RLBot, '🤖原版'), ('improved_rl_bot', ImprovedRLBot, '🚀改进版'), ('conservative_rl_bot', ConservativeRLBot, '🛡️保守版')]
            
            for bot_id, bot_class, bot_name in bot_types_to_save:
                try:
                    temp_bot = bot_class(f"{bot_id}_temp", f"临时{bot_name}机器人", 1000)
                    temp_bot.save_model()
                    stats = temp_bot.get_learning_stats()
                    print(f"{bot_name} 最终状态:")
                    print(f"   Q表大小: {stats['q_table_size']} 状态")
                    print(f"   探索率: {stats['epsilon']:.4f}")
                except Exception as save_error:
                    print(f"   ⚠️  保存{bot_name}失败: {save_error}")
    
    except Exception as e:
        print(f"\n❌ 永久训练出现错误: {e}")
        print(f"📊 训练统计 (错误前):")
        print(f"   总手牌数: {total_hands_played:,}")
        print(f"   总游戏局数: {total_games_played}")
    
    print(f"\n✅ 永久训练结束！")

def _create_training_game(rl_bot_count, bot_type_choice):
    """创建训练游戏"""
    game = PokerGame(small_blind=10, big_blind=20)
    
    # 根据选择创建不同类型的强化学习机器人
    if bot_type_choice == 1:  # 原版强化学习机器人
        for i in range(rl_bot_count):
            rl_bot = RLBot(f"rl_bot_{i+1}", f"原版学习机器人{i+1}", 1000)
            game.add_player(rl_bot)
    
    elif bot_type_choice == 2:  # 改进版强化学习机器人
        for i in range(rl_bot_count):
            rl_bot = ImprovedRLBot(f"improved_rl_bot_{i+1}", f"🚀改进版机器人{i+1}", 1000)
            game.add_player(rl_bot)
    
    elif bot_type_choice == 3:  # 保守版强化学习机器人
        for i in range(rl_bot_count):
            rl_bot = ConservativeRLBot(f"conservative_rl_bot_{i+1}", f"🛡️保守版机器人{i+1}", 1000)
            game.add_player(rl_bot)
    
    elif bot_type_choice == 4:  # 混合训练 (原版+改进版)
        # 平均分配两种类型
        original_count = rl_bot_count // 2
        improved_count = rl_bot_count - original_count
        
        for i in range(original_count):
            rl_bot = RLBot(f"rl_bot_{i+1}", f"原版机器人{i+1}", 1000)
            game.add_player(rl_bot)
        
        for i in range(improved_count):
            rl_bot = ImprovedRLBot(f"improved_rl_bot_{i+1}", f"🚀改进版机器人{i+1}", 1000)
            game.add_player(rl_bot)
    
    elif bot_type_choice == 5:  # 全类型训练 (三种机器人同时)
        # 平均分配三种类型
        per_type = rl_bot_count // 3
        remainder = rl_bot_count % 3
        
        # 原版机器人
        original_count = per_type + (1 if remainder > 0 else 0)
        for i in range(original_count):
            rl_bot = RLBot(f"rl_bot_{i+1}", f"原版机器人{i+1}", 1000)
            game.add_player(rl_bot)
        
        # 改进版机器人
        improved_count = per_type + (1 if remainder > 1 else 0)
        for i in range(improved_count):
            rl_bot = ImprovedRLBot(f"improved_rl_bot_{i+1}", f"🚀改进版机器人{i+1}", 1000)
            game.add_player(rl_bot)
        
        # 保守版机器人
        conservative_count = per_type
        for i in range(conservative_count):
            rl_bot = ConservativeRLBot(f"conservative_rl_bot_{i+1}", f"🛡️保守版机器人{i+1}", 1000)
            game.add_player(rl_bot)
    
    # 添加其他机器人作为对手
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

def show_training_progress():
    """显示训练进步过程"""
    print("\n" + "=" * 60)
    print("📈 强化学习机器人训练进步过程")
    print("=" * 60)
    
    try:
        tracker = TrainingTracker()
        
        # 主菜单
        while True:
            print(f"\n📊 训练进度查看器")
            print("─" * 30)
            print("1. 查看所有机器人对比")
            print("2. 查看原版强化学习机器人进步")
            print("3. 查看改进版强化学习机器人进步")
            print("4. 查看保守版强化学习机器人进步")
            print("5. 生成训练图表")
            print("6. 导出训练数据")
            print("7. 清理旧数据")
            print("8. 返回主菜单")
            print("─" * 30)
            
            try:
                choice = int(input("请选择 (1-8): "))
                
                if choice == 1:
                    # 查看所有机器人对比
                    show_bots_comparison(tracker)
                    
                elif choice == 2:
                    # 原版机器人进步
                    show_bot_detailed_progress(tracker, 'rl_bot')
                    
                elif choice == 3:
                    # 改进版机器人进步
                    show_bot_detailed_progress(tracker, 'improved_rl_bot')
                    
                elif choice == 4:
                    # 保守版机器人进步
                    show_bot_detailed_progress(tracker, 'conservative_rl_bot')
                    
                elif choice == 5:
                    # 生成训练图表
                    show_training_charts(tracker)
                    
                elif choice == 6:
                    # 导出训练数据
                    export_training_data(tracker)
                    
                elif choice == 7:
                    # 清理旧数据
                    clean_training_data(tracker)
                    
                elif choice == 8:
                    # 返回主菜单
                    break
                    
                else:
                    print("请输入有效的选择 (1-8)")
                    
            except ValueError:
                print("请输入有效的数字")
                
            if choice != 8:
                input("\n按回车键继续...")
                
    except Exception as e:
        print(f"❌ 访问训练数据失败: {e}")

def show_bots_comparison(tracker):
    """显示所有机器人对比"""
    print("\n" + "🔍" * 20 + " 机器人对比分析 " + "🔍" * 20)
    
    comparison = tracker.get_comparison_data()
    
    if not comparison['bots']:
        print("❌ 暂无训练数据")
        return
    
    print(f"\n📊 总体表现排行榜:")
    print("─" * 60)
    
    for bot_type, rank_info in comparison['rankings'].items():
        bot_info = comparison['bots'][bot_type]
        rank_emoji = "🥇" if rank_info['rank'] == 1 else "🥈" if rank_info['rank'] == 2 else "🥉" if rank_info['rank'] == 3 else f"{rank_info['rank']}️⃣"
        
        print(f"{rank_emoji} {bot_info['name']}")
        print(f"   当前胜率: {bot_info['win_rate']:.1f}%")
        print(f"   最佳胜率: {bot_info['best_win_rate']:.1f}%")
        print(f"   训练次数: {bot_info['total_snapshots']} 次")
        print(f"   总手牌数: {bot_info['total_hands']}")
        print(f"   当前探索率: {bot_info['latest_stats'].get('epsilon', 0):.1%}")
        print()
    
    if 'summary' in comparison and comparison['summary']:
        summary = comparison['summary']
        print(f"📈 统计摘要:")
        print(f"   最佳表现者: {comparison['bots'][summary['best_performer']]['name']}")
        print(f"   最高胜率: {summary['best_win_rate']:.1f}%")
        print(f"   平均胜率: {summary['avg_win_rate']:.1f}%")
        print(f"   有数据机器人: {summary['total_bots_with_data']}/3")

def show_bot_detailed_progress(tracker, bot_type):
    """显示单个机器人详细进步情况"""
    bot_names = {
        'rl_bot': '原版强化学习机器人',
        'improved_rl_bot': '改进版强化学习机器人',
        'conservative_rl_bot': '保守版强化学习机器人'
    }
    
    bot_name = bot_names.get(bot_type, bot_type)
    print(f"\n" + "📈" * 15 + f" {bot_name} 详细进步分析 " + "📈" * 15)
    
    progress = tracker.get_bot_progress(bot_type)
    
    if not progress.get('has_data', False):
        print(f"❌ {bot_name}: {progress.get('message', '暂无数据')}")
        return
    
    # 基本信息
    print(f"\n📋 基本信息:")
    print(f"   总训练快照: {progress['total_snapshots']} 次")
    print(f"   分析快照数: {progress['snapshots_analyzed']} 次")
    
    # 最新状态
    latest = progress['latest_snapshot']
    print(f"\n📊 最新状态 ({latest['timestamp'][:19]}):")
    stats = latest['stats']
    print(f"   胜率: {latest.get('calculated_win_rate', 0):.1f}%")
    print(f"   游戏次数: {stats.get('game_count', 0)}")
    print(f"   探索率: {stats.get('epsilon', 0):.1%}")
    print(f"   Q表大小: {stats.get('q_table_size', 0)}")
    print(f"   平均奖励: {stats.get('avg_reward', 0):.3f}")
    print(f"   当前筹码: {latest['session_info'].get('current_chips', 0)}")
    
    # 第一次记录对比
    if 'first_snapshot' in progress:
        first = progress['first_snapshot']
        print(f"\n📅 首次记录 ({first['timestamp'][:19]}):")
        first_stats = first['stats']
        print(f"   胜率: {first.get('calculated_win_rate', 0):.1f}%")
        print(f"   游戏次数: {first_stats.get('game_count', 0)}")
        print(f"   探索率: {first_stats.get('epsilon', 0):.1%}")
        print(f"   Q表大小: {first_stats.get('q_table_size', 0)}")
    
    # 进步分析
    if 'progress_analysis' in progress:
        analysis = progress['progress_analysis']
        print(f"\n🔬 进步分析:")
        
        trend_emoji = {
            'improving_well': '🚀',
            'improving_slowly': '📈',
            'stable': '➡️',
            'declining': '📉',
            'insufficient_data': '❓'
        }
        
        trend = analysis.get('trend', 'unknown')
        trend_text = {
            'improving_well': '快速进步',
            'improving_slowly': '缓慢进步',
            'stable': '表现稳定',
            'declining': '表现下降',
            'insufficient_data': '数据不足'
        }
        
        print(f"   总体趋势: {trend_emoji.get(trend, '❓')} {trend_text.get(trend, '未知')}")
        
        if 'win_rate_improvement' in analysis:
            improvement = analysis['win_rate_improvement']
            print(f"   胜率改进: {improvement:+.1f}%")
            print(f"   平均改进速度: {analysis.get('avg_improvement_per_snapshot', 0):+.3f}%/次")
            
        if 'win_rate_range' in analysis:
            wr_range = analysis['win_rate_range']
            print(f"   胜率范围: {wr_range['min']:.1f}% - {wr_range['max']:.1f}%")
            
        if 'q_table_growth' in analysis:
            print(f"   Q表增长: +{analysis['q_table_growth']} 状态")
            
        epsilon_trend = analysis.get('epsilon_trend', 'unknown')
        if epsilon_trend == 'decreasing':
            print(f"   探索策略: 📉 探索率正常下降 (学习进展良好)")
        else:
            print(f"   探索策略: ➡️ 探索率稳定")
    
    # 统计数据
    if 'statistics' in progress:
        stats = progress['statistics']
        print(f"\n📈 历史统计:")
        print(f"   最佳胜率: {stats['best_win_rate']:.1f}%")
        print(f"   总训练手数: {stats['total_hands']}")
        print(f"   当前连胜: {stats['current_streak']} 次改进")
        print(f"   最长连胜: {stats['longest_streak']} 次改进")

def show_training_charts(tracker):
    """显示训练图表"""
    print(f"\n📈 训练图表生成器")
    print("─" * 30)
    print("1. 胜率变化趋势图")
    print("2. 探索率变化趋势图")
    print("3. Q表大小变化趋势图")
    print("4. 返回上级菜单")
    
    try:
        choice = int(input("请选择图表类型 (1-4): "))
        
        if choice == 4:
            return
            
        print(f"\n选择机器人:")
        print("1. 原版强化学习机器人")
        print("2. 改进版强化学习机器人")
        print("3. 保守版强化学习机器人")
        
        bot_choice = int(input("请选择机器人 (1-3): "))
        bot_types = ['rl_bot', 'improved_rl_bot', 'conservative_rl_bot']
        
        if 1 <= bot_choice <= 3:
            bot_type = bot_types[bot_choice - 1]
            
            metrics = ['win_rate', 'epsilon', 'q_table_size']
            if 1 <= choice <= 3:
                metric = metrics[choice - 1]
                chart = tracker.generate_simple_chart(bot_type, metric)
                print(chart)
            else:
                print("❌ 无效的图表类型")
        else:
            print("❌ 无效的机器人选择")
            
    except ValueError:
        print("❌ 请输入有效的数字")

def export_training_data(tracker):
    """导出训练数据"""
    print(f"\n📁 训练数据导出")
    print("─" * 20)
    print("选择要导出的机器人:")
    print("1. 原版强化学习机器人")
    print("2. 改进版强化学习机器人")
    print("3. 保守版强化学习机器人")
    
    try:
        choice = int(input("请选择 (1-3): "))
        bot_types = {
            1: ('rl_bot', '原版强化学习机器人'),
            2: ('improved_rl_bot', '改进版强化学习机器人'),
            3: ('conservative_rl_bot', '保守版强化学习机器人')
        }
        
        if choice in bot_types:
            bot_type, bot_name = bot_types[choice]
            
            # 生成文件名
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{bot_type}_training_data_{timestamp}.csv"
            
            success = tracker.export_csv(bot_type, filename)
            if success:
                print(f"🎉 {bot_name} 训练数据已导出到: {filename}")
                print(f"💡 可以使用Excel或其他工具打开CSV文件查看详细数据")
            else:
                print(f"❌ 导出失败")
        else:
            print("❌ 无效的选择")
            
    except ValueError:
        print("❌ 请输入有效的数字")

def clean_training_data(tracker):
    """清理训练数据"""
    print(f"\n🗃️  训练数据清理")
    print("─" * 20)
    print("⚠️  此操作将删除旧的训练快照数据，但保留最近的记录")
    
    try:
        days = int(input("保留最近多少天的数据? (默认: 30): ") or "30")
        confirm = input(f"确认清理 {days} 天之前的训练快照? (y/n): ").lower()
        
        if confirm in ['y', 'yes']:
            cleaned_count = tracker.clean_old_snapshots(days)
            if cleaned_count > 0:
                print(f"✅ 已清理 {cleaned_count} 个旧的训练快照")
            else:
                print(f"ℹ️  没有需要清理的数据")
        else:
            print("❌ 清理操作已取消")
            
    except ValueError:
        print("❌ 请输入有效的天数")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序出现严重错误: {e}")
        sys.exit(1) 