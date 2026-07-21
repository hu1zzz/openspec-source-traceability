from __future__ import annotations
import argparse, hashlib, re
from pathlib import Path
HEADING=re.compile(r"(?m)^(#{1,6}\s+.+|\d+(?:\.\d+)*\s+.+)$")
ID=re.compile(r"(?:需求编号|Requirement ID)\s*[：:]\s*([A-Za-z][A-Za-z0-9_-]+)")
REV=re.compile(r"(?:修订号|Revision)\s*[：:]\s*([^\r\n]+)")
def write(path,text): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8")
def slug(text): return re.sub(r"[^a-z0-9]+","-",re.sub(r"^#+\s*|^\d+(?:\.\d+)*\s*","",text).lower()).strip("-") or "requirement-package"
def package_requirements(source,source_name,output_dir,max_package_units=12):
 matches=list(HEADING.finditer(source)) or [re.match(r"(?s)^",source)]; packages=[]; unresolved=[]
 for i,m in enumerate(matches):
  end=matches[i+1].start() if i+1<len(matches) else len(source); body=source[m.start():end].strip()
  if not body or not (ID.search(body) or "应" in body or "shall" in body.lower()): continue
  title=m.group(0).strip() if m.group(0) else "未命名需求片段"; ident=ID.search(body); rev=REV.search(body); n=len(packages)+1; identity=ident.group(1) if ident else f"INFERRED-{n:03d}"; executable=ident is not None; start=source[:m.start()].count("\n")+1; stop=source[:end].count("\n")+1; digest=hashlib.sha256((body.replace("\r\n","\n").rstrip()+"\n").encode()).hexdigest(); folder=f"{n:02d}-{slug(title)}"
  if not executable: unresolved.append(f"- `sourceIdentity: inferred` — {title}（{start}-{stop} 行）：不具备外部双向追溯声明条件。")
  write(output_dir/folder/"input.md",f"<!-- requirement-package: true\nsource-document: {source_name}\nsource-lines: {start}-{stop}\nsource-body-sha256: {digest}\n-->\n\n{body}\n")
  suffix="@"+rev.group(1).strip() if rev else ""; write(output_dir/folder/"package.yaml",f"id: {folder}\nchangeName: {slug(title)}\nexecutable: {str(executable).lower()}\nprimarySources:\n  - {identity}{suffix}\ndependencies: []\n"); packages.append((folder,identity,executable,digest))
 manifest=["packages:"]
 for folder,identity,executable,digest in packages: manifest += [f"  - id: {folder}",f"    executable: {str(executable).lower()}",f"    primarySource: {identity}",f"    hash: {digest}"]
 write(output_dir/"manifest.yaml","\n".join(manifest)+"\n"); issues=validate_manifest(output_dir); write(output_dir/"validation-report.md","# 验证报告\n\n"+(("BLOCKING\n"+"\n".join("- "+x for x in issues)) if issues else "PASS：主归属唯一、输出哈希已生成。")+"\n"); write(output_dir/"unresolved-items.md","# 待确认项\n\n"+("\n".join(unresolved) if unresolved else "无。")+"\n"); return {"executablePackages":sum(p[2] for p in packages),"issues":issues}
def validate_manifest(output_dir):
 values=re.findall(r"^\s+primarySource: (.+)$",(output_dir/"manifest.yaml").read_text(encoding="utf-8"),re.M); return [f"重复主归属：{v}" for v in set(values) if values.count(v)>1]
def main():
 p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("output_dir",type=Path);a=p.parse_args();result=package_requirements(a.input.read_text(encoding="utf-8"),a.input.name,a.output_dir);print("BLOCKING: "+"; ".join(result["issues"]) if result["issues"] else f"PASS: executable packages={result['executablePackages']}");raise SystemExit(2 if result["issues"] else 0)
if __name__=="__main__": main()
