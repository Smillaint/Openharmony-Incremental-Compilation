# SSH 远程操作手册

## 1. 连接信息

```text
服务器：119.3.182.128
SSH 端口：42247
用户：root
本地私钥：C:\Users\31854\.ssh\id_ed25519
远端 OpenHarmony 源码：/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
远端 Git 精简仓库：/srv/workspace/github_upload/action_incremental_fixes
```

## 2. 打开远程终端

### 2.1 基本连接

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" root@119.3.182.128
```

连接成功后，当前 PowerShell 会进入远端 Linux 终端。可以执行：

```bash
pwd
whoami
hostname
ls -la
```

退出远程终端：

```bash
exit
```

也可以按 `Ctrl+D` 退出。

### 2.2 首次连接的主机指纹

首次连接可能显示：

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

确认服务器指纹无误后输入：

```text
yes
```

自动接受新主机指纹：

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" `
  -o StrictHostKeyChecking=accept-new `
  root@119.3.182.128
```

`accept-new` 只自动接受尚未记录的主机，不接受已记录主机的指纹变化。不要长期使用 `StrictHostKeyChecking=no` 处理生产服务器。

### 2.3 非交互连接测试

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" `
  -o BatchMode=yes `
  -o ConnectTimeout=15 `
  root@119.3.182.128 "whoami; hostname; pwd"
```

`BatchMode=yes` 表示禁止弹出密码输入，适合脚本和连接检查。

## 3. 进入 OpenHarmony 源码目录

登录远程终端后执行：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
pwd
```

确认输出：

```text
/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

查看源码根目录：

```bash
ls -la
```

## 4. 读取远程文件

### 4.1 查看完整文件

```bash
cat third_party/sane-airscan/BUILD.gn
```

适合较短文件。长文件不建议直接使用 `cat`。

### 4.2 按行号查看

查看第 1 至 120 行：

```bash
sed -n '1,120p' third_party/sane-airscan/BUILD.gn
```

显示行号：

```bash
nl -ba third_party/sane-airscan/BUILD.gn | sed -n '1,120p'
```

查看文件尾部：

```bash
tail -n 100 third_party/sane-airscan/patch_install.py
```

持续查看正在追加的日志：

```bash
tail -f out/rk3568/build.log
```

按 `Ctrl+C` 停止持续查看。

### 4.3 分页查看

```bash
less third_party/sane-airscan/BUILD.gn
```

常用按键：

- `Space`：下一页；
- `b`：上一页；
- `/文本`：向下搜索；
- `n`：下一个匹配；
- `q`：退出。

### 4.4 不进入终端，直接读取远程文件

在本地 PowerShell 执行：

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" root@119.3.182.128 `
  "sed -n '1,120p' /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/third_party/sane-airscan/BUILD.gn"
```

## 5. 搜索文件和代码

### 5.1 按文件名查找

```bash
find . -name 'BUILD.gn' | head -100
```

查找指定脚本：

```bash
find . -name 'patch_install.py'
```

### 5.2 使用 grep 搜索代码

```bash
grep -R -n 'airscan_action' third_party/sane-airscan
```

显示匹配行前后各 10 行：

```bash
grep -R -n -A10 -B10 'action("airscan_action")' third_party/sane-airscan
```

搜索多个关键词：

```bash
grep -R -n -E 'airscan_action|ark_jsf|gen_snapshot' third_party
```

忽略 `.git` 和输出目录：

```bash
grep -R -n \
  --exclude-dir=.git \
  --exclude-dir=out \
  'airscan_action' .
```

### 5.3 使用 ripgrep

如果远端安装了 `rg`，优先使用：

```bash
rg -n 'airscan_action' third_party/sane-airscan
```

列出文件：

```bash
rg --files third_party/sane-airscan
```

## 6. 查看文件属性和时间戳

```bash
stat third_party/sane-airscan/patch_install.py
```

只输出大小和纳秒级时间：

```bash
stat -c 'size=%s mtime=%Y.%N path=%n' \
  third_party/sane-airscan/patch_install.py
```

查看目录大小：

```bash
du -sh third_party/sane-airscan
```

找出超过 10 MiB 的文件：

```bash
find third_party/sane-airscan \
  -type f \
  -size +10M \
  -printf '%s %p\n' | sort -nr
