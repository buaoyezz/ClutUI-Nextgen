import json
import os

def merge_locales():
    # 加载共享内容
    with open('locales/shared_content.json', 'r', encoding='utf-8') as f:
        shared = json.load(f)
    
    # 获取所有语言文件
    locale_files = [f for f in os.listdir('locales') 
                   if f.endswith('.json') and f != 'shared_content.json' and f != 'base.json']
    
    # 合并每个语言文件
    for locale_file in locale_files:
        file_path = os.path.join('locales', locale_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
        
        # 合并共享内容（不覆盖已有内容）
        for key, value in shared.items():
            if key not in locale_data:
                locale_data[key] = value
        
        # 保存合并后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(locale_data, f, ensure_ascii=False, indent=4)
        
        print(f"已更新: {locale_file}")

if __name__ == "__main__":
    merge_locales() 