#!/usr/bin/env python3
"""
数据库清理模块
提供自动清理过多游戏记录的功能
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Any

class DatabaseCleaner:
    """数据库清理器"""
    
    # 清理阈值配置 - 针对强化学习训练优化
    SIZE_THRESHOLDS = {
        'critical': 20 * 1024 * 1024,     # 20MB - 立即清理
        'large': 10 * 1024 * 1024,        # 10MB - 建议清理
        'medium': 5 * 1024 * 1024,        # 5MB - 可以清理
        'small': 2 * 1024 * 1024          # 2MB - 暂不需要
    }
    
    RECORD_THRESHOLDS = {
        'critical': 50000,      # 5万条记录 - 立即清理
        'large': 25000,         # 2.5万条记录 - 建议清理
        'medium': 10000,        # 1万条记录 - 可以清理
        'small': 5000           # 5千条记录 - 暂不需要
    }
    
    def __init__(self, db_path: str = "data/poker_game.db"):
        self.db_path = db_path
    
    def check_database_status(self) -> Dict[str, Any]:
        """检查数据库状态"""
        if not os.path.exists(self.db_path):
            return {'exists': False}
        
        file_size = os.path.getsize(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 统计各表记录数
        tables_info = {}
        total_records = 0
        
        for table in ['games', 'hands', 'player_actions', 'bot_learning_data']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                tables_info[table] = count
                total_records += count
            except:
                tables_info[table] = 0
        
        # 获取时间范围
        time_ranges = {}
        for table, time_col in [
            ('hands', 'timestamp'),
            ('player_actions', 'timestamp'),  
            ('bot_learning_data', 'timestamp')
        ]:
            try:
                cursor.execute(f"SELECT MIN({time_col}), MAX({time_col}) FROM {table}")
                min_time, max_time = cursor.fetchone()
                if min_time and max_time:
                    time_ranges[table] = {'min': min_time, 'max': max_time}
            except:
                pass
        
        conn.close()
        
        # 评估清理需求
        size_level = self._get_threshold_level(file_size, self.SIZE_THRESHOLDS)
        record_level = self._get_threshold_level(total_records, self.RECORD_THRESHOLDS)
        
        return {
            'exists': True,
            'file_size': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'total_records': total_records,
            'tables_info': tables_info,
            'time_ranges': time_ranges,
            'size_level': size_level,
            'record_level': record_level,
            'needs_cleaning': size_level in ['large', 'critical'] or record_level in ['large', 'critical']
        }
    
    def _get_threshold_level(self, value: int, thresholds: Dict[str, int]) -> str:
        """根据阈值判断级别"""
        if value >= thresholds['critical']:
            return 'critical'
        elif value >= thresholds['large']:
            return 'large'
        elif value >= thresholds['medium']:
            return 'medium'
        else:
            return 'small'
    
    def auto_clean_if_needed(self) -> Dict[str, Any]:
        """自动检查并清理数据库"""
        status = self.check_database_status()
        
        if not status['exists']:
            return {'cleaned': False, 'reason': '数据库不存在'}
        
        if not status['needs_cleaning']:
            return {
                'cleaned': False, 
                'reason': f"数据库大小适中 ({status['file_size_mb']:.1f}MB, {status['total_records']:,}条记录)"
            }
        
        # 根据级别选择清理策略 - 针对强化学习训练优化
        size_mb = status['file_size_mb']
        
        if size_mb >= 100:
            # 数据库超过100MB，极度激进清理，只保留最近1天
            days_to_keep = 1
        elif status['size_level'] == 'critical' or status['record_level'] == 'critical':
            # 严重超限，保留最近3天
            days_to_keep = 3
        elif status['size_level'] == 'large' or status['record_level'] == 'large':
            # 超限，保留最近7天
            days_to_keep = 7
        else:
            # 中等，保留最近14天
            days_to_keep = 14
        
        return self.clean_old_data(days_to_keep)
    
    def clean_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """清理指定天数之前的数据"""
        if not os.path.exists(self.db_path):
            return {'success': False, 'error': '数据库不存在'}
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cleaned_counts = {}
        
        try:
            # 清理bot_learning_data（通常最多）
            cursor.execute("SELECT COUNT(*) FROM bot_learning_data WHERE timestamp < ?", (cutoff_str,))
            old_learning_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM bot_learning_data WHERE timestamp < ?", (cutoff_str,))
            cleaned_counts['bot_learning_data'] = old_learning_count
            
            # 清理player_actions
            cursor.execute("SELECT COUNT(*) FROM player_actions WHERE timestamp < ?", (cutoff_str,))
            old_actions_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM player_actions WHERE timestamp < ?", (cutoff_str,))
            cleaned_counts['player_actions'] = old_actions_count
            
            # 清理hands
            cursor.execute("SELECT COUNT(*) FROM hands WHERE timestamp < ?", (cutoff_str,))
            old_hands_count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM hands WHERE timestamp < ?", (cutoff_str,))
            cleaned_counts['hands'] = old_hands_count
            
            # 清理games（如果有start_time字段）
            try:
                cursor.execute("SELECT COUNT(*) FROM games WHERE start_time < ?", (cutoff_str,))
                old_games_count = cursor.fetchone()[0]
                
                cursor.execute("DELETE FROM games WHERE start_time < ?", (cutoff_str,))
                cleaned_counts['games'] = old_games_count
            except:
                cleaned_counts['games'] = 0
            
            # 提交删除操作
            conn.commit()
            
            # 关闭连接，然后重新打开执行VACUUM（VACUUM不能在事务中执行）
            conn.close()
            
            # 重新连接执行VACUUM来回收空间
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("VACUUM")
            conn.close()
            
            # 获取清理后的状态
            new_status = self.check_database_status()
            
            result = {
                'success': True,
                'days_kept': days_to_keep,
                'cutoff_date': cutoff_str,
                'cleaned_counts': cleaned_counts,
                'total_cleaned': sum(cleaned_counts.values()),
                'before_size_mb': None,  # 需要在清理前记录
                'after_size_mb': new_status['file_size_mb'],
                'after_records': new_status['total_records']
            }
            
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            result = {
                'success': False,
                'error': str(e)
            }
        
        finally:
            try:
                conn.close()
            except:
                pass
        
        return result
    
    def get_cleaning_recommendation(self) -> str:
        """获取清理建议"""
        status = self.check_database_status()
        
        if not status['exists']:
            return "数据库不存在"
        
        size_mb = status['file_size_mb']
        records = status['total_records']
        
        recommendations = []
        
        # 基于文件大小的建议 - 针对强化学习训练优化
        if size_mb >= 100:
            recommendations.append(f"🚨 数据库极大 ({size_mb:.1f}MB)，立即激进清理，只保留最近1天数据")
        elif size_mb >= 20:
            recommendations.append(f"📦 数据库过大 ({size_mb:.1f}MB)，建议立即清理，保留最近3天数据")
        elif size_mb >= 10:
            recommendations.append(f"⚠️  数据库偏大 ({size_mb:.1f}MB)，建议清理，保留最近7天数据")
        elif size_mb >= 5:
            recommendations.append(f"💡 数据库适中 ({size_mb:.1f}MB)，可考虑清理，保留最近14天数据")
        else:
            recommendations.append(f"✅ 数据库较小 ({size_mb:.1f}MB)，暂不需要清理")
        
        # 基于记录数的建议 - 针对强化学习训练优化
        if records >= 50000:
            recommendations.append(f"📊 记录数过多 ({records:,})，强烈建议清理")
        elif records >= 25000:
            recommendations.append(f"📊 记录数较多 ({records:,})，建议清理")
        elif records >= 10000:
            recommendations.append(f"📊 记录数适中 ({records:,})，可考虑清理")
        else:
            recommendations.append(f"📊 记录数较少 ({records:,})，暂不需要清理")
        
        return "\n".join(recommendations)
    
    def print_status_report(self):
        """打印详细的状态报告"""
        status = self.check_database_status()
        
        if not status['exists']:
            print("❌ 数据库文件不存在")
            return
        
        print("=" * 60)
        print("🗃️  数据库状态报告")
        print("=" * 60)
        print(f"📄 文件大小: {status['file_size_mb']:.2f} MB")
        print(f"📊 总记录数: {status['total_records']:,}")
        print()
        
        print("📋 各表记录数:")
        for table, count in status['tables_info'].items():
            print(f"  {table}: {count:,}")
        print()
        
        if status['time_ranges']:
            print("⏰ 数据时间范围:")
            for table, time_range in status['time_ranges'].items():
                print(f"  {table}: {time_range['min']} ~ {time_range['max']}")
            print()
        
        print("💡 清理建议:")
        print(self.get_cleaning_recommendation())
        print()
        
        if status['needs_cleaning']:
            print("🚀 推荐操作: 运行 clean_old_data() 进行清理")
        else:
            print("😊 当前状态良好，无需清理")
    
    def clean_by_size(self, target_size_mb: float = 10.0) -> Dict[str, Any]:
        """按目标大小清理数据库 - 专为永久训练模式设计"""
        if not os.path.exists(self.db_path):
            return {'success': False, 'error': '数据库不存在'}
        
        status = self.check_database_status()
        current_size_mb = status['file_size_mb']
        
        if current_size_mb <= target_size_mb:
            return {
                'success': True,
                'cleaned': False,
                'reason': f"数据库大小 ({current_size_mb:.1f}MB) 已在目标范围内 (≤{target_size_mb}MB)"
            }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cleaned_counts = {}
        
        try:
            # 计算需要删除的比例，目标是将数据库减小到目标大小的80%
            target_reduction = (current_size_mb - target_size_mb * 0.8) / current_size_mb
            target_reduction = max(0.1, min(0.9, target_reduction))  # 限制在10%-90%之间
            
            # 按表的大小顺序清理，优先清理最大的表
            tables_to_clean = [
                ('bot_learning_data', 'timestamp'),
                ('player_actions', 'timestamp'),
                ('hands', 'timestamp')
            ]
            
            for table, time_col in tables_to_clean:
                # 获取表的总记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_count = cursor.fetchone()[0]
                
                if total_count == 0:
                    cleaned_counts[table] = 0
                    continue
                
                # 计算要删除的记录数
                records_to_delete = int(total_count * target_reduction)
                
                if records_to_delete > 0:
                    # 删除最旧的记录
                    cursor.execute(f"""
                        DELETE FROM {table} 
                        WHERE rowid IN (
                            SELECT rowid FROM {table} 
                            ORDER BY {time_col} ASC 
                            LIMIT ?
                        )
                    """, (records_to_delete,))
                    
                    cleaned_counts[table] = records_to_delete
                else:
                    cleaned_counts[table] = 0
            
            # 清理games表（如果有的话）
            try:
                cursor.execute("SELECT COUNT(*) FROM games")
                games_count = cursor.fetchone()[0]
                if games_count > 0:
                    games_to_delete = int(games_count * target_reduction)
                    if games_to_delete > 0:
                        cursor.execute("""
                            DELETE FROM games 
                            WHERE rowid IN (
                                SELECT rowid FROM games 
                                ORDER BY start_time ASC 
                                LIMIT ?
                            )
                        """, (games_to_delete,))
                        cleaned_counts['games'] = games_to_delete
                    else:
                        cleaned_counts['games'] = 0
                else:
                    cleaned_counts['games'] = 0
            except:
                cleaned_counts['games'] = 0
            
            # 提交删除操作
            conn.commit()
            conn.close()
            
            # 重新连接执行VACUUM来回收空间
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("VACUUM")
            conn.close()
            
            # 获取清理后的状态
            new_status = self.check_database_status()
            
            result = {
                'success': True,
                'cleaned': True,
                'target_size_mb': target_size_mb,
                'before_size_mb': current_size_mb,
                'after_size_mb': new_status['file_size_mb'],
                'reduction_percentage': target_reduction * 100,
                'cleaned_counts': cleaned_counts,
                'total_cleaned': sum(cleaned_counts.values()),
                'before_records': status['total_records'],
                'after_records': new_status['total_records']
            }
            
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            result = {
                'success': False,
                'error': str(e)
            }
        
        finally:
            try:
                conn.close()
            except:
                pass
        
        return result
    
    def auto_clean_for_training(self, target_size_mb: float = 10.0) -> Dict[str, Any]:
        """专为永久训练模式设计的自动清理"""
        status = self.check_database_status()
        
        if not status['exists']:
            return {'cleaned': False, 'reason': '数据库不存在'}
        
        current_size_mb = status['file_size_mb']
        
        if current_size_mb <= target_size_mb:
            return {
                'cleaned': False,
                'reason': f"数据库大小适中 ({current_size_mb:.1f}MB ≤ {target_size_mb}MB)"
            }
        
        return self.clean_by_size(target_size_mb)

def main():
    """主函数 - 可以直接运行进行检查"""
    cleaner = DatabaseCleaner()
    cleaner.print_status_report()
    
    # 询问是否自动清理
    status = cleaner.check_database_status()
    if status.get('needs_cleaning', False):
        response = input("\n是否执行自动清理? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n开始清理...")
            result = cleaner.auto_clean_if_needed()
            if result['cleaned']:
                print(f"✅ 清理完成!")
                print(f"保留天数: {result['days_kept']}")
                print(f"清理记录数: {result['total_cleaned']:,}")
                print(f"清理后大小: {result['after_size_mb']:.2f} MB")
                print(f"清理后记录数: {result['after_records']:,}")
            else:
                print(f"ℹ️  {result['reason']}")

if __name__ == "__main__":
    main() 