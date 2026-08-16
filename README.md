# e-language-bench

> 面向易语言代码生成模型的本地编译基准测试框架

本项目通过完整的工具链验证模型输出，包括 e-packager 文本工作区处理、预检、回包、重新解包、一致性比较和 AutoLinker 无头编译，全面评估模型在格式准确性、核心库使用和流程控制等方面的能力。

---

## 📋 基准设计

### 测试集组成

`v1-compile` 包含 **15 道题目**，每题运行 `raw` 和 `skill` 两个轨道，共 **30 个独立的 pass@1 样本**：

- **格式与工程**：入口、声明槽位、固定表和自定义类型
- **核心库指令**：文本、数值和动态数组命令
- **流程控制**：嵌套分支、循环、多路判断和循环跳转
- **子程序与数据结构**：参考参数、递归和公开类
- **修复与综合**：跨语言语法修复、声明纠错和文本数组统计

### 轨道说明

| 轨道 | 输入内容 |
|------|----------|
| **Raw** | 仅提供任务描述和当前源码 |
| **Skill** | 额外提供来自 `e-language-skill` 的实现规范 |

两条轨道使用相同题目，不共享模型上下文。

### 设计理念

本基准参考主流代码评测标准，针对易语言特性定制：

- **[HumanEval](https://arxiv.org/abs/2107.03374) & [MBPP](https://arxiv.org/abs/2108.07732)**：独立小任务 + pass@1 口径
- **[EvalPlus](https://github.com/evalplus/evalplus)**：增加隐藏语义检查，防止表面样例拟合
- **[MultiPL-E](https://github.com/nuprl/MultiPL-E)**：语言特有语法、格式和真实工具链验证
- **[SWE-bench](https://arxiv.org/abs/2310.06770)**：可编辑工作区 + 实际执行环境

> **注**：本项目为隔离的易语言代码生成基准，非仓库级问题修复任务。

---

## 🎯 评分体系

### 总分构成

每题总分 **100 分**：

- **格式与工程可靠性**：45%
- **真实无头编译**：35%
- **隐藏静态语义断言**：20%

### 格式分细则

格式分按 100 分制展示，细分如下：

| 格式项目 | 分值 |
|----------|-----:|
| 严格 JSON、UTF-8 和授权路径 | 10 |
| 声明字段、顺序和文本语法 | 25 |
| 流程闭合、名称与类型链接 | 20 |
| e-packager 成功回包 | 15 |
| 重新解包与 compare-bundle 一致 | 15 |
| AutoLinker 成功打开工程 | 15 |

#### 评分项说明

- **严格 JSON、UTF-8 和授权路径**：验证输出文件格式规范性和路径合法性
- **声明字段、顺序和文本语法**：检查变量、子程序等声明的完整性和语法正确性
- **流程闭合、名称与类型链接**：确保分支、循环等结构完整闭合，标识符正确引用
- **e-packager 成功回包**：文本工作区能否成功打包为二进制工程文件
- **重新解包与 compare-bundle 一致**：回包后重新解包的内容与原始输入一致性检查
- **AutoLinker 成功打开工程**：易语言 IDE 能否正常加载生成的工程文件

### 扣分规则

- 格式错误按 e-packager 的文件、行号和错误代码逐项扣分，同一位置的同一错误去重
- 每次实际执行 e-packager 回包失败扣 15 分，格式分最低为 0
- HTTP、限流和网络重试不计入回包尝试，不参与格式扣分
- 验证失败、无法回包、回包后损坏、IDE 无法打开和编译失败分别设置总分上限，确保不可用源码无法通过文本匹配取得高分

> **运行时说明**：本机 Defender 会阻止新编译的易语言 EXE 启动，因此 `v1-compile` 不执行产物，报告固定标记 `runtime_unavailable_defender_blocked`。未来启用运行断言时应发布新基准版本，不可与本版混榜。

---

## 🏆 当前跑分

**测试日期**：2026-08-15 至 2026-08-16<br>
**数据集版本**：`v1-compile`  
**评分规则版本**：`v1.1-pack-failure-count`  
**样本数**：30（每组），并发数：2

| 模型 | 思考等级 | 总分 | Raw | Skill | 综合格式分 | 编译率 | pass@1 | 回包失败/尝试 | Skill 增益 | 结果 |
|------|---------|-----:|----:|------:|----------:|-------:|-------:|-------------:|----------:|------|
| gemini-3.6-flash | `high`（最大） | **65.78** | 61.14 | 70.42 | 84.20 | 30.0% | 23.3% | 8/30 | +9.28 | [报告](results/20260815-right-gemini-3.6-flash-high-v1.1-p2/report.md) / [JSON](results/20260815-right-gemini-3.6-flash-high-v1.1-p2/scorecard.json) |
| gpt-5.6-sol | `max` | **64.53** | 61.58 | 67.49 | 88.60 | 23.3% | 23.3% | 5/30 | +5.91 | [报告](results/20260816-0elog-gpt-5.6-sol-max-v1.1-p2/report.md) / [JSON](results/20260816-0elog-gpt-5.6-sol-max-v1.1-p2/scorecard.json) |
| gpt-5.6-sol | `medium` | **58.67** | 53.67 | 63.67 | 81.60 | 23.3% | 13.3% | 8/29 | +10.00 | [报告](results/20260815-right-gpt-5.6-sol-medium-v1.1-p2/report.md) / [JSON](results/20260815-right-gpt-5.6-sol-medium-v1.1-p2/scorecard.json) |
| deepseek-v4-pro | `max`（最大） | **57.03** | 50.37 | 63.70 | 74.93 | 23.3% | 13.3% | 13/30 | +13.33 | [报告](results/20260815-deepseek-v4-pro-max-v1.1-p2/report.md) / [JSON](results/20260815-deepseek-v4-pro-max-v1.1-p2/scorecard.json) |
| glm-5.2 | `max` | **52.41** | 46.10 | 58.73 | 74.30 | 16.7% | 6.7% | 13/30 | +12.63 | [报告](results/20260815-ark-glm-5.2-max-responses-v1.1-p2/report.md) / [JSON](results/20260815-ark-glm-5.2-max-responses-v1.1-p2/scorecard.json) |
| doubao-seed-2.0-lite | `enabled`（深度思考） | **51.02** | 50.91 | 51.14 | 80.18 | 3.3% | 3.3% | 11/30 | +0.23 | [报告](results/20260816-ark-doubao-seed-2.0-lite-thinking-v1.1-p2/report.md) / [JSON](results/20260816-ark-doubao-seed-2.0-lite-thinking-v1.1-p2/scorecard.json) |
| gpt-5.6-luna | `max` | **49.45** | 47.52 | 51.37 | 65.73 | 20.0% | 16.7% | 16/28 | +3.85 | [报告](results/20260815-right-gpt-5.6-luna-max-v1.1-p2/report.md) / [JSON](results/20260815-right-gpt-5.6-luna-max-v1.1-p2/scorecard.json) |
| minimax-m3 | `enabled`（深度思考） | **49.16** | 49.57 | 48.76 | 70.33 | 16.7% | 10.0% | 16/30 | -0.81 | [报告](results/20260816-ark-minimax-m3-thinking-v1.1-p2/report.md) / [JSON](results/20260816-ark-minimax-m3-thinking-v1.1-p2/scorecard.json) |
| glm-5.3 | `max` | **48.97** | 42.04 | 55.89 | 70.47 | 6.7% | 6.7% | 15/30 | +13.85 | [报告](results/20260816-ark-glm-5.3-max-v1.1-p2/report.md) / [JSON](results/20260816-ark-glm-5.3-max-v1.1-p2/scorecard.json) |
| doubao-seed-2.1-turbo | `enabled`（深度思考） | **46.81** | 42.79 | 50.84 | 72.63 | 3.3% | 3.3% | 16/30 | +8.05 | [报告](results/20260816-ark-doubao-seed-2.1-turbo-thinking-v1.1-p2/report.md) / [JSON](results/20260816-ark-doubao-seed-2.1-turbo-thinking-v1.1-p2/scorecard.json) |
| deepseek-v4-flash | `max`（最大） | **46.76** | 42.42 | 51.09 | 68.25 | 10.0% | 6.7% | 16/30 | +8.67 | [报告](results/20260815-deepseek-v4-flash-max-v1.1-p2/report.md) / [JSON](results/20260815-deepseek-v4-flash-max-v1.1-p2/scorecard.json) |
| claude-sonnet-5 | `high` | **41.17** | 37.64 | 44.70 | 54.87 | 10.0% | 3.3% | 20/29 | +7.06 | [报告](results/20260815-right-claude-sonnet-5-high-v1.1-p2/report.md) / [JSON](results/20260815-right-claude-sonnet-5-high-v1.1-p2/scorecard.json) |
| grok-4.6 | `max` | **18.42** | 15.27 | 21.58 | 21.32 | 6.7% | 6.7% | 25/27 | +6.31 | [报告](results/20260815-right-grok-4.6-max-responses-v1.1-p2/report.md) / [JSON](results/20260815-right-grok-4.6-max-responses-v1.1-p2/scorecard.json) |

### 评分列说明

- **总分**：综合评分（满分 100），包含格式、编译和语义三部分
- **Raw / Skill**：两个轨道的独立得分
- **综合格式分**：所有样本的格式分平均值（满分 100）
- **编译率**：成功通过 AutoLinker 无头编译的样本比例
- **pass@1**：完全通过所有检查的样本比例
- **回包失败/尝试**：e-packager 回包失败次数 / 总尝试次数
- **Skill 增益**：Skill 轨道相对 Raw 轨道的分数提升

### 供应商行为说明

- `gpt-5.6-sol` 的 `max` 成绩通过 `https://api.0elog.com/` 完成，服务端模型标识为 `gpt-5.6-sol`
- `glm-5.3` 成绩通过火山引擎 `https://ark.cn-beijing.volces.com/api/coding/v3` 完成，服务端模型标识为 `glm-5.3`
- `doubao-seed-2.0-lite`、`doubao-seed-2.1-turbo` 和 `minimax-m3` 通过同一火山 Coding Responses 端点完成；三者按官方开关式配置发送 `thinking.type=enabled`，不宣称存在 `max` 强度档位
- 请求 `doubao-seed-2.1-turbo` 时，服务端在全部响应中标识模型为版本化的 `doubao-seed-2-1-turbo-260628`
- 请求 `gpt-5.6-luna` 时，服务端在全部响应中标识模型为 `gpt-5.6-terra`
- 请求 `glm-5.2` 时，服务端标识为 `glm-5.3`
- Claude 端点的原生 Responses 路由返回 `not implemented`，因此适配器保持统一 Responses 语义，但 wire 层显式桥接到 Anthropic Messages

这些差异均在 manifest、scorecard 和报告中保留，避免把请求名或适配层协议误当成服务端实际行为。

思考配置依据：[火山方舟 Responses API](https://www.volcengine.com/docs/82379/1795150)、[火山方舟深度思考](https://www.volcengine.com/docs/82379/1956279)和 [MiniMax M3 官方说明](https://www.minimax.io/blog/minimax-m3)。

### 特殊情况

Grok 的 `repair-03/skill` 首轮请求经历 3 次 HTTP 504；按供应商 `retry_after=120` 退避后，相同 run-id 只补跑该基础设施失败项并成功。HTTP 重试未计入格式分或回包失败次数。

### 工具链指纹

- e-packager: `09d7f1e291d2ba190c28fcdc07d2460a6222baf1b7e935c34a9660807aed7785`
- AutoLinkerTest: `57cc17e7584f54b0b30b0e55e799c097d68e6bb7c71650654cc58846a5b37358`
- AutoLinker.fne: `cba2e177c86d5bfa60c50b6b19d89e564c1bcaa5b26a5563fcea63308e17aa32`

不同 `.e` 工程已验证可并发编译，每个 case 使用独立 candidate、EXE、结果 JSON 和编译临时目录。

---

## 🔧 环境配置

### 本地依赖

默认配置位于 `bench.json`，需要以下本地依赖：

```
D:\git\e-packager\bin\Win32\Release\e-packager.exe
D:\git\e-packager\eproj
D:\git\AutoLinker\bin\fne_release\AutoLinkerTest.exe
C:\Users\aiqin\OneDrive\e5.6\lib\AutoLinker.fne
C:\Users\aiqin\OneDrive\e5.6\e5.95.exe
D:\git\e-language-skill
```

### 环境检查

```powershell
$env:PYTHONPATH = "src"
python -m elang_bench check
```

---

## 🚀 运行基准

### API Key 配置

⚠️ API Key 只允许通过环境变量传入，不要写入 `bench.json`：

```powershell
$env:PYTHONPATH = "src"
$env:ELANG_BENCH_API_KEY = "<api-key>"
python -m elang_bench --config bench.right-luna-max.json run --run-id 20260815-right-gpt-5.6-luna-max-v1.1-p2 --workers 2
```

### 运行说明

- 各 `bench*.json` 均使用 `protocol=openai_responses`
- 对只支持思考开关的 Responses 模型，使用 `reasoning_effort=enabled` 作为报告标签，并配置 `responses_thinking_type=enabled`；wire 请求发送 `thinking.type=enabled` 并省略 `reasoning.effort`
- 供应商无法直接接收 Responses wire format 时，由配置显式选择兼容传输
- case 之间无上下文继承，可通过 `--workers` 并发执行，默认值来自配置的 `parallel_workers`
- 429、5xx、524 和连接中断属于 API 基础设施失败，不生成模型成绩，不计入格式或回包失败次数
- 批次继续处理其他 case，使用相同 `--run-id` 时只重试失败项，避免重复计费

### 续跑校验

续跑会校验以下内容，任何影响可比性的输入变化都必须使用新的 `run-id`：

- 评分版本、模型、思考等级
- 统一协议、实际传输、并发数
- 数据集、模板
- e-packager、AutoLinkerTest、AutoLinker.fne 的 SHA-256

### 重新生成报告

```powershell
python -m elang_bench report 20260815-right-gpt-5.6-luna-max-v1.1-p2
```

### 结果输出

结果位于 `results/<run-id>/`：

```
manifest.json         # 模型、工具路径、依赖 commit 和 SHA-256，不含密钥
records/              # 每题状态、回包尝试/失败次数、分数、错误位置和扣分原因
cases/                # 脱敏请求、原始 API 响应、工作区和编译诊断
scorecard.json        # 机器可读成绩
report.md             # 中文报告
```

Git 默认保留脱敏请求、API 原始响应、编译结果、逐题记录和汇总报告；`.gitignore` 排除可重新生成且体积较大的 workspace、reunpacked、候选 `.e/.exe`、监控日志和本地凭据文件。

---

## 🧪 测试

### 单元测试

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

### 集成测试

```powershell
$env:ELANG_BENCH_INTEGRATION = "1"
python -m unittest tests.test_integration -v
```

集成测试会真实调用 e-packager 和 AutoLinker，但不会请求模型。它验证最小工程、自定义类型固定表和新增类页均能回包、重新解包并编译，也验证两个独立工程可同时完成无头编译。

---

## 📄 许可

本项目为易语言代码生成能力评测基准，详细评分规则和工具链依赖见文档。
