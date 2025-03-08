代码中形如askForXXX的方法现在都升级了askToXXX，原有的方法不能再使用需要翻新。

重构这些方法的基本思路是参数表发生了改变，其中大部分是保留一个player参数，
其余参数通过表的形式组织。例如下面：

```lua
local discards = room:askForDiscard(from, 2, 2, false, self.name, true)
```

会被重构为

```lua
local discards = room:askToDiscard(from, {
  min_num = 2,
  max_num = 2,
  include_equip = false,
  skill_name = ganglie.name,
  cancelable = true,
})
```

参数表的各个参数与新版的table参数对应关系将在下面一一解释。
若返回值发生了改变，则会单独说明，没说明的情况下说明返回值没有发生变化。

以下是各个方法重构方法：

---

旧版：

```lua
---@param player ServerPlayer @ 询问目标
---@param skill_name string @ 主动技的技能名
---@param prompt? string @ 烧条上面显示的提示文本内容
---@param cancelable? boolean @ 是否可以点取消
---@param extra_data? table @ 额外信息，因技能而异了
---@param no_indicate? boolean @ 是否不显示指示线
function Room:askForUseActiveSkill(player, skill_name, prompt, cancelable, extra_data, no_indicate) end
```

新版：

```lua
---@class AskToUseActiveSkillParams: AskToSkillInvokeParams
---@field cancelable? boolean @ 是否可以点取消
---@field no_indicate? boolean @ 是否不显示指示线
---@field extra_data? table @ 额外信息
---@field skip? boolean @ 是否跳过实际执行流程

---@param player ServerPlayer @ 询问目标
---@param params AskToUseActiveSkillParams @ 各种变量
function Room:askToUseActiveSkill(player, params) end
```

旧版：

```lua
--- 询问一名角色弃牌。
---
--- 在这个函数里面牌已经被弃掉了（除非skipDiscard为true）。
---@param player ServerPlayer @ 弃牌角色
---@param minNum integer @ 最小值
---@param maxNum integer @ 最大值
---@param includeEquip? boolean @ 能不能弃装备区？
---@param skillName? string @ 引发弃牌的技能名
---@param cancelable? boolean @ 能不能点取消？
---@param pattern? string @ 弃牌需要符合的规则
---@param prompt? string @ 提示信息
---@param skipDiscard? boolean @ 是否跳过弃牌（即只询问选择可以弃置的牌）
---@param no_indicate? boolean @ 是否不显示指示线
---@return integer[] @ 弃掉的牌的id列表，可能是空的
---@deprecated
function CompatAskFor:askForDiscard(player, minNum, maxNum, includeEquip, skillName, cancelable, pattern, prompt, skipDiscard, no_indicate)
```

新版：

```lua
---@class AskToDiscardParams: AskToUseActiveSkillParams
---@field min_num integer @ 最小值
---@field max_num integer @ 最大值
---@field include_equip? boolean @ 能不能弃装备区？
---@field pattern? string @ 弃牌需要符合的规则
---@field skip? boolean @ 是否跳过弃牌（即只询问选择可以弃置的牌）

--- 询问一名角色弃牌。
---
--- 在这个函数里面牌已经被弃掉了（除非skipDiscard为true）。
---@param player ServerPlayer @ 弃牌角色
---@param params AskToDiscardParams @ 各种变量
---@return integer[] @ 弃掉的牌的id列表，可能是空的
function Room:askToDiscard(player, params) end
```

旧版：

```lua
--- 询问一名玩家从targets中选择若干名玩家出来。
---@param player ServerPlayer @ 要做选择的玩家
---@param targets integer[] @ 可以选的目标范围，是玩家id数组
---@param minNum integer @ 最小值
---@param maxNum integer @ 最大值
---@param prompt? string @ 提示信息
---@param skillName? string @ 技能名
---@param cancelable? boolean @ 能否点取消，默认可以
---@param no_indicate? boolean @ 是否不显示指示线
---@param targetTipName? string @ 引用的选择目标提示的函数名
---@param extra_data? table @额外信息
---@return integer[] @ 选择的玩家id列表，可能为空
---@deprecated
function CompatAskFor:askForChoosePlayers(player, targets, minNum, maxNum, prompt, skillName, cancelable, no_indicate, targetTipName, extra_data)
```

新版：

