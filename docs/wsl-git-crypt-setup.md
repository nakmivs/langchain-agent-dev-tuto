# WSL 环境配置 git-crypt 解密指南

本仓库使用 git-crypt 加密 `.env` 文件。在新电脑（WSL）上 clone 仓库后，需要以下步骤来解锁加密文件。

## 前提条件

- 已安装 WSL（Ubuntu）
- 已将 GPG 私钥文件 `gpg-private-key.asc` 通过安全方式传输到 WSL 中

## 步骤

### 1. 安装依赖

```bash
sudo apt update && sudo apt install -y git-crypt gnupg
```

### 2. 导入 GPG 私钥

将 `gpg-private-key.asc` 复制到 WSL 中，然后导入：

```bash
gpg --import gpg-private-key.asc
```

验证导入成功：

```bash
gpg --list-secret-keys --keyid-format=long
```

应看到类似输出：

```
sec   rsa4096/1B52F28624AE313F 2026-03-15 [SCEAR]
      3749D00D29F3ADFD9D98C7EF1B52F28624AE313F
uid                 [unknown] nakmi <1770379469@qq.com>
```

### 3. 信任密钥

导入后密钥默认为 `[unknown]` 信任级别，需要手动设置为信任：

```bash
gpg --edit-key 1B52F28624AE313F
```

在交互界面中输入：

```
trust
5
y
quit
```

### 4. Clone 并解锁仓库

```bash
git clone git@github.com:nakmivs/langchain-agent-dev-tuto.git
cd langchain-agent-dev-tuto
git-crypt unlock
```

解锁后 `.env` 文件会自动变为明文，后续的 pull/push 操作中加解密完全透明。

### 5. 验证

```bash
cat .env
```

应能看到完整的明文 API Key 内容。

```bash
git-crypt status .env
```

应输出：`encrypted: .env`

## 常见问题

### Q: git-crypt unlock 失败，提示 "no secret key"

确保 GPG 私钥已正确导入且信任级别为 ultimate：

```bash
gpg --list-secret-keys
```

如果没有输出，说明私钥未导入，重新执行步骤 2。

### Q: 如何安全传输 GPG 私钥到 WSL？

推荐方式（选其一）：

1. **USB 存储**：将 `gpg-private-key.asc` 放在 U 盘中，在 WSL 中通过 `/mnt/` 访问
2. **密码管理器**：将私钥内容存入 1Password / Bitwarden 等工具的安全笔记
3. **局域网传输**：通过 `scp` 或共享文件夹传输（避免通过互联网明文传输）

### Q: 新增了其他需要加密的文件怎么办？

编辑仓库根目录的 `.gitattributes`，添加新的加密规则：

```
.env filter=git-crypt diff=git-crypt
secret.yaml filter=git-crypt diff=git-crypt
```

然后正常 `git add` 和 `git commit` 即可。
