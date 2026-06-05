# .specify/scripts/bash/ 脚本详解

## 调用关系总览

```
speckit-specify
  └─ before_specify hook → create-new-feature.sh       # 创建分支+目录+spec

speckit-clarify
  └─ check-prerequisites.sh --json --paths-only         # 只取路径，不校验

speckit-plan
  └─ setup-plan.sh --json                               # 创建 plan.md

speckit-tasks
  └─ setup-tasks.sh --json                              # 扫描文档，定位模板

speckit-implement
  └─ check-prerequisites.sh --json --require-tasks      # 校验 tasks.md 存在
```

---

## 1. common.sh — 公共函数库

**不直接执行**，被其他脚本通过 `source "$SCRIPT_DIR/common.sh"` 加载。定义了所有脚本共享的基础函数。

### 1.1 find_specify_root()

从传入目录（默认当前目录）一级一级向上找 `.specify/` 目录，找到就返回根路径；到文件系统根目录还没找到就返回失败。

**这是整个项目定位"我在哪个 spec-kit 项目里"的核心逻辑。**

### 1.2 get_repo_root()

三级 fallback 找项目根目录：

| 优先级 | 方式 | 说明 |
|---|---|---|
| 1 | `.specify/` 目录 | spec-kit 项目的核心标记 |
| 2 | `git rev-parse --show-toplevel` | git 仓库根目录 |
| 3 | 脚本所在位置的上级目录 | 非 git / 非 spec-kit 环境兜底 |

### 1.3 get_current_branch()

四级 fallback 获取"当前功能名"：

| 优先级 | 方式 | 说明 |
|---|---|---|
| 1 | `SPECIFY_FEATURE` 环境变量 | 用户显式指定 |
| 2 | `git rev-parse --abbrev-ref HEAD` | git 分支名 |
| 3 | `specs/` 下编号最大的目录名 | 非 git 环境，支持时间戳和序号两种格式 |
| 4 | 返回 `"main"` | 兜底 |

### 1.4 has_git()

三步判断当前是否在 git 仓库内：

1. `git` 命令可用
2. `.git` 存在（目录或 file，兼容 worktree/submodule）
3. `git rev-parse --is-inside-work-tree` 返回成功

### 1.5 spec_kit_effective_branch_name()

如果分支名是两段式（如 `feat/004-name`），去掉前缀只取第二段 `004-name`；否则原样返回。

### 1.6 check_feature_branch()

校验分支名格式，合法格式有两种：

- **序号式**：`001-feature-name`（3位以上数字开头）
- **时间戳式**：`20260319-143022-feature-name`

同时排除畸形的时间戳（如 `2026031-143022` 只有7位日期）。非 git 环境跳过校验，仅输出警告。

### 1.7 read_feature_json_feature_directory()

三级 fallback 解析 `.specify/feature.json` 中的 `feature_directory` 字段：

| 优先级 | 工具 |
|---|---|
| 1 | `jq` |
| 2 | `python3` |
| 3 | `grep + sed` |

始终返回 0（即使解析失败返回空字符串），防止 `set -e` 中断调用方。

### 1.8 feature_json_matches_feature_dir()

校验 `.specify/feature.json` 里记录的目录路径是否和当前实际的功能目录一致。用于判断是否需要执行分支名校验。

### 1.9 find_feature_dir_by_prefix()

从分支名提取数字前缀（如 `004` 或 `20260319-143022`），去 `specs/` 下匹配对应的目录。

这样即使你在 `004-fix-bug` 分支上操作，也能找到 `specs/004-add-feature` 这个 spec 目录——允许多个分支操作同一个 spec。

### 1.10 get_feature_paths()

**核心函数**：一次输出所有路径变量。

```bash
REPO_ROOT=...
CURRENT_BRANCH=...
HAS_GIT=...
FEATURE_DIR=...          # specs/NNN-xxx
FEATURE_SPEC=...         # specs/NNN-xxx/spec.md
IMPL_PLAN=...            # specs/NNN-xxx/plan.md
TASKS=...                # specs/NNN-xxx/tasks.md
RESEARCH=...             # specs/NNN-xxx/research.md
DATA_MODEL=...           # specs/NNN-xxx/data-model.md
QUICKSTART=...           # specs/NNN-xxx/quickstart.md
CONTRACTS_DIR=...        # specs/NNN-xxx/contracts
```

三级优先级解析 `FEATURE_DIR`：
1. `SPECIFY_FEATURE_DIRECTORY` 环境变量
2. `.specify/feature.json` 的 `feature_directory` 字段
3. 分支名前缀匹配（fallback）

调用方通过 `eval "$(get_feature_paths)"` 把这些变成环境变量。

使用 `printf '%q'` 做 shell 安全转义，防止路径含空格或特殊字符被注入。

### 1.11 resolve_template()

按 4 级优先级查找模板文件：

