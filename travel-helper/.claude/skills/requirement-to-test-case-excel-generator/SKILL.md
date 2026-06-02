---
name: Requirement to Test Case Excel Generator
description: Generate structured test cases from requirement documents and export them to Excel in a fixed template format.
---

---
name: Expert Requirement to Test Case Excel Generator
description: Generate expert-level structured test cases from requirement documents and export them to Excel with standardized format and full scenario coverage.
---

# Skill: Expert Requirement to Test Case Excel Generator

## Purpose

根据需求描述文档，自动识别业务功能与测试点，生成 **测试专家级测试用例**，并输出为 **Excel (.xlsx)** 文件。

生成的测试用例应满足以下目标：

- 覆盖核心业务流程
- 覆盖逻辑分支
- 覆盖异常路径
- 覆盖边界条件
- 可直接交付测试团队执行

Excel 表头格式必须与指定模板完全一致。

---

# Scope

本 Skill 只负责：

1. 解析需求文档
2. 识别业务模块与功能点
3. 识别核心业务场景
4. 生成结构化测试用例
5. 输出 Excel 测试用例文件

本 Skill 不负责：

- 编写自动化测试代码
- 执行测试
- 推断技术架构
- 生成数据库设计
- 生成接口代码

---

# Input

支持以下输入来源：

requirement_doc

需求文档内容，可以是：

- Markdown
- Text
- Word
- PDF
- Excel
- 粘贴在对话中的需求内容

optional_context

可选补充信息：

- 系统名称
- 业务背景
- 模块名称
- 测试范围
- 是否需要覆盖异常场景
- 是否需要覆盖边界情况

optional_prefix

用例编号前缀（可选）

例如：

TC
LOGIN-TC
UAT-TC

默认使用：

TC

---

# Output

输出一个 Excel 文件：

文件格式：

xlsx

默认 Sheet 名称：

测试用例

如果模块较多，也可以按模块拆分多个 Sheet。

---

# Excel Column Template

Excel 表头必须严格按以下顺序生成：

用例编号
模块
功能点
前置条件
操作步骤
预期结果
优先级
执行状态
备注

列顺序不可改变。

---

# Excel Column Rules

## 用例编号

自动递增：

TC001
TC002
TC003

规则：

- 3 位数字补零
- 编号必须唯一
- 编号必须连续

---

## 模块

从需求文档中识别模块名称。

如果需求没有明确模块：

按功能逻辑自动分组。

例如：

用户管理
店铺管理
活动管理
数据查询

---

## 功能点

功能点必须：

- 简洁
- 清晰
- 表达测试目标

示例：

正确账号密码登录
错误账号密码登录
忘记密码邮箱找回
店铺列表分页查询
店铺上线操作

---

## 前置条件

只描述执行该用例前必须满足的条件。

例如：

已登录系统
系统存在有效用户账号
已进入对应页面

不得写操作步骤。

---

## 操作步骤

操作步骤必须：

- 按顺序编号
- 每一步清晰可执行

示例：

1. 输入账号
2. 输入密码
3. 点击登录按钮

步骤必须保证：

- 测试人员可以复现
- 每一步都有明确动作

---

## 预期结果

必须可验证。

正确示例：

页面提示“账号或密码错误”
成功跳转至首页
列表显示新建数据

错误示例：

系统正常
页面没有问题

---

## 优先级

Excel 中必须设置 **下拉列表**。

允许值：

高
中
低

优先级判断规则：

核心业务流程 → 高  
高频功能 → 高  
普通功能 → 中  
边界测试 → 中  
低影响功能 → 低

---

## 执行状态

Excel 中必须设置 **下拉列表**。

允许值：

未执行
执行中
已执行

默认值：

未执行

---

## 备注

用于补充信息，例如：

核心业务场景
依赖数据
需求待确认

---

# Core Business Scenario Identification

必须自动识别 **核心业务场景**。

核心业务场景定义：

1. 用户主流程
2. 高频操作
3. 关键业务能力
4. 关键业务节点
5. 高风险逻辑

示例：

用户登录
创建订单
创建活动
新建店铺

---

# Core Scenario Marking

如果是核心业务场景：

在备注列标记：

核心业务场景

---

# Core Scenario Coverage Rules

核心业务场景必须生成更完整的测试用例集合。

至少覆盖以下类型：

正常路径

例如：

正确账号密码登录

逻辑分支

例如：

不同权限
不同状态
不同输入组合

异常路径

例如：

错误账号
参数非法
权限不足

边界情况

例如：

最大长度
最小长度
分页边界
空数据

状态流转

例如：

创建 → 编辑 → 删除

---

# Scenario Coverage Matrix

生成测试用例时建议遵循以下测试矩阵：

场景类型：

正常场景
异常场景
边界场景
状态场景
权限场景

输入类型：

合法输入
非法输入
空输入
极值输入

系统状态：

未登录
已登录
无权限
数据不存在

---

# Test Case Generation Strategy

对于每个功能点：

至少生成：

正常流程用例
异常输入用例
边界输入用例
权限校验用例

对于核心业务场景：

至少生成：

5 条以上测试用例。

---

# Excel Formatting Requirements

Excel 输出需要包含：

表头加粗  
单元格自动换行  
表格边框  
合理列宽  
冻结首行  

建议列宽：

用例编号：12  
模块：16  
功能点：28  
前置条件：24  
操作步骤：40  
预期结果：40  
优先级：10  
执行状态：12  
备注：18  

---

# Excel Data Validation

以下列必须配置 Excel 下拉列表：

优先级：

高
中
低

执行状态：

未执行
执行中
已执行

默认值：

未执行

---

# Output Quality Requirements

生成结果必须满足：

1. 覆盖核心业务流程
2. 不遗漏关键测试点
3. 操作步骤可复现
4. 预期结果可验证
5. 编号连续
6. 不生成明显重复用例
7. 核心业务场景必须标记
8. Excel 可直接交付测试人员使用

---

# Incomplete Requirement Handling

如果需求不完整：

优先生成明确可执行的测试用例。

对不确定部分：

在备注中标记：

需求未明确
需产品确认
需补充校验规则

禁止臆造业务逻辑。

---

# Final Instruction

当用户提供需求文档后：

1. 解析模块与功能点
2. 识别核心业务场景
3. 生成完整测试用例
4. 生成 Excel 文件
5. 设置下拉列表
6. 标记核心业务场景

最终输出为：

测试用例 Excel 文件。