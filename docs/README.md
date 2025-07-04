# 🎲 德州扑克游戏 (Texas Hold'em Poker)

一个功能完整的德州扑克游戏，支持人类玩家与多种AI机器人对战，特别针对强化学习机器人训练进行了优化。

## 🌟 主要特性

### 🎮 游戏模式
- **人机对战**: 人类玩家与AI机器人对战
- **自动训练模式**: 机器人之间自动对战训练
- **🔄 永久自动训练模式**: 无限循环训练，自动重开新局

### 🤖 AI机器人类型
- **简单机器人**: 基础策略，适合新手练习
- **中等机器人**: 中等难度，平衡的游戏策略
- **困难机器人**: 高级策略，挑战性对手
- **强化学习机器人**: 基于Q-Learning的自学习AI

### 📊 数据管理
- **游戏数据库**: SQLite数据库存储游戏历史
- **智能清理**: 自动清理历史数据，防止数据库过大
- **学习数据**: 记录强化学习机器人的训练过程

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行游戏
```bash
python main.py
```

### 游戏菜单
1. **开始新游戏** - 创建人机对战游戏
2. **自动训练模式** - 设定轮数的机器人训练
3. **🔄 永久自动训练模式** - 无限循环训练
4. **查看游戏统计** - 查看游戏数据
5. **查看强化学习机器人状态** - 查看AI学习进度
6. **查看游戏历史** - 浏览历史记录
7. **🗃️ 数据库管理** - 管理游戏数据
8. **退出**

## 🔄 永久自动训练模式

### 特色功能
- ✅ **无限循环训练**: 自动重开新局，无需手动干预
- ✅ **智能数据管理**: 数据库超过10MB自动清理
- ✅ **定期模型保存**: 可配置保存间隔
- ✅ **实时监控**: 显示训练进度和机器人状态
- ✅ **优雅停止**: 支持Ctrl+C停止并保存模型

### 使用方法
1. 选择菜单选项3
2. 配置训练参数：
   - 模型保存间隔（推荐50-100手）
   - 数据清理间隔（推荐1000-5000手）
   - 强化学习机器人数量（1-4个）
3. 开始训练，按Ctrl+C停止

### 数据库自动清理
- **触发条件**: 数据库超过10MB或达到清理间隔
- **清理策略**: 按大小清理，保留最新数据
- **清理效果**: 自动将数据库减小到目标大小的80%

## 🏗️ 项目结构

```
TexasHoldem/
├── main.py                          # 主程序入口
├── poker_game/                      # 游戏核心模块
│   ├── __init__.py                 # 模块初始化
│   ├── game.py                     # 游戏逻辑
│   ├── player.py                   # 玩家基类
│   ├── human_player.py             # 人类玩家
│   ├── bot_players.py              # AI机器人
│   ├── rl_bot.py                   # 强化学习机器人
│   ├── card.py                     # 扑克牌类
│   ├── hand_evaluator.py           # 牌型评估
│   ├── database.py                 # 数据库管理
│   └── database_cleaner.py         # 数据库清理
├── PERMANENT_TRAINING_README.md     # 永久训练模式文档
├── requirements.txt                 # 依赖包列表
├── .gitignore                      # Git忽略文件
└── README.md                       # 项目说明
```

## 🤖 强化学习机器人

### 技术特点
- **算法**: Q-Learning强化学习
- **状态空间**: 手牌强度、位置、筹码比例等
- **动作空间**: 弃牌、跟注、加注
- **学习策略**: ε-贪婪策略，动态调整探索率

### 学习数据
- Q表大小：学习到的状态数量
- 探索率(ε)：探索vs利用的平衡
- 记忆大小：经验回放缓冲区大小
- 学习记录：动作、奖励、手牌强度等

## 📈 性能优化

### 训练优化
- **快速模式**: 跳过人工等待，最大化训练速度
- **筹码平衡**: 自动重新分配筹码，保持训练连续性
- **异常处理**: 错误恢复机制，确保训练稳定性

### 数据库优化
- **按大小清理**: 精确控制数据库大小
- **VACUUM操作**: 自动回收存储空间
- **批量操作**: 提高数据库操作效率

## 🛠️ 技术栈

- **Python 3.7+**: 主要编程语言
- **SQLite**: 轻量级数据库
- **NumPy**: 数值计算（如果使用）
- **面向对象设计**: 清晰的代码结构

## 📋 系统要求

- Python 3.7或更高版本
- 至少100MB可用磁盘空间
- 支持Windows、macOS、Linux

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🎯 未来计划

- [ ] 添加更多AI算法（深度Q网络、策略梯度等）
- [ ] 实现多人在线对战
- [ ] 添加图形用户界面
- [ ] 支持锦标赛模式
- [ ] 添加更多扑克变体

---

**享受德州扑克的乐趣，见证AI的学习成长！** 🎲🤖 