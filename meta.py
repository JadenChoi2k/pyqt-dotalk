import os
import preferences

# calculate number of letters, lines


def add_vector2(v1:tuple, v2:tuple)->tuple:
    if not len(v1) == 2 or not len(v2) == 2:
        return None
    return v1[0] + v2[0], v1[1] + v2[1]


# find .py files and returns (letters, lines)
def research_size_in_curdir(path):
    listdir = os.listdir(path)
    ret = (0, 0)

    for item in listdir:
        isdir = '.' not in item

        try:
            if isdir:
                ret = add_vector2(ret, research_size_in_curdir(os.path.join(path, item)))
            else:
                if os.path.splitext(item)[1] == '.py':
                    with open(os.path.join(path, item), encoding='utf-8', mode='rt') as f:
                        content = f.read()
                        charsize, linesize = (len(content), content.count('\n') + 1)
                        ret = add_vector2(ret, (charsize - linesize, linesize))
        except Exception as e:
            print(f'error from {item}', e)
    return ret


def project_info():
    charsize, linesize = research_size_in_curdir('.')
    print(f'''
========================== dotalk ==========================

 'dotalk' is desktop messenger application made with PyQt5 and basic python modules.
 
 current version : {preferences.VERSION}

============================================================
''')
