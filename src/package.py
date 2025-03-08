import os
import re
from openai import OpenAI

class Skill:
    name: str
    contents = []
    translations = []
    def __init__(self, name, contents, trans):
        self.name = name
        self.contents = contents
        self.translations = trans

class GPT:
    basic_prompt: str # 用来指示技能基本架构如何进行改变的prompt
    misc_prompt: str
    askto_prompt: str # 用来杀askFor系列的prompt
    model = "qwen2.5:32b_72Kctx" # 用ollama创建的context window增大版的model

    def __init__(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(dir_path, "prompts")
        with open(os.path.join(base_path, "01-basic.md")) as f:
            self.basic_prompt = f.read()
        with open(os.path.join(base_path, "02-misc.md")) as f:
            self.misc_prompt = f.read()
        with open(os.path.join(base_path, "03-askto.md")) as f:
            self.askto_prompt = f.read()
        
        # 根据自己需求修改key
        # 不过如果用的是公开厂商的API key，那么绝对不要公布出来！
        # 这里是我本地部署的ai所以我就对key随便处理了
        api_end_point = "http://localhost:8080/api"
        api_key = "sk-cb7ee040c840447ca35cc6e63c25bebf"
        self.client = OpenAI(api_key=api_key, base_url=api_end_point)

    def chat(self, sys_prompt, skill) -> str:
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": skill},
            ],
            stream=False
        ).choices[0].message.content

