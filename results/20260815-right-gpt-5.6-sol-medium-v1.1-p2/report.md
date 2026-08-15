# 易语言大模型基准测试报告

- 运行编号：`20260815-right-gpt-5.6-sol-medium-v1.1-p2`
- 模型：`gpt-5.6-sol`
- 推理等级：`medium`
- 统一协议：`openai_responses`
- 外部传输协议：`openai_responses`
- 服务端模型标识：`gpt-5.6-sol`
- 基准版本：`v1-compile`
- 评分版本：`v1.1-pack-failure-count`
- 运行状态：`complete`
- 总分：**58.67 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 格式分 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw | 53.67 | 74.93 | 5/14 | 20.0% | 6.7% |
| skill | 63.67 | 88.27 | 3/15 | 26.7% | 20.0% |

Skill 增益：**+10.00**

## 能力分项

| 能力 | 得分 | 格式分 | pass@1 |
| --- | ---: | ---: | ---: |
| 格式与工程 | 52.87 | 75.17 | 16.7% |
| 核心库指令 | 62.50 | 100.00 | 0.0% |
| 流程控制 | 27.32 | 46.17 | 0.0% |
| 子程序与数据结构 | 86.67 | 100.00 | 50.0% |
| 修复与综合 | 64.00 | 86.67 | 0.0% |

## 失败分布

- 回包尝试：`29` 次，失败 `8` 次，累计格式原始分扣除 `120` 分。
- 总分上限原因：`compile_failed` 12，`none` 7，`validation_failed` 6，`pack_failed` 2，`contract_invalid` 1，`packed_project_unusable` 2
- 回包失败根因：`source_preflight_failed` 6，`other` 2，`semantic_method_rebuild_failed` 1

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 格式 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 90.00 | 100.00 | 100 | 50.00 | FAIL |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| core-01 核心文本处理 | raw | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-02 数值核心命令 | skill | 核心库指令 | 60.00 | 100.00 | 0 | 75.00 | compile_failed |
| core-03 动态数组核心命令 | raw | 核心库指令 | 55.00 | 100.00 | 0 | 50.00 | compile_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 27.10 | 38.00 | 0 | 50.00 | validation_failed |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 55.00 | 100.00 | 0 | 50.00 | compile_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 30.70 | 46.00 | 0 | 50.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 29.00 | 55.00 | 0 | 50.00 | pack_failed |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 22.10 | 38.00 | 0 | 25.00 | validation_failed |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 29.00 | 55.00 | 0 | 100.00 | pack_failed |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 32.50 | 50.00 | 0 | 50.00 | validation_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 25.70 | 46.00 | 0 | 25.00 | validation_failed |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 95.00 | 100.00 | 100 | 75.00 | FAIL |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 95.00 | 100.00 | 100 | 75.00 | FAIL |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 37.50 | 50.00 | 0 | 75.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 48.25 | 85.00 | 0 | 50.00 | packed_project_unusable |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 43.25 | 85.00 | 0 | 25.00 | packed_project_unusable |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。格式分已经覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。
