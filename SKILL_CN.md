---
name: pdf-metadata-cleaner
description: 清除 PDF 文件中的隐私元数据（EXIF/XMP/DocInfo/作者/设备标识/扫描软件信息），并移除页面水印文字。当用户要求"清理""去EXIF""去水印""清除元数据""去掉扫描信息"时使用。支持柯尼卡美能达复合机、CamScanner 扫描全能王、WPS、iText 水印、Adobe InDesign 等常见来源。
---

# PDF 元数据与水印清理

## 标准流程

1. **检查**：用 exiftool 查看外壳元数据和 XMP，用 PyMuPDF 检查页数、水印文本。
2. **清理元数据**：`exiftool -all= -o <output> <input>` 清除所有外壳和 XMP。
3. **重构**：PyMuPDF `set_metadata({})` + `garbage=4, deflate=True` 另存。
4. **水印处理**（如有）：PyMuPDF `search_for` + `add_redact_annot` + `apply_redactions`。
5. **验证**：exiftool 复查无残留，渲染首尾页确认非白。

## 工具依赖

- **exiftool**：需自行安装并加入 PATH，下载地址 [exiftool.org](https://exiftool.org/)。
- **PyMuPDF**：`pip install pymupdf`
- **清理脚本**：`scripts/clean_pdf.py <input> [output]`

## 关键禁忌（已验证的教训）

- **不要**用 Pillow 重编码 PDF 内嵌 JPEG 后通过 PyMuPDF `update_stream` 替换流——会导致对象字典不匹配，页面白屏黑条。
- **不要**仅用 PyMuPDF `set_metadata({})`——它只清 Info 字典，不清 XMP 流。必须先用 exiftool `-all=`，再 `garbage=4` 重构。
- 内嵌图片流**原封不动**，不重编码。

## 常见水印模式

| 来源 | 水印特征 | 处理方式 |
|---|---|---|
| CamScanner/扫描全能王 | "扫描全能王 创建"（每页底部） | `search_for("扫描全能王")` 后 redact |
| iText 账号水印 | 重复网格的"部门:用户名"，含截断变体 | 搜索短而稳定的子串（如拼音/用户名片段）匹配所有变体 |
| 柯尼卡美能达复合机 | JPEG Comment 字段含 `KM_<型号>` | `exiftool -Comment=` 无损移除（为空则跳过） |
| WPS 文字 | Author 字段含真实姓名 | exiftool `-all=` 自动清除 |

## 输出命名

- 默认使用原文件名输出；用户指定名称时按用户要求。
