你现在负责实现当前仓库中的“生物医学 Reusability Report 候选闸门”。

先完整阅读：

`docs/superpowers/plans/2026-07-22-biomed-reusability-gate.md`

然后严格执行以下要求：

1. 先检查 Git、Python、uv、Docker/Apptainer、GPU、磁盘和当前仓库状态，生成 `reports/environment_inventory.md`。
2. 创建 `docs/progress.md`，把主计划中的 Common Task 1–18 以及三个条件分支任务登记成复选框。
3. 严格执行测试驱动开发：生产代码之前先写会因功能缺失而失败的最小测试；实际运行确认 RED；再写最小实现；确认 GREEN；运行全量 unit tests、Ruff 和 mypy；最后提交。
4. 不允许补写测试，不允许未观察 RED 就实现，不允许用测试数据做调参、早停、特征选择、标准化拟合或校准。
5. 单元测试不联网、不使用 GPU、不下载完整数据。联网测试标记 `integration`；GPU 测试同时标记 `gpu`；昂贵测试标记 `slow`。
6. 不直接假设主项目。严格执行候选优先级：
   - 先完成 NicheTrans 可行性门槛；
   - NicheTrans 全部门槛通过就选 NicheTrans，并停止其他候选的默认执行；
   - NicheTrans 失败才评估 Squidiff；
   - Squidiff 失败才评估 CMonge；
   - 全部失败则输出 `NO_GO`。
7. 上游仓库首次成功解析后立即固定精确 commit，并写入 `vendor/manifests/`。不得持续跟随 main。
8. 不修改上游科学实现。兼容补丁放到 `vendor/patches/<candidate>/`，必须有回归测试和说明。
9. 每个候选失败时，先生成完整 feasibility report，再转向下一候选。
10. `reports/selection_decision.json` 生成后不可覆盖。需要改变结论时创建 amendment 文件。
11. 只允许被选中的候选执行 Tier 0。只有 Tier 0 满足计划中的 GO 条件才执行 Tier 1。
12. 每个任务完成后更新 `docs/progress.md`，记录：
    - 失败测试命令和失败原因；
    - 通过命令；
    - 生成文件；
    - 数据/上游 checksum；
    - Git commit SHA；
    - 未解决风险。
13. 遇到次要实现不确定性时，采用最保守且可审计的方案，不要频繁请求确认。遇到会改变研究问题的阻断事项时，停止该候选并写入 feasibility report。
14. 现在开始执行 Task 1：仓库脚手架与严格模式定义。
