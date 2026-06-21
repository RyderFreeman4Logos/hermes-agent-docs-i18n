---
name: test-driven-development
description: "TDD: enforce RED-GREEN-REFACTOR, tests before code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, tdd, development, quality, red-green-refactor]
    related_skills: [systematic-debugging, plan, subagent-driven-development]
---

# 测试驱动开发（TDD）

## 概述

先编写测试用例。观察其失败情况，再编写最少的代码来使其通过。

**核心原则：** 如果你没有亲眼看到测试用例失败，你就无法确定它是否在检测正确的内容。

**违背规则的字面要求，等同于违背了规则的精神。**

## 适用场景

**始终适用的情况：**
- 新功能开发
- 错误修复
- 代码重构
- 行为变更

**例外情况（需先征求用户意见）：**
- 临时原型
- 自动生成的代码
- 配置文件

是否有“就这一次跳过TDD”的想法？请停下，那只是借口罢了。

## 不变定律

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

在编写测试之前先写代码？那就删掉它，重新开始。

**绝无例外：**
- 不得将其保留作为“参考”
- 编写测试时不得对其进行“修改”
- 也不得查看它
- “删除”就是彻底删除

必须从测试出发，全新实现。没有商量余地。

## 红绿重构循环

### RED — 编写失败的测试

编写一个最简的测试，用以展示预期结果。

**优秀的测试应满足：**
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'

    result = retry_operation(operation)

    assert result == 'success'
    assert attempts == 3
```
名称清晰，能真实测试行为，仅此一点。

**糟糕的测试示例：**
```python
def test_retry_works():
    mock = MagicMock()
    mock.side_effect = [Exception(), Exception(), 'success']
    result = retry_operation(mock)
    assert result == 'success'  # What about retry count? Timing?
```
名称模糊，测试用例使用的是模拟代码而非真实代码。

**要求：**
- 每个测试用例仅对应一种行为
- 名称需清晰具描述性（名称中包含“和”字时请拆分）
- 必须使用真实代码，不得使用模拟代码（确实无法避免的情况除外）
- 名称应描述行为本身，而非实现方式

### 验证 RED — 观看其失败过程

**此项为强制要求，绝不可跳过。**

```bash
# Use terminal tool to run the specific test
pytest tests/test_feature.py::test_specific_behavior -v
```

确认以下情况：
- 测试失败（非因拼写错误导致的异常）
- 出现预期的失败信息
- 因功能缺失而失败

**测试立即通过？** 说明你正在测试现有行为。请修正该测试用例。

**测试出现错误？** 先修复错误，然后重新运行直至测试正确失败。

### 绿色状态 — 最小化代码量

只需编写最简的代码即可让测试通过，无需更多内容。

**良好：**
```python
def add(a, b):
    return a + b  # Nothing extra
```

**错误：**
```python
def add(a, b):
    result = a + b
    logging.info(f"Adding {a} + {b} = {result}")  # Extra!
    return result
```

不得添加新功能，也不得重构其他代码或进行超出测试范围的“改进”。

在 **GREEN** 模式下，以下行为属于允许的“作弊”手段：
- 硬编码返回值
- 直接复制粘贴
- 重复代码
- 跳过边界情况处理

我们会在 **REFACTOR** 模式中修复这些问题。

### 验证 **GREEN** 状态——观察其通过测试

**此项为必做要求。**

```bash
# Run the specific test
pytest tests/test_feature.py::test_specific_behavior -v

