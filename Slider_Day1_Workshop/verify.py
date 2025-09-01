import subprocess, sys, re

def run(cmd):
 p=subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);return p.returncode,p.stdout

def cp1():
 c,o=run('lli build/hello.ll');
 assert c==0,o
 for s in ['Hail, Twelve!','x (dec): 34','sum 0..9: 45','nonzero']:
  assert s in o, f'missing {s}'
 print('[PASS] cp1')

def cp2():
 c,o=run('lli build/hello.ll');assert c==0,o
 assert 'x (dec): 34' in o and 'sum 0..9: 45' in o
 print('[PASS] cp2')

def cp3():
 c,o=run('./build/demo_acs_v1');assert c==0,o
 assert len(re.findall(r'ix:\s*\d+\s+val:\s*\d+', o))>=5, o
 print('[PASS] cp3')

def cp4():
 c,o=run('clang build/hello.ll examples/cdeps/add.c -o build/hello && ./build/hello');assert c==0,o
 print('[PASS] cp4')

if __name__=='__main__':
 getattr(sys.modules[__name__], sys.argv[1])()
