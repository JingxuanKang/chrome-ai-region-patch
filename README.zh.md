# Chrome AI Region Patch

一个用于修补 Chrome 本地地区资格字段的小脚本，可用于恢复 Gemini in Chrome、AI 历史搜索、DevTools AI 等内置 AI 入口。

这是一个 macOS 优先、零第三方依赖的 Python 脚本。它只修改 Chrome 本地的 `Local State` JSON 文件，写入前会自动创建带时间戳的备份；不安装扩展、不上传数据、不依赖外部服务。

> 状态：这是非官方的本地 workaround。Chrome 和 Google 服务端资格规则可能变化，即使本地补丁成功，浏览器入口也可能需要一段时间才恢复。

## 快速开始

```bash
git clone https://github.com/JingxuanKang/chrome-ai-region-patch.git
cd chrome-ai-region-patch
python3 chrome_ai_region_patch.py --force-kill
```

`--force-kill` 只在 Chrome 无法正常退出时使用。脚本默认会先让 macOS 正常退出 Chrome，补丁完成后再重新打开。

只检查不写入：

```bash
python3 chrome_ai_region_patch.py --dry-run
```

指定某个 Chrome 用户数据目录：

```bash
python3 chrome_ai_region_patch.py --profile-dir "~/Library/Application Support/Google/Chrome"
```

## 它修改什么

脚本会打开 Chrome 用户数据目录下的 `Local State`，然后：

- 将所有 `is_glic_eligible` 设为 `true`；
- 默认将 `variations_country` 设为 `us`；
- 将 `variations_permanent_consistency_country` 设为 `[<Chrome app version>, "us"]`；
- 保存前创建带时间戳的备份。

macOS 上 Chrome 用户数据目录通常是：

```text
~/Library/Application Support/Google/Chrome
```

如果本机存在 Chrome Beta、Dev、Canary profile，脚本也会一并检查。

## 为什么更新后 Ask Gemini 会消失

Chrome 更新或重启后可能重写 `Local State`。实际表现通常是地区字段恢复到真实地区，例如 `gb`，即使 `is_glic_eligible` 仍然是 `true`。

这时重新运行：

```bash
python3 chrome_ai_region_patch.py --force-kill
```

如果 Chrome 刚更新，脚本会优先读取已安装 Chrome app bundle 的真实版本号，而不是只相信 profile 中可能滞后的 `Last Version` 文件。

## 相似项目

这个仓库不是原创发现底层 workaround，而是把日常使用需要的部分整理成更小、更容易审计、适合 Chrome 更新后反复运行的 macOS 脚本。

- [`lcandy2/enable-chrome-ai`](https://github.com/lcandy2/enable-chrome-ai)：主要上游 Python 实现，支持多平台和多个 Chrome 渠道，但依赖 `psutil`，并使用 profile 里的 `Last Version`。
- [`appsail/Gemini-in-Chrome`](https://github.com/appsail/Gemini-in-Chrome)：面向 macOS、Linux、Windows 的一键 shell / PowerShell 脚本。
- [`tianlanyb/Gemini-in-Chrome`](https://github.com/tianlanyb/Gemini-in-Chrome)：另一个面向非美国用户的一键脚本集合。
- [`gemini-unlock`](https://lib.rs/crates/gemini-unlock)：同一问题空间里的 Rust 工具。
- 还有不少论坛和教程会指导手动编辑 `Local State`。

本项目刻意收窄范围：零第三方 Python 依赖、自动时间戳备份、支持 dry-run、macOS 上优先读取 Chrome app bundle 版本、不硬编码个人路径。

## 参数

```text
--country CODE       要写入的国家代码，默认 us
--channels ...       macOS 下要修补的渠道：stable beta dev canary
--profile-dir PATH   只修补指定用户数据目录
--dry-run            只显示计划修改，不写文件
--no-restart         修补后不重新打开 Chrome
--force-kill         正常退出失败时强制结束 Chrome
```

## 隐私

脚本只读写 Chrome 本地配置文件。它不会上传数据，也不会读取浏览历史、cookies、保存的密码、书签或扩展数据。

仓库内容刻意避免写入机器专属路径、用户名、token、主机名和个人 profile 内容。

## English

English documentation is the default. See [README.md](README.md).

## 致谢

本项目基于 [`lcandy2/enable-chrome-ai`](https://github.com/lcandy2/enable-chrome-ai) 的 Local State 补丁思路，该项目使用 MIT License 发布。详见 [NOTICE.md](NOTICE.md)。

## 许可证

MIT。详见 [LICENSE](LICENSE)。