```lua
---@class AskToChoosePlayersParams: AskToUseActiveSkillParams
---@field targets ServerPlayer[] @ 可以选的目标范围
---@field min_num integer @ 最小值
---@field max_num integer @ 最大值
---@field target_tip_name? string @ 引用的选择目标提示的函数名

--- 询问一名玩家从targets中选择若干名玩家出来。
---@param player ServerPlayer @ 要做选择的玩家
---@param params AskToChoosePlayersParams @ 各种变量
---@return ServerPlayer[] @ 选择的玩家列表，可能为空
function Room:askToChoosePlayers(player, params)
```

旧版：

```lua
--- 询问一名玩家选择自己的几张牌。
---
--- 与askForDiscard类似，但是不对选择的牌进行操作就是了。
---@param player ServerPlayer @ 要询问的玩家
---@param minNum integer @ 最小值
---@param maxNum integer @ 最大值
---@param includeEquip? boolean @ 能不能选装备
---@param skillName? string @ 技能名
---@param cancelable? boolean @ 能否点取消
---@param pattern? string @ 选牌规则
---@param prompt? string @ 提示信息
---@param expand_pile? string|integer[] @ 可选私人牌堆名称，或额外可选牌
---@param no_indicate? boolean @ 是否不显示指示线
---@return integer[] @ 选择的牌的id列表，可能是空的
---@deprecated
function CompatAskFor:askForCard(player, minNum, maxNum, includeEquip, skillName, cancelable, pattern, prompt, expand_pile, no_indicate)
```

新版：

```lua
---@class AskToCardsParams: AskToUseActiveSkillParams
---@field min_num integer @ 最小值
---@field max_num integer @ 最大值
---@field include_equip? boolean @ 能不能选装备
---@field pattern? string @ 选牌规则
---@field expand_pile? string|integer[] @ 可选私人牌堆名称，或额外可选牌

--- 询问一名玩家选择自己的几张牌。
---
--- 与askForDiscard类似，但是不对选择的牌进行操作就是了。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToCardsParams @ 各种变量
---@return integer[] @ 选择的牌的id列表，可能是空的
function Room:askToCards(player, params)
```

旧版：

```lua
--- 询问玩家选择1张牌和若干名角色。
---
--- 返回两个值，第一个是选择的目标列表，第二个是选择的那张牌的id
---@param player ServerPlayer @ 要询问的玩家
---@param targets integer[] @ 选择目标的id范围
---@param minNum integer @ 选目标最小值
---@param maxNum integer @ 选目标最大值
---@param pattern? string @ 选牌规则
---@param prompt? string @ 提示信息
---@param cancelable? boolean @ 能否点取消
---@param no_indicate? boolean @ 是否不显示指示线
---@param targetTipName? string @ 引用的选择目标提示的函数名
---@param extra_data? table @额外信息
---@return integer[], integer?
---@deprecated
function CompatAskFor:askForChooseCardAndPlayers(player, targets, minNum, maxNum, pattern, prompt, skillName, cancelable, no_indicate, targetTipName, extra_data)
```

新版：

```lua
--- 询问玩家选择X张牌和Y名角色。
---
--- 返回两个值，第一个是选择目标id列表，第二个是选择的牌id列表，第三个是否按了确定
---@param player ServerPlayer @ 要询问的玩家
---@param minCardNum integer @ 选卡牌最小值
---@param maxCardNum integer @ 选卡牌最大值
---@param targets integer[] @ 选择目标的id范围
---@param minTargetNum integer @ 选目标最小值
---@param maxTargetNum integer @ 选目标最大值
---@param pattern? string @ 选牌规则
---@param prompt? string @ 提示信息
---@param cancelable? boolean @ 能否点取消
---@param no_indicate? boolean @ 是否不显示指示线
---@param extra_data? table @额外信息
---@return integer[], integer[], boolean @ 第一个是选择目标id列表，第二个是选择的牌id列表，第三个是否按了确定
---@deprecated
function CompatAskFor:askForChooseCardsAndPlayers(player, minCardNum, maxCardNum, targets, minTargetNum, maxTargetNum, pattern, prompt, skillName, cancelable, no_indicate, targetTipName, extra_data)
```

新版：