```

## 7. 下载远程文件到本地

以下命令在本地 PowerShell 中执行。

### 7.1 下载单个文件

```powershell
scp -P 42247 -i "C:\Users\31854\.ssh\id_ed25519" `
  "root@119.3.182.128:/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/third_party/sane-airscan/BUILD.gn" `
  "D:\zlby\BUILD.gn"
```

注意：`scp` 的端口参数是大写 `-P`，SSH 的端口参数是小写 `-p`。

### 7.2 下载目录

```powershell
scp -P 42247 -i "C:\Users\31854\.ssh\id_ed25519" -r `
  "root@119.3.182.128:/srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/third_party/sane-airscan" `
  "D:\zlby\remote_source"
```

直接使用 `scp -r` 会包含目录中的普通隐藏文件。若源目录存在 `.git`，建议使用远端 `rsync` 建立排除后的暂存目录，再下载暂存目录。

## 8. 上传本地文件到远程

### 8.1 上传单个文件

```powershell
scp -P 42247 -i "C:\Users\31854\.ssh\id_ed25519" `
  "D:\workspace\README.md" `
  "root@119.3.182.128:/srv/workspace/github_upload/action_incremental_fixes/README.md"
```

### 8.2 上传目录

```powershell
scp -P 42247 -i "C:\Users\31854\.ssh\id_ed25519" -r `
  "D:\workspace\修改后脚本" `
  "root@119.3.182.128:/srv/workspace/github_upload/action_incremental_fixes/"
```

覆盖远程源码前必须先比较文件，避免覆盖其他人的修改。

## 9. 远程复制源码子目录

在远程服务器内部复制文件时，推荐使用 `rsync`，并排除 Git 元数据、缓存和构建产物。

```bash
rsync -a \
  --exclude='.git/' \
  --exclude='.repo/' \
  --exclude='__pycache__/' \
  --exclude='out/' \
  /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/third_party/sane-airscan/ \
  /srv/workspace/github_upload/action_incremental_fixes/third_party/sane-airscan/
```

参数说明：

- `-a`：保留目录结构、权限和时间；
- 源目录末尾的 `/`：复制目录内容；
- `--exclude`：排除不应进入目标仓库的内容。

先预演，不实际复制：

```bash
rsync -anv \
  --exclude='.git/' \
  --exclude='out/' \
  source_dir/ destination_dir/
```

## 10. 执行远程命令

### 10.1 执行单条命令

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" root@119.3.182.128 `
  "cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code && git status --short"
```

### 10.2 执行多条命令

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" root@119.3.182.128 `
  "cd /srv/workspace/github_upload/action_incremental_fixes; git status --short; git log -3 --oneline"
```

涉及删除、覆盖、移动、恢复或强制推送时，不要把未经检查的变量、通配符和递归命令拼接到 SSH 命令中。

## 11. 远程构建和 Ninja 检查

进入源码目录：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code
```

执行构建：

```bash
./build.sh -p rk3568 --build-target make_all
```

只分析 Ninja，不实际编译：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -n \
  -d explain \
  make_all
```

查询目标依赖：

```bash
prebuilts/build-tools/linux-x86/bin/ninja \
  -w dupbuild=warn \
  -C out/rk3568 \
  -t query \
  '目标输出路径'
```

查看 Ninja 历史：

```bash
grep 'airscan' out/rk3568/.ninja_log | tail -50
```

## 12. 远程 Git 操作

远端精简仓库：

```bash
cd /srv/workspace/github_upload/action_incremental_fixes
```

查看状态：

```bash
git status --short
```

查看修改：

```bash
git diff
```

查看暂存修改：

```bash
git diff --cached
```

提交：

```bash
git add README.md arkcompiler build third_party
git commit -m "Update ACTION incremental build analysis"
```

使用专用 GitHub Deploy key 推送：

```bash
GIT_SSH_COMMAND='ssh -i /root/.ssh/id_ed25519_github_openharmony -o IdentitiesOnly=yes' \
  git push origin main
```

验证远端分支：

```bash
GIT_SSH_COMMAND='ssh -i /root/.ssh/id_ed25519_github_openharmony -o IdentitiesOnly=yes' \
  git ls-remote origin refs/heads/main
