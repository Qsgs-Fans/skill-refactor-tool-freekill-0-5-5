你需要针对技能代码的结构进行初步重构，重构的方法具体如下：

## 1. 技能总体结构的变化

旧版本中，技能代码的结构如下（假设研究技能biyue）：

```lua
local biyue = fk.CreateXXXSkill { ... }
local biyue_sub1 = fk.CreateXXXSkill { ... }
biyue:addRelatedSkill(biyue_sub1)
-- 后面是更多的Create某某Skill以及addRelatedSkill等

-- 可能有LoadTranslationTable
Fk:loadTranslationTable { ... }
```

而在新版本中，技能代码的结构变成了这样：

```lua
-- 首先是fk.CreateSkill开头，内部没有任何和技能有关的代码
local biyue = fk.CreateSkill {
    name = "biyue"
}

-- 若原版有LoadTranslationTable，那么放在此处
Fk:loadTranslationTable { ... }

-- 对应上文中第一个local biyue = fk.CreateXXXSkill
biyue:addEffect(xxx, { ... })
-- 对应上文的sub1子技能及其addRelatedSkill
biyue:addEffect(xxx, { ... })
-- ... 以及更多的addEffect，对应着更多的addRelatedSkill

return biyue
```

注意向addEffect传递的表不需要指定name。

___

## 2. 各种CreateXXXSkill具体的重构方式

接下来我将用luadoc类似的格式来解说代码中变量类型，以及这些类型的变化情况。

### fk.CreateTriggerSkill

触发技的创建。旧版本的CreateTriggerSkill如下：

```lua
---@class SkillSpec
---@field public name? string @ 技能名
---@field public frequency? Frequency @ 技能发动的频繁程度，通常compulsory（锁定技）及limited（限定技）用的多。
---@field public mute? boolean @ 决定是否关闭技能配音
---@field public no_indicate? boolean @ 决定是否关闭技能指示线
---@field public anim_type? string|AnimationType @ 技能类型定义
---@field public global? boolean @ 决定是否是全局技能
---@field public attached_equip? string @ 属于什么装备的技能？
---@field public switch_skill_name? string @ 转换技名字
---@field public relate_to_place? string @ 主将技/副将技
---@field public on_acquire? fun(self: UsableSkill, player: ServerPlayer, is_start: boolean)
---@field public on_lose? fun(self: UsableSkill, player: ServerPlayer, is_death: boolean)
---@field public dynamic_desc? fun(self: UsableSkill, player: Player, lang: string): string
---@field public attached_skill_name? string @ 给其他角色添加技能的名称

---@alias TrigFunc fun(self: TriggerSkill, event: TriggerEvent, target: ServerPlayer?, player: ServerPlayer, data: any): any

---@class LegacyTriggerSkillSpec: SkillSpec
---@field public global? boolean
---@field public events? (TriggerEvent|integer|string) | (TriggerEvent|integer|string)[]
---@field public refresh_events? (TriggerEvent|integer|string) | (TriggerEvent|integer|string)[]
---@field public priority? number | table<(TriggerEvent|integer|string), number>
---@field public on_trigger? TrigFunc
---@field public can_trigger? TrigFunc
---@field public on_cost? TrigFunc
---@field public on_use? TrigFunc
---@field public on_refresh? TrigFunc
---@field public can_refresh? TrigFunc
---@field public can_wake? TrigFunc

---@deprecated
---@param spec LegacyTriggerSkillSpec
fk.CreateTriggerSkill(spec)
```

新版本中，触发技的时机数量由多个变成了一个，且废除了refresh_events等，大致来说
新版本的触发技是这个格式：

```lua
skel:addEffect(event, {
    global = ...,
    can_trigger = ...,
    on_trigger = ...,
    on_cost = ...,
    on_use = ...,

    can_refresh = ...,
    on_refresh = ...,
})
```

函数的参数和之前的触发技没有区别（除了data参数的类型发生了重大变化，之后详细
介绍），但是所有的函数在新版本中只需要处理单一的event，其他多余的if分支就不需要了。

注意了，refresh_events被废除了。如果有技能的refresh_events和events是重合的，
那么在重构版本中直接在同一个effect里面写好trigger和refresh二者就行了。

### fk.CreateViewAsSkill

旧版：

```lua
fk.CreateViewAsSkill { ... }
```

新版：

```lua
skel:addEffect('viewas', { ... })
```

就是这么简单，将CreateViewAsSkill改成addEffect('viewas', ...)就行了。但是其中
不少函数的参数类型与顺序发生了变化:

这是旧版的函数类型：

