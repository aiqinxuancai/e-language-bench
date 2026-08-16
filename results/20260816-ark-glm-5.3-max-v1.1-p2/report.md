# 易语言大模型基准测试报告

- 运行编号：`20260816-ark-glm-5.3-max-v1.1-p2`
- 模型：`glm-5.3`
- 推理等级：`max`
- 统一协议：`openai_responses`
- 外部传输协议：`openai_responses`
- 服务端模型标识：`glm-5.3`
- 基准版本：`v1-compile`
- 评分版本：`v1.1-pack-failure-count`
- 运行状态：`complete`
- 总分：**48.97 / 100**
- 运行期验证：`runtime_unavailable_defender_blocked`

## 轨道成绩

| 轨道 | 得分 | 格式分 | 回包失败/尝试 | 编译率 | pass@1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw | 42.04 | 58.33 | 10/15 | 6.7% | 6.7% |
| skill | 55.89 | 82.60 | 5/15 | 6.7% | 6.7% |

Skill 增益：**+13.85**

## 能力分项

| 能力 | 得分 | 格式分 | pass@1 |
| --- | ---: | ---: | ---: |
| 格式与工程 | 65.11 | 80.50 | 33.3% |
| 核心库指令 | 59.28 | 91.00 | 0.0% |
| 流程控制 | 40.70 | 68.50 | 0.0% |
| 子程序与数据结构 | 40.98 | 58.00 | 0.0% |
| 修复与综合 | 38.76 | 54.33 | 0.0% |

## 失败分布

- 回包尝试：`30` 次，失败 `15` 次，累计格式原始分扣除 `225` 分。
- 总分上限原因：`validation_failed` 12，`compile_failed` 13，`pack_failed` 3，`none` 2
- 回包失败根因：`source_preflight_failed` 12，`semantic_method_rebuild_failed` 1，`other` 2

## 逐题结果

| 题目 | 轨道 | 类别 | 总分 | 格式 | 编译 | 语义 | 状态 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| abs-01 参考参数交换 | raw | 子程序与数据结构 | 19.50 | 10.00 | 0 | 75.00 | validation_failed |
| abs-01 参考参数交换 | skill | 子程序与数据结构 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| abs-02 递归子程序 | raw | 子程序与数据结构 | 29.00 | 55.00 | 0 | 50.00 | pack_failed |
| abs-02 递归子程序 | skill | 子程序与数据结构 | 35.70 | 46.00 | 0 | 75.00 | validation_failed |
| abs-03 公开类与生命周期 | raw | 子程序与数据结构 | 31.65 | 37.00 | 0 | 75.00 | validation_failed |
| abs-03 公开类与生命周期 | skill | 子程序与数据结构 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-01 核心文本处理 | raw | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-01 核心文本处理 | skill | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-02 数值核心命令 | raw | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-02 数值核心命令 | skill | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| core-03 动态数组核心命令 | raw | 核心库指令 | 30.70 | 46.00 | 0 | 50.00 | validation_failed |
| core-03 动态数组核心命令 | skill | 核心库指令 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| flow-01 双分支与嵌套条件 | raw | 流程控制 | 55.00 | 100.00 | 0 | 50.00 | compile_failed |
| flow-01 双分支与嵌套条件 | skill | 流程控制 | 55.00 | 100.00 | 0 | 50.00 | compile_failed |
| flow-02 循环与跳过本轮 | raw | 流程控制 | 14.50 | 10.00 | 0 | 50.00 | validation_failed |
| flow-02 循环与跳过本轮 | skill | 流程控制 | 30.70 | 46.00 | 0 | 50.00 | validation_failed |
| flow-03 多路判断与变量循环 | raw | 流程控制 | 29.00 | 55.00 | 0 | 75.00 | pack_failed |
| flow-03 多路判断与变量循环 | skill | 流程控制 | 60.00 | 100.00 | 0 | 75.00 | compile_failed |
| fmt-01 最小控制台入口 | raw | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-01 最小控制台入口 | skill | 格式与工程 | 100.00 | 100.00 | 100 | 100.00 | PASS |
| fmt-02 声明槽位与顺序 | raw | 格式与工程 | 31.65 | 37.00 | 0 | 75.00 | validation_failed |
| fmt-02 声明槽位与顺序 | skill | 格式与工程 | 65.00 | 100.00 | 0 | 100.00 | compile_failed |
| fmt-03 固定表与自定义类型 | raw | 格式与工程 | 55.00 | 100.00 | 0 | 50.00 | compile_failed |
| fmt-03 固定表与自定义类型 | skill | 格式与工程 | 39.00 | 46.00 | 0 | 100.00 | validation_failed |
| repair-01 跨语言语法修复 | raw | 修复与综合 | 37.95 | 51.00 | 0 | 75.00 | validation_failed |
| repair-01 跨语言语法修复 | skill | 修复与综合 | 60.00 | 100.00 | 0 | 75.00 | compile_failed |
| repair-02 声明与控制块纠错 | raw | 修复与综合 | 39.00 | 46.00 | 0 | 100.00 | validation_failed |
| repair-02 声明与控制块纠错 | skill | 修复与综合 | 39.00 | 46.00 | 0 | 100.00 | validation_failed |
| repair-03 综合文本数组统计 | raw | 修复与综合 | 27.60 | 28.00 | 0 | 75.00 | validation_failed |
| repair-03 综合文本数组统计 | skill | 修复与综合 | 29.00 | 55.00 | 0 | 50.00 | pack_failed |

## 说明

本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。格式分已经覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。
