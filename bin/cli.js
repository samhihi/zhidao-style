#!/usr/bin/env node
'use strict';

// zhidao-style 安装器：把本包携带的 skill 资产整目录拷进 agent 的 skills 目录。
// 零依赖；升级即整目录覆盖（与 SKILL.md 安装口径一致）。

const fs = require('fs');
const os = require('os');
const path = require('path');

const SKILL_NAME = 'zhidao-style';
const PKG_ROOT = path.resolve(__dirname, '..');
const PKG = JSON.parse(fs.readFileSync(path.join(PKG_ROOT, 'package.json'), 'utf8'));
// 拷贝 = 包根全部内容，排除安装器自身与包元数据
const COPY_EXCLUDE = new Set(['bin', 'package.json', 'node_modules', '.git']);

const HOME = os.homedir();
const TARGETS = {
  claude: { skillsDir: path.join(HOME, '.claude', 'skills'), label: 'Claude Code' },
  codex: { skillsDir: path.join(HOME, '.agents', 'skills'), label: 'Codex 等兼容 agent' },
};

function help() {
  console.log(`知到风 zhidao-style · Agent Skill 安装器 v${PKG.version}

用法：
  npx zhidao-style [install]      安装/升级（默认命令）
  npx zhidao-style uninstall      卸载

目标（可组合；不指定则自动检测 ~/.claude 与 ~/.agents，都没有时默认装 Claude Code）：
  --claude            ~/.claude/skills/${SKILL_NAME}   （Claude Code）
  --codex             ~/.agents/skills/${SKILL_NAME}   （Codex 及其他兼容 SKILL.md 开放标准的 agent）
  --project           ./.claude/skills/${SKILL_NAME}   （当前项目级）
  --dir <skills目录>   装到 <skills目录>/${SKILL_NAME}

其他：
  -v, --version       版本
  -h, --help          本帮助`);
}

function parseArgs(argv) {
  const opts = { command: 'install', targets: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === 'install' || a === 'uninstall') opts.command = a;
    else if (a === '--claude') opts.targets.push(TARGETS.claude);
    else if (a === '--codex') opts.targets.push(TARGETS.codex);
    else if (a === '--project')
      opts.targets.push({ skillsDir: path.join(process.cwd(), '.claude', 'skills'), label: '当前项目' });
    else if (a === '--dir') {
      const dir = argv[++i];
      if (!dir) fail('--dir 需要一个 skills 目录路径');
      opts.targets.push({ skillsDir: path.resolve(dir), label: '自定义目录' });
    } else if (a === '-h' || a === '--help') opts.command = 'help';
    else if (a === '-v' || a === '--version') opts.command = 'version';
    else fail(`未知参数：${a}（用 --help 查看用法）`);
  }
  return opts;
}

function fail(msg) {
  console.error(`✗ ${msg}`);
  process.exit(1);
}

// 未显式指定目标时：自动检测已有的 agent 目录；都没有则默认 Claude Code
function detectTargets(forUninstall) {
  const found = [];
  if (fs.existsSync(path.join(HOME, '.claude'))) found.push(TARGETS.claude);
  if (fs.existsSync(path.join(HOME, '.agents'))) found.push(TARGETS.codex);
  if (found.length === 0 && !forUninstall) found.push(TARGETS.claude);
  return found;
}

function install(target) {
  const dest = path.join(target.skillsDir, SKILL_NAME);
  if (path.basename(dest) !== SKILL_NAME) fail(`目标路径异常，拒绝写入：${dest}`);
  if (fs.existsSync(dest)) fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(PKG_ROOT)) {
    if (COPY_EXCLUDE.has(entry)) continue;
    fs.cpSync(path.join(PKG_ROOT, entry), path.join(dest, entry), { recursive: true });
  }
  console.log(`✔ 已安装 ${SKILL_NAME} v${PKG.version} → ${dest}（${target.label}）`);
}

function uninstall(target) {
  const dest = path.join(target.skillsDir, SKILL_NAME);
  if (path.basename(dest) !== SKILL_NAME) fail(`目标路径异常，拒绝删除：${dest}`);
  if (!fs.existsSync(dest)) {
    console.log(`- 未找到安装：${dest}`);
    return;
  }
  fs.rmSync(dest, { recursive: true, force: true });
  console.log(`✔ 已卸载：${dest}`);
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.command === 'help') return help();
  if (opts.command === 'version') return console.log(PKG.version);

  const targets = opts.targets.length ? opts.targets : detectTargets(opts.command === 'uninstall');
  if (targets.length === 0) fail('未检测到 ~/.claude 或 ~/.agents，也未指定目标（--claude/--codex/--project/--dir）');

  for (const t of targets) (opts.command === 'uninstall' ? uninstall : install)(t);

  if (opts.command === 'install') {
    console.log(`\n开工：对 agent 说「用知到风做一份 XX 的 HTML 文档」「按知到的设计系统出一版 deck」即可。`);
    console.log(`升级：重跑 npx ${SKILL_NAME}@latest`);
  }
}

main();
