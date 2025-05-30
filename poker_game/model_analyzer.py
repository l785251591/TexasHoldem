#!/usr/bin/env python3
"""
强化学习模型分析工具
分析模型文件大小变化原因和学习效率
"""

import pickle
import os
import sys
from typing import Dict, Any, List, Tuple
import matplotlib.pyplot as plt
from collections import defaultdict
import json

class ModelAnalyzer:
    """模型分析器"""
    
    def __init__(self):
        self.analysis_data = []
    
    def analyze_model_file(self, model_path: str) -> Dict[str, Any]:
        """分析单个模型文件"""
        if not os.path.exists(model_path):
            return {"error": f"文件不存在: {model_path}"}
        
        try:
            # 文件基本信息
            file_size = os.path.getsize(model_path)
            
            # 加载模型数据
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            
            # 分析各组件大小
            analysis = {
                "file_path": model_path,
                "total_file_size": file_size,
                "components": {},
                "learning_metrics": {},
                "efficiency_metrics": {}
            }
            
            # 分析各个组件的大小
            for key, value in data.items():
                component_size = sys.getsizeof(pickle.dumps(value))
                analysis["components"][key] = {
                    "size_bytes": component_size,
                    "size_percentage": (component_size / file_size) * 100
                }
            
            # 分析Q表详细信息
            if 'q_table' in data:
                q_table = data['q_table']
                analysis["q_table_stats"] = self._analyze_q_table(q_table, "single")
            elif 'q_table_1' in data and 'q_table_2' in data:
                q_table_1 = data['q_table_1']
                q_table_2 = data['q_table_2']
                analysis["q_table_stats"] = {
                    "q_table_1": self._analyze_q_table(q_table_1, "double_1"),
                    "q_table_2": self._analyze_q_table(q_table_2, "double_2"),
                    "combined": self._analyze_combined_q_tables(q_table_1, q_table_2)
                }
            
            # 学习指标
            analysis["learning_metrics"] = {
                "game_count": data.get('game_count', 0),
                "win_count": data.get('win_count', 0),
                "win_rate": data.get('win_count', 0) / max(1, data.get('game_count', 1)) * 100,
                "total_reward": data.get('total_reward', 0),
                "avg_reward": data.get('total_reward', 0) / max(1, data.get('game_count', 1)),
                "current_epsilon": data.get('epsilon', 0)
            }
            
            # 效率指标
            analysis["efficiency_metrics"] = self._calculate_efficiency_metrics(data)
            
            return analysis
            
        except Exception as e:
            return {"error": f"分析失败: {str(e)}"}
    
    def _analyze_q_table(self, q_table: Dict, table_type: str) -> Dict[str, Any]:
        """分析Q表结构"""
        total_states = len(q_table)
        total_state_action_pairs = 0
        action_distribution = defaultdict(int)
        value_distribution = {'positive': 0, 'negative': 0, 'zero': 0}
        
        for state, actions in q_table.items():
            total_state_action_pairs += len(actions)
            for action, value in actions.items():
                action_distribution[action] += 1
                if value > 0.001:
                    value_distribution['positive'] += 1
                elif value < -0.001:
                    value_distribution['negative'] += 1
                else:
                    value_distribution['zero'] += 1
        
        avg_actions_per_state = total_state_action_pairs / max(1, total_states)
        
        return {
            "table_type": table_type,
            "total_states": total_states,
            "total_state_action_pairs": total_state_action_pairs,
            "avg_actions_per_state": avg_actions_per_state,
            "action_distribution": dict(action_distribution),
            "value_distribution": dict(value_distribution),
            "memory_usage_estimation": total_state_action_pairs * 64  # 估算字节数
        }
    
    def _analyze_combined_q_tables(self, q_table_1: Dict, q_table_2: Dict) -> Dict[str, Any]:
        """分析双Q表的组合信息"""
        all_states = set(q_table_1.keys()) | set(q_table_2.keys())
        common_states = set(q_table_1.keys()) & set(q_table_2.keys())
        
        return {
            "total_unique_states": len(all_states),
            "common_states": len(common_states),
            "state_overlap_percentage": len(common_states) / len(all_states) * 100 if all_states else 0,
            "q1_only_states": len(set(q_table_1.keys()) - set(q_table_2.keys())),
            "q2_only_states": len(set(q_table_2.keys()) - set(q_table_1.keys()))
        }
    
    def _calculate_efficiency_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算学习效率指标"""
        game_count = data.get('game_count', 0)
        win_count = data.get('win_count', 0)
        
        # Q表大小相关
        if 'q_table' in data:
            total_states = len(data['q_table'])
            total_entries = sum(len(actions) for actions in data['q_table'].values())
        elif 'q_table_1' in data:
            total_states = len(set(data['q_table_1'].keys()) | set(data.get('q_table_2', {}).keys()))
            total_entries = (sum(len(actions) for actions in data['q_table_1'].values()) + 
                           sum(len(actions) for actions in data.get('q_table_2', {}).values()))
        else:
            total_states = 0
            total_entries = 0
        
        # 状态访问统计
        state_visits = data.get('state_visit_count', {})
        total_state_visits = sum(state_visits.values()) if state_visits else 0
        
        # 效率指标
        metrics = {
            "states_per_game": total_states / max(1, game_count),
            "entries_per_game": total_entries / max(1, game_count),
            "avg_state_visits": total_state_visits / max(1, total_states),
            "learning_density": total_entries / max(1, total_state_visits),  # 每次访问产生的Q值数
            "exploration_efficiency": total_states / max(1, total_state_visits),  # 探索效率
            "win_rate_per_1000_states": (win_count / max(1, game_count)) * 1000 / max(1, total_states)
        }
        
        return metrics
    
    def compare_model_snapshots(self, model_paths: List[str]) -> Dict[str, Any]:
        """比较多个模型快照，分析增长趋势"""
        analyses = []
        
        for path in sorted(model_paths):
            analysis = self.analyze_model_file(path)
            if "error" not in analysis:
                analyses.append(analysis)
        
        if len(analyses) < 2:
            return {"error": "需要至少2个有效的模型文件进行比较"}
        
        # 趋势分析
        trends = {
            "file_size_trend": [],
            "q_table_growth": [],
            "learning_progress": [],
            "efficiency_trend": []
        }
        
        for i, analysis in enumerate(analyses):
            trends["file_size_trend"].append({
                "index": i,
                "size": analysis["total_file_size"],
                "game_count": analysis["learning_metrics"]["game_count"]
            })
            
            if "q_table_stats" in analysis:
                if "total_states" in analysis["q_table_stats"]:
                    # 单Q表
                    states = analysis["q_table_stats"]["total_states"]
                    entries = analysis["q_table_stats"]["total_state_action_pairs"]
                else:
                    # 双Q表
                    states = analysis["q_table_stats"]["combined"]["total_unique_states"]
                    entries = (analysis["q_table_stats"]["q_table_1"]["total_state_action_pairs"] + 
                             analysis["q_table_stats"]["q_table_2"]["total_state_action_pairs"])
                
                trends["q_table_growth"].append({
                    "index": i,
                    "states": states,
                    "entries": entries,
                    "game_count": analysis["learning_metrics"]["game_count"]
                })
            
            trends["learning_progress"].append({
                "index": i,
                "win_rate": analysis["learning_metrics"]["win_rate"],
                "avg_reward": analysis["learning_metrics"]["avg_reward"],
                "epsilon": analysis["learning_metrics"]["current_epsilon"],
                "game_count": analysis["learning_metrics"]["game_count"]
            })
            
            trends["efficiency_trend"].append({
                "index": i,
                "states_per_game": analysis["efficiency_metrics"]["states_per_game"],
                "exploration_efficiency": analysis["efficiency_metrics"]["exploration_efficiency"],
                "game_count": analysis["learning_metrics"]["game_count"]
            })
        
        # 计算增长率
        growth_analysis = self._analyze_growth_patterns(trends)
        
        return {
            "total_snapshots": len(analyses),
            "trends": trends,
            "growth_analysis": growth_analysis,
            "recommendations": self._generate_recommendations(growth_analysis)
        }
    
    def _analyze_growth_patterns(self, trends: Dict[str, List]) -> Dict[str, Any]:
        """分析增长模式"""
        analysis = {}
        
        # 文件大小增长率
        if len(trends["file_size_trend"]) >= 2:
            sizes = [item["size"] for item in trends["file_size_trend"]]
            games = [item["game_count"] for item in trends["file_size_trend"]]
            
            early_growth = (sizes[len(sizes)//3] - sizes[0]) / max(1, games[len(games)//3] - games[0])
            late_growth = (sizes[-1] - sizes[2*len(sizes)//3]) / max(1, games[-1] - games[2*len(games)//3])
            
            analysis["file_size_growth"] = {
                "early_growth_rate": early_growth,
                "late_growth_rate": late_growth,
                "growth_deceleration": (early_growth - late_growth) / max(1, early_growth) * 100,
                "total_growth": sizes[-1] - sizes[0]
            }
        
        # Q表增长率
        if len(trends["q_table_growth"]) >= 2:
            states = [item["states"] for item in trends["q_table_growth"]]
            games = [item["game_count"] for item in trends["q_table_growth"]]
            
            early_state_growth = (states[len(states)//3] - states[0]) / max(1, games[len(games)//3] - games[0])
            late_state_growth = (states[-1] - states[2*len(states)//3]) / max(1, games[-1] - games[2*len(games)//3])
            
            analysis["q_table_growth"] = {
                "early_state_growth_rate": early_state_growth,
                "late_state_growth_rate": late_state_growth,
                "state_growth_deceleration": (early_state_growth - late_state_growth) / max(1, early_state_growth) * 100,
                "total_states": states[-1] - states[0]
            }
        
        # 学习效率
        if len(trends["learning_progress"]) >= 2:
            win_rates = [item["win_rate"] for item in trends["learning_progress"]]
            epsilons = [item["epsilon"] for item in trends["learning_progress"]]
            
            analysis["learning_efficiency"] = {
                "win_rate_improvement": win_rates[-1] - win_rates[0],
                "epsilon_decay": epsilons[0] - epsilons[-1],
                "learning_stability": self._calculate_stability(win_rates)
            }
        
        return analysis
    
    def _calculate_stability(self, values: List[float]) -> float:
        """计算数值序列的稳定性（变异系数的倒数）"""
        if len(values) < 2:
            return 0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        if mean_val == 0:
            return 0
        
        cv = std_dev / abs(mean_val)  # 变异系数
        return 1 / (1 + cv)  # 稳定性指标
    
    def _generate_recommendations(self, growth_analysis: Dict[str, Any]) -> List[str]:
        """基于分析结果生成建议"""
        recommendations = []
        
        # 文件增长建议
        if "file_size_growth" in growth_analysis:
            growth_data = growth_analysis["file_size_growth"]
            if growth_data["growth_deceleration"] > 50:
                recommendations.append(
                    "✅ 文件大小增长放缓是正常现象，表明模型趋于收敛"
                )
            elif growth_data["growth_deceleration"] < 10:
                recommendations.append(
                    "⚠️ 文件仍在快速增长，可能需要更多训练时间来收敛"
                )
        
        # Q表增长建议
        if "q_table_growth" in growth_analysis:
            q_data = growth_analysis["q_table_growth"]
            if q_data["state_growth_deceleration"] > 60:
                recommendations.append(
                    "✅ Q表状态增长放缓，模型已探索大部分重要状态"
                )
                recommendations.append(
                    "💡 可以考虑降低探索率(epsilon)以专注于利用学到的知识"
                )
            elif q_data["state_growth_deceleration"] < 20:
                recommendations.append(
                    "🔍 Q表仍在快速扩展，模型正在积极探索新状态"
                )
        
        # 学习效率建议
        if "learning_efficiency" in growth_analysis:
            learn_data = growth_analysis["learning_efficiency"]
            if learn_data["win_rate_improvement"] > 5:
                recommendations.append(
                    "🎯 胜率有显著提升，学习效果良好"
                )
            elif learn_data["win_rate_improvement"] < 1:
                recommendations.append(
                    "📈 胜率提升缓慢，可能需要调整学习参数"
                )
            
            if learn_data["learning_stability"] > 0.7:
                recommendations.append(
                    "🎪 学习过程稳定，模型性能一致"
                )
            else:
                recommendations.append(
                    "🎢 学习过程波动较大，可能需要调整学习率"
                )
        
        if not recommendations:
            recommendations.append("📊 需要更多数据进行深入分析")
        
        return recommendations
    
    def generate_report(self, model_path: str, output_file: str = None):
        """生成详细的分析报告"""
        analysis = self.analyze_model_file(model_path)
        
        if "error" in analysis:
            print(f"❌ 分析失败: {analysis['error']}")
            return
        
        report = self._format_analysis_report(analysis)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 报告已保存到: {output_file}")
        else:
            print(report)
    
    def _format_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """格式化分析报告"""
        report = []
        report.append("🤖 强化学习模型分析报告")
        report.append("=" * 60)
        report.append(f"📁 模型文件: {analysis['file_path']}")
        report.append(f"📦 文件大小: {analysis['total_file_size']:,} 字节 ({analysis['total_file_size']/1024:.1f} KB)")
        report.append("")
        
        # 组件分析
        report.append("📊 组件大小分析:")
        report.append("-" * 40)
        for component, info in analysis['components'].items():
            report.append(f"  {component:20s}: {info['size_bytes']:8,} 字节 ({info['size_percentage']:5.1f}%)")
        report.append("")
        
        # Q表统计
        if "q_table_stats" in analysis:
            report.append("🧠 Q表统计信息:")
            report.append("-" * 40)
            q_stats = analysis["q_table_stats"]
            
            if "total_states" in q_stats:
                # 单Q表
                report.append(f"  状态总数: {q_stats['total_states']:,}")
                report.append(f"  状态-动作对: {q_stats['total_state_action_pairs']:,}")
                report.append(f"  平均动作数/状态: {q_stats['avg_actions_per_state']:.2f}")
            else:
                # 双Q表
                report.append(f"  Q表1状态数: {q_stats['q_table_1']['total_states']:,}")
                report.append(f"  Q表2状态数: {q_stats['q_table_2']['total_states']:,}")
                report.append(f"  总唯一状态: {q_stats['combined']['total_unique_states']:,}")
                report.append(f"  状态重叠率: {q_stats['combined']['state_overlap_percentage']:.1f}%")
        
        report.append("")
        
        # 学习指标
        report.append("📈 学习指标:")
        report.append("-" * 40)
        metrics = analysis["learning_metrics"]
        report.append(f"  游戏次数: {metrics['game_count']:,}")
        report.append(f"  胜利次数: {metrics['win_count']:,}")
        report.append(f"  胜率: {metrics['win_rate']:.2f}%")
        report.append(f"  总奖励: {metrics['total_reward']:.2f}")
        report.append(f"  平均奖励: {metrics['avg_reward']:.4f}")
        report.append(f"  当前探索率: {metrics['current_epsilon']:.4f}")
        report.append("")
        
        # 效率指标
        report.append("⚡ 效率指标:")
        report.append("-" * 40)
        eff = analysis["efficiency_metrics"]
        report.append(f"  状态数/游戏: {eff['states_per_game']:.2f}")
        report.append(f"  Q值条目数/游戏: {eff['entries_per_game']:.2f}")
        report.append(f"  平均状态访问次数: {eff['avg_state_visits']:.2f}")
        report.append(f"  学习密度: {eff['learning_density']:.4f}")
        report.append(f"  探索效率: {eff['exploration_efficiency']:.4f}")
        
        return "\n".join(report)

def analyze_model_growth_pattern(models_dir: str = "models"):
    """分析模型目录中的增长模式"""
    analyzer = ModelAnalyzer()
    
    if not os.path.exists(models_dir):
        print(f"❌ 模型目录不存在: {models_dir}")
        return
    
    # 查找模型文件
    model_files = []
    for file in os.listdir(models_dir):
        if file.endswith('.pkl'):
            model_files.append(os.path.join(models_dir, file))
    
    if not model_files:
        print(f"❌ 在 {models_dir} 中未找到pkl模型文件")
        return
    
    print(f"🔍 找到 {len(model_files)} 个模型文件")
    
    # 分析每个文件
    for model_file in sorted(model_files):
        print(f"\n📋 分析: {model_file}")
        print("-" * 50)
        
        analysis = analyzer.analyze_model_file(model_file)
        if "error" not in analysis:
            # 简要信息
            size_kb = analysis['total_file_size'] / 1024
            games = analysis['learning_metrics']['game_count']
            win_rate = analysis['learning_metrics']['win_rate']
            
            if 'q_table_stats' in analysis:
                q_stats = analysis['q_table_stats']
                if 'total_states' in q_stats:
                    states = q_stats['total_states']
                else:
                    states = q_stats['combined']['total_unique_states']
            else:
                states = 0
            
            print(f"  大小: {size_kb:.1f} KB | 游戏: {games:,} | 胜率: {win_rate:.1f}% | 状态: {states:,}")
        else:
            print(f"  ❌ {analysis['error']}")

if __name__ == "__main__":
    # 使用示例
    print("🤖 强化学习模型分析工具")
    print("=" * 60)
    
    # 分析模型目录
    analyze_model_growth_pattern() 