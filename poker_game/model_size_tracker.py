#!/usr/bin/env python3
"""
模型大小跟踪器
跟踪和分析训练过程中模型文件大小的变化趋势
"""

import os
import pickle
import time
from datetime import datetime
from typing import Dict, List, Tuple
import json

class ModelSizeTracker:
    """模型大小跟踪器"""
    
    def __init__(self, tracking_file: str = "model_size_tracking.json"):
        self.tracking_file = tracking_file
        self.tracking_data = self._load_tracking_data()
    
    def _load_tracking_data(self) -> Dict:
        """加载跟踪数据"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "models": {},
            "snapshots": []
        }
    
    def _save_tracking_data(self):
        """保存跟踪数据"""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.tracking_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存跟踪数据失败: {e}")
    
    def record_model_snapshot(self, model_path: str, force: bool = False):
        """记录模型快照"""
        if not os.path.exists(model_path):
            return False
        
        model_name = os.path.basename(model_path)
        file_size = os.path.getsize(model_path)
        timestamp = datetime.now().isoformat()
        
        # 检查是否需要记录（避免重复记录相同大小）
        if not force and model_name in self.tracking_data["models"]:
            last_record = self.tracking_data["models"][model_name]
            if last_record.get("size", 0) == file_size:
                return False
        
        # 尝试加载模型数据获取更详细信息
        model_info = self._analyze_model_content(model_path)
        
        # 记录信息
        record = {
            "timestamp": timestamp,
            "size": file_size,
            "size_kb": round(file_size / 1024, 2),
            **model_info
        }
        
        # 更新模型记录
        if model_name not in self.tracking_data["models"]:
            self.tracking_data["models"][model_name] = {
                "first_seen": timestamp,
                "snapshots": []
            }
        
        self.tracking_data["models"][model_name]["snapshots"].append(record)
        self.tracking_data["models"][model_name]["latest"] = record
        
        # 添加到全局快照
        self.tracking_data["snapshots"].append({
            "model": model_name,
            "timestamp": timestamp,
            "size": file_size,
            **model_info
        })
        
        self._save_tracking_data()
        return True
    
    def _analyze_model_content(self, model_path: str) -> Dict:
        """分析模型内容"""
        try:
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
            
            info = {
                "game_count": data.get('game_count', 0),
                "win_count": data.get('win_count', 0),
                "total_reward": data.get('total_reward', 0),
                "epsilon": data.get('epsilon', 0),
            }
            
            # 计算胜率
            if info["game_count"] > 0:
                info["win_rate"] = round((info["win_count"] / info["game_count"]) * 100, 2)
                info["avg_reward"] = round(info["total_reward"] / info["game_count"], 4)
            else:
                info["win_rate"] = 0
                info["avg_reward"] = 0
            
            # 分析Q表大小
            if 'q_table' in data:
                q_table = data['q_table']
                info["states_count"] = len(q_table)
                info["state_action_pairs"] = sum(len(actions) for actions in q_table.values())
            elif 'q_table_1' in data and 'q_table_2' in data:
                q1 = data['q_table_1']
                q2 = data['q_table_2']
                all_states = set(q1.keys()) | set(q2.keys())
                info["states_count"] = len(all_states)
                info["state_action_pairs"] = (sum(len(actions) for actions in q1.values()) + 
                                            sum(len(actions) for actions in q2.values()))
            else:
                info["states_count"] = 0
                info["state_action_pairs"] = 0
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_growth_pattern(self, model_name: str) -> Dict:
        """分析特定模型的增长模式"""
        if model_name not in self.tracking_data["models"]:
            return {"error": f"模型 {model_name} 未找到跟踪记录"}
        
        snapshots = self.tracking_data["models"][model_name]["snapshots"]
        if len(snapshots) < 2:
            return {"error": "需要至少2个快照进行分析"}
        
        # 计算增长趋势
        analysis = {
            "total_snapshots": len(snapshots),
            "first_record": snapshots[0],
            "latest_record": snapshots[-1],
            "growth_analysis": {}
        }
        
        # 文件大小增长
        size_growth = snapshots[-1]["size"] - snapshots[0]["size"]
        size_growth_rate = size_growth / max(1, len(snapshots) - 1)
        
        analysis["growth_analysis"]["file_size"] = {
            "total_growth_bytes": size_growth,
            "total_growth_kb": round(size_growth / 1024, 2),
            "avg_growth_per_snapshot": round(size_growth_rate / 1024, 2),
            "growth_percentage": round((size_growth / max(1, snapshots[0]["size"])) * 100, 2)
        }
        
        # 学习进度增长
        game_growth = snapshots[-1]["game_count"] - snapshots[0]["game_count"]
        state_growth = snapshots[-1]["states_count"] - snapshots[0]["states_count"]
        
        analysis["growth_analysis"]["learning"] = {
            "game_count_growth": game_growth,
            "states_growth": state_growth,
            "win_rate_change": snapshots[-1]["win_rate"] - snapshots[0]["win_rate"],
            "epsilon_decay": snapshots[0]["epsilon"] - snapshots[-1]["epsilon"]
        }
        
        # 效率指标
        if game_growth > 0:
            analysis["growth_analysis"]["efficiency"] = {
                "size_per_game": round(size_growth / game_growth, 2),
                "states_per_game": round(state_growth / game_growth, 4),
                "avg_states_per_kb": round(state_growth / max(1, size_growth / 1024), 2)
            }
        
        # 增长阶段分析
        if len(snapshots) >= 4:
            mid_point = len(snapshots) // 2
            
            early_phase = snapshots[:mid_point]
            late_phase = snapshots[mid_point:]
            
            early_size_growth = early_phase[-1]["size"] - early_phase[0]["size"]
            late_size_growth = late_phase[-1]["size"] - late_phase[0]["size"]
            
            early_rate = early_size_growth / max(1, len(early_phase) - 1)
            late_rate = late_size_growth / max(1, len(late_phase) - 1)
            
            deceleration = ((early_rate - late_rate) / max(1, early_rate)) * 100 if early_rate > 0 else 0
            
            analysis["growth_analysis"]["phases"] = {
                "early_growth_rate_kb": round(early_rate / 1024, 2),
                "late_growth_rate_kb": round(late_rate / 1024, 2),
                "deceleration_percentage": round(deceleration, 2),
                "trend": "加速" if late_rate > early_rate * 1.1 else "减速" if deceleration > 20 else "稳定"
            }
        
        return analysis
    
    def generate_growth_report(self, model_name: str = None) -> str:
        """生成增长报告"""
        if model_name:
            return self._generate_single_model_report(model_name)
        else:
            return self._generate_all_models_report()
    
    def _generate_single_model_report(self, model_name: str) -> str:
        """生成单个模型的增长报告"""
        analysis = self.analyze_growth_pattern(model_name)
        
        if "error" in analysis:
            return f"❌ 无法生成报告: {analysis['error']}"
        
        report = []
        report.append(f"📊 {model_name} 增长分析报告")
        report.append("=" * 60)
        
        first = analysis["first_record"]
        latest = analysis["latest_record"]
        growth = analysis["growth_analysis"]
        
        report.append(f"🕐 首次记录: {first['timestamp'][:19]}")
        report.append(f"🕐 最新记录: {latest['timestamp'][:19]}")
        report.append(f"📈 总快照数: {analysis['total_snapshots']}")
        report.append("")
        
        # 文件大小增长
        size_info = growth["file_size"]
        report.append("📦 文件大小变化:")
        report.append(f"  初始大小: {first['size_kb']} KB")
        report.append(f"  当前大小: {latest['size_kb']} KB")
        report.append(f"  总增长: {size_info['total_growth_kb']} KB ({size_info['growth_percentage']}%)")
        report.append(f"  平均增长: {size_info['avg_growth_per_snapshot']} KB/快照")
        report.append("")
        
        # 学习进度
        learn_info = growth["learning"]
        report.append("🎯 学习进度变化:")
        report.append(f"  游戏局数: {first['game_count']} → {latest['game_count']} (+{learn_info['game_count_growth']})")
        report.append(f"  学习状态: {first['states_count']} → {latest['states_count']} (+{learn_info['states_growth']})")
        report.append(f"  胜率变化: {first['win_rate']}% → {latest['win_rate']}% ({learn_info['win_rate_change']:+.1f}%)")
        report.append(f"  探索率: {first['epsilon']:.4f} → {latest['epsilon']:.4f} (-{learn_info['epsilon_decay']:.4f})")
        report.append("")
        
        # 效率指标
        if "efficiency" in growth:
            eff_info = growth["efficiency"]
            report.append("⚡ 学习效率:")
            report.append(f"  文件增长率: {eff_info['size_per_game']:.2f} 字节/游戏")
            report.append(f"  状态发现率: {eff_info['states_per_game']:.4f} 状态/游戏")
            report.append(f"  状态密度: {eff_info['avg_states_per_kb']:.2f} 状态/KB")
            report.append("")
        
        # 增长阶段分析
        if "phases" in growth:
            phase_info = growth["phases"]
            report.append("📈 增长趋势分析:")
            report.append(f"  早期增长率: {phase_info['early_growth_rate_kb']} KB/快照")
            report.append(f"  后期增长率: {phase_info['late_growth_rate_kb']} KB/快照")
            report.append(f"  减速幅度: {phase_info['deceleration_percentage']:.1f}%")
            report.append(f"  增长趋势: {phase_info['trend']}")
            report.append("")
            
            # 解释趋势
            if phase_info['trend'] == "减速":
                report.append("💡 分析: 文件增长减速是正常现象，表明:")
                report.append("  • 模型正在收敛，发现新状态的频率降低")
                report.append("  • 探索率衰减，更多时间用于利用已学知识") 
                report.append("  • Q值趋于稳定，更新幅度减小")
            elif phase_info['trend'] == "加速":
                report.append("💡 分析: 文件增长加速可能表明:")
                report.append("  • 模型遇到了新的复杂情况")
                report.append("  • 学习参数可能需要调整")
                report.append("  • 正在探索新的状态空间")
            else:
                report.append("💡 分析: 文件增长稳定表明:")
                report.append("  • 模型学习过程平衡")
                report.append("  • 探索与利用达到良好平衡")
        
        return "\n".join(report)
    
    def _generate_all_models_report(self) -> str:
        """生成所有模型的概览报告"""
        report = []
        report.append("🤖 所有模型增长概览")
        report.append("=" * 60)
        
        for model_name, model_data in self.tracking_data["models"].items():
            if "latest" in model_data:
                latest = model_data["latest"]
                snapshots_count = len(model_data["snapshots"])
                
                report.append(f"\n📋 {model_name}:")
                report.append(f"  大小: {latest['size_kb']} KB")
                report.append(f"  游戏: {latest['game_count']:,} 局")
                report.append(f"  胜率: {latest['win_rate']:.1f}%")
                report.append(f"  状态: {latest['states_count']:,} 个")
                report.append(f"  快照: {snapshots_count} 次")
        
        return "\n".join(report)

def track_models_in_directory(models_dir: str = "models"):
    """跟踪目录中的所有模型文件"""
    tracker = ModelSizeTracker()
    
    if not os.path.exists(models_dir):
        print(f"❌ 模型目录不存在: {models_dir}")
        return
    
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
    
    if not model_files:
        print(f"❌ 在 {models_dir} 中未找到pkl模型文件")
        return
    
    print(f"🔍 跟踪 {len(model_files)} 个模型文件...")
    
    for model_file in model_files:
        model_path = os.path.join(models_dir, model_file)
        if tracker.record_model_snapshot(model_path, force=True):
            print(f"✅ 已记录: {model_file}")
        else:
            print(f"⚠️ 跳过: {model_file}")
    
    print("\n📊 生成增长报告:")
    print(tracker.generate_growth_report())

if __name__ == "__main__":
    # 跟踪所有模型
    track_models_in_directory() 