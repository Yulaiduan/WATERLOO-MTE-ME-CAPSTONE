"""Check repository-relative Markdown links and code fences.

Run: python scripts/check_docs.py from app root.
Inputs: tracked/nonignored Markdown files from Git; no physical units.
Outputs: diagnostics and exit status; writes no files. Requires Python/Git.
Limitations: external URLs and target anchors are not verified.
"""
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

def main():
 root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip())
 paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=root,text=True).splitlines()
 errors=[];checked=0
 for name in sorted(set(paths)):
  if not name.endswith('.md'):continue
  p=root/name
  if not p.exists():continue
  text=p.read_text(encoding='utf-8')
  if len(re.findall(r'^```',text,re.M))%2:errors.append(f'{name}: unbalanced fences')
  text=re.sub(r'```.*?```','',text,flags=re.S)
  for target in re.findall(r'\]\(([^)]+)\)',text):
   target=target.strip().strip('<>').split('#',1)[0]
   if not target or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:',target):continue
   target=unquote(target);checked+=1
   if not (p.parent/target).resolve().exists():errors.append(f'{name}: missing {target}')
 if errors:print('\n'.join(errors));return 1
 print(f'PASS: {checked} relative Markdown links resolve; fences balanced.');return 0

if __name__=='__main__':raise SystemExit(main())
