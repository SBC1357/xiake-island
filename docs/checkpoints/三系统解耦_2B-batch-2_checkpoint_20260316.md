# 三系统解耦_2B-batch-2_checkpoint_20260316

## 阶段包
**2B-2**: 多疾病领域 PDF 提取与 L3/L4 建设

## 执行时间
2026-03-16 +08:00

## 完成项

### 1. 胃癌 (Gastric Cancer)
- **Raw 层**: 52 PDFs 复制到 `raw/pdf/oncology/gastric_cancer/`
- **子目录**: HER2+胃癌, Claudin18.2阳性, 免疫一线, 晚期二线, 失败的研究
- **L3**: `l3/oncology/gastric_cancer/disease_knowledge.json`
- **L4**: `l4/trastuzumab_deruxtecan_gastric/product_manifest.json`

### 2. 前列腺癌 (Prostate Cancer)
- **Raw 层**: PDFs 复制到 `raw/pdf/oncology/prostate_cancer/`
- **L3**: `l3/oncology/prostate_cancer/disease_knowledge.json`
- **L4**: `l4/pluvicto/product_manifest.json`
- **临床试验**: VISION, PSMAfore, TheraP, ENZA-P

### 3. 失眠 (Insomnia)
- **Raw 层**: 3 PDFs 复制到 `raw/pdf/neurology/insomnia/`
- **L3**: `l3/neurology/insomnia/disease_knowledge.json`
- **L4**: `l4/lemborexant/product_manifest.json`
- **临床试验**: PIONEER 7, SOLSTICE, CHAMPION

### 4. 肺癌 (Lung Cancer)
- **Raw 层**: PDFs 复制到 `raw/pdf/oncology/lung_cancer/`
- **子目录**: NSCLC, SCLC
- **L3**: `l3/oncology/lung_cancer/disease_knowledge.json`
- **L4**: `l4/furmonertinib/product_manifest.json`
- **临床试验**: FURLONG, ASTRUM-005, RATIONALE-312

## 当前统计

| 层级 | 文件数 | 说明 |
|------|--------|------|
| raw/pdf | 77 | 提取的 PDF 文件 |
| l3 | 8 | 疾病知识 JSON |
| l4 | 5 | 产品证据 JSON |

## 产品覆盖

| 产品 | 疾病领域 | 状态 |
|------|----------|------|
| lecanemab | 阿尔茨海默病 | ✅ 已创建 |
| donanemab | 阿尔茨海默病 | ✅ 已创建 |
| trastuzumab_deruxtecan_gastric | 胃癌 | ✅ 已创建 |
| pluvicto | 前列腺癌 | ✅ 已创建 |
| furmonertinib | 肺癌 | ✅ 已创建 |
| lemborexant | 失眠 | ✅ 已创建 |

## P1/P2 Issues
无

## 下一步动作
- 2B-3: 完成血缘记录 (进行中)
- 2B-4: 发布新 release 并验证

## 签名
- 阶段状态: **IN PROGRESS**
- 胃癌: **COMPLETED**
- 前列腺癌: **COMPLETED**
- 失眠: **COMPLETED**
- 肺癌: **IN PROGRESS**