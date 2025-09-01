#!/usr/bin/env python3
import os, datetime
HDR = """// Author: Joey Soprano (c) {year}
// Prepared with assistance by GPT-5 Thinking
// License: S.U.E.T. — see LICENSE or https://github.com/JoeySoprano420/S.U.E.T.-License/blob/main/License.md
"""
EXTS = ('.sdr','.py','.c','.h','.hpp','.cc','.cpp','.md','.yml','.yaml','.toml','.mk','.txt')
def main(root='.'):
    y = datetime.datetime.now().year
    for dp,_,fs in os.walk(root):
        if any(x in dp for x in ('.git','build','dist','site','.venv','__pycache__')): continue
        for fn in fs:
            if fn.endswith(EXTS):
                p = os.path.join(dp, fn)
                with open(p,'r',encoding='utf-8') as f: c = f.read()
                if 'S.U.E.T.' in c[:200]: continue
                with open(p,'w',encoding='utf-8',newline='\n') as f: f.write(HDR.format(year=y)+'\n'+c)
if __name__=='__main__': main()