| 优先级 | 路径 | 说明 |
|---|---|---|
| 1 | `.specify/templates/overrides/${name}.md` | 项目级覆盖 |
| 2 | `.specify/presets/<id>/templates/${name}.md` | 预设模板（按 priority 排序） |
| 3 | `.specify/extensions/<ext>/templates/${name}.md` | 扩展提供的模板 |
| 4 | `.specify/templates/${name}.md` | 核心默认模板 |

找到第一个就返回路径。

### 1.12 resolve_template_content()

比 `resolve_template` 更高级——不只是返回文件路径，而是把多层模板**按策略合并**成最终内容。

支持四种组合策略：

| 策略 | 行为 |
|---|---|
| `replace` | 完全替换（高优先级覆盖低优先级） |
| `prepend` |  prepend 到 base 内容之前 |
| `append` | append 到 base 内容之后 |
| `wrap` | 用高优先级模板包裹 base 内容（通过 `{CORE_TEMPLATE}` 占位符） |

### 1.13 辅助函数

| 函数 | 作用 |
|---|---|
| `has_jq()` | 判断 `jq` 是否可用 |
| `json_escape()` | 手动转义 JSON 特殊字符和控制字符（无 jq 时的 fallback） |
| `check_file()` | 打印文件存在状态：`✓ xxx` 或 `✗ xxx` |
| `check_dir()` | 打印目录存在状态（非空）：`✓ xxx` 或 `✗ xxx` |

---

## 2. create-new-feature.sh — 创建新功能分支和目录

**调用者**：`speckit-specify` 的 `before_specify` hook（git 扩展）

### 2.1 参数解析

```
--json                      输出 JSON 格式
--dry-run                   只计算不创建
--allow-existing-branch     允许切换到已存在的分支
--short-name <name>         手动指定短名称
--number N                  手动指定编号
--timestamp                 用时间戳代替序号
```

### 2.2 序号检测函数

| 函数 | 扫描来源 |
|---|---|
| `get_highest_from_specs()` | 本地 `specs/` 目录 |
| `get_highest_from_branches()` | 本地 git 分支 |
| `get_highest_from_remote_refs()` | 远程分支（通过 `git ls-remote`，无副作用） |
| `check_existing_branches()` | 综合三者，取最大值 +1 |

匹配规则：`^[0-9]{3,}-` 但排除 `^[0-9]{8}-[0-9]{6}-`（时间戳格式）。

### 2.3 短名称生成

```bash
generate_branch_name() {
    # 1. 定义停用词列表（i, a, an, the, to, for, want, need, add, ...）
    # 2. 描述转小写，非字母数字变空格
    # 3. 过滤掉停用词和 <3 字符的词（除非原文是大写缩写）
    # 4. 取前 3-4 个有意义的词用短横线连接
}
```

示例：`"I want to add user authentication"` → `user-auth`

如果用户提供了 `--short-name`，跳过生成，直接清理后使用。

### 2.4 组装分支名

```
序号模式：  printf "%03d" → 003    →  003-user-auth
时间戳模式：date +%Y%m%d-%H%M%S   →  20260605-143022-user-auth
```

**GitHub 244 字节限制校验**：如果超长，截断后缀到单词边界，并输出警告。

### 2.5 创建动作（非 dry-run 时）

```bash
# 1. 创建 git 分支
git checkout -q -b "$BRANCH_NAME"

# 2. 如果已存在：根据 ALLOW_EXISTING 决定是否切换
#    - 已在该分支上 → 无操作
#    - ALLOW_EXISTING=true → checkout 切换
#    - 否则 → 报错退出

# 3. 创建目录
mkdir -p "$FEATURE_DIR"

# 4. 复制 spec 模板
TEMPLATE=$(resolve_template "spec-template" "$REPO_ROOT")
cp "$TEMPLATE" "$SPEC_FILE"

# 5. 输出结果（JSON 或文本）
{"BRANCH_NAME":"003-user-auth","SPEC_FILE":"...","FEATURE_NUM":"003"}
```

---

## 3. check-prerequisites.sh — 前置条件检查

**调用者**：`speckit-clarify`、`speckit-implement`

### 3.1 参数

| 参数 | 作用 |
|---|---|
| `--json` | 输出 JSON 格式 |
| `--paths-only` | 只输出路径变量，不做任何校验 |
| `--require-tasks` | 额外要求 `tasks.md` 存在（implement 阶段用） |
| `--include-tasks` | 在 `AVAILABLE_DOCS` 列表中包含 `tasks.md` |

### 3.2 --paths-only 模式

```bash
if $PATHS_ONLY; then
    # 输出所有路径，不做校验，直接退出
    exit 0
fi
```

`speckit-clarify` 使用此模式，只需要路径，不校验前置条件。

### 3.3 前置校验（非 paths-only 时）