# 先就解决一下提取技能和提取武将的问题
class FkPackage:
    skills: dict[str, Skill] = {}
    generals = []
    translations = {}

    def __init__(self, filepath: str):
        self.gpt = GPT()
        self.filepath = filepath
        with open(filepath, 'r', encoding='utf-8') as f:
            self.file_content = f.read()
        self._extract_translations()
        self._extract_skills()

    '''
    直接检索文件中的Fk:loadTranslationTable { ... }
    花括号中的内容必定是形如 ["xxx"] = "xxx2", 之类的表形式
    并且必定不产生嵌套 只有string-string的键值对
    可能利用了lua的字符串拼接符号..进行多行字符串，亦可能使用单引号
    将提取到的翻译表内容翻译成python字典语法，然后直接读取该字典
    '''
    def _extract_translations(self):
        self.translations = {}
        # 查找Fk:loadTranslationTable的位置
        start_pattern = re.compile(r'Fk:loadTranslationTable\s*{', re.DOTALL)
        for match in start_pattern.finditer(self.file_content):
            start_pos = match.end()

            # 提取直到匹配的闭合花括号的内容
            brace_count = 1
            current_pos = start_pos
            content = []
            while current_pos < len(self.file_content) and brace_count > 0:
                char = self.file_content[current_pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                if brace_count > 0:
                    content.append(char)
                current_pos += 1
            table_content = ''.join(content)

            # 去除注释
            cleaned_content = re.sub(r'--.*', '', table_content, flags=re.MULTILINE)

            # 分割键值对
            entries = re.split(r',\s*', cleaned_content)

            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue

                # 解析键
                key_match = re.match(r'\s*\[\s*(["\'])(.*?)\1\s*\]\s*=\s*(.*)', entry, re.DOTALL)
                if not key_match:
                    continue
                quote_type, key_content, value_expr = key_match.groups()

                # 处理键的转义
                key = self._unescape_lua_string(key_content)

                # 解析值中的字符串
                value = self._parse_lua_value(value_expr)

                if key and value is not None:
                    self.translations[key] = value

    def _unescape_lua_string(self, s):
        # 处理Lua字符串中的转义字符
        replacements = {
            '\\\\': '\\',
            '\\"': '"',
            "\\'": "'",
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\b': '\b',
            '\\f': '\f',
            '\\a': '\a',
            '\\v': '\v'
        }
        for escaped, unescaped in replacements.items():
            s = s.replace(escaped, unescaped)
        return s

    def _parse_lua_value(self, expr):
        # 解析Lua字符串拼接表达式
        str_pattern = re.compile(r'''["']((?:[^\\"']|\\.)*)["']''', re.DOTALL)
        parts = []
        for match in str_pattern.finditer(expr):
            str_content = match.group(1)
            parts.append(self._unescape_lua_string(str_content))
        return ''.join(parts) if parts else None

    '''
    把东西作为字典放入自己的skills里面
    name: 技能名，content: 源代码内容
    translations: 翻译表

    技能的格式为：
    local xxx = fk.CreateXXXSkill {
      <中间全部>
    }
    xxx:addRelatedSkill(yyy)

    如果某个技能是为了被addRelatedSkill而创建的，那他就不是
    
    翻译表是{ key: "xxx", value: "yyy" }格式的数组。检索方法是首先
    找出代码内容中全部字符串，然后再从整个文件中找形如["xxx"] = "yyy"的行
    （单引号亦可，后者可能有折行），将这样的加入到translation中。

    最后加入数组
    '''
    def _extract_skills(self):
        self.skills = {}
        skill_pattern = re.compile(r'local\s+(\w+)\s*=\s*fk\.Create\w+Skill\s*\{', re.IGNORECASE)
        for match in skill_pattern.finditer(self.file_content):
            skill_name = match.group(1)
            start_pos = match.start()
            level = 1
            end_pos = match.end()
            while end_pos < len(self.file_content) and level > 0:
                char = self.file_content[end_pos]
                if char == '{':
                    level += 1
                elif char == '}':
                    level -= 1
                end_pos += 1
            content = self.file_content[start_pos:end_pos]  # 提取完整技能内容
            skill_str_name = re.compile(r'name = ["\'](.*?)["\'],').findall(content)[0]
            self.skills[skill_name] = Skill(skill_str_name, [content], [])
            
        related_pattern = re.compile(r'(\w+):addRelatedSkill\(\s*(\w+)\s*\)')
        for match in related_pattern.finditer(self.file_content):
            main_skill = match.group(1)
            sub_skill = match.group(2)
            if not main_skill in self.skills:
                continue
            main_skill_obj = self.skills[main_skill]
            sub_skill_obj = self.skills[sub_skill]
            main_skill_obj.contents.append(sub_skill_obj.contents[0])
            del self.skills[sub_skill]

        for k in self.skills:
            sk = self.skills[k]
            content = '\n'.join(sk.contents)
            strings: list[str] = re.findall(r'["\'](.*?)["\']', content, re.DOTALL)
            for i in range(0, len(strings)):
                if strings[i].endswith(':'):
                    strings[i] = strings[i].rstrip(':')
            strings.append(sk.name)
            strings.append(":" + sk.name)
            strings.append("$" + sk.name)
            for i in range(1, 9):
                strings.append("$" + sk.name + str(i))
            # 收集翻译并去重
            translations = []
            seen = set()
            for s in strings:
                if s in self.translations and s not in seen:
                    seen.add(s)
                    translations.append({'key': s, 'value': self.translations[s]})
            sk.translations = translations

    def mkSkillDir(self):
        """创建技能文件目录结构并写入技能内容"""
        # 获取基础路径信息
        dir_path = os.path.dirname(os.path.abspath(self.filepath))
        base_name = os.path.splitext(os.path.basename(self.filepath))[0]
        
        # 创建目标文件夹
        target_dir = os.path.join(dir_path, "pkg", base_name, "skills")
        os.makedirs(target_dir, exist_ok=True)

        i = 0
        n = len(self.skills.keys())

        # 写入技能文件
        for skill_name in self.skills:
            i += 1
            print("[*] 正在处理第 %d/%d 个技能：%s" % (i, n, skill_name))
            skill = self.skills[skill_name]
            # 清理非法文件名字符
            safe_name = re.sub(r'[\\/*?:"<>|]', '_', skill_name)
            file_path = os.path.join(target_dir, f"{safe_name}.lua")
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._refactor_skill(skill))

            except Exception as e:
                print(f"写入技能文件失败: {file_path} | 错误: {str(e)}")

    def _refactor_skill(self, skillObj: Skill) -> str:
        content = '\n\n'.join(skillObj.contents)
        content += "Fk:loadTranslationTable{\n"
        for kv in skillObj.translations:
            content += "  [%s] = %s,\n" % (repr(kv['key']), repr(kv['value']))
        content += "}\n"
        gpt = self.gpt
        n = 2

        print ("  [1/%d] 将技能主体结构调整为新版" % n)
        content = gpt.chat(gpt.basic_prompt, content)
        print ("  [2/%d] 调整self.name，cost_data等" % n)
        content = gpt.chat(gpt.misc_prompt, content)
        print ("  [3/%d] 重构askFor系列函数" % n)
        content = gpt.chat(gpt.askto_prompt, content)

        content = content.replace('    ', '  ')

        return content
