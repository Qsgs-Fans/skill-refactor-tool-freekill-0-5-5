import os
import sys
from src.package import FkPackage

def main():
    args = sys.argv
    if len(args) < 2:
        print(f"Usage: {args[0]} <full path of lua file>")
        return

    path = args[1]
    pkg = FkPackage(path)
    obj = pkg.skills['jilei']
    print(obj['content'])
    print(obj['translations'])
    pkg.mkSkillDir()

if __name__ == "__main__":
    main()