| 校验项 | 条件 | 失败提示 |
|---|---|---|
| 分支名格式 | `check_feature_branch` | "Not on a feature branch" |
| 功能目录存在 | `-d $FEATURE_DIR` | "Run /speckit-specify first" |
| plan.md 存在 | `-f $IMPL_PLAN` | "Run /speckit-plan first" |
| tasks.md 存在 | `--require-tasks` 时检查 | "Run /speckit-tasks first" |

### 3.4 扫描可用文档

```bash
docs=()
[[ -f "$RESEARCH" ]] && docs+=("research.md")
[[ -f "$DATA_MODEL" ]] && docs+=("data-model.md")
[[ -d "$CONTRACTS_DIR" && -n "$(ls -A "$CONTRACTS_DIR")" ]] && docs+=("contracts/")
[[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")
$INCLUDE_TASKS && [[ -f "$TASKS" ]] && docs+=("tasks.md")
```

输出格式：

```json
{"FEATURE_DIR":"specs/002-travel-plan-detail","AVAILABLE_DOCS":["research.md","contracts/"]}
```

---

## 4. setup-plan.sh — 初始化实现计划

**调用者**：`speckit-plan`

### 4.1 流程

```
1. source common.sh
2. eval "$(get_feature_paths)"          # 获取所有路径
3. check_feature_branch()               # 校验分支名
4. feature_json_matches_feature_dir()   # 校验 feature.json 是否匹配
```

### 4.2 创建或跳过 plan.md

```bash
if [[ -f "$IMPL_PLAN" ]]; then
    # 已存在 → 跳过，避免覆盖用户已填内容
    echo "Plan already exists, skipping template copy"
else
    TEMPLATE=$(resolve_template "plan-template" "$REPO_ROOT")
    if [[ -n "$TEMPLATE" ]] && [[ -f "$TEMPLATE" ]]; then
        cp "$TEMPLATE" "$IMPL_PLAN"     # 从模板复制
    else
        touch "$IMPL_PLAN"              # 模板找不到 → 创建空文件
    fi
fi
```

**关键设计**：`plan.md` 已存在时跳过复制，不会覆盖用户已填的内容。

### 4.3 输出

```json
{
  "FEATURE_SPEC":"specs/002-xxx/spec.md",
  "IMPL_PLAN":"specs/002-xxx/plan.md",
  "SPECS_DIR":"specs/002-xxx",
  "BRANCH":"002-travel-plan-detail",
  "HAS_GIT":"true"
}
```

---

## 5. setup-tasks.sh — 初始化任务清单

**调用者**：`speckit-tasks`

### 5.1 流程

```
1. source common.sh
2. eval "$(get_feature_paths)"          # 获取所有路径
3. check_feature_branch()               # 校验分支名
4. feature_json_matches_feature_dir()   # 校验 feature.json 是否匹配
5. mkdir -p "$FEATURE_DIR"              # 确保目录存在
```

### 5.2 校验前置文件

| 文件 | 必须存在 | 失败提示 |
|---|---|---|
| `plan.md` | ✅ | "Run /speckit-plan first" |
| `spec.md` | ✅ | "Run /speckit-specify first" |

### 5.3 扫描可用文档

```bash
docs=()
[[ -f "$RESEARCH" ]] && docs+=("research.md")
[[ -f "$DATA_MODEL" ]] && docs+=("data-model.md")
[[ -d "$CONTRACTS_DIR" && -n "$(ls -A "$CONTRACTS_DIR")" ]] && docs+=("contracts/")
[[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")
```

### 5.4 解析 tasks 模板

```bash
TASKS_TEMPLATE=$(resolve_template "tasks-template" "$REPO_ROOT") || true
if [[ -z "$TASKS_TEMPLATE" ]] || [[ ! -f "$TASKS_TEMPLATE" ]]; then
    echo "ERROR: Could not resolve required tasks-template" >&2
    exit 1
fi
```

通过 4 级优先级栈查找 `tasks-template.md`，找不到就报错退出。

### 5.5 输出

```json
{
  "FEATURE_DIR":"specs/002-travel-plan-detail",
  "AVAILABLE_DOCS":["research.md","contracts/"],
  "TASKS_TEMPLATE":"/absolute/path/to/tasks-template.md"
}
```

`AVAILABLE_DOCS` 告诉 `speckit-tasks` 哪些设计文档已经存在，让它可以按需读取。

---

## 附录：数据流

```
create-new-feature.sh
  输出：BRANCH_NAME, FEATURE_NUM, SPEC_FILE
  作用：创建 git 分支 + specs/NNN-xxx/ 目录 + spec.md
       写入 .specify/feature.json

check-prerequisites.sh (--paths-only)
  输出：REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, IMPL_PLAN, TASKS
  作用：纯路径查询，不校验

setup-plan.sh
  输入：无（自动探测）
  输出：FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH, HAS_GIT
  作用：创建 plan.md 模板

setup-tasks.sh
  输入：无（自动探测）
  输出：FEATURE_DIR, TASKS_TEMPLATE, AVAILABLE_DOCS[]
  作用：校验前置文件，扫描设计文档，定位 tasks 模板
```