```lua
---@class AskToChooseCardsAndPlayersParams: AskToChoosePlayersParams
---@field min_card_num integer @ 选卡牌最小值
---@field max_card_num integer @ 选卡牌最大值
---@field expand_pile? string|integer[] @ 可选私人牌堆名称，或额外可选牌
---@field will_throw? boolean @ 选卡牌须能弃置

--- 询问玩家选择X张牌和Y名角色。
---
--- 返回两个值，第一个是选择目标列表，第二个是选择的牌id列表，第三个是否按了确定
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToChooseCardsAndPlayersParams @ 各种变量
---@return ServerPlayer[], integer[], boolean @ 第一个是选择目标列表，第二个是选择的牌id列表，第三个是否按了确定
function Room:askToChooseCardsAndPlayers(player, params)
```

旧版：

```lua
--- 询问将卡牌分配给任意角色。
---@param player ServerPlayer @ 要询问的玩家
---@param cards? integer[] @ 要分配的卡牌。默认拥有的所有牌
---@param targets? ServerPlayer[] @ 可以获得卡牌的角色。默认所有存活角色
---@param skillName? string @ 技能名，影响焦点信息。默认为“分配”
---@param minNum? integer @ 最少交出的卡牌数，默认0
---@param maxNum? integer @ 最多交出的卡牌数，默认所有牌
---@param prompt? string @ 询问提示信息
---@param expand_pile? string|integer[] @ 可选私人牌堆名称，如要分配你武将牌上的牌请填写
---@param skipMove? boolean @ 是否跳过移动。默认不跳过
---@param single_max? integer|table @ 限制每人能获得的最大牌数。输入整数或(以角色id为键以整数为值)的表
---@return table<integer, integer[]> @ 返回一个表，键为角色id，值为分配给其的牌id数组
---@deprecated
function CompatAskFor:askForYiji(player, cards, targets, skillName, minNum, maxNum, prompt, expand_pile, skipMove, single_max)
```

新版：

```lua
---@class AskToYijiParams: AskToChoosePlayersParams
---@field cards? integer[] @ 要分配的卡牌。默认拥有的所有牌
---@field expand_pile? string|integer[] @ 可选私人牌堆名称，或额外可选牌
---@field single_max? integer|table @ 限制每人能获得的最大牌数。输入整数或(以角色id为键以整数为值)的表
---@field skip? boolean @ 是否跳过移动。默认不跳过

--- 询问将卡牌分配给任意角色。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToYijiParams @ 各种变量
---@return table<integer, integer[]> @ 返回一个表，键为角色id，值为分配给其的牌id数组
function Room:askToYiji(player, params)
```

旧版：

```lua
--- 询问玩家选择一名武将。
---@param player ServerPlayer @ 询问目标
---@param generals string[] @ 可选武将
---@param n integer @ 可选数量，默认为1
---@param noConvert? boolean @ 可否变更，默认可
---@return string|string[] @ 选择的武将
---@deprecated
function CompatAskFor:askForGeneral(player, generals, n, noConvert)
```

新版：

```lua
---@class AskToChooseGeneralParams
---@field generals string[] @ 可选武将
---@field n integer @ 可选数量，默认为1
---@field no_convert? boolean @ 可否同名替换，默认可

--- 询问玩家选择一名武将。
---@param player ServerPlayer @ 询问目标
---@param params AskToChooseGeneralParams @ 各种变量
---@return string|string[] @ 选择的武将
function Room:askToChooseGeneral(player, params)
```

旧版：

```lua
function CompatAskFor:askForChooseKingdom(players)
```

新版：

```lua
function Room:askToChooseKingdom(players)
```

旧版：

```lua
--- 询问chooser，选择target的一张牌。
---@param chooser ServerPlayer @ 要被询问的人
---@param target ServerPlayer @ 被选牌的人
---@param flag any @ 用"hej"三个字母的组合表示能选择哪些区域, h 手牌区, e - 装备区, j - 判定区
---@param reason string @ 原因，一般是技能名
---@param prompt? string @ 提示信息
---@return integer @ 选择的卡牌id
---@deprecated
function CompatAskFor:askForCardChosen(chooser, target, flag, reason, prompt)
```

新版：

```lua
---@class AskToChooseCardParams: AskToSkillInvokeParams
---@field target ServerPlayer @ 被选牌的人
---@field flag string | table @ 用"hej"三个字母的组合表示能选择哪些区域, h 手牌区, e - 装备区, j - 判定区
---@field skill_name string @ 原因，一般是技能名

--- 询问player，选择target的一张牌。
---@param player ServerPlayer @ 要被询问的人
---@param params AskToChooseCardParams @ 各种变量
---@return integer @ 选择的卡牌id
function Room:askToChooseCard(player, params)
```

