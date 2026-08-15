# 易语言大模型基准测试报告

- 运行编号：`20260815-deepseek-v4-pro-max-v1.1-p2`
- 模型：`deepseek-v4-pro`
- 推理等级：`max`
- 统一协议：`openai_responses`
- 外部传输协议：`openai_responses`
- 服务端模型标识：`deepseek-v4-pro`
- 基准版本：`v1-compile`
- 评分版本：`v1.1-pack-failure-count`
- 运行状态：`complete`
- 总分：**57.03 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 格式分 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw | 50.37 | 63.13 | 9/15 | 20.0% | 6.7% |
| skill | 63.70 | 86.73 | 4/15 | 26.7% | 20.0% |

Skill 增益：**+13.33**

## 能力分项

| 能力 | 得分 | 格式分 | pass@1 |
| --- | ---: | ---: | ---: |
| 格式与工程 | 60.68 | 70.67 | 33.3% |
| 核心库指令 | 71.50 | 91.67 | 16.7% |
| 流程控制 | 40.69 | 59.50 | 0.0% |
| 子程序与数据结构 | 56.06 | 72.33 | 16.7% |
| 修复与综合 | 56.23 | 80.50 | 0.0% |

## 失败分布

- 回包尝试：`30` 次，失败 `13` 次，累计格式原始分扣除 `195` 分。
- 总分上限原因：`validation_failed` 11，`compile_failed` 10，`none` 7，`pack_failed` 2
- 回包失败根因：`source_preflight_failed` 11，`semantic_method_rebuild_failed` 1，`other` 1

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 格式 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 39.00 | 51.00 | 0 | 100.00 | validation_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 35.70 | 46.00 | 0 | 75.00 | validation_failed |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 60.00 | 100.00 | 0 | 75.00 | compile_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 36.65 | 37.00 | 0 | 100.00 | validation_failed |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| core-01 核心文本处理 | raw | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 95.00 | 100.00 | 100 | 75.00 | FAIL |
| core-02 数值核心命令 | skill | 核心库指令 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| core-03 动态数组核心命令 | raw | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 39.00 | 50.00 | 0 | 100.00 | validation_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 55.00 | 100.00 | 0 | 50.00 | compile_failed |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 29.00 | 55.00 | 0 | 50.00 | pack_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 31.65 | 37.00 | 0 | 75.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 90.00 | 100.00 | 100 | 50.00 | FAIL |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 9.50 | 10.00 | 0 | 25.00 | validation_failed |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 29.00 | 55.00 | 0 | 25.00 | pack_failed |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 26.65 | 37.00 | 0 | 50.00 | validation_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 39.00 | 46.00 | 0 | 100.00 | validation_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 33.45 | 41.00 | 0 | 75.00 | validation_failed |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 95.00 | 100.00 | 100 | 75.00 | FAIL |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 31.65 | 37.00 | 0 | 75.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 30.70 | 46.00 | 0 | 50.00 | validation_failed |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 50.00 | 100.00 | 0 | 25.00 | compile_failed |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。格式分已经覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。