```

这里引用的是远端私钥路径，不能执行 `cat /root/.ssh/id_ed25519_github_openharmony`，也不能把该私钥复制进仓库。

### 12.1 虚拟机通过 SSH 访问 GitCode fork

2026-08-13 已在 GitCode 账号 `SmillySmillick` 登记虚拟机构建密钥，名称为：

```text
openharmony-build-server
```

虚拟机对应私钥路径：

```text
/root/.ssh/id_ed25519_github_openharmony
```

packing_tool 仓已使用仓库级 SSH 配置，不影响其他仓库：

```bash
cd /srv/workspace/openharmony_master_default_20260723175927_huawei_33e607913/code/developtools/packing_tool

git config --get core.sshCommand
git remote -v
git ls-remote fork refs/heads/master
```

预期配置：

```text
core.sshCommand = ssh -i /root/.ssh/id_ed25519_github_openharmony -o IdentitiesOnly=yes
fork = git@gitcode.com:SmillySmillick/developtools_packing_tool.git
```

认证测试：

```bash
ssh -T \
  -i /root/.ssh/id_ed25519_github_openharmony \
  -o IdentitiesOnly=yes \
  git@gitcode.com
```

GitCode 返回欢迎信息即认证成功；Git 托管服务不提供交互 Shell，命令退出码不一定为零。

不得读取、复制、上传或提交 `/root/.ssh/id_ed25519_github_openharmony`。仓库中只能记录密钥路径和配置方式。

## 13. 保持 SSH 会话稳定

连接时启用客户端保活：

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" `
  -o ServerAliveInterval=30 `
  -o ServerAliveCountMax=6 `
  root@119.3.182.128
```

含义：

- 每 30 秒发送一次保活包；
- 连续 6 次无响应后断开。

长时间构建建议使用 `tmux`：

```bash
tmux new -s ohos-build
```

在 tmux 中启动构建后，按以下组合键暂时离开：

```text
Ctrl+B，然后按 D
```

重新进入：

```bash
tmux attach -t ohos-build
```

列出会话：

```bash
tmux ls
```

## 14. UTF-8 和中文路径

PowerShell 执行前可设置 UTF-8 输出：

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

远程 Linux 查看区域设置：

```bash
locale
```

临时使用 UTF-8：

```bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
```

所有包含空格或中文的 Windows 路径都应使用双引号包裹。

## 15. 常见错误

### 15.1 `Permission denied (publickey)`

检查：

```powershell
ssh -vvv -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" root@119.3.182.128
```

常见原因：

- 私钥路径错误；
- 服务端未配置对应公钥；
- 用户名错误；
- 私钥权限不安全；
- SSH 实际使用了其他密钥。

可强制只使用指定密钥：

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" `
  -o IdentitiesOnly=yes `
  root@119.3.182.128
```

### 15.2 `Host key verification failed`

先确认服务器地址和主机指纹，再清理旧记录：

```powershell
ssh-keygen -R "[119.3.182.128]:42247"
```

然后重新连接并确认新指纹。主机指纹意外变化可能意味着服务器重装，也可能是安全风险，不能直接忽略。

### 15.3 `REMOTE HOST IDENTIFICATION HAS CHANGED`

不要立即禁用主机验证。先联系服务器维护者确认是否更换过主机密钥，确认后再执行 `ssh-keygen -R`。

### 15.4 `scp` 找不到文件

检查：

- SSH 使用 `-p 42247`，scp 使用 `-P 42247`；
- 远程路径是否为绝对路径；
- Windows 本地路径是否使用双引号；
- 远程文件是否存在。

远程检查：

```powershell
ssh -p 42247 -i "C:\Users\31854\.ssh\id_ed25519" root@119.3.182.128 `
  "test -f /绝对路径/文件 && echo EXISTS"
```

## 16. 安全要求

以下文件禁止上传：

```text
id_ed25519
id_ed25519_github_openharmony
*.pem
*.key
.env
credentials 文件
访问令牌
包含密码的配置
```

提交前检查大文件：

```bash
find . -type f -not -path './.git/*' -size +10M -printf '%s %p\n'
```

检查敏感文件名：

```bash
find . -type f \
  \( -name 'id_*' -o -name '*.pem' -o -name '*.key' -o -name '.env' \) \
  -print
```

检查 Git 待提交文件：

```bash
git status --short
git diff --cached --stat
git diff --cached
```

必须在确认文件范围、大小和内容后再执行 `git push`。
