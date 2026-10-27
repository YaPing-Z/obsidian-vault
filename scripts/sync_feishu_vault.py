#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书知识库(ObsidianVault) -> 本地 Obsidian 库 增量同步脚本
- 列出知识库所有 docx 节点
- 拉取 Markdown，仅当内容有变化(或新增)时才写文件
- 自动 git add/commit/push 到 GitHub
配合 WorkBuddy 定时自动化使用，实现"手机存飞书 -> 自动进 Obsidian"闭环。

注意：lark-cli 与 git 通过 Git-Bash 调用（Windows 上无扩展名脚本无法直接 CreateProcess）。
"""
import json
import subprocess
import hashlib
import os
import re
import sys
import datetime

VAULT = r"D:\PING OB\ObsidianVault"
SPACE_ID = "7700080442656951542"
OUT_DIR = os.path.join(VAULT, "飞书导入")
STATE_FILE = os.path.join(VAULT, ".scripts", "feishu_sync_state.json")
BASH = r"D:\Program Files\WorkBuddy\resources\vendor\PortableGit\usr\bin\bash.exe"
LARK = "/c/Users/Yaping/.workbuddy/binaries/node/cli-connector-packages/lark-cli"
GIT = "/c/Program Files/Git/bin/git.exe"


def run(cmd_str):
    """通过 Git-Bash 执行命令，返回 CompletedProcess（stdout/stderr 为文本）。"""
    return subprocess.run(
        [BASH, "-lc", cmd_str],
        capture_output=True, text=True,
    )


def list_nodes():
    r = run(f'{LARK} wiki +node-list --space-id {SPACE_ID} --as user --format json')
    if r.returncode != 0:
        print(f"[ERR] 列出节点失败:\n{r.stderr[:600]}", file=sys.stderr)
        return []
    try:
        data = json.loads(r.stdout)
        return [n for n in data.get("data", {}).get("nodes", [])
                if n.get("obj_type") == "docx"]
    except Exception as e:
        print("[ERR] 解析节点列表失败:", e, file=sys.stderr)
        return []


def fetch_md(obj_token):
    r = run(f'{LARK} docs +fetch --doc {obj_token} --doc-format markdown '
            f'--detail simple --as user')
    if r.returncode != 0:
        return None, None
    try:
        data = json.loads(r.stdout)
        content = data["data"]["document"]["content"]
    except Exception:
        return None, None
    m = re.match(r"\s*<title>(.*?)</title>\s*", content)
    title = m.group(1).strip() if m else ""
    body = content[m.end():] if m else content
    return title, body.strip()


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    state = load_state()
    nodes = list_nodes()
    print(f"知识库节点数(docx): {len(nodes)}")

    changed = []
    for n in nodes:
        obj = n["obj_token"]
        title_from_node = n.get("title", "").strip()
        title, body = fetch_md(obj)
        if title is None:
            print(f"  [跳过] 拉取失败: {title_from_node} ({obj})")
            continue
        final_title = title or title_from_node or obj
        # 节点 title 有时包含整篇正文（多行），取首行作为标题与文件名
        display_title = final_title.split("\n", 1)[0].strip()
        if not display_title:
            display_title = obj
        h = hashlib.md5((display_title + "\n" + body).encode("utf-8")).hexdigest()
        if state.get(obj) == h:
            continue  # 无变化
        md = (
            f"---\n"
            f"tags:\n  - 飞书导入\n  - 知识库\n"
            f"source: https://feishu.cn/docx/{obj}\n"
            f"updated: {datetime.date.today().isoformat()}\n"
            f"---\n\n"
            f"# {display_title}\n\n{body}\n"
        )
        # 文件名：去除非法字符（含换行/控制符），空白折叠并截断，避免超长
        safe = re.sub(r'[\x00-\x1f\x7f\\/:*?"<>|]', "_", display_title)
        safe = re.sub(r'\s+', " ", safe).strip()
        if not safe:
            safe = obj
        fname = safe[:120].rstrip("_.") + ".md"
        path = os.path.join(OUT_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        state[obj] = h
        changed.append((display_title, fname))
        print(f"  [更新] {display_title} -> {fname}")

    save_state(state)

    if not changed:
        print("无新增/变更，跳过提交。")
        return

    run(f'"{GIT}" -C "{VAULT}" add -A')
    msg = "自动同步飞书知识库 ObsidianVault：" + "、".join(t for t, _ in changed)
    rc = run(f'"{GIT}" -C "{VAULT}" commit -m "{msg}"')
    if rc.returncode == 0:
        run(f'"{GIT}" -C "{VAULT}" push')
        print(f"已提交并推送 {len(changed)} 篇。")
    else:
        print("提交无变化或失败。")


if __name__ == "__main__":
    main()