旧版：

```lua
---@param player ServerPlayer @ 要被询问的人
---@param poxi_type string @ poxi关键词
---@param data any @ 牌堆信息
---@param extra_data any @ 额外信息
---@param cancelable? boolean @ 是否可取消
---@return integer[] @ 选择的牌ID数组
---@deprecated
function CompatAskFor:askForPoxi(player, poxi_type, data, extra_data, cancelable)
```

新版：

```lua
---@class AskToPoxiParams
---@field poxi_type string @ poxi关键词
---@field data any @ 牌堆信息
---@field extra_data any @ 额外信息
---@field cancelable? boolean @ 是否可取消

--- 谋askForCardsChosen，需使用Fk:addPoxiMethod定义好方法
---
--- 选卡规则和返回值啥的全部自己想办法解决，data填入所有卡的列表（类似ui.card_data）
---
--- 注意一定要返回一个表，毕竟本质上是选卡函数
---@param player ServerPlayer @ 要被询问的人
---@param params AskToPoxiParams @ 各种变量
---@return integer[] @ 选择的牌ID数组
function Room:askToPoxi(player, params)
```

旧版：

```lua
--- 完全类似askForCardChosen，但是可以选择多张牌。
--- 相应的，返回的是id的数组而不是单个id。
---@param chooser ServerPlayer @ 要被询问的人
---@param target ServerPlayer @ 被选牌的人
---@param min integer @ 最小选牌数
---@param max integer @ 最大选牌数
---@param flag any @ 用"hej"三个字母的组合表示能选择哪些区域, h 手牌区, e - 装备区, j - 判定区
---可以通过flag.card_data = {{牌堆1名, 牌堆1ID表},...}来定制能选择的牌
---@param reason string @ 原因，一般是技能名
---@param prompt? string @ 提示信息
---@return integer[] @ 选择的id
---@deprecated
function CompatAskFor:askForCardsChosen(chooser, target, min, max, flag, reason, prompt)
```

新版：

```lua
---@class AskToChooseCardsParams: AskToChooseCardParams
---@field min integer @ 最小选牌数
---@field max integer @ 最大选牌数

--- 完全类似askForCardChosen，但是可以选择多张牌。
--- 相应的，返回的是id的数组而不是单个id。
---@param player ServerPlayer @ 要被询问的人
---@param params AskToChooseCardsParams @ 各种变量
---@return integer[] @ 选择的id
function Room:askToChooseCards(player, params)
```

旧版：

```lua
--- 询问一名玩家从众多选项中选择一个。
---@param player ServerPlayer @ 要询问的玩家
---@param choices string[] @ 可选选项列表
---@param skill_name? string @ 技能名
---@param prompt? string @ 提示信息
---@param detailed? boolean @ 选项详细描述
---@param all_choices? string[] @ 所有选项（不可选变灰）
---@return string @ 选择的选项
---@deprecated
function CompatAskFor:askForChoice(player, choices, skill_name, prompt, detailed, all_choices)
```

新版：

```lua
---@class AskToChoiceParams
---@field choices string[] @ 可选选项列表
---@field skill_name? string @ 技能名
---@field prompt? string @ 提示信息
---@field detailed? boolean @ 选项是否详细描述
---@field all_choices? string[] @ 所有选项（不可选变灰）
---@field cancelable? boolean @ 是否可以点取消

--- 询问一名玩家从众多选项中选择一个。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToChoiceParams @ 各种变量
---@return string @ 选择的选项
function Room:askToChoice(player, params)
```

旧版：

```lua
--- 询问一名玩家从众多选项中勾选任意项。
---@param player ServerPlayer @ 要询问的玩家
---@param choices string[] @ 可选选项列表
---@param minNum number @ 最少选择项数
---@param maxNum number @ 最多选择项数
---@param skill_name? string @ 技能名
---@param prompt? string @ 提示信息
---@param cancelable? boolean @ 是否可取消
---@param detailed? boolean @ 选项详细描述
---@param all_choices? string[] @ 所有选项（不可选变灰）
---@return string[] @ 选择的选项
---@deprecated
function CompatAskFor:askForChoices(player, choices, minNum, maxNum, skill_name, prompt, cancelable, detailed, all_choices)
```

新版：

