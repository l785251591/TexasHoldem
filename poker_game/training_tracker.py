#!/usr/bin/env python3
"""
训练进度追踪器
监控强化学习机器人的学习进步过程
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import pickle

class TrainingTracker:
    """训练进度追踪器"""
    
    def __init__(self, tracker_file: str = "training_history.json"):
        self.tracker_file = tracker_file
        self.history = self.load_history()
        
    def load_history(self) -> Dict[str, Any]:
        """加载历史记录"""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载训练历史失败: {e}")
                return self._create_empty_history()
        else:
            return self._create_empty_history()
    
    def _create_empty_history(self) -> Dict[str, Any]:
        """创建空的历史记录结构"""
        return {
            'bots': {
                'rl_bot': {
                    'name': '原版强化学习机器人',
                    'snapshots': [],
                    'statistics': {
                        'total_training_time': 0,
                        'total_hands': 0,
                        'best_win_rate': 0,
                        'current_streak': 0,
                        'longest_streak': 0
                    }
                },
                'improved_rl_bot': {
                    'name': '改进版强化学习机器人',
                    'snapshots': [],
                    'statistics': {
                        'total_training_time': 0,
                        'total_hands': 0,
                        'best_win_rate': 0,
                        'current_streak': 0,
                        'longest_streak': 0
                    }
                },
                'conservative_rl_bot': {
                    'name': '保守版强化学习机器人',
                    'snapshots': [],
                    'statistics': {
                        'total_training_time': 0,
                        'total_hands': 0,
                        'best_win_rate': 0,
                        'current_streak': 0,
                        'longest_streak': 0
                    }
                }
            },
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_snapshots': 0
            }
        }
    
    def save_history(self):
        """保存历史记录"""
        try:
            self.history['metadata']['last_updated'] = datetime.now().isoformat()
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  保存训练历史失败: {e}")
    
    def record_snapshot(self, bot_type: str, bot_stats: Dict[str, Any], 
                       additional_info: Optional[Dict[str, Any]] = None):
        """记录训练快照"""
        if bot_type not in self.history['bots']:
            print(f"⚠️  未知的机器人类型: {bot_type}")
            return
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'unix_timestamp': time.time(),
            'stats': bot_stats.copy(),
            'session_info': additional_info or {}
        }
        
        # 添加计算字段
        if 'game_count' in bot_stats and 'win_count' in bot_stats:
            snapshot['calculated_win_rate'] = (bot_stats['win_count'] / max(1, bot_stats['game_count'])) * 100
        
        # 添加快照
        self.history['bots'][bot_type]['snapshots'].append(snapshot)
        
        # 更新统计
        self._update_bot_statistics(bot_type, snapshot)
        
        # 更新元数据
        self.history['metadata']['total_snapshots'] += 1
        
        # 自动保存
        self.save_history()
    
    def _update_bot_statistics(self, bot_type: str, snapshot: Dict[str, Any]):
        """更新机器人统计信息"""
        stats = self.history['bots'][bot_type]['statistics']
        snapshot_stats = snapshot['stats']
        
        # 更新总训练时间和手数
        if 'game_count' in snapshot_stats:
            stats['total_hands'] = max(stats['total_hands'], snapshot_stats['game_count'])
        
        # 更新最佳胜率
        if 'calculated_win_rate' in snapshot:
            win_rate = snapshot['calculated_win_rate']
            if win_rate > stats['best_win_rate']:
                stats['best_win_rate'] = win_rate
                
        # 计算连胜记录 (基于胜率提升)
        snapshots = self.history['bots'][bot_type]['snapshots']
        if len(snapshots) >= 2:
            current_wr = snapshot.get('calculated_win_rate', 0)
            prev_wr = snapshots[-2].get('calculated_win_rate', 0)
            
            if current_wr > prev_wr:
                stats['current_streak'] += 1
                stats['longest_streak'] = max(stats['longest_streak'], stats['current_streak'])
            else:
                stats['current_streak'] = 0
    
    def get_bot_progress(self, bot_type: str, last_n_snapshots: Optional[int] = None) -> Dict[str, Any]:
        """获取机器人进步情况"""
        if bot_type not in self.history['bots']:
            return {}
        
        bot_data = self.history['bots'][bot_type]
        snapshots = bot_data['snapshots']
        
        if last_n_snapshots:
            snapshots = snapshots[-last_n_snapshots:]
        
        if not snapshots:
            return {
                'bot_name': bot_data['name'],
                'has_data': False,
                'message': '暂无训练数据'
            }
        
        # 计算进步趋势
        progress_analysis = self._analyze_progress(snapshots)
        
        return {
            'bot_name': bot_data['name'],
            'has_data': True,
            'total_snapshots': len(bot_data['snapshots']),
            'snapshots_analyzed': len(snapshots),
            'first_snapshot': snapshots[0],
            'latest_snapshot': snapshots[-1],
            'statistics': bot_data['statistics'],
            'progress_analysis': progress_analysis,
            'recent_snapshots': snapshots[-10:] if len(snapshots) > 10 else snapshots
        }
    
    def _analyze_progress(self, snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析进步趋势"""
        if len(snapshots) < 2:
            return {'trend': 'insufficient_data'}
        
        # 胜率趋势
        win_rates = [s.get('calculated_win_rate', 0) for s in snapshots if 'calculated_win_rate' in s]
        
        if len(win_rates) < 2:
            return {'trend': 'no_win_rate_data'}
        
        # 计算趋势
        first_wr = win_rates[0]
        latest_wr = win_rates[-1]
        improvement = latest_wr - first_wr
        
        # 计算平均改进速度 (每个快照的改进)
        improvements = []
        for i in range(1, len(win_rates)):
            improvements.append(win_rates[i] - win_rates[i-1])
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # 探索率变化
        epsilons = [s['stats'].get('epsilon', 0) for s in snapshots if 'epsilon' in s.get('stats', {})]
        epsilon_trend = 'decreasing' if len(epsilons) >= 2 and epsilons[-1] < epsilons[0] else 'stable'
        
        # Q表增长
        q_sizes = [s['stats'].get('q_table_size', 0) for s in snapshots if 'q_table_size' in s.get('stats', {})]
        q_growth = q_sizes[-1] - q_sizes[0] if len(q_sizes) >= 2 else 0
        
        # 判断整体趋势
        if improvement > 5:
            trend = 'improving_well'
        elif improvement > 1:
            trend = 'improving_slowly'
        elif improvement > -1:
            trend = 'stable'
        else:
            trend = 'declining'
        
        return {
            'trend': trend,
            'win_rate_improvement': improvement,
            'avg_improvement_per_snapshot': avg_improvement,
            'epsilon_trend': epsilon_trend,
            'q_table_growth': q_growth,
            'win_rate_range': {'min': min(win_rates), 'max': max(win_rates)},
            'latest_win_rate': latest_wr,
            'total_training_sessions': len(snapshots)
        }
    
    def get_comparison_data(self) -> Dict[str, Any]:
        """获取所有机器人的对比数据"""
        comparison = {
            'bots': {},
            'rankings': {},
            'summary': {}
        }
        
        bot_performance = []
        
        for bot_type, bot_data in self.history['bots'].items():
            if not bot_data['snapshots']:
                continue
            
            latest_snapshot = bot_data['snapshots'][-1]
            win_rate = latest_snapshot.get('calculated_win_rate', 0)
            
            bot_info = {
                'type': bot_type,
                'name': bot_data['name'],
                'win_rate': win_rate,
                'total_snapshots': len(bot_data['snapshots']),
                'best_win_rate': bot_data['statistics']['best_win_rate'],
                'total_hands': bot_data['statistics']['total_hands'],
                'latest_stats': latest_snapshot['stats']
            }
            
            comparison['bots'][bot_type] = bot_info
            bot_performance.append((bot_type, win_rate))
        
        # 排序
        bot_performance.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (bot_type, win_rate) in enumerate(bot_performance, 1):
            comparison['rankings'][bot_type] = {
                'rank': rank,
                'win_rate': win_rate
            }
        
        # 摘要统计
        if bot_performance:
            win_rates = [wr for _, wr in bot_performance]
            comparison['summary'] = {
                'best_performer': bot_performance[0][0] if bot_performance else None,
                'best_win_rate': max(win_rates),
                'avg_win_rate': sum(win_rates) / len(win_rates),
                'total_bots_with_data': len(bot_performance)
            }
        
        return comparison
    
    def clean_old_snapshots(self, days_to_keep: int = 30):
        """清理旧的快照数据"""
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        total_cleaned = 0
        
        for bot_type in self.history['bots']:
            original_count = len(self.history['bots'][bot_type]['snapshots'])
            
            # 保留最近的快照
            self.history['bots'][bot_type]['snapshots'] = [
                snapshot for snapshot in self.history['bots'][bot_type]['snapshots']
                if snapshot.get('unix_timestamp', time.time()) > cutoff_time
            ]
            
            # 但至少保留最后10个快照
            if len(self.history['bots'][bot_type]['snapshots']) < 10:
                all_snapshots = sorted(
                    self.history['bots'][bot_type]['snapshots'],
                    key=lambda x: x.get('unix_timestamp', 0)
                )
                self.history['bots'][bot_type]['snapshots'] = all_snapshots[-10:]
            
            cleaned = original_count - len(self.history['bots'][bot_type]['snapshots'])
            total_cleaned += cleaned
        
        if total_cleaned > 0:
            print(f"🗃️  清理了 {total_cleaned} 个旧的训练快照")
            self.save_history()
        
        return total_cleaned
    
    def export_csv(self, bot_type: str, output_file: str):
        """导出训练数据为CSV格式"""
        if bot_type not in self.history['bots']:
            print(f"❌ 未找到机器人类型: {bot_type}")
            return False
        
        snapshots = self.history['bots'][bot_type]['snapshots']
        if not snapshots:
            print(f"❌ {bot_type} 没有训练数据")
            return False
        
        try:
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'win_rate', 'game_count', 'epsilon', 
                    'q_table_size', 'avg_reward', 'total_reward'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for snapshot in snapshots:
                    stats = snapshot['stats']
                    row = {
                        'timestamp': snapshot['timestamp'],
                        'win_rate': snapshot.get('calculated_win_rate', 0),
                        'game_count': stats.get('game_count', 0),
                        'epsilon': stats.get('epsilon', 0),
                        'q_table_size': stats.get('q_table_size', 0),
                        'avg_reward': stats.get('avg_reward', 0),
                        'total_reward': stats.get('total_reward', 0)
                    }
                    writer.writerow(row)
            
            print(f"✅ 导出成功: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False
    
    def generate_simple_chart(self, bot_type: str, metric: str = 'win_rate') -> str:
        """生成简单的文本图表"""
        if bot_type not in self.history['bots']:
            return "❌ 机器人类型不存在"
        
        snapshots = self.history['bots'][bot_type]['snapshots']
        if len(snapshots) < 2:
            return "❌ 数据不足，需要至少2个快照"
        
        # 提取数据
        if metric == 'win_rate':
            values = [s.get('calculated_win_rate', 0) for s in snapshots[-20:]]  # 最近20个点
            title = "胜率变化趋势"
            unit = "%"
        elif metric == 'epsilon':
            values = [s['stats'].get('epsilon', 0) for s in snapshots[-20:]]
            title = "探索率变化趋势"
            unit = ""
        elif metric == 'q_table_size':
            values = [s['stats'].get('q_table_size', 0) for s in snapshots[-20:]]
            title = "Q表大小变化趋势"
            unit = ""
        else:
            return "❌ 不支持的指标类型"
        
        if not values or all(v == 0 for v in values):
            return f"❌ {title}: 无有效数据"
        
        # 生成简单的ASCII图表
        chart_lines = [f"\n📈 {title} (最近 {len(values)} 个快照)"]
        chart_lines.append("=" * 50)
        
        # 计算缩放
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            chart_lines.append("数据无变化")
            return "\n".join(chart_lines)
        
        # 绘制图表
        chart_width = 40
        for i, value in enumerate(values):
            # 标准化到0-chart_width
            if max_val > min_val:
                normalized = int(((value - min_val) / (max_val - min_val)) * chart_width)
            else:
                normalized = chart_width // 2
            
            bar = "█" * normalized + "░" * (chart_width - normalized)
            chart_lines.append(f"{i+1:2d}│{bar}│ {value:.2f}{unit}")
        
        chart_lines.append("=" * 50)
        chart_lines.append(f"范围: {min_val:.2f}{unit} - {max_val:.2f}{unit}")
        chart_lines.append(f"趋势: {'📈上升' if values[-1] > values[0] else '📉下降' if values[-1] < values[0] else '➡️平稳'}")
        
        return "\n".join(chart_lines) 