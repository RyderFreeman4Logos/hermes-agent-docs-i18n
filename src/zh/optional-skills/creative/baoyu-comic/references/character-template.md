# 角色定义模板

## 角色文档格式

按照以下结构创建 `characters/characters.md` 文件：

```markdown
# Character Definitions - [Comic Title]

**Style**: [selected style]
**Art Direction**: [Ligne Claire / Manga / etc.]

---

## Character 1: [Name]

**Role**: [Protagonist / Mentor / Antagonist / Narrator]
**Age**: [approximate age or age range in story]

**Appearance**:
- Face shape: [oval/square/round]
- Hair: [color, style, length]
- Eyes: [color, shape, distinctive features]
- Build: [height, body type]
- Distinguishing features: [glasses, beard, scar, etc.]

**Costume**:
- Default outfit: [detailed description]
- Color palette: [primary colors for this character]
- Accessories: [hat, bag, tools, etc.]

**Expression Range**:
- Neutral: [description]
- Happy/Excited: [description]
- Thinking/Confused: [description]
- Determined: [description]

**Visual Reference Notes**:
[Any specific artistic direction]

---

## Character 2: [Name]
...
```

## 参考资料页图像提示词

在定义角色之后，需添加用于生成参考资料页的提示词：

```markdown
## Reference Sheet Prompt

Character reference sheet in [style] style, clean lines, flat colors:

[ROW 1 - Character Name]:
- Front view: [detailed description]
- 3/4 view: [description]
- Expression sheet: Neutral | Happy | Focused | Worried

[ROW 2 - Character Name]:
...

COLOR PALETTE:
- [Character 1]: [colors]
- [Character 2]: [colors]

White background, clear labels under each character.
```

## 示例：图灵传记

```markdown
# Character Definitions - The Imitation Game

**Style**: classic (Ligne Claire)
**Art Direction**: Clean lines, muted colors, period-accurate details

---

## Character 1: Alan Turing

**Role**: Protagonist
**Age**: 25-40 (varies across story)

**Appearance**:
- Face shape: Oval, slightly angular
- Hair: Dark brown, wavy, slightly disheveled
- Eyes: Deep-set, intense gaze
- Build: Tall, lean, slightly awkward posture
- Distinguishing features: Prominent brow, thoughtful expression

**Costume**:
- Default outfit: Tweed jacket with elbow patches, white shirt, no tie
- Color palette: Muted browns, navy blue, cream
- Accessories: Occasionally a pipe, papers/notebooks

**Expression Range**:
- Neutral: Thoughtful, slightly distant
- Happy/Excited: Eureka moment, eyes bright, subtle smile
- Thinking/Confused: Furrowed brow, looking at abstract space
- Determined: Jaw set, focused eyes

---

## Character 2: The Bombe Machine

**Role**: Supporting (anthropomorphized)
**Appearance**:
- Large brass and wood cabinet
- Dial "eyes" that can express states
- Paper tape "mouth"
- Indicator lights for emotions

**Expression Range**:
- Processing: Spinning dials, humming
- Success: Lights up warmly
- Stuck: Smoke wisps, stuttering

---

## Reference Sheet Prompt

Character reference sheet in Ligne Claire style, clean lines, flat colors:

TOP ROW - Alan Turing:
- Front view: Young man, 30s, short dark wavy hair, thoughtful expression, wearing tweed jacket with elbow patches, white shirt
- 3/4 view: Same character, slight smile, showing profile of nose
- Expression sheet: Neutral | Excited (eureka moment) | Focused (working) | Worried

BOTTOM ROW - The Bombe Machine (anthropomorphized):
- Bombe machine as character: Large, brass and wood, dial "eyes", paper tape "mouth"
- Expressions: Processing (spinning dials) | Success (lights up) | Stuck (smoke wisps)

COLOR PALETTE:
- Turing: Muted browns (#8B7355), navy blue (#2C3E50), cream (#F5F5DC)
- Machine: Brass (#B5A642), mahogany (#4E2728), emerald indicators (#2ECC71)

White background, clear labels under each character.
```

## 处理不同年龄版本

对于涵盖多年生平的资料，需定义不同的年龄版本：

```markdown
## Alan Turing - Age Variants

### Young (1920s, age 10-18)
- Boyish features, round face
- School uniform (Sherborne)
- Curious, eager expression

### Adult (1930s-40s, age 25-35)
- Angular face, defined jaw
- Tweed jacket, rumpled appearance
- Intense, focused expression

### Later (1950s, age 40+)
- Slightly weathered
- More casual dress
- Thoughtful, sometimes melancholic
```

## 最佳实践

| 实践要点 | 说明 |
|----------|------|
| 描述要具体 | 不要只写“深色头发”，而应明确为“左分短款深色波浪发” |
| 利用独特特征 | 可参考眼镜、疤痕或能识别角色的配饰等细节 |
| 明确指定颜色代码 | 使用具体的颜色名称或十六进制代码 |
| 添加年龄特征提示 | 通过皱纹、体态或符合时代风格的服装来体现年龄 |
| 参考真实人物 | 对于历史人物，需注明“基于20世纪40年代的照片” |

## 为何需要角色参考资料

若没有统一的角色定义，AI生成的形象就会千差万别。参考资料能提供：
1. 用于保持特征一致性的视觉参照
2. 用于确保色彩统一的配色方案
3. 用于呈现情感表达的表情描述指南