```lua
---@class AskToChoicesParams: AskToChoiceParams
---@field min_num number @ 最少选择项数
---@field max_num number @ 最多选择项数

--- 询问一名玩家从众多选项中勾选任意项。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToChoicesParams @ 各种变量
---@return string[] @ 选择的选项
function Room:askToChoices(player, params)
```

旧版：

```lua
---@param player ServerPlayer @ 要询问的玩家
---@param skill_name string @ 技能名
---@param data? any @ 未使用
---@param prompt? string @ 提示信息
---@return boolean
---@deprecated
function CompatAskFor:askForSkillInvoke(player, skill_name, data, prompt)
```

新版：

```lua
---@class AskToSkillInvokeParams
---@field skill_name string @ 询问技能名（烧条时显示）
---@field prompt? string @ 提示信息

--- 询问玩家是否发动技能。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToSkillInvokeParams @ 各种变量
---@return boolean @ 是否发动
function Room:askToSkillInvoke(player, params)
```

旧版：

```lua
--- 询问玩家在自定义大小的框中排列卡牌（观星、交换、拖拽选牌）
---@param player ServerPlayer @ 要询问的玩家
---@param skillname string @ 烧条技能名
---@param cardMap any @ { "牌堆1卡表", "牌堆2卡表", …… }
---@param prompt? string @ 操作提示
---@param box_size? integer @ 数值对应卡牌平铺张数的最大值，为0则有单个卡位，每张卡占100单位长度，默认为7
---@param max_limit? integer[] @ 每一行牌上限 { 第一行, 第二行，…… }，不填写则不限
---@param min_limit? integer[] @ 每一行牌下限 { 第一行, 第二行，…… }，不填写则不限
---@param free_arrange? boolean @ 是否允许自由排列第一行卡的位置，默认不能
---@param pattern? string @ 控制第一行卡牌是否可以操作，不填写默认均可操作
---@param poxi_type? string @ 控制每张卡牌是否可以操作、确定键是否可以点击，不填写默认均可操作
---@param default_choice? table[] @ 超时的默认响应值，在带poxi_type时需要填写
---@return table[] @ 排列后的牌堆结果
---@deprecated
function CompatAskFor:askForArrangeCards(player, skillname, cardMap, prompt, free_arrange, box_size, max_limit, min_limit, pattern, poxi_type, default_choice)
```

新版：

```lua
---@class AskToArrangeCardsParams: AskToSkillInvokeParams
---@field card_map any @ { "牌堆1卡表", "牌堆2卡表", …… }
---@field prompt? string @ 操作提示
---@field box_size? integer @ 数值对应卡牌平铺张数的最大值，为0则有单个卡位，每张卡占100单位长度，默认为7
---@field max_limit? integer[] @ 每一行牌上限 { 第一行, 第二行，…… }，不填写则不限
---@field min_limit? integer[] @ 每一行牌下限 { 第一行, 第二行，…… }，不填写则不限
---@field free_arrange? boolean @ 是否允许自由排列第一行卡的位置，默认不能
---@field pattern? string @ 控制第一行卡牌是否可以操作，不填写默认均可操作
---@field poxi_type? string @ 控制每张卡牌是否可以操作、确定键是否可以点击，不填写默认均可操作
---@field default_choice? table[] @ 超时的默认响应值，在带poxi_type时需要填写

--- 询问玩家在自定义大小的框中排列卡牌（观星、交换、拖拽选牌）
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToArrangeCardsParams @ 各种变量
---@return table[] @ 排列后的牌堆结果
function Room:askToArrangeCards(player, params)
```

旧版：

```lua
---@param player ServerPlayer @ 要询问的玩家
---@param cards integer[] @ 可以被观星的卡牌id列表
---@param top_limit? integer[] @ 置于牌堆顶的牌的限制(下限,上限)，不填写则不限
---@param bottom_limit? integer[] @ 置于牌堆底的牌的限制(下限,上限)，不填写则不限
---@param customNotify? string @ 自定义读条操作提示
---param prompt? string @ 观星框的标题(暂时雪藏)
---@param noPut? boolean @ 是否进行放置牌操作
---@param areaNames? string[] @ 左侧提示信息
---@return table<"top"|"bottom", integer[]> @ 左侧提示信息
---@deprecated
function CompatAskFor:askForGuanxing(player, cards, top_limit, bottom_limit, customNotify, noPut, areaNames)
```

