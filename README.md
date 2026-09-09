# e-language-bench

面向易语言代码生成模型的本地编译基准。通过 e-packager 的工作区预检、回包、重新解包、一致性比较和独立编译完成验证。

最新分数、能力矩阵和模型诊断请访问 [评分网站](https://e-language-bench.apptest.dev)。README 不维护模型榜单。

## 快速开始

需要 Windows、Python 3.11+、[e-packager v1.2.7 正式包](https://github.com/aiqinxuancai/e-packager/releases/tag/v1.2.7)、e-packager 工程模板和 [BlackMoonModernCore](https://github.com/aiqinxuancai/BlackMoonModernCore) 对应架构的 adapter。V2 在运行前核对 e-packager 版本。

```powershell
Copy-Item config/bench.example.json config/bench.json
```

编辑 `config/bench.json`，填写 API 地址、模型名和 `tools` 中的本地路径。API Key 通过环境变量传入。

```powershell
python scripts/bench.py --check
$env:ELANG_BENCH_API_KEY = "<api-key>"
python scripts/bench.py
```

入口不需要安装 Python 包或设置 `PYTHONPATH`。默认执行全部 20 道题目，自动生成运行编号与报告。也可指定配置和覆盖参数：

```powershell
python scripts/bench.py config/bench.json --model your-model --reasoning-effort high --workers 2 --run-id my-run
```

`--base-url`、`--protocol` 可覆盖 API 设置。默认并发来自配置的 `parallel_workers`。使用相同配置和 `--run-id` 续跑时会跳过已有模型响应，只重试基础设施失败项。模型、工具链、数据集或并发数变化时应使用新的运行编号。

## 基准与评分

`v2-compile` 包含 20 道题目，覆盖格式与工程、核心库、流程控制、子程序与数据结构、修复与综合五类能力。仅测试 `raw` 轨道，不提供 Skill 上下文，共 20 个 pass@1 样本。总分为全部题目的平均分。

V2 沿用原有题目和编译门槛评分规则，以 e-packager v1.2.7 重新评测。V1 已废弃，旧成绩不进入 V2 榜单。

每题总分 100 分：格式与工程可靠性 45%、真实编译 35%、隐藏静态语义断言 20%。源码只有通过真实编译才能获得总分。预编译结构分用于诊断格式和回包问题；每次回包失败扣 15 分。HTTP 和网络重试不计入回包失败。编译结果临时写入 `.temp/`，不执行生成的 EXE。

## 项目目录

- `src/elang_bench/`：API、执行器和评分逻辑。
- `scripts/bench.py`：一键运行入口。
- `benchmarks/`：版本化题库。
- `config/`：配置模板；`bench.json` 和 `local/` 仅供本机使用。
- `tests/`：单元测试和真实工具链集成测试。
- `web/`：评分网站及公开报告。

运行输出保存到被 Git 忽略的 `results/<run-id>/`，配置、运行明细、缓存及编译产物不会上传。

重新生成本地报告无需请求模型：

```powershell
$env:PYTHONPATH = "src"
python -m elang_bench report my-run
python -m elang_bench report my-run --rescore
```

## 开发与测试

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

准备好 `config/bench.json` 后可运行真实工具链测试，不调用模型 API：

```powershell
$env:ELANG_BENCH_INTEGRATION = "1"
python -m unittest discover -s tests -p test_integration.py -v
```

网站构建直接使用 `web/public/data.json`，不读取或更新 README：

```powershell
npm ci
npm run web:build
npm run web:dev
```

## 许可

[MIT](LICENSE)
