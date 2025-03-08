import os
import re

# 先就解决一下提取技能和提取武将的问题
class FkPackage:
    skills = {}
    generals = []
    translations = {}

    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath, 'r', encoding='utf-8') as f:
            self.file_content = f.read()
        self._extract_translations()
        self._extract_skills()
        self._extract_generals()

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
    def _extract_translations(self):
        # 提取所有翻译项
        trans_pattern = re.compile(r'\[["\'](.*?)["\']\]\s*=\s*["\'](.*?)["\']', re.DOTALL)
        self.translations = {}
        for match in trans_pattern.finditer(self.file_content):
            key, value = match.groups()
            self.translations[key] = value

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
            self.skills[skill_name] = ({
                'content': content,
                'translations': [],
            })
            
        related_pattern = re.compile(r'(\w+):addRelatedSkill\(\s*(\w+)\s*\)')
        for match in related_pattern.finditer(self.file_content):
            main_skill = match.group(1)
            sub_skill = match.group(2)
            if not main_skill in self.skills:
                continue
            main_skill_obj = self.skills[main_skill]
            sub_skill_obj = self.skills[sub_skill]
            main_skill_obj['content'] += "\n\n"
            main_skill_obj['content'] += sub_skill_obj['content']
            main_skill_obj['content'] += "\n"
            main_skill_obj['content'] += match.group()
            del self.skills[sub_skill]

        for k in self.skills:
            sk = self.skills[k]
            content = sk['content']
            strings = re.findall(r'["\'](.*?)["\']', content, re.DOTALL)
            # 收集翻译并去重
            translations = []
            seen = set()
            for s in set(strings):
                if s in self.translations and s not in seen:
                    seen.add(s)
                    translations.append({'key': s, 'value': self.translations[s]})
            sk['translations'] = translations

    def _extract_generals(self):
        self.generals = []
        general_pattern = re.compile(r'local\s+(\w+)\s*=\s*General(?::new)?\s*\(', re.IGNORECASE)
        for match in general_pattern.finditer(self.file_content):
            general_name = match.group(1)
            # 定位参数括号位置
            general_match = match.group(0)
            paren_pos = general_match.rfind('(')
            start_paren_pos = match.start() + paren_pos
            level = 1
            end_paren_pos = start_paren_pos + 1
            while end_paren_pos < len(self.file_content) and level > 0:
                char = self.file_content[end_paren_pos]
                if char == '(':
                    level += 1
                elif char == ')':
                    level -= 1
                end_paren_pos += 1
            creation_content = self.file_content[match.start():end_paren_pos]
            # 收集关联调用
            related_lines = []
            line_pattern = re.compile(r'^\s*{}\b\s*[:.]'.format(re.escape(general_name)), re.MULTILINE)
            for line_match in line_pattern.finditer(self.file_content, end_paren_pos):
                line_start = line_match.start()
                line_end = self.file_content.find('\n', line_start)
                line = self.file_content[line_start:line_end if line_end != -1 else None].strip()
                related_lines.append(line)
            # 合并内容
            content = '\n'.join([creation_content] + related_lines)
            # 处理翻译
            strings = re.findall(r'["\'](.*?)["\']', content, re.DOTALL)
            translations = []
            seen = set()
            for s in set(strings):
                if s in self.translations and s not in seen:
                    seen.add(s)
                    translations.append({'key': s, 'value': self.translations[s]})
            self.generals.append({
                'name': general_name,
                'content': content,
                'translations': translations
            })

    def mkSkillDir(self):
        """创建技能文件目录结构并写入技能内容"""
        # 获取基础路径信息
        dir_path = os.path.dirname(os.path.abspath(self.filepath))
        base_name = os.path.splitext(os.path.basename(self.filepath))[0]
        
        # 创建目标文件夹
        target_dir = os.path.join(dir_path, "pkg", base_name, "skills")
        os.makedirs(target_dir, exist_ok=True)

        # 写入技能文件
        for skill_name in self.skills:
            skill = self.skills[skill_name]
            # 清理非法文件名字符
            safe_name = re.sub(r'[\\/*?:"<>|]', '_', skill_name)
            file_path = os.path.join(target_dir, f"{safe_name}.lua")
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(skill['content'])
            except Exception as e:
                print(f"写入技能文件失败: {file_path} | 错误: {str(e)}")