新版：

```lua
---@class AskToGuanxingParams
---@field cards integer[] @ 可以被观星的卡牌id列表
---@field top_limit? integer[] @ 置于牌堆顶的牌的限制(下限,上限)，不填写则不限
---@field bottom_limit? integer[] @ 置于牌堆底的牌的限制(下限,上限)，不填写则不限
---@field skill_name? string @ 烧条时显示的技能名
---@field title? string @ 观星框的标题
---@field skip? boolean @ 是否进行放置牌操作
---@field area_names? string[] @ 左侧提示信息

--- 询问玩家对若干牌进行观星。
---
--- 观星完成后，相关的牌会被置于牌堆顶或者牌堆底。所以这些cards最好不要来自牌堆，一般先用getNCards从牌堆拿出一些牌。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToGuanxingParams @ 各种变量
---@return table<"top"|"bottom", integer[]> @ 观星后的牌堆结果
function Room:askToGuanxing(player, params)
```

旧版：

```lua
--- 询问玩家任意交换几堆牌堆。
---
---@param player ServerPlayer @ 要询问的玩家
---@param piles integer[][] @ 卡牌id列表的列表，也就是……几堆牌堆的集合
---@param piles_name string[] @ 牌堆名，不足部分替换为“牌堆1、牌堆2...”
---@param customNotify? string @ 自定义读条操作提示
---@return integer[][] @ 交换后的结果
---@deprecated
function CompatAskFor:askForExchange(player, piles, piles_name, customNotify)
```

新版：

```lua
---@class AskToExchangeParams
---@field piles integer[][] @ 卡牌id列表的列表，也就是……几堆牌堆的集合
---@field piles_name? string[] @ 牌堆名，不足部分替换为“牌堆1、牌堆2...”
---@field skill_name? string @ 烧条时显示的技能名

--- 询问玩家任意交换几堆牌堆。
---
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToExchangeParams @ 各种变量
---@return integer[][] @ 交换后的结果
function Room:askToExchange(player, params)
```

旧版：

```lua
--- 询问玩家从一些实体牌中选一个使用。默认无次数限制，与askForUseCard主要区别是不能调用转化技
---@param player ServerPlayer @ 要询问的玩家
---@param pattern string|integer[] @ 选卡规则，或可选的牌id表
---@param skillName? string @ 技能名，用于焦点提示
---@param prompt? string @ 询问提示信息。默认为：请使用一张牌
---@param extra_data? UseExtraData|table @ 额外信息，因技能而异了
---@param cancelable? boolean @ 是否可以取消。默认可以取消
---@param skipUse? boolean @ 是否跳过使用。默认不跳过
---@return UseCardDataSpec? @ 返回卡牌使用框架。取消使用则返回空
---@deprecated
function CompatAskFor:askForUseRealCard(player, pattern, skillName, prompt, extra_data, cancelable, skipUse)
```

新版：

```lua
---@class AskToUseRealCardParams
---@field pattern string|integer[] @ 选卡规则，或可选的牌id表
---@field skill_name? string @ 烧条时显示的技能名
---@field prompt? string @ 询问提示信息。默认为：请使用一张牌
---@field extra_data? UseExtraData|table @ 额外信息，因技能而异了
---@field cancelable? boolean @ 是否可以取消。默认可以取消
---@field skip? boolean @ 是否跳过使用。默认不跳过
---@field expand_pile? string|integer[] @ 可选私人牌堆名称，或额外可选牌

--- 询问玩家从一些实体牌中选一个使用。默认无次数限制，与askForUseCard主要区别是不能调用转化技
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToUseRealCardParams @ 各种变量
---@return UseCardDataSpec? @ 返回卡牌使用框架。取消使用则返回空
function Room:askToUseRealCard(player, params)
```

旧版：

```lua
--- 询问玩家使用一张牌。
---@param player ServerPlayer @ 要询问的玩家
---@param card_name? string @ 使用牌的牌名，若pattern指定了则可随意写，它影响的是烧条的提示信息
---@param pattern? string @ 使用牌的规则，默认就是card_name的值
---@param prompt? string @ 提示信息
---@param cancelable? boolean @ 能否点取消
---@param extra_data? UseExtraData @ 额外信息
---@param event_data? CardEffectData @ 事件信息
---@return UseCardDataSpec? @ 返回关于本次使用牌的数据，以便后续处理
---@deprecated
function CompatAskFor:askForUseCard(player, card_name, pattern, prompt, cancelable, extra_data, event_data)
```

