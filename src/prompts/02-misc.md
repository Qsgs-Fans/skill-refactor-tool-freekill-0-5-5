部分代码还用着旧版写法的self.name、hasSkill(self)、self.cost_data之类的东西。
你需要针对以上三个东西进行重构。

___

## self.name相关

这里的self是指函数参数中的那个self，在新版本代码中应该用skill.name而不是self.name，
其中skill指的是文件开头那个`local skill = fk.CreateSkill{ ... }`的skill。

例如：

```lua
local biyue = fk.CreateSkill { ... }

-- ...

player:drawCards(2, self.name)
```

应该改成

```lua
player:drawCards(2, biyue.name)
```

## hasSkill(self)

将它理解成hasSkill(self.name)，然后把参数类似之前的改成skill.name

## cost_data相关

当处于有event参数的函数内部时，对于self.cost_data的写入：

```lua
self.cost_data = xxx
```

改成

```lua
event:setCostData(self, xxx)
```

当读取self.cost_data时：

```lua
local a = self.cost_data
```

改成

```lua
local a = event:getCostData(self)
```

___

除了这些方法之外的任何代码你不能做出任何改动。

接下来会给你需要重构的技能代码，你需要将技能用新版本的格式进行重构，将结果代码直接输出，
不要额外解释也不要添加markdown风格的```lua之类的东西：

-- <这里是你重构后的代码>