---
name: Prototype Image Requirement Extractor
description: Extract structured requirements from product prototypes image for SDD specification generation
---

---
name: Prototype Image Requirement Extractor
description: Extract industrial-grade, structured requirements (including layout/position) from product prototypes for SDD specification generation
---

# Skill: Prototype Image Requirement Extractor (Industrial)

## Purpose

从产品原型图中提取：

1. **业务向需求文字描述**（模块级，单文件）
2. **UI Contract**（页面级，多文件）

输出用于后续 SDD / Speckit 流程。

本 Skill **仅负责需求提取**，不进行任何技术设计。

---

# Hard Constraints

禁止执行：

- 创建 speckit spec
- 执行 speckit 命令
- 生成代码
- 设计系统架构
- 设计 API
- 设计数据库

只允许输出：

- 业务需求描述
- UI Contract（按页面拆分）

---

# Input

支持以下输入：

| Field | Type | Description |
|------|------|-------------|
| prototype_image | image | 原型截图 |
| prototype_link | string | Figma / Axure / 墨刀 |
| page_description | markdown | 页面描述 |

---

# Output Directory Convention

输出必须遵循 speckit 目录规范：

```
specs/<NNN>-<short-name>/
├── prototype-requirements.md
└── contracts/
    └── ui-contracts/
        ├── index.yaml
        ├── <page-key>.page.yaml
        ├── <overlay-key>.modal.yaml
        ├── <overlay-key>.drawer.yaml
        └── <overlay-key>.popover.yaml
```

说明：

- `prototype-requirements.md`：模块级业务需求描述（单文件）
- `contracts/ui-contracts/index.yaml`：该模块的 UI 合集索引（列出所有页面与契约文件）
- `contracts/ui-contracts/<page-key>.*.yaml`：页面/弹层级 UI 契约（一个页面/弹层一个文件）
- API 契约（`*-api.md`）由后续流程生成，放在 `contracts/` 根目录

---

# Naming Rules

## Feature Naming (short-name)

short-name 使用：

```
action-noun
```

示例：

```
user-management
member-search
points-adjustment
coupon-management
order-query
```

命名要求：

- kebab-case
- 2–4 个单词
- 保留业务术语

## Page Key Naming (page-key / overlay-key)

统一使用：

```
<entity>-<action>
```

示例：

```
user-list
user-create
user-edit
role-assign
coupon-detail
order-list
```

要求：

- kebab-case
- 2–4 个单词
- 同一模块内必须唯一
- page-key 必须稳定（不要随文案变化）

---

# Extraction Principle

需求提取遵循以下顺序：

```
Prototype
↓
Module Purpose
↓
Pages & Overlays
↓
User Actions
↓
Business Requirements
↓
UI Contracts (per page)
```

核心原则：

**UI → 用户行为 → 业务需求**

需求描述必须：

- 简洁
- 清晰
- 业务导向
- 不包含技术实现

---

# Output: prototype-requirements.md (Module-level, Single File)

需求文档为模块级，必须包含该模块下的页面清单，但不写 UI 细节。

结构如下：

```
# Feature

User Management

---

# Module Purpose

该模块用于管理系统用户，支持用户查询、创建、编辑、启用/禁用等管理操作。

---

# Pages & Overlays

- user-list (page): 用户列表页，用于查看与检索用户，并发起创建/编辑/禁用操作
- user-create (modal): 创建用户弹窗，用于录入新用户信息并提交
- user-edit (drawer): 编辑用户抽屉，用于修改用户信息并保存

---

# User Actions

管理员可以执行以下操作：

- 查看用户列表
- 搜索用户（用户名/邮箱/状态）
- 创建用户
- 编辑用户
- 禁用用户
- 启用用户

---

# Business Requirements

1. 系统应提供用户列表查询能力，并支持分页展示。
2. 管理员可以按用户名、邮箱、状态检索用户。
3. 管理员可以创建新用户，创建时必须填写用户名和邮箱。
4. 用户名必须唯一。
5. 管理员可以编辑用户信息并保存。
6. 管理员可以禁用用户，禁用后用户无法登录。
7. 管理员可以启用已禁用用户，启用后恢复登录能力。
```