新版：

```lua
---@class AskToUseCardParams
---@field skill_name? string @ 烧条时显示的技能名
---@field pattern string @ 使用牌的规则
---@field prompt? string @ 提示信息
---@field cancelable? boolean @ 是否可以取消。默认可以取消
---@field extra_data? UseExtraData|table @ 额外信息，因技能而异了
---@field event_data? CardEffectData @ 事件信息，如借刀事件之于询问杀

-- available extra_data:
-- * must_targets: integer[]
-- * exclusive_targets: integer[]
-- * fix_targets: integer[]
-- * bypass_distances: boolean
-- * bypass_times: boolean
---
--- 询问玩家使用一张牌。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToUseCardParams @ 各种变量
---@return UseCardDataSpec? @ 返回关于本次使用牌的数据，以便后续处理
function Room:askToUseCard(player, params)
```

旧版：

```lua
--- 询问一名玩家打出一张牌。
---@param player ServerPlayer @ 要询问的玩家
---@param card_name string @ 牌名
---@param pattern? string @ 牌的规则
---@param prompt? string @ 提示信息
---@param cancelable? boolean @ 能否取消
---@param extra_data? any @ 额外数据
---@param effectData? CardEffectData @ 关联的卡牌生效流程
---@return Card? @ 打出的牌
---@deprecated
function CompatAskFor:askForResponse(player, card_name, pattern, prompt, cancelable, extra_data, effectData)
```

新版：

```lua
--- 询问一名玩家打出一张牌。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToUseCardParams @ 各种变量
---@return RespondCardDataSpec? @ 打出的事件
function Room:askToResponse(player, params)
```

旧版：

```lua
---@param players ServerPlayer[] @ 要询问的玩家列表
---@param card_name string @ 询问的牌名，默认为无懈
---@param pattern string @ 牌的规则
---@param prompt? string @ 提示信息
---@param cancelable? boolean @ 能否点取消
---@param extra_data? any @ 额外信息
---@param effectData? CardEffectData @ 关联的卡牌生效流程
---@return UseCardDataSpec? @ 最终决胜出的卡牌使用信息
function CompatAskFor:askForNullification(players, card_name, pattern, prompt, cancelable, extra_data, effectData)
```

新版：

```lua
---@param players ServerPlayer[] @ 要询问的玩家列表
---@param params AskToUseCardParams @ 各种变量
---@return UseCardDataSpec? @ 最终决胜出的卡牌使用信息
function Room:askToNullification(players, params)
```

旧版：

```lua
---@param player ServerPlayer @ 要询问的玩家
---@param id_list integer[] | Card[] @ 可选的卡牌列表
---@param cancelable? boolean @ 能否点取消
---@param reason? string @ 原因
---@return integer @ 选择的卡牌
---@deprecated
function CompatAskFor:askForAG(player, id_list, cancelable, reason)
```

新版：

```lua
---@class AskToAGParams
---@field id_list integer[] | Card[] @ 可选的卡牌列表
---@field cancelable? boolean @ 能否点取消
---@field skill_name? string @ 烧条时显示的技能名

-- AG(a.k.a. Amazing Grace) functions
-- Popup a box that contains many cards, then ask player to choose one

--- 询问玩家从AG中选择一张牌。
---@param player ServerPlayer @ 要询问的玩家
---@param params AskToAGParams @ 各种变量
---@return integer @ 选择的卡牌
function Room:askToAG(player, params)
```

旧版：

```lua
---@param players ServerPlayer[]
---@param focus string
---@param game_type string
---@param data_table table<integer, any> @ 对应每个player
---@deprecated
function CompatAskFor:askForMiniGame(players, focus, game_type, data_table)
```

新版：

```lua
---@class AskToMiniGameParams
---@field skill_name string @ 烧条时显示的技能名
---@field game_type string @ 小游戏框关键词
---@field data_table table<integer, any> @ 以每个playerID为键的数据数组

-- TODO: 重构request机制，不然这个还得手动拿client_reply
---@param players ServerPlayer[] @ 需要参与这个框的角色
---@param params AskToMiniGameParams @ 各种变量
function Room:askToMiniGame(players, params)
```

旧版：

