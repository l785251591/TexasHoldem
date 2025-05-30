#!/usr/bin/env python3
"""
展示强化学习机器人的统计数据
"""

from poker_game.model_analyzer import ModelAnalyzer
import os

def main():
    analyzer = ModelAnalyzer()
    
    print('🤖 强化学习机器人统计逻辑展示')
    print('=' * 60)
    
    models_dir = 'models'
    if not os.path.exists(models_dir):
        print('❌ 模型目录不存在')
        return
    
    for file in sorted(os.listdir(models_dir)):
        if file.endswith('.pkl'):
            print(f'\n📊 分析: {file}')
            print('-' * 40)
            
            analysis = analyzer.analyze_model_file(os.path.join(models_dir, file))
            if 'error' not in analysis:
                metrics = analysis['learning_metrics']
                print(f'游戏局数: {metrics["game_count"]:,}')
                print(f'获胜局数: {metrics["win_count"]:,}')
                print(f'胜率: {metrics["win_rate"]:.2f}%')
                print(f'累计奖励: {metrics["total_reward"]:.2f}')
                print(f'平均奖励: {metrics["avg_reward"]:.4f}')
                print(f'当前探索率: {metrics["current_epsilon"]:.4f}')
                
                # Q表信息
                if 'q_table_stats' in analysis:
                    q_stats = analysis['q_table_stats']
                    if 'total_states' in q_stats:
                        print(f'学习状态数: {q_stats["total_states"]:,}')
                        print(f'Q值条目数: {q_stats["total_state_action_pairs"]:,}')
                    else:
                        print(f'学习状态数: {q_stats["combined"]["total_unique_states"]:,}')
                        total_entries = (q_stats["q_table_1"]["total_state_action_pairs"] + 
                                       q_stats["q_table_2"]["total_state_action_pairs"])
                        print(f'Q值条目数: {total_entries:,}')
                
                print('\n🔍 统计逻辑说明:')
                print('  - 胜率 = win_count / game_count * 100%')
                print('  - 平均奖励 = total_reward / game_count')
                print('  - 每手牌结束调用 learn_from_hand_result()')
                print('  - 奖励函数根据机器人类型差异化计算')
            else:
                print(f'❌ {analysis["error"]}')
    
    print('\n💡 Reward计算要点:')
    print('-' * 40)
    print('1. 原版机器人: 简单ROI奖励')
    print('   - 获胜: winnings/投入 (限制≤10.0)')
    print('   - 失败: -投入/总筹码')
    print('   - 弃牌: -0.1')
    
    print('\n2. 改进版机器人: 复杂奖励')
    print('   - 基础胜负奖励 (限制≤5.0)')
    print('   - 决策质量奖励 (+0.05~0.1)')
    print('   - 生存奖励 (+0.05)')
    print('   - 适应性奖励 (+0.1)')
    
    print('\n3. 保守版机器人: 保守策略奖励')
    print('   - 基础胜负奖励')
    print('   - 保守决策奖励 (+0.05~0.12)')
    print('   - 高生存奖励 (+0.1)')
    print('   - 筹码管理奖励 (±0.05~0.1)')
    print('   - 一致性奖励 (+0.05)')

if __name__ == "__main__":
    main() 