```lua
---@field public card_filter? fun(self: ViewAsSkill, to_select: integer, selected: integer[], player: Player): any @ 判断卡牌能否选择
---@field public view_as fun(self: ViewAsSkill, cards: integer[], player: Player): Card? @ 判断转化为什么牌
---@field public prompt? string|fun(self: ViewAsSkill, selected_cards: integer[], selected: integer[]): string
```

这是新版的函数类型：

```lua
---@field public card_filter? fun(self: ViewAsSkill, player: Player, to_select: integer, selected: integer[]): any @ 判断卡牌能否选择
---@field public view_as fun(self: ViewAsSkill, player: Player, cards: integer[]): Card? @ 判断转化为什么牌
---@field public prompt? string|fun(self: ActiveSkill, player: Player, selected_cards: integer[], selected: Player[]): string
```

没有提到的函数表明其参数类型没有发生过变化，和以往一致。

简而言之就是添加了player参数。player参数用来取代旧版本函数中的Self。
在重构的代码中，Self都要换成这个player参数。

### fk.CreateActiveSkill

类似前者，改成了skel:addEffect('active', ...)

函数的类型也发生了变化。旧版本：

```lua
---@field public can_use? fun(self: ActiveSkill, player: Player, card?: Card, extra_data: any): any @ 判断主动技能否发动
---@field public card_filter? fun(self: ActiveSkill, to_select: integer, selected: integer[], player: Player): any @ 判断卡牌能否选择
---@field public target_filter? fun(self: ActiveSkill, to_select: integer, selected: integer[], selected_cards: integer[], card?: Card, extra_data: any, player: Player?): any @ 判定目标能否选择
---@field public feasible? fun(self: ActiveSkill, selected: integer[], selected_cards: integer[], player: Player, card: Card): any @ 判断卡牌和目标是否符合技能限制
---@field public mod_target_filter? fun(self: ActiveSkill, to_select: integer, selected: integer[], player: Player, card?: Card, distance_limited: boolean, extra_data: any): any
---@field public prompt? string|fun(self: ActiveSkill, selected_cards: integer[], selected_targets: integer[]): string @ 提示信息
---@field public target_tip? fun(self: ActiveSkill, to_select: integer, selected: integer[], selected_cards: integer[], card?: Card, selectable: boolean, extra_data: any): string|TargetTipDataSpec?
```

新版本：

```lua
---@field public can_use? fun(self: ActiveSkill, player: Player, card?: Card, extra_data: any): any @ 判断主动技能否发动
---@field public card_filter? fun(self: ActiveSkill, player: Player, to_select: integer, selected: integer[]): any @ 判断卡牌能否选择
---@field public target_filter? fun(self: ActiveSkill, player: Player?, to_select: Player, selected: Player[], selected_cards: integer[], card?: Card, extra_data: any): any @ 判定目标能否选择
---@field public feasible? fun(self: ActiveSkill, player: Player, selected: Player[], selected_cards: integer[]): any @ 判断卡牌和目标是否符合技能限制
---@field public mod_target_filter? fun(self: ActiveSkill, player: Player, to_select: Player, selected: Player[], card?: Card, extra_data: any): any
---@field public prompt? string|fun(self: ActiveSkill, player: Player, selected_cards: integer[], selected_targets: Player[]): string @ 提示信息
---@field public target_tip? fun(self: ActiveSkill, player: Player, to_select: Player, selected: Player[], selected_cards: integer[], card?: Card, selectable: boolean, extra_data: any): string|TargetTipDataSpec?
```

没有提到的函数表明其参数类型没有发生过变化，和以往一致。

简而言之就是添加了player参数，或者调整了player参数的位置。
player参数用来取代旧版本函数中的Self。
在重构的代码中，Self都要换成这个player参数。

### 其他技能类型

- `fk.CreateDistanceSkill { ... }` --> `skel:addEffect('distance', { ... })`
- `fk.CreateProhibitSkill { ... }` --> `skel:addEffect('prohibit', { ... })`
- `fk.CreateAttackRangeSkill { ... }` --> `skel:addEffect('atkrange', { ... })`
- `fk.CreateMaxCardsSkill { ... }` --> `skel:addEffect('maxcards', { ... })`
- `fk.CreateTargetModSkill { ... }` --> `skel:addEffect('targetmod', { ... })`
- `fk.CreateFilterSkill { ... }` --> `skel:addEffect('filter', { ... })`
- `fk.CreateInvaliditySkill { ... }` --> `skel:addEffect('invalidity', { ... })`
- `fk.CreateVisibilitySkill { ... }` --> `skel:addEffect('visibility', { ... })`

spec中的函数类型无任何变化。

___

接下来会给你需要重构的技能代码，你需要将技能用新版本的格式进行重构，将结果代码直接输出，
不要额外解释也不要添加markdown风格的```lua之类的东西：

-- <这里是你重构后的代码>
