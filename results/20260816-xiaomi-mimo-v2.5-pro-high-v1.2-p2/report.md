# 易语言大模型基准测试报告

- 运行编号：`20260816-xiaomi-mimo-v2.5-pro-high-v1.2-p2`
- 模型：`mimo-v2.5-pro`
- 推理等级：`high`
- 统一协议：`openai_responses`
- 外部传输协议：`openai_responses`
- 服务端模型标识：`mimo-v2.5-pro`
- 基准版本：`v1-compile`
- 评分版本：`v1.2-compile-gated`
- 运行状态：`complete`
- 总分：**3.17 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 有效格式 | 预编译结构 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw | 0.00 | 0.00 | 28.23 | 13/14 | 0.0% | 0.0% |
| skill | 6.33 | 6.67 | 64.67 | 10/15 | 6.7% | 0.0% |

Skill 增益：**+6.33**

## 能力分项

| 能力 | 得分 | 有效格式 | 预编译结构 | pass@1 |
| --- | ---: | ---: | ---: | ---: |
| 格式与工程 | 0.00 | 0.00 | 53.25 | 0.0% |
| 核心库指令 | 0.00 | 0.00 | 61.83 | 0.0% |
| 流程控制 | 0.00 | 0.00 | 27.83 | 0.0% |
| 子程序与数据结构 | 0.00 | 0.00 | 44.50 | 0.0% |
| 修复与综合 | 15.83 | 16.67 | 44.83 | 0.0% |

## 失败分布

- 回包尝试：`29` 次，失败 `23` 次，累计预编译结构分扣除 `345` 分。
- 编译硬门槛/失败原因：`validation_failed` 18，`pack_failed` 5，`compile_failed` 5，`contract_invalid` 1，`none` 1
- 回包失败根因：`source_preflight_failed` 18，`other` 3，`semantic_method_rebuild_failed` 3

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 有效格式 | 预编译结构 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 0.00 | 0.00 | 25.00 | 0 | 0.00 | validation_failed |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 0.00 | 0.00 | 22.00 | 0 | 0.00 | validation_failed |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| core-01 核心文本处理 | raw | 核心库指令 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 0.00 | 0.00 | 20.00 | 0 | 0.00 | validation_failed |
| core-02 数值核心命令 | skill | 核心库指令 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| core-03 动态数组核心命令 | raw | 核心库指令 | 0.00 | 0.00 | 45.00 | 0 | 0.00 | validation_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 0.00 | 0.00 | 51.00 | 0 | 0.00 | validation_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 0.00 | 0.00 | 0.00 | 0 | 0.00 | contract_invalid |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 0.00 | 0.00 | 46.00 | 0 | 0.00 | validation_failed |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 0.00 | 0.00 | 46.00 | 0 | 0.00 | validation_failed |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 0.00 | 0.00 | 19.00 | 0 | 0.00 | validation_failed |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 0.00 | 0.00 | 37.00 | 0 | 0.00 | validation_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 0.00 | 0.00 | 100.00 | 0 | 0.00 | compile_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 0.00 | 0.00 | 22.50 | 0 | 0.00 | validation_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 0.00 | 0.00 | 41.00 | 0 | 0.00 | validation_failed |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 0.00 | 0.00 | 47.00 | 0 | 0.00 | validation_failed |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 95.00 | 100.00 | 100.00 | 100 | 75.00 | FAIL |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 0.00 | 0.00 | 55.00 | 0 | 0.00 | pack_failed |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 0.00 | 0.00 | 10.00 | 0 | 0.00 | validation_failed |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 0.00 | 0.00 | 47.00 | 0 | 0.00 | validation_failed |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。预编译结构分覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。源码只有通过真实编译后才能获得有效格式分、语义分和总分。