# Then run ALL tests to check for regressions
pytest tests/ -q
```

确认以下内容：
- 测试通过
- 其他测试仍全部通过
- 输出结果完整（无错误、无警告）

**测试失败了？** 修复代码，而非测试本身。

**其他测试失败了？** 立即处理回归问题。

### 重构 —— 优化整理

仅在所有测试通过后执行：
- 删除重复代码
- 优化变量/函数命名
- 提取辅助函数
- 简化表达式

始终确保测试保持通过状态，切勿新增功能逻辑。

**如果在重构过程中测试失败：** 立即回退，采用更小的步骤逐步处理。

### 重复执行

针对下一个需要处理的功能，依次进行下一个失败的测试。一次完成一个循环。

## 避免横向切分

切勿先编写所有测试，再实现所有功能。这就是所谓的横向切分：此时“红色”状态意味着“编写一堆假设的测试”，而“绿色”状态则意味着“让这些测试全部通过”。这种做法会导致测试过于脆弱，因为在实现代码之前，就预先设定了测试用例，而实际上只有通过实际运行才能了解哪些功能和接口才是真正重要的。

建议改用纵向追踪式任务列表：

```text
WRONG:
  RED:   test1, test2, test3, test4
  GREEN: impl1, impl2, impl3, impl4

RIGHT:
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

追踪子弹是一种端到端的行为切片。它能够证明路径是可行的，帮助你了解接口功能，同时让后续的每一项测试都建立在刚刚学到的知识基础上。

## 顺序为何重要

**“我稍后会写测试来验证功能是否正常”**

在代码通过后再编写的测试其实无法提供任何有效证明：
- 可能测试的内容有误
- 可能测试的是实现细节而非实际行为
- 可能遗漏了那些被忽略的边界情况
- 你根本看不到它是否能捕获错误

采用“先测试后编码”的方式，能迫使你直面测试失败的情况，从而确认测试确实针对了某个具体功能。

**“我已经手动测试过所有边界情况了”**

手动测试属于临时性的做法。你可能以为已经测试了一切，但实际上：
- 没有任何测试记录
- 代码发生变化时无法重新运行测试
- 在压力之下很容易忘记某些测试用例
- “我试的时候它能正常工作”并不等同于测试全面

自动化测试则具有系统性，每次运行的方式都完全一致。

**“删除数小时的工作成果太浪费了”**

这是沉没成本谬误。时间已经消耗殆尽。你现在可以选择：
- 删除代码并使用TDD重新编写（可靠性高）
- 保留代码，之后再补充测试（可靠性低，很可能会出现错误）

真正的“浪费”在于保留那些不可靠的代码。

**“TDD过于僵化，务实意味着要灵活调整”**

实际上TDD才是最务实的做法：
- 在提交代码之前就能发现错误（比事后调试更快）
- 防止功能退化（测试能立即捕捉到异常）
- 记录代码行为（测试展示了如何使用代码）
- 支持代码重构（可自由修改代码，测试会及时发现问题）

而所谓的“务实”捷径，实际上就是在生产环境中进行调试，效率反而更低。

**“先写测试也能达到相同目标——重要的是精神而非形式”**

并非如此。后写测试只能回答“这个功能现在能做什么？”，而先写测试则能回答“这个功能应该做什么？”

后写测试会受到实现方式的限制，你测试的只是自己构建的功能，而非需求所要求的真正功能。而先写测试则要求在实现之前就发现边界情况。

## 常见的借口

| 借口 | 实际情况 |
|------|----------|
| “太简单了，没必要测试” | 简单的代码也可能会出错。编写测试只需30秒而已。 |
| “我稍后会测试” | 代码立即通过并不能证明任何问题。 |
| “先写测试和后写测试目标一样” | 后写测试对应“它能做什么？”，而先写测试对应“它应该做什么？” |
| “我已经手动测试过了” | 临时性测试≠系统性测试。没有记录，也无法重复执行。 |
| “删除数小时的工作成果太浪费了” | 这是沉没成本谬误。保留未经验证的代码就是技术债务。 |
| “先保留作为参考，再写测试” | 你最终还是会对其进行修改，这其实还是后写测试。要么删除，要么重来。 |
| “需要先探索一下” | 没问题。但可以先放弃探索，直接从TDD开始。 |
| “测试难度大意味着设计不清晰” | 应该听从测试的反馈。难以测试的功能，其使用体验也会很差。 |
| “TDD会降低我的效率” | 实际上TDD比调试更快。务实的做法就是先写测试。 |
| “手动测试速度更快” | 手动测试无法覆盖边界情况。每次代码更改后都需要重新测试。 |
| “现有代码没有测试” | 你正在对代码进行改进，那就为所修改的代码添加测试吧。 |

