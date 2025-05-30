# 🎰 德州扑克强化学习AI项目

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![RL](https://img.shields.io/badge/RL-Q%20Learning-orange.svg)](#强化学习算法)

一个完整的德州扑克游戏实现，支持人类玩家和多种智能AI机器人，特别专注于强化学习AI的训练和分析。

## 🌟 项目特色

### 🤖 多样化AI机器人
- **传统AI机器人**：简单、中等、困难三个难度等级
- **强化学习机器人**：基于Q-Learning的自学习AI
- **抽象基类架构**：支持配置驱动的不同策略机器人

### 🧠 强化学习功能
- **Q-Learning算法**：支持单Q表和双Q学习
- **经验回放**：提升学习效率
- **增强状态表示**：考虑位置、对手数量、游戏阶段等因素
- **动态动作空间**：根据游戏状态智能调整可选动作
- **差异化奖励函数**：针对不同策略风格优化

### 📊 训练分析工具
- **模型分析器**：分析模型文件大小、学习进度
- **训练跟踪**：记录训练历史和性能指标
- **可视化工具**：展示学习曲线和统计数据

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基础游戏
```bash
python main.py
```

### 强化学习训练
```python
from poker_game import RLBotFactory

# 创建不同风格的机器人
conservative_bot = RLBotFactory.create_bot('conservative', 'c1', '保守派')
aggressive_bot = RLBotFactory.create_bot('aggressive', 'a1', '激进派')
improved_bot = RLBotFactory.create_bot('improved', 'i1', '改进版')

# 开始训练
game = PokerGame([conservative_bot, aggressive_bot, improved_bot])
game.start_game()
```

## 🏗️ 项目架构

### 核心模块
```
poker_game/
├── base_rl_bot.py          # 强化学习抽象基类
├── rl_bot_configs.py       # 机器人配置集合
├── rl_bot_factory.py       # 机器人工厂
├── rl_bot_new.py          # 原版强化学习机器人
├── improved_rl_bot_new.py  # 改进版强化学习机器人
├── conservative_rl_bot_new.py # 保守版强化学习机器人
├── model_analyzer.py       # 模型分析工具
├── training_tracker.py     # 训练跟踪器
├── game_engine.py         # 游戏引擎
├── player.py             # 玩家基类
└── hand_evaluator.py     # 手牌评估器
```

### 分析工具
```
├── analyze_models.py      # 模型文件分析脚本
├── show_stats.py         # 统计数据展示脚本
└── docs/                 # 项目文档
```

## 🎮 游戏功能

### 完整的德州扑克实现
- **标准规则**：支持标准德州扑克规则
- **多人游戏**：支持2-8人游戏
- **盲注系统**：大盲注、小盲注自动轮换
- **边池分配**：正确处理全押情况下的边池

### 智能AI系统
- **规则AI**：基于固定策略的传统AI
- **学习AI**：基于强化学习的自适应AI
- **混合对战**：支持人类与AI混合游戏

## 🧠 强化学习算法

### 核心算法
- **Q-Learning**：值函数学习
- **Double Q-Learning**：减少过度估计偏差
- **Experience Replay**：经验回放机制
- **ε-贪婪策略**：平衡探索与利用

### 状态表示
- **基础状态**：手牌强度、底池赔率、对手数量
- **增强状态**：位置信息、游戏阶段、下注压力、底池相对大小

### 动作空间
- **静态动作**：弃牌、跟注、加注、全押
- **动态动作**：根据底池大小智能调整加注金额

### 奖励设计
#### 原版机器人（简单ROI）
```python
if 获胜:
    reward = min(10.0, winnings / 投入)
else:
    reward = -投入 / 总筹码
```

#### 改进版机器人（多维度奖励）
```python
reward = 基础胜负奖励 + 决策质量奖励 + 生存奖励 + 适应性奖励
```

#### 保守版机器人（保守策略）
```python
reward = 基础奖励 + 保守决策奖励 + 筹码管理奖励 + 一致性奖励
```

## 📊 性能分析

### 模型分析
```bash
python analyze_models.py
```
- 文件大小分析
- Q表增长趋势
- 学习效率评估

### 统计展示
```bash
python show_stats.py
```
- 胜率统计
- 平均奖励
- 探索率变化
- 学习状态数量

### 训练跟踪
```python
from poker_game import TrainingTracker

tracker = TrainingTracker()
tracker.plot_training_history()  # 可视化训练历史
```

## 🔧 配置系统

### 预定义配置
- **original**：保守学习，基础功能
- **improved**：激进学习，全部功能
- **conservative**：稳健学习，保守策略
- **aggressive**：极度激进，高风险高回报
- **tight**：极度保守，只玩强牌
- **bluff**：诈唬型，善于心理战
- **adaptive**：适应型，善于适应对手
- **experimental**：实验性配置

### 自定义配置
```python
from poker_game import RLBotConfig, RLBotFactory

custom_config = RLBotConfig(
    epsilon=0.25,
    learning_rate=0.015,
    aggression_threshold=0.45,
    max_bet_ratio=0.6,
    use_double_q_learning=True,
    use_experience_replay=True
)

bot = RLBotFactory.create_custom_bot('custom1', '自定义机器人', config=custom_config)
```

## 📈 训练建议

### 初期训练（探索阶段）
- 高探索率（ε=0.3-0.5）
- 较高学习率（α=0.01-0.02）
- 启用经验回放

### 中期训练（学习阶段）
- 中等探索率（ε=0.1-0.3）
- 适中学习率（α=0.005-0.015）
- 双Q学习 + 经验回放

### 后期训练（收敛阶段）
- 低探索率（ε=0.05-0.1）
- 低学习率（α=0.001-0.008）
- 专注利用已学知识

## 🔍 模型文件分析

### 文件大小变化
- **初期快速增长**：发现大量新状态
- **中期增长放缓**：重复状态增多
- **后期趋于稳定**：模型收敛

### 这是否意味着学习效率降低？
**答案：不是！** 这是**收敛的正面信号**：
- ✅ 模型已探索大部分重要状态
- ✅ 从探索转向利用，提高决策质量
- ✅ 不再浪费时间在无关紧要的新状态上

## 📁 数据文件

### 模型文件 (`models/`)
- `*.pkl`：训练好的机器人模型
- 包含Q表、统计数据、配置信息

### 训练数据 (`data/`)
- 游戏历史记录
- 性能统计数据
- 训练轨迹

### 分析结果
- `training_history.json`：训练历史
- `model_size_tracking.json`：模型大小跟踪

## 🛠️ 开发工具

### 测试脚本
```bash
# 测试新架构
python test_new_architecture.py

# 性能基准测试
python scripts/benchmark.py

# 模型对比
python scripts/model_comparison.py
```

### 调试工具
```python
from poker_game import ModelAnalyzer

analyzer = ModelAnalyzer()
analysis = analyzer.analyze_model_file('models/improved_rl_bot_model.pkl')
print(analyzer._format_analysis_report(analysis))
```

## 🤝 贡献指南

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📝 更新日志

### v2.0.0 (最新)
- ✨ 新增抽象基类架构
- ✨ 配置驱动的机器人创建
- ✨ 8种预定义机器人配置
- ✨ 工厂模式支持
- ✨ 模型分析工具
- ✨ 训练跟踪系统
- 🐛 修复Q值溢出问题
- 🐛 优化内存使用
- 📊 增强统计功能

### v1.0.0
- 🎯 基础德州扑克游戏
- 🤖 传统AI机器人
- 🧠 基础强化学习实现

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有为强化学习理论做出贡献的研究者
- 感谢Python社区提供的优秀工具和库
- 感谢所有测试和反馈的用户

## 📞 联系方式

- 项目问题：请在GitHub Issues中提出
- 功能建议：欢迎通过Pull Request贡献

---

**🎰 愿你在德州扑克的AI世界中收获满满！** 🚀 