要求：

- 只描述“业务需求”，不描述实现方式
- 不输出 Acceptance Criteria / Edge Cases / API
- “Pages & Overlays” 仅列清单与一句话用途

---

# Output: UI Contracts (Page-level, Multiple Files)

## contracts/ui-contracts/index.yaml (Module UI Index)

该文件用于汇总模块内的所有页面与契约文件，便于工具/AI 批处理读取。

```yaml
feature:
  short_name: user-management
  title: User Management

contracts:
  pages:
    - page_key: user-list
      type: page
      file: user-list.page.yaml
    - page_key: user-create
      type: modal
      file: user-create.modal.yaml
    - page_key: user-edit
      type: drawer
      file: user-edit.drawer.yaml

conventions:
  page_key_pattern: "<entity>-<action>"
  file_naming:
    page: "<page-key>.page.yaml"
    modal: "<overlay-key>.modal.yaml"
    drawer: "<overlay-key>.drawer.yaml"
    popover: "<overlay-key>.popover.yaml"
```

---

## UI Contract YAML Structure (Industrial, Per Page)

每个页面/弹层契约文件必须符合以下结构（一个文件只描述一个 page_key）：

```yaml
feature:
  short_name: <kebab-case>

page:
  key: <page-key>
  name: <string>
  type: page|modal|drawer|popover
  route: <string|unknown>

layout:
  regions:
    - key: header
      position: top
      containers: [page-header]
    - key: toolbar
      position: top-right
      containers: [action-bar]
    - key: filters
      position: top
      containers: [filter-card]
    - key: content
      position: main
      containers: [content-card]
    - key: footer
      position: bottom
      containers: [pagination-bar]

containers:
  - key: page-header
    type: header
    title: <string>
  - key: action-bar
    type: toolbar
  - key: filter-card
    type: card
  - key: content-card
    type: card

components:

  toolbar:
    container: action-bar
    buttons:
      - key: <string>
        label: <string>
        intent: primary|default|danger|link
        visibility: public|role_based|permission_based|unknown
        action: <user_action_key>

  search:
    container: filter-card
    mode: submit|auto|mixed|unknown
    fields:
      - key: <string>
        label: <string>
        type: text|number|select|date|daterange|switch|custom
        required: true|false|unknown
        default: <any>
        placeholder: <string|empty>
        validation:
          - rule: <string>
            message: <string>
        options:
          - label: <string>
            value: <string>

  table:
    container: content-card
    row_key: <string>
    pagination:
      enabled: true|false|unknown
      page_size_options: [10, 20, 50, 100]
    columns:
      - key: <string>
        label: <string>
        type: text|enum|date|datetime|currency|number|status|tag|custom
        sortable: true|false|unknown
        filterable: true|false|unknown
        formatter: <string|empty>
    row_actions:
      - key: <string>
        label: <string>
        danger: true|false|unknown
        confirm: true|false|unknown
        action: <user_action_key>

overlays:
  - key: <overlay-key>
    type: modal|drawer|popover
    trigger:
      from: toolbar|row_action|link|unknown
      action: <user_action_key>
    title: <string>

states:
  loading:
    enabled: true
    skeleton: true|false|unknown
  empty:
    message: <string>
  error:
    message: <string>
    retry: true|false|unknown
```

---

## Example: contracts/ui-contracts/user-list.page.yaml

```yaml
feature:
  short_name: user-management

page:
  key: user-list
  name: User List
  type: page
  route: /users

layout:
  regions:
    - key: header
      position: top
      containers: [page-header]
    - key: toolbar
      position: top-right
      containers: [action-bar]
    - key: filters
      position: top
      containers: [filter-card]
    - key: content
      position: main
      containers: [table-card]
    - key: footer
      position: bottom
      containers: [pagination-bar]

containers:
  - key: page-header
    type: header
    title: User Management
  - key: action-bar
    type: toolbar
  - key: filter-card
    type: card
  - key: table-card
    type: card
  - key: pagination-bar
    type: footer

components:

  toolbar:
    container: action-bar
    buttons:
      - key: create-user
        label: Create User
        intent: primary
        visibility: permission_based
        action: create_user

  search:
    container: filter-card
    mode: submit
    fields:
      - key: username
        label: Username
        type: text
        required: false
      - key: email
        label: Email
        type: text
        required: false
      - key: status
        label: Status
        type: select
        required: false
        options:
          - label: ACTIVE
            value: ACTIVE
          - label: DISABLED
            value: DISABLED

  table:
    container: table-card
    row_key: userId
    pagination:
      enabled: true
      page_size_options: [10, 20, 50, 100]
    columns:
      - key: username
        label: Username
        type: text
        sortable: true
      - key: email
        label: Email
        type: text
      - key: status
        label: Status
        type: status
        filterable: true
      - key: created_time
        label: Created Time
        type: datetime
        sortable: true
    row_actions:
      - key: edit
        label: Edit
        danger: false
        confirm: false
        action: edit_user
      - key: disable
        label: Disable
        danger: true
        confirm: true
        action: disable_user

overlays:
  - key: user-create
    type: modal
    trigger:
      from: toolbar
      action: create_user
    title: Create User
  - key: user-edit
    type: drawer
    trigger:
      from: row_action
      action: edit_user
    title: Edit User

states:
  loading:
    enabled: true
    skeleton: true
  empty:
    message: No users found
  error:
    message: Failed to load users
    retry: true
```

---

## Example: contracts/ui-contracts/user-create.modal.yaml

```yaml
feature:
  short_name: user-management

page:
  key: user-create
  name: Create User
  type: modal
  route: unknown

layout:
  regions:
    - key: header
      position: top
      containers: [modal-header]
    - key: content
      position: main
      containers: [form-card]
    - key: footer
      position: bottom
      containers: [modal-actions]

containers:
  - key: modal-header
    type: header
    title: Create User
  - key: form-card
    type: card
  - key: modal-actions
    type: footer

components:

  form:
    container: form-card
    fields:
      - key: username
        label: Username
        type: text
        required: true
      - key: email
        label: Email
        type: text
        required: true
      - key: status
        label: Status
        type: select
        required: false
        default: ACTIVE
        options:
          - label: ACTIVE
            value: ACTIVE
          - label: DISABLED
            value: DISABLED

  actions:
    container: modal-actions
    buttons:
      - key: submit
        label: Save
        intent: primary
        action: submit_create_user
      - key: cancel
        label: Cancel
        intent: default
        action: cancel

states:
  loading:
    enabled: false
    skeleton: false
  empty:
    message: ""
  error:
    message: Failed to create user
    retry: false
```

---

# Extraction Quality Checklist (Must Self-Validate)

在输出前自检以下项（只做自检，不输出 checklist）：

- contracts/ui-contracts/ 目录下是否按页面拆分为多个 YAML 文件
- 是否存在 contracts/ui-contracts/index.yaml 且列出所有契约文件
- 每个 page_key 是否唯一且稳定
- 每个契约文件是否只包含一个 page.key
- 是否包含 layout.regions 的 position 信息
- 关键组件（toolbar/search/table/form/actions）是否具备可用字段

---

# Summary

本 Skill 的职责：

Prototype  
↓  
模块级业务需求提取（单文件）  
↓  
prototype-requirements.md  

Prototype  
↓  
页面级 UI 契约提取（多文件）  
↓  
contracts/ui-contracts/index.yaml + contracts/ui-contracts/*.yaml  

输出用于后续流程：

/speckit.specify  
/speckit.plan  
/speckit.tasks  
/speckit.implement