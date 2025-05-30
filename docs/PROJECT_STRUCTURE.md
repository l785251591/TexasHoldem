# 📁 德州扑克项目目录结构

## 🏗️ 项目结构概览

```
TexasHoldem/
├── 📁 poker_game/          # 核心游戏引擎
│   ├── __init__.py         # 包初始化
│   ├── game_engine.py      # 游戏引擎主逻辑
│   ├── player.py           # 玩家基类
│   ├── card.py             # 纸牌系统
│   ├── hand_evaluator.py   # 手牌评估器
│   ├── bot_players.py      # 规则机器人
│   ├── rl_bot.py           # 原版强化学习机器人
│   ├── improved_rl_bot.py  # 改进版强化学习机器人
│   ├── conservative_rl_bot.py # 保守版强化学习机器人
│   ├── training_tracker.py # 训练进度追踪器
│   ├── database.py         # 数据库管理
│   └── database_cleaner.py # 数据库清理工具
├── 📁 models/              # 强化学习模型文件
│   ├── rl_bot_model.pkl    # 原版机器人模型
│   ├── improved_rl_bot_model.pkl # 改进版机器人模型
│   ├── conservative_rl_bot_model.pkl # 保守版机器人模型 (自动生成)
│   └── rl_bot_model_bak.pkl # 模型备份文件
├── 📁 data/                # 数据存储
│   ├── poker_game.db       # 游戏数据库
│   └── training_history.json # 训练历史记录
├── 📁 scripts/             # 工具脚本
│   ├── demo.py             # 演示脚本
│   ├── compare_bots.py     # 机器人对比脚本
│   └── quick_train.py      # 快速训练脚本
├── 📁 tests/               # 测试文件
│   ├── test_permanent_training.py # 永久训练测试
│   └── test_training_tracker.py   # 训练追踪器测试
├── 📁 docs/                # 文档文件
│   ├── README.md           # 项目主文档
│   ├── TRAINING_GUIDE.md   # 训练指南
│   ├── PERMANENT_TRAINING_GUIDE.md # 永久训练指南
│   ├── TRAINING_PROGRESS_GUIDE.md  # 训练进度指南
│   ├── IMPROVED_RL_BOT_README.md   # 改进版机器人说明
│   ├── PERMANENT_TRAINING_README.md # 永久训练说明
│   ├── ERROR_EXPLANATION.md        # 错误说明
│   ├── BUG_FIX_SUMMARY.md         # 错误修复总结
│   └── SOLUTION_SUMMARY.md        # 解决方案总结
├── 📄 main.py              # 主程序入口
├── 📄 requirements.txt     # 依赖包列表
└── 📄 .gitignore          # Git忽略规则
```

## 📂 目录说明

### 🎮 `poker_game/` - 核心游戏引擎
包含游戏的所有核心逻辑和AI实现：

- **game_engine.py**: 德州扑克游戏主引擎
- **player.py**: 玩家基类和人类玩家实现
- **card.py**: 纸牌和牌组系统
- **hand_evaluator.py**: 手牌强度评估算法
- **bot_players.py**: 规则机器人（简单、中等、困难）
- **rl_bot.py**: 原版Q学习强化学习机器人
- **improved_rl_bot.py**: 改进版强化学习机器人（双Q学习+经验回放）
- **conservative_rl_bot.py**: 保守版强化学习机器人（风险控制）
- **training_tracker.py**: 训练进度追踪和分析系统
- **database.py**: SQLite数据库管理
- **database_cleaner.py**: 数据库维护和清理工具

### 🤖 `models/` - AI模型存储
存储所有强化学习机器人的训练模型：

- **rl_bot_model.pkl**: 原版Q学习机器人的模型文件
- **improved_rl_bot_model.pkl**: 改进版机器人的模型文件
- **conservative_rl_bot_model.pkl**: 保守版机器人的模型文件
- **rl_bot_model_bak.pkl**: 模型备份文件

### 💾 `data/` - 数据存储
存储游戏数据和训练历史：

- **poker_game.db**: SQLite数据库文件，存储游戏历史、学习数据等
- **training_history.json**: 训练过程的详细历史记录

### 🔧 `scripts/` - 工具脚本
包含各种实用脚本：

- **demo.py**: 游戏演示脚本
- **compare_bots.py**: 机器人性能对比分析
- **quick_train.py**: 快速训练脚本

### 🧪 `tests/` - 测试文件
包含单元测试和功能测试：

- **test_permanent_training.py**: 永久训练模式功能测试
- **test_training_tracker.py**: 训练追踪器功能测试

### 📖 `docs/` - 文档集合
包含所有项目文档：

- **README.md**: 项目主要说明文档
- **TRAINING_GUIDE.md**: 强化学习训练完整指南
- **PERMANENT_TRAINING_GUIDE.md**: 永久训练模式使用指南
- **TRAINING_PROGRESS_GUIDE.md**: 训练进度追踪使用指南
- 以及其他技术文档和说明

## 🚀 使用方法

### 快速开始
```bash
# 启动主程序
python main.py

# 运行演示
python scripts/demo.py

# 对比机器人性能
python scripts/compare_bots.py

# 快速训练
python scripts/quick_train.py
```

### 运行测试
```bash
# 测试永久训练功能
python tests/test_permanent_training.py

# 测试训练追踪器
python tests/test_training_tracker.py
```

## 📈 功能特性

### 🎯 主要功能
1. **多种游戏模式**: 人机对战、自动训练、永久训练
2. **三种强化学习AI**: 原版、改进版、保守版
3. **完整训练系统**: 进度追踪、数据分析、模型管理
4. **数据库管理**: 自动清理、性能优化
5. **可视化分析**: 胜率图表、趋势分析

### 🤖 AI机器人类型
- **🤖 原版强化学习机器人**: 基础Q学习算法
- **🚀 改进版强化学习机器人**: 双Q学习+经验回放+UCB探索
- **🛡️ 保守版强化学习机器人**: 风险控制+稳健策略
- **🔧 规则机器人**: 简单、中等、困难三个级别

## 🔄 迁移说明

### 从旧结构迁移
如果你正在从旧的文件结构迁移，请注意：

1. **模型文件**: 自动从 `models/` 目录加载
2. **数据库**: 自动从 `data/` 目录访问
3. **配置无需更改**: 程序自动适应新路径
4. **脚本路径**: 使用 `python scripts/script_name.py` 运行

### 手动迁移数据库
如果数据库文件被占用无法自动移动：
```bash
# 停止所有Python进程后
mv poker_game.db data/
# 或者在Windows中
move poker_game.db data/
```

## 🛠️ 开发说明

### 添加新功能
- **新机器人**: 在 `poker_game/` 目录添加新的AI类
- **新脚本**: 在 `scripts/` 目录添加工具脚本
- **新测试**: 在 `tests/` 目录添加测试文件
- **新文档**: 在 `docs/` 目录添加说明文档

### 代码规范
- 核心逻辑放在 `poker_game/` 包中
- 模型文件统一保存到 `models/` 目录
- 数据文件统一保存到 `data/` 目录
- 保持目录结构清晰，职责分明

---

🎉 **新的目录结构让项目更加清晰和易于维护！** 