# e-language-bench

> 面向易语言代码生成模型的本地编译基准测试框架

本项目通过完整的工具链验证模型输出，包括 e-packager 文本工作区处理、预检、回包、重新解包、一致性比较和 AutoLinker 无头编译，全面评估模型在格式准确性、核心库使用和流程控制等方面的能力。

---

## 📊 评分页面

在线查看完整评分报告：[e-language-bench.apptest.dev](https://e-language-bench.apptest.dev)

页面包含编译验证总榜、编译硬门槛影响、评分规则、五类能力矩阵和逐模型失败诊断。

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

上述权重仅对通过真实无头编译的源码生效。任何未能编译的样本，其有效格式分、语义分和总分均为 0。

### 预编译结构分细则

预编译结构分按 100 分制展示，细分如下：

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

预编译结构分用于定位 JSON、源码文本、回包和工程打开问题，不直接代表源码可用性。只有 AutoLinker 真实编译成功后，该分数才成为计入总分的有效格式分。

### 扣分规则

- 格式错误按 e-packager 的文件、行号和错误代码逐项扣分，同一位置的同一错误去重
- 每次实际执行 e-packager 回包失败扣 15 分，预编译结构分最低为 0
- HTTP、限流和网络重试不计入回包尝试，不参与格式扣分
- 验证失败、无法回包、回包后损坏、IDE 无法打开或编译失败均触发编译硬门槛，不可用源码不能通过文本匹配取得任何总分

> **运行时说明**：本机 Defender 会阻止新编译的易语言 EXE 启动，因此 `v1-compile` 不执行产物，报告固定标记 `runtime_unavailable_defender_blocked`。未来启用运行断言时应发布新基准版本，不可与本版混榜。

---

## 🏆 当前跑分

**测试日期**：2026-08-15 至 2026-08-19<br>
**数据集版本**：`v1-compile`<br>
**评分规则版本**：`v1.2-compile-gated`<br>
**样本数**：30（每组），并发数：2

结果目录沿用模型生成时的 run-id，其中部分名称包含 `v1.1`；重算后的权威评分版本以各目录 manifest 和 scorecard 中的 `v1.2-compile-gated` 为准。

| 模型 | 思考等级 | 总分 | Raw | Skill | 有效格式 | 预编译结构 | 编译率 | pass@1 | 回包失败/尝试 | Skill 增益 | 结果 |
|------|---------|-----:|----:|------:|---------:|-----------:|-------:|-------:|-------------:|----------:|------|
| gemini-3.6-flash | `high` | **36.16** | 39.33 | 33.00 | 36.67 | 82.24 | 36.7% | 30.0% | 9/30 | -6.33 | [报告](results/20260819-right-gemini-3.6-flash-high-v1.2-p2-r2/report.md) / [JSON](results/20260819-right-gemini-3.6-flash-high-v1.2-p2-r2/scorecard.json) |
| gpt-5.6-sol | `max` | **23.34** | 20.00 | 26.67 | 23.33 | 88.60 | 23.3% | 23.3% | 5/30 | +6.67 | [报告](results/20260816-0elog-gpt-5.6-sol-max-v1.1-p2/report.md) / [JSON](results/20260816-0elog-gpt-5.6-sol-max-v1.1-p2/scorecard.json) |
| gpt-5.6-sol | `medium` | **22.66** | 19.00 | 26.33 | 23.33 | 81.60 | 23.3% | 13.3% | 8/29 | +7.33 | [报告](results/20260815-right-gpt-5.6-sol-medium-v1.1-p2/report.md) / [JSON](results/20260815-right-gpt-5.6-sol-medium-v1.1-p2/scorecard.json) |
| deepseek-v4-pro | `max` | **22.66** | 19.33 | 26.00 | 23.33 | 74.93 | 23.3% | 13.3% | 13/30 | +6.67 | [报告](results/20260815-deepseek-v4-pro-max-v1.1-p2/report.md) / [JSON](results/20260815-deepseek-v4-pro-max-v1.1-p2/scorecard.json) |
| gpt-5.6-luna | `max` | **19.84** | 6.67 | 33.00 | 20.00 | 65.73 | 20.0% | 16.7% | 16/28 | +26.33 | [报告](results/20260815-right-gpt-5.6-luna-max-v1.1-p2/report.md) / [JSON](results/20260815-right-gpt-5.6-luna-max-v1.1-p2/scorecard.json) |
| claude-opus-5 | `max` | **19.83** | 13.33 | 26.33 | 20.00 | 65.40 | 20.0% | 16.7% | 7/24 | +13.00 | [报告](results/20260816-right-claude-opus-5-max-v1.2-p2/report.md) / [JSON](results/20260816-right-claude-opus-5-max-v1.2-p2/scorecard.json) |
| gemini-3.1-pro | `high` | **16.50** | 19.67 | 13.33 | 16.67 | 92.20 | 16.7% | 13.3% | 2/29 | -6.34 | [报告](results/20260819-right-gemini-3.1-pro-high-v1.2-p2/report.md) / [JSON](results/20260819-right-gemini-3.1-pro-high-v1.2-p2/scorecard.json) |
| minimax-m3 | `enabled` | **16.33** | 19.33 | 13.33 | 16.67 | 70.33 | 16.7% | 10.0% | 16/30 | -6.00 | [报告](results/20260816-ark-minimax-m3-thinking-v1.1-p2/report.md) / [JSON](results/20260816-ark-minimax-m3-thinking-v1.1-p2/scorecard.json) |
| glm-5.2 | `max` | **16.00** | 19.00 | 13.00 | 16.67 | 74.30 | 16.7% | 6.7% | 13/30 | -6.00 | [报告](results/20260815-ark-glm-5.2-max-responses-v1.1-p2/report.md) / [JSON](results/20260815-ark-glm-5.2-max-responses-v1.1-p2/scorecard.json) |
| gemini-3.5-flash | `high` | **16.00** | 18.67 | 13.33 | 16.67 | 84.87 | 16.7% | 10.0% | 8/30 | -5.34 | [报告](results/20260819-right-gemini-3.5-flash-high-v1.2-p2/report.md) / [JSON](results/20260819-right-gemini-3.5-flash-high-v1.2-p2/scorecard.json) |
| grok-4.6 | `high` | **13.34** | 6.67 | 20.00 | 13.34 | 72.74 | 13.3% | 13.3% | 14/30 | +13.33 | [报告](results/20260819-xai-grok-4.6-high-v1.2-p2-r2/report.md) / [JSON](results/20260819-xai-grok-4.6-high-v1.2-p2-r2/scorecard.json) |
| gemini-3.7-flash | `high` | **10.00** | 6.67 | 13.33 | 10.00 | 84.20 | 10.0% | 10.0% | 8/30 | +6.66 | [报告](results/20260819-right-gemini-3.7-flash-high-v1.2-p2-r2/report.md) / [JSON](results/20260819-right-gemini-3.7-flash-high-v1.2-p2-r2/scorecard.json) |
| deepseek-v4-flash | `max` | **9.84** | 13.00 | 6.67 | 10.00 | 68.25 | 10.0% | 6.7% | 16/30 | -6.33 | [报告](results/20260815-deepseek-v4-flash-max-v1.1-p2/report.md) / [JSON](results/20260815-deepseek-v4-flash-max-v1.1-p2/scorecard.json) |
| hy3 | `high` | **9.66** | 6.00 | 13.33 | 10.00 | 68.20 | 10.0% | 6.7% | 18/30 | +7.33 | [报告](results/20260817-tokenhub-hy3-high-v1.2-p2/report.md) / [JSON](results/20260817-tokenhub-hy3-high-v1.2-p2/scorecard.json) |
| claude-sonnet-5 | `high` | **9.50** | 6.00 | 13.00 | 10.00 | 54.87 | 10.0% | 3.3% | 20/29 | +7.00 | [报告](results/20260815-right-claude-sonnet-5-high-v1.1-p2/report.md) / [JSON](results/20260815-right-claude-sonnet-5-high-v1.1-p2/scorecard.json) |
| glm-5.3 | `max` | **6.67** | 6.67 | 6.67 | 6.67 | 70.47 | 6.7% | 6.7% | 15/30 | +0.00 | [报告](results/20260816-ark-glm-5.3-max-v1.1-p2/report.md) / [JSON](results/20260816-ark-glm-5.3-max-v1.1-p2/scorecard.json) |
| grok-4.6（降智） | `max` | **6.67** | 6.67 | 6.67 | 6.67 | 21.32 | 6.7% | 6.7% | 25/27 | +0.00 | [报告](results/20260815-right-grok-4.6-max-responses-v1.1-p2/report.md) / [JSON](results/20260815-right-grok-4.6-max-responses-v1.1-p2/scorecard.json) |
| mimo-v2.5 | `high (enabled)` | **6.67** | 13.33 | 0.00 | 6.67 | 46.12 | 6.7% | 6.7% | 27/30 | -13.33 | [报告](results/20260816-xiaomi-mimo-v2.5-high-v1.2-p2/report.md) / [JSON](results/20260816-xiaomi-mimo-v2.5-high-v1.2-p2/scorecard.json) |
| doubao-seed-2.0-lite | `enabled` | **3.33** | 6.67 | 0.00 | 3.33 | 80.18 | 3.3% | 3.3% | 11/30 | -6.67 | [报告](results/20260816-ark-doubao-seed-2.0-lite-thinking-v1.1-p2/report.md) / [JSON](results/20260816-ark-doubao-seed-2.0-lite-thinking-v1.1-p2/scorecard.json) |
| doubao-seed-2.1-turbo | `enabled` | **3.33** | 0.00 | 6.67 | 3.33 | 72.63 | 3.3% | 3.3% | 16/30 | +6.67 | [报告](results/20260816-ark-doubao-seed-2.1-turbo-thinking-v1.1-p2/report.md) / [JSON](results/20260816-ark-doubao-seed-2.1-turbo-thinking-v1.1-p2/scorecard.json) |
| mimo-v2.5-pro | `high (enabled)` | **3.17** | 0.00 | 6.33 | 3.33 | 46.45 | 3.3% | 0.0% | 23/29 | +6.33 | [报告](results/20260816-xiaomi-mimo-v2.5-pro-high-v1.2-p2/report.md) / [JSON](results/20260816-xiaomi-mimo-v2.5-pro-high-v1.2-p2/scorecard.json) |

### 评分列说明

- **总分**：综合评分（满分 100）；未通过真实编译的样本记 0 分
- **Raw / Skill**：两个轨道的独立得分
- **有效格式**：仅编译成功样本能够获得的格式分，按全部样本平均（满分 100）
- **预编译结构**：JSON、声明、流程、回包、重解包和 IDE 打开的诊断分，不计入未编译样本总分
- **编译率**：成功通过 AutoLinker 无头编译的样本比例
- **pass@1**：完全通过所有检查的样本比例
- **回包失败/尝试**：e-packager 回包失败次数 / 总尝试次数
- **Skill 增益**：Skill 轨道相对 Raw 轨道的分数提升

### 供应商行为说明

- `gemini-3.1-pro`、`gemini-3.5-flash`、`gemini-3.6-flash` 和 `gemini-3.7-flash` 通过 RightAPI `https://www.rightapi.ai/gemini/v1/responses` 完成，按 `reasoning.effort=high` 运行；四组各 30 次响应的服务端模型标识均与请求模型一致，且每次响应均报告非零 reasoning token
- `grok-4.6` 官方成绩通过 xAI 官方 `https://api.x.ai/v1/responses` 完成，使用 `reasoning.effort=high` 和 SSE 流式传输；30 次响应的服务端模型标识均为 `grok-4.6`，每次均报告非零 reasoning token。该批次平均响应耗时约 81.82 秒，reasoning token 平均 4,166.9
- 旧的 `grok-4.6（降智）` 成绩来自 RightAPI 中转站，不代表 xAI 官方模型能力；旧批次保留用于历史对照，manifest、scorecard、报告和 Web 均标记为“降智”
- `gpt-5.6-sol` 的 `max` 成绩通过 `https://api.0elog.com/` 完成，服务端模型标识为 `gpt-5.6-sol`
- `claude-opus-5` 通过 RightAPI Claude AWS 路径完成，按官方最高档发送 `output_config.effort=max` 并配置 65536 个最大输出 token；30 次响应的服务端模型标识均为 `claude-opus-5`
- `mimo-v2.5-pro` 和 `mimo-v2.5` 通过小米官方 Responses 端点完成，显式发送最高枚举值 `reasoning.effort=high`；小米当前不支持调节实际思考强度，`low`、`medium`、`high` 均映射为启用思考，因此榜单标记为 `high (enabled)`
- 两组 MiMo 响应均包含 reasoning 输出块和 reasoning token 计数，且 30 次响应的服务端模型标识分别与请求模型一致
- `glm-5.3` 成绩通过火山引擎 `https://ark.cn-beijing.volces.com/api/coding/v3` 完成，服务端模型标识为 `glm-5.3`
- `hy3` 成绩通过 TokenHub `https://tokenhub.tencentmaas.com/` 的 OpenAI Responses 端点完成，服务端模型标识为 `hy3`；该端点的 `reasoning.effort` 仅接受 `no_think`、`low`、`high`，本次按最高档 `high` 运行
- `doubao-seed-2.0-lite`、`doubao-seed-2.1-turbo` 和 `minimax-m3` 通过同一火山 Coding Responses 端点完成；三者按官方开关式配置发送 `thinking.type=enabled`，不宣称存在 `max` 强度档位
- 请求 `doubao-seed-2.1-turbo` 时，服务端在全部响应中标识模型为版本化的 `doubao-seed-2-1-turbo-260628`
- 请求 `gpt-5.6-luna` 时，服务端在全部响应中标识模型为 `gpt-5.6-terra`
- 请求 `glm-5.2` 时，服务端标识为 `glm-5.3`
- Claude 端点的原生 Responses 路由返回 `not implemented`，因此适配器保持统一 Responses 语义，但 wire 层显式桥接到 Anthropic Messages

这些差异均在 manifest、scorecard 和报告中保留，避免把请求名或适配层协议误当成服务端实际行为。

思考配置依据：[Claude effort 官方文档](https://platform.claude.com/docs/en/build-with-claude/effort)、[小米 MiMo Responses API](https://mimo.mi.com/docs/en-US/api/chat/responses)、[火山方舟 Responses API](https://www.volcengine.com/docs/82379/1795150)、[火山方舟深度思考](https://www.volcengine.com/docs/82379/1956279)和 [MiniMax M3 官方说明](https://www.minimax.io/blog/minimax-m3)。

### 特殊情况

Grok 的 `repair-03/skill` 首轮请求经历 3 次 HTTP 504；按供应商 `retry_after=120` 退避后，相同 run-id 只补跑该基础设施失败项并成功。HTTP 重试未计入格式分或回包失败次数。

### 工具链指纹

各结果的权威工具链指纹和依赖 commit 以对应 `manifest.json` 为准：

| 批次 | e-packager | AutoLinkerTest | AutoLinker.fne |
|------|------------|----------------|----------------|
| 2026-08-15 至 2026-08-17 | `09d7f1e291d2…` | `57cc17e7584f…` | `cba2e177c86d…` |
| 2026-08-19 Gemini 3.1 Pro、3.5/3.6/3.7 Flash | `09d7f1e291d2…` | `309534632abe…` | `309824c0714e…` |

2026-08-19 Gemini 批次使用了更新后的 AutoLinker 工具链和依赖仓库版本，因此与此前结果并非严格的模型单变量对照；榜单保留结果，但跨批次比较时应同时核对 manifest。

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

已有结果可在不重新请求模型的情况下按当前规则重算：

```powershell
$env:PYTHONPATH = "src"
python -m elang_bench report <run-id> --rescore
```

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
