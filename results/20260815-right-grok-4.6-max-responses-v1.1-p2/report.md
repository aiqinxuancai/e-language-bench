# 易语言大模型基准测试报告

- 运行编号：`20260815-right-grok-4.6-max-responses-v1.1-p2`
- 模型：`grok-4.6`
- 推理等级：`max`
- 统一协议：`openai_responses`
- 外部传输协议：`openai_responses`
- 服务端模型标识：`grok-4.6`
- 基准版本：`v1-compile`
- 评分版本：`v1.1-pack-failure-count`
- 运行状态：`complete`
- 总分：**18.42 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 格式分 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw | 15.27 | 19.87 | 14/15 | 6.7% | 6.7% |
| skill | 21.58 | 22.77 | 11/12 | 6.7% | 6.7% |

Skill 增益：**+6.31**

## 能力分项

| 能力 | 得分 | 格式分 | pass@1 |
| --- | ---: | ---: | ---: |
| 格式与工程 | 37.95 | 41.75 | 33.3% |
| 核心库指令 | 14.52 | 13.75 | 0.0% |
| 流程控制 | 10.93 | 11.33 | 0.0% |
| 子程序与数据结构 | 19.59 | 23.17 | 0.0% |
| 修复与综合 | 9.13 | 16.58 | 0.0% |

## 失败分布

- 回包尝试：`27` 次，失败 `25` 次，累计格式原始分扣除 `375` 分。
- 总分上限原因：`validation_failed` 25，`contract_invalid` 3，`none` 2
- 回包失败根因：`source_preflight_failed` 25，`other` 3

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 格式 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 31.25 | 25.00 | 0 | 100.00 | validation_failed |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 26.65 | 37.00 | 0 | 50.00 | validation_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 14.00 | 20.00 | 0 | 25.00 | validation_failed |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 36.65 | 37.00 | 0 | 100.00 | validation_failed |
| core-01 核心文本处理 | raw | 核心库指令 | 11.53 | 14.50 | 0 | 25.00 | validation_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 25.58 | 23.50 | 0 | 75.00 | validation_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 9.50 | 10.00 | 0 | 25.00 | validation_failed |
| core-02 数值核心命令 | skill | 核心库指令 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| core-03 动态数组核心命令 | raw | 核心库指令 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 16.52 | 14.50 | 0 | 50.00 | validation_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 12.60 | 28.00 | 0 | 0.00 | validation_failed |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 9.50 | 10.00 | 0 | 25.00 | validation_failed |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 13.33 | 18.50 | 0 | 25.00 | validation_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 9.90 | 22.00 | 0 | 0.00 | validation_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 23.68 | 41.50 | 0 | 25.00 | validation_failed |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 17.60 | 28.00 | 0 | 25.00 | validation_failed |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。格式分已经覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。
