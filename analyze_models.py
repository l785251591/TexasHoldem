#!/usr/bin/env python3
"""
详细分析模型文件大小变化原因
"""

from poker_game.model_analyzer import ModelAnalyzer
import os

def main():
    analyzer = ModelAnalyzer()
    
    print("🤖 强化学习模型文件大小分析")
    print("=" * 60)
    
    # 分析所有模型文件
    models_dir = "models"
    if not os.path.exists(models_dir):
        print(f"❌ 模型目录不存在: {models_dir}")
        return
    
    model_files = []
    for file in os.listdir(models_dir):
        if file.endswith('.pkl'):
            model_files.append(os.path.join(models_dir, file))
    
    if not model_files:
        print(f"❌ 在 {models_dir} 中未找到pkl模型文件")
        return
    
    # 按文件大小排序
    model_files_with_size = []
    for file_path in model_files:
        size = os.path.getsize(file_path)
        model_files_with_size.append((file_path, size))
    
    model_files_with_size.sort(key=lambda x: x[1], reverse=True)
    
    print("\n📋 模型文件概览 (按大小排序):")
    print("-" * 60)
    for file_path, size in model_files_with_size:
        print(f"  {os.path.basename(file_path):30s}: {size/1024:6.1f} KB")
    
    # 详细分析最大的模型文件
    largest_model = model_files_with_size[0][0]
    print(f"\n🔍 详细分析: {os.path.basename(largest_model)}")
    print("=" * 60)
    
    analysis = analyzer.analyze_model_file(largest_model)
    
    if 'error' not in analysis:
        # 组件分析
        print("📊 文件组件构成:")
        print("-" * 40)
        for component, info in analysis['components'].items():
            print(f"  {component:20s}: {info['size_bytes']:8,} 字节 ({info['size_percentage']:5.1f}%)")
        
        print()
        print("🧠 Q表详细信息:")
        print("-" * 40)
        if 'q_table_stats' in analysis:
            q_stats = analysis['q_table_stats']
            if 'total_states' in q_stats:
                print(f"  状态总数: {q_stats['total_states']:,}")
                print(f"  状态-动作对: {q_stats['total_state_action_pairs']:,}")
                print(f"  平均动作数/状态: {q_stats['avg_actions_per_state']:.2f}")
                print(f"  动作分布: {q_stats['action_distribution']}")
            else:
                print(f"  Q表1状态数: {q_stats['q_table_1']['total_states']:,}")
                print(f"  Q表2状态数: {q_stats['q_table_2']['total_states']:,}")
                print(f"  总唯一状态: {q_stats['combined']['total_unique_states']:,}")
                print(f"  状态重叠率: {q_stats['combined']['state_overlap_percentage']:.1f}%")
        
        print()
        print("⚡ 学习效率分析:")
        print("-" * 40)
        eff = analysis['efficiency_metrics']
        metrics = analysis['learning_metrics']
        print(f"  游戏次数: {metrics['game_count']:,}")
        print(f"  状态增长率: {eff['states_per_game']:.2f} 状态/游戏")
        print(f"  Q值增长率: {eff['entries_per_game']:.2f} 条目/游戏")
        print(f"  探索效率: {eff['exploration_efficiency']:.4f}")
        print(f"  当前探索率: {metrics['current_epsilon']:.4f}")
        
        print()
        print("💡 文件大小增长原因分析:")
        print("-" * 50)
        
        # Q表是主要增长因素
        q_table_percentage = 0
        for component, info in analysis['components'].items():
            if 'q_table' in component:
                q_table_percentage += info['size_percentage']
        
        print(f"1. Q表占文件大小的 {q_table_percentage:.1f}%，是文件增长的主要原因")
        
        if 'q_table_stats' in analysis:
            q_stats = analysis['q_table_stats']
            if 'total_states' in q_stats:
                states = q_stats['total_states']
                entries = q_stats['total_state_action_pairs']
            else:
                states = q_stats['combined']['total_unique_states']
                entries = (q_stats['q_table_1']['total_state_action_pairs'] + 
                          q_stats['q_table_2']['total_state_action_pairs'])
            
            print(f"2. 模型已学习 {states:,} 个状态，包含 {entries:,} 个状态-动作对")
            print(f"3. 每个状态平均有 {entries/max(1,states):.1f} 个可选动作")
            
            # 分析增长趋势
            games = metrics['game_count']
            if games > 0:
                print(f"4. 经过 {games:,} 局游戏，平均每局发现 {states/max(1,games):.2f} 个新状态")
                
                # 预测收敛
                if eff['states_per_game'] < 1.0:
                    print("5. ✅ 状态发现率已降至每局<1个，模型趋于收敛")
                elif eff['states_per_game'] < 2.0:
                    print("5. ⚠️ 状态发现率仍有每局2个以上，模型仍在学习")
                else:
                    print("5. 🔍 状态发现率较高，模型正在积极探索")
        
        print()
        print("📈 为什么文件增长会放缓？")
        print("-" * 50)
        print("1. 🎯 状态空间有限：德州扑克的有效状态数量是有限的")
        print("2. 📊 重复状态：随着训练深入，遇到新状态的概率降低")
        print("3. 🎲 探索率衰减：epsilon从初始值逐渐减小，减少了探索新状态")
        print("4. 🧠 学习收敛：Q值逐渐稳定，更新幅度减小")
        print("5. 💾 状态复用：已学习的状态被重复访问和优化")
        
        print()
        print("🚀 这是否意味着学习效率降低？")
        print("-" * 50)
        if metrics['win_rate'] > 45:
            print("✅ 胜率良好，文件增长放缓是收敛的正面信号")
        elif metrics['win_rate'] > 35:
            print("📈 胜率中等，仍有改进空间")
        else:
            print("⚠️ 胜率较低，可能需要调整学习参数")
        
        if eff['exploration_efficiency'] > 0.5:
            print("✅ 探索效率高，模型有效利用了学习到的状态")
        else:
            print("🔍 探索效率偏低，可能需要平衡探索与利用")
        
        print("\n💡 优化建议:")
        print("-" * 30)
        print("1. 如果胜率稳定提升：文件增长放缓是好现象")
        print("2. 如果胜率停滞：考虑调整学习率或探索策略") 
        print("3. 定期清理过时的Q值以减小文件大小")
        print("4. 使用更紧凑的状态表示减少内存占用")
        
    else:
        print('❌ 分析失败:', analysis['error'])

if __name__ == "__main__":
    main() 