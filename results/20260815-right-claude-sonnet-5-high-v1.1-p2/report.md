# 易语言大模型基准测试报告

- 运行编号：`20260815-right-claude-sonnet-5-high-v1.1-p2`
- 模型：`claude-sonnet-5`
- 推理等级：`high`
- 统一协议：`openai_responses`
- 外部传输协议：`anthropic_messages`
- 服务端模型标识：`claude-sonnet-5`
- 基准版本：`v1-compile`
- 评分版本：`v1.2-compile-gated`
- 运行状态：`complete`
- 总分：**9.50 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 有效格式 | 预编译结构 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw | 6.00 | 6.67 | 50.67 | 11/15 | 6.7% | 0.0% |
| skill | 13.00 | 13.33 | 59.07 | 9/14 | 13.3% | 6.7% |

Skill 增益：**+7.00**

## 能力分项

| 能力 | 得分 | 有效格式 | 预编译结构 | pass@1 |
| --- | ---: | ---: | ---: | ---: |
| 格式与工程 | 16.67 | 16.67 | 62.83 | 16.7% |
| 核心库指令 | 15.83 | 16.67 | 51.83 | 0.0% |
| 流程控制 | 0.00 | 0.00 | 43.00 | 0.0% |
| 子程序与数据结构 | 15.00 | 16.67 | 64.83 | 0.0% |
| 修复与综合 | 0.00 | 0.00 | 51.83 | 0.0% |

## 失败分布

- 回包尝试：`29` 次，失败 `20` 次，累计预编译结构分扣除 `300` 分。
- 编译硬门槛/失败原因：`validation_failed` 17，`compile_failed` 6，`none` 3，`pack_failed` 3，`contract_invalid` 1
- 回包失败根因：`source_preflight_failed` 17，`semantic_method_rebuild_failed` 3，`other` 1

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 有效格式 | 预编译结构 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 0.00 | 0.00 | 46.00 | 0 | 0.00 | validation_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 90.00 | 100.00 | 100.00 | 100 | 50.00 | FAIL |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 0.00 | 0.00 | 33.00 | 0 | 0.00 | validation_failed |
| core-01 核心文本处理 | raw | 核心库指令 | 0.00 | 0.00 | 46.00 | 0 | 0.00 | validation_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 0.00 | 0.00 | 46.00 | 0 | 0.00 | validation_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 0.00 | 0.00 | 28.00 | 0 | 0.00 | validation_failed |
| core-02 数值核心命令 | skill | 核心库指令 | 95.00 | 100.00 | 100.00 | 100 | 75.00 | FAIL |
| core-03 动态数组核心命令 | raw | 核心库指令 | 0.00 | 0.00 | 46.00 | 0 | 0.00 | validation_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 0.00 | 0.00 | 45.00 | 0 | 0.00 | validation_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 0.00 | 0.00 | 37.00 | 0 | 0.00 | validation_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 0.00 | 0.00 | 37.00 | 0 | 0.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 0.00 | 0.00 | 19.00 | 0 | 0.00 | validation_failed |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 100.00 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 0.00 | 0.00 | 37.00 | 0 | 0.00 | validation_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 0.00 | 0.00 | 35.00 | 0 | 0.00 | validation_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 0.00 | 0.00 | 50.00 | 0 | 0.00 | validation_failed |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 0.00 | 0.00 | 37.00 | 0 | 0.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 0.00 | 0.00 | 19.00 | 0 | 0.00 | validation_failed |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 0.00 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。预编译结构分覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。源码只有通过真实编译后才能获得有效格式分、语义分和总分。