```lua
-- 调用一个自定义对话框，须自备loadData方法
---@param player ServerPlayer
---@param focustxt string
---@param qmlPath string
---@param extra_data any
---@return string
---@deprecated
function CompatAskFor:askForCustomDialog(player, focustxt, qmlPath, extra_data)
```

新版：

```lua
---@class AskToCustomDialogParams
---@field skill_name string @ 烧条时显示的技能名
---@field qml_path string @ 小游戏框关键词
---@field extra_data any @ 额外信息，因技能而异了

-- Show a qml dialog and return qml's ClientInstance.replyToServer
-- Do anything you like through this function

-- 调用一个自定义对话框，须自备loadData方法
---@param player ServerPlayer @ 询问的角色
---@param params AskToCustomDialogParams @ 各种变量
---@return string @ 格式化字符串，可能需要json.decode
function Room:askToCustomDialog(player, params)
```

旧版：

```lua
--- 询问移动场上的一张牌。不可取消
---@param player ServerPlayer @ 移动的操作
---@param targetOne ServerPlayer @ 移动的目标1玩家
---@param targetTwo ServerPlayer @ 移动的目标2玩家
---@param skillName string @ 技能名
---@param flag? string @ 限定可移动的区域，值为nil（装备区和判定区）、‘e’或‘j’
---@param moveFrom? ServerPlayer @ 是否只是目标1移动给目标2
---@param excludeIds? integer[] @ 本次不可移动的卡牌id
---@return table<"card"|"from"|"to">? @ 选择的卡牌、起点玩家id和终点玩家id列表
---@deprecated
function CompatAskFor:askForMoveCardInBoard(player, targetOne, targetTwo, skillName, flag, moveFrom, excludeIds)
```

新版：

```lua
---@class AskToMoveCardInBoardParams
---@field target_one ServerPlayer @ 移动的目标1玩家
---@field target_two ServerPlayer @ 移动的目标2玩家
---@field skill_name string @ 技能名
---@field flag? "e" | "j" @ 限定可移动的区域，值为nil（装备区和判定区）、‘e’或‘j’
---@field move_from? ServerPlayer @ 移动来源是否只能是某角色
---@field exclude_ids? integer[] @ 本次不可移动的卡牌id
---@field skip? boolean @ 是否跳过移动。默认不跳过

--- 询问移动场上的一张牌。不可取消
---@param player ServerPlayer @ 移动的操作者
---@param params AskToMoveCardInBoardParams @ 各种变量
---@return { card: Card | integer, from: ServerPlayer, to: ServerPlayer }? @ 选择的卡牌、起点玩家id和终点玩家id列表
function Room:askToMoveCardInBoard(player, params)
```

旧版：

```lua
--- 询问一名玩家从targets中选择出若干名玩家来移动场上的牌。
---@param player ServerPlayer @ 要做选择的玩家
---@param prompt string @ 提示信息
---@param skillName string @ 技能名
---@param cancelable? boolean @ 是否可以取消选择
---@param flag? string @ 限定可移动的区域，值为nil（装备区和判定区）、‘e’或‘j’
---@param no_indicate? boolean @ 是否不显示指示线
---@return integer[] @ 选择的玩家id列表，可能为空
---@deprecated
function CompatAskFor:askForChooseToMoveCardInBoard(player, prompt, skillName, cancelable, flag, no_indicate, excludeIds)
```

新版：

```lua
---@class AskToChooseToMoveCardInBoardParams: AskToUseActiveSkillParams
---@field flag? "e" | "j" @ 限定可移动的区域，值为nil（装备区和判定区）、‘e’或‘j’
---@field exclude_ids? integer[] @ 本次不可移动的卡牌id

--- 询问一名玩家选择两名角色，在这两名角色之间移动场上一张牌
---@param player ServerPlayer @ 要做选择的玩家
---@param params AskToChooseToMoveCardInBoardParams @ 各种变量
---@return ServerPlayer[] @ 选择的两个玩家的列表，若未选择，返回空表
function Room:askToChooseToMoveCardInBoard(player, params)



___

除了这些方法之外的任何代码你不能做出任何改动。

注意了，你做这个重构的过程中，不要新建param局部变量来保存变量，而是直接把表写在askToXXX函数调用内部。

接下来会给你需要重构的技能代码，你需要将技能用新版本的格式进行重构，将结果代码直接输出，
不要额外解释也不要添加markdown风格的```lua之类的东西：

-- <这里是你重构后的代码>