## 危险信号——立即停止并重新开始

如果你发现自己有以下任何行为，应立即删除相关代码，从TDD重新开始：

- 先写代码，后写测试
- 在实现功能后才编写测试
- 测试在首次运行时就立即通过
- 无法解释测试失败的原因
- “稍后”才添加测试
- 以“就这一次”作为借口
| “我已经手动测试过它了” |
| “先写测试和后写测试目的相同” |
| “先保留作为参考”或“修改现有代码” |
| “已经花了X小时，删除太浪费了” |
| “TDD过于僵化，我更务实” |
| “这次情况不同……” |

**所有这些情况都意味着：删除代码，从TDD重新开始。**

## 验证检查清单

在认为工作已完成之前，请确认以下各项：

- [ ] 每个新函数/方法都有对应的测试
- [ ] 在实现功能之前，已让每个测试都失败过
- [ ] 每个测试失败的原因都是预期的（如功能缺失，而非拼写错误）
- [ ] 为通过每个测试而编写的代码尽可能简洁
- [ ] 所有测试都能通过
- [ ] 输出结果完美无缺（无错误、无警告）
- [ | 测试使用的是真实代码（只有在不可避免的情况下才使用模拟对象） |
| [ ] 已覆盖所有边界情况和错误场景

如果无法满足所有条件，说明你没有遵循TDD流程，需要重新开始。

## 遇到困难时的解决方法

| 问题 | 解决方案 |
|------|----------|
| 不知道如何编写测试 | 先设计出期望的API接口。先写出断言内容。也可以向用户咨询需求。 |
| 测试过于复杂 | 可能是设计本身太复杂，应简化接口设计。 |
| 必须对所有内容进行模拟 | 说明代码耦合度过高，应使用依赖注入技术。 |
| 测试准备过程过于繁琐 | 可以提取辅助函数。如果仍然复杂，则需要进一步简化设计。 |

## Hermes Agent集成

### 运行测试

可以在每个步骤中使用`terminal`工具来运行测试：

```python
# RED — verify failure
terminal("pytest tests/test_feature.py::test_name -v")

# GREEN — verify pass
terminal("pytest tests/test_feature.py::test_name -v")

# Full suite — verify no regressions
terminal("pytest tests/ -q")
```

### 使用 delegate_task 时

在派发子智能体执行任务时，需在目标中强制实施测试驱动开发原则：

```python
delegate_task(
    goal="Implement [feature] using strict TDD",
    context="""
    Follow test-driven-development skill:
    1. Write failing test FIRST
    2. Run test to verify it fails
    3. Write minimal code to pass
    4. Run test to verify it passes
    5. Refactor if needed
    6. Commit

    Project test command: pytest tests/ -q
    Project structure: [describe relevant files]
    """,
    toolsets=['terminal', 'file']
)
```

### 采用系统化调试方法

发现漏洞？请编写能够复现该问题的失败测试，然后遵循测试驱动开发（TDD）流程。测试不仅可用于验证修复方案的有效性，还能防止问题再次出现。

绝不要在没有测试的情况下直接修复漏洞。

## 常见的测试反模式

- **测试模拟行为而非真实行为**——模拟对象应用于验证系统间的交互，而非替代被测系统本身
- **测试实现细节**——应关注行为或结果，而非内部方法调用
- **仅测试正常流程**——务必同时测试边界情况、错误处理以及极端场景
- **脆弱性过高的测试**——测试应侧重于验证功能行为，而非代码结构；重构不应导致测试失效

## 最终准则

```
Production code → test exists and failed first
Otherwise → not TDD
```

未经用户明确许可，不得抛出任何异常。
