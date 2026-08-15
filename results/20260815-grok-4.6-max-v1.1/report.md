# 易语言大模型基准测试报告

- 运行编号：`20260815-grok-4.6-max-v1.1`
- 模型：`grok-4.6`
- 推理等级：`max`
- 统一协议：`openai_chat`
- 外部传输协议：`openai_chat`
- 服务端模型标识：`未返回`
- 基准版本：`v1-compile`
- 评分版本：`v1.1-pack-failure-count`
- 运行状态：`complete`
- 总分：**14.81 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 格式分 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw | 12.34 | 19.27 | 13/14 | 0.0% | 0.0% |
| skill | 17.28 | 22.10 | 13/13 | 0.0% | 0.0% |

Skill 增益：**+4.94**

## 能力分项

| 能力 | 得分 | 格式分 | pass@1 |
| --- | ---: | ---: | ---: |
| 格式与工程 | 24.44 | 39.50 | 0.0% |
| 核心库指令 | 15.73 | 22.00 | 0.0% |
| 流程控制 | 14.02 | 16.33 | 0.0% |
| 子程序与数据结构 | 8.48 | 9.58 | 0.0% |
| 修复与综合 | 11.37 | 16.00 | 0.0% |

## 失败分布

- 回包尝试：`27` 次，失败 `26` 次，累计格式原始分扣除 `390` 分。
- 总分上限原因：`validation_failed` 26，`contract_invalid` 3，`compile_failed` 1
- 回包失败根因：`source_preflight_failed` 26，`other` 3

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 格式 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 5.62 | 12.50 | 0 | 0.00 | validation_failed |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 21.25 | 25.00 | 0 | 50.00 | validation_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| core-01 核心文本处理 | raw | 核心库指令 | 9.50 | 10.00 | 0 | 25.00 | validation_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 35.70 | 46.00 | 0 | 75.00 | validation_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 9.50 | 10.00 | 0 | 25.00 | validation_failed |
| core-02 数值核心命令 | skill | 核心库指令 | 30.70 | 46.00 | 0 | 50.00 | validation_failed |
| core-03 动态数组核心命令 | raw | 核心库指令 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 26.25 | 25.00 | 0 | 75.00 | validation_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 12.83 | 28.50 | 0 | 0.00 | validation_failed |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 9.50 | 10.00 | 0 | 25.00 | validation_failed |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 11.53 | 14.50 | 0 | 25.00 | validation_failed |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 12.60 | 28.00 | 0 | 0.00 | validation_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 28.90 | 42.00 | 0 | 50.00 | validation_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 11.70 | 26.00 | 0 | 0.00 | validation_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 28.45 | 41.00 | 0 | 50.00 | validation_failed |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 19.62 | 32.50 | 0 | 25.00 | validation_failed |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 15.58 | 23.50 | 0 | 25.00 | validation_failed |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 4.50 | 10.00 | 0 | 0.00 | validation_failed |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。格式分已经覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。
