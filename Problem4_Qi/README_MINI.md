---
noteId: "d2ef0c9021cd11f1818e37f92666e700"
tags: []

---

# Problem4_Qi 最小可用说明

本目录文件较多，推荐仅关注以下“核心最小集”：

- `problem4_cmaes_optimization.py` 核心优化器（CMA-ES + 物理仿真）
- `hierarchical_drone_optimizer.py` 分层协同优化（先单/双机，再协调）
- `main.py` 统一入口：
  - `python main.py single` 运行一次默认 CMA-ES 优化
  - `python main.py hier`   运行分层协同优化

可暂时忽略（非必须）的文件：
- `*_test.py`, `tests/`：单元/集成测试
- `*_notes.py`, `*_plan.py`, `docs/`, `README.md`：文档/说明/计划
- `visual_*.py`, `generate_fixed_plot.py`：可视化脚本
- `parallel_*`, `quick_*`, `enhanced_*`：扩展/并行/快速版本
- `results/`：运行结果

如需进一步“瘦身”，可以将上面“可忽略”文件移动到 `archive/`，不影响核心功能。
