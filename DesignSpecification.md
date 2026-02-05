# VeriCite CLI: Next-Gen Academic Integrity Linter

**Slogan:** "Context-Aware Verification for the AI Era."

**定位:** 一个集成下一代 Visual-Language OCR 技术的命令行工具，专注于从复杂排版（双栏、多图表）的学术文档中精准提取并验证引用真实性。

---

## 1. 核心价值 (Core Value Proposition)

VeriCite 不做"润色"，只做"查毒"。它利用最新的视觉大模型（VLM）技术，像人类阅读一样理解文档布局，精准剥离参考文献，通过权威数据库（Crossref/Semantic Scholar）验证是否存在"大模型幻觉"。

---

## 2. 用户故事 (User Stories)

### 场景 A (隐私敏感)
Alice 在本地撰写一篇涉及未公开数据的论文。她使用 `vericite scan draft.pdf --engine local`，利用内置的轻量级 PaddleOCR-VL 模型在不联网上传内容的情况下完成检查。

### 场景 B (复杂排版)
Bob 下载了一篇 1980 年代的扫描版双栏论文，排版混乱。他使用 `vericite scan paper.pdf --engine cloud`，调用 DeepSeek-OCR 2 的 API，利用其"视觉因果流"技术完美还原了阅读顺序，找出了断行的引用。

---

## 3. 功能特性 (Features)

### 3.1 v0.1 MVP (核心功能)

- [x] **智能切片 (Smart Slicing)**: 自动识别并只提取 "References/Bibliography" 页面（大幅节省计算资源）。
- [x] **双引擎解析 (Hybrid Parsing)**:
  - **Local (默认)**: 集成 PaddleOCR-VL (0.9B)，实现毫秒级、离线的本地解析。
  - **Cloud (高精)**: 集成 DeepSeek-OCR / GLM-OCR API，用于处理难以识别的扫描件。
- [x] **权威验证**: Crossref (DOI) + Semantic Scholar (Title) 双重校验。
- [x] **终端可视化报告**: 使用 Rich 库展示 🟢 Pass / 🔴 Fail / 🟡 Warn。

### 3.2 v1.0 规划

- [ ] **视觉定位**: 在 PDF 原文中高亮显示虚假的引用位置（Annotate PDF）。
- [ ] **幻觉修正**: 基于 RapidFuzz 模糊匹配，提示"你是不是想引用...？"

---

## 4. 关键技术革新 (Technical Innovations)

### 4.1 基于"视觉因果流"的排版解析 (Visual Causal Flow Parsing)

传统 OCR 经常把双栏论文的左栏第一行和右栏第一行拼在一起。VeriCite 引入 DeepSeek-OCR 2 的视觉因果流 (Visual Causal Flow) 概念：

- **原理**: 不再按像素扫描，而是基于语义逻辑（Semantic Logic）重排 Token。
- **应用**: 确保引用列表中的 `[1]` 及其对应的多行文本被作为一个完整的语义块读取，而不是被打断的碎片。

&gt; **技术验证**: DeepSeek-OCR 2 采用 DeepEncoder-V2（基于 Qwen2-0.5B 的语言模型式视觉编码器），在 OmniDocBench v1.5 上取得 91.09 分，阅读顺序错误率（Edit Distance）从 0.085 降至 0.057[^22^][^20^]。

### 4.2 混合 OCR 架构 (Hybrid OCR Architecture)

为了平衡隐私/速度与精度，VeriCite 采用动态路由策略：

| 引擎类型 | 选型模型 | 适用场景 | 优势 |
|---------|---------|---------|-----|
| **Local (速度)** | PaddleOCR-VL (0.9B) | 电子版 PDF、清晰截图、隐私文档 | 极速 (比 MinerU 快 14%)，隐私 (本地推理)，显存占用低。 |
| **Cloud (精度)** | DeepSeek-OCR 2 / GLM-OCR | 古旧扫描件、手写笔记、复杂公式 | SOTA 精度 (OmniDocBench 第一)，利用 MTP 技术精准识别特殊符号。 |

&gt; **技术验证**: PaddleOCR-VL 采用两阶段架构（PP-DocLayoutV2 布局分析 + PaddleOCR-VL-0.9B 元素识别），在 A100 上处理速度达 1.22 页/秒，支持 109 种语言，显存占用 &lt;8GB[^21^][^24^]。

```
# 建议的智能路由（三级降级）
def smart_routing(pdf_path, user_preference="auto"):
    # Level 1: 用户强制选择
    if user_preference in ["local", "cloud"]:
        return user_preference
    
    # Level 2: 自动判断文档质量
    quality_score = assess_document_quality(pdf_path)
    
    if quality_score > 0.8:  # 清晰的电子版 PDF
        return "local"
    elif quality_score > 0.5:  # 扫描件但质量尚可
        # 先尝试 Local，如果失败再用 Cloud
        try:
            result = local_ocr(pdf_path)
            if result.confidence > 0.7:
                return "local"
        except:
            pass
        return "cloud"
    else:  # 质量很差（模糊、倾斜、手写）
        return "cloud"

def assess_document_quality(pdf_path):
    """快速评估文档质量（避免完整 OCR）"""
    sample_page = extract_page(pdf_path, page=0)
    
    # 检查是否有文本层（电子版 vs 扫描件）
    has_text_layer = len(sample_page.get_text()) > 100
    
    # 检查图像清晰度（如果是扫描件）
    if not has_text_layer:
        image = page_to_image(sample_page)
        sharpness = calculate_laplacian_variance(image)
        return sharpness / 1000  # 归一化到 0-1
    
    return 1.0  # 电子版默认高质量
```

**优势**：
- 用户不需要理解技术细节（auto 模式自动优化）
- 节省成本（只在必要时调用 Cloud API）
- 更好的用户体验（"它就是知道该怎么做"）
---

## 5. 技术栈决策 (Tech Stack)

| 模块 | 选型 | 理由 |
|-----|-----|-----|
| **语言** | Python 3.10+ | AI 工程首选。 |
| **CLI 框架** | Typer | 现代 CLI 标准。 |
| **PDF 处理** | PyMuPDF (fitz) | 用于快速提取页面图像和定位关键词。 |
| **本地 OCR** | PaddleOCR (v2.7+) | 0.9B 参数量适合在用户笔记本上跑，支持中英混排。 |
| **云端 VLM** | OpenAI Compatible API | 兼容 DeepSeek/GLM 的 API 接口调用。 |
| **文本比对** | RapidFuzz | 验证引用标题相似度。 |

---

## 6. 核心处理流程 (Pipeline Logic)

```mermaid
graph TD
    A[Input: paper.pdf] --&gt; B{Strategy Check};
    B -- "Mode: Local (Default)" --&gt; C[PyMuPDF Rasterize];
    C --&gt; D[PaddleOCR-VL Inference];
    B -- "Mode: Cloud" --&gt; E[Upload Image to DeepSeek/GLM API];
    D --&gt; F[JSON Extraction];
    E --&gt; F;
    F --&gt; G[Validation (Crossref/Web)];
    G --&gt; H[Output Report];

```

```
Step 1: 定位 (Locate)
扫描 PDF 文本层，寻找 Reference 关键词。截取该页及之后的所有页面为图像（300 DPI）。
可能存在问题：

老旧扫描件没有文本层，只有图像
有些论文用 "Bibliography" 或 "Works Cited" 而非 "References"
arXiv 预印本可能把参考文献放在附录（Appendix）
```

优化方案：
```
# 更鲁棒的检测策略
REFERENCE_KEYWORDS = [
    "References", "Bibliography", "Works Cited", 
    "Literature Cited", "参考文献", "引用文献"
]
def locate_references(pdf_path):
    # 方法 1: 尝试从文本层提取
    text_pages = extract_text_layer(pdf_path)
    for i, page in enumerate(text_pages):
        if any(kw in page for kw in REFERENCE_KEYWORDS):
            return i
    
    # 方法 2: 如果文本层失败，OCR 前几页和后几页
    # 参考文献通常在最后 10% 的页面
    total_pages = get_page_count(pdf_path)
    start_scan = int(total_pages * 0.9)
    for i in range(start_scan, total_pages):
        ocr_result = light_ocr(pdf_path, page=i)
        if any(kw in ocr_result for kw in REFERENCE_KEYWORDS):
            return i
    
    # 方法 3: 启发式规则（密度检测）
    # 参考文献页面通常字体更小、行间距更紧
    return detect_by_text_density(pdf_path)
```

```
Step 2: 视觉解析 (Visual Parse)
Local 模式: 运行本地 PaddleOCR-VL 权重。
Prompt: "Recognize text boxes and sort by reading order."
Cloud 模式: 发送图片至 DeepSeek API。
prompt = """
You are a precision OCR system for academic citations. Extract ONLY the reference list from this image.

RULES:
1. Each reference should be a complete bibliographic entry (author, title, venue, year)
2. Maintain the EXACT reading order as it appears in the document
3. For multi-column layouts, read LEFT column fully before moving to RIGHT column
4. Preserve ALL special characters (accents, em-dashes, etc.)
5. If a reference spans multiple lines, merge them into a single entry

OUTPUT FORMAT (JSON):
[
  {
    "index": 1,
    "raw_text": "Smith, J. (2020). Title of Paper. Journal of AI, 15(3), 123-145.",
    "confidence": 0.95
  }
]

DO NOT include page headers, footers, or footnotes.
"""
```

```
Step 3: 验证 (Verify)
并发请求 Crossref API。计算 Similarity Score。
```

## 7.开发计划与注意事项 (Development Plan)
### Cloud 模式的 API 选择过于激进
计划"OpenAI Compatible API"来兼容 DeepSeek/GLM，但有几个问题：

DeepSeek-OCR 2 的 API 尚未公开：DeepSeek-OCR 2 的论文已发表，但商业 API 可能还未开放 SPY Lab
GLM-OCR 的定价未知：智谱可能收费很高
API 稳定性风险：初创公司的 API 可能有中断

建议：

Phase 1（MVP）：Cloud 模式暂时只支持 Mistral OCR 或 GPT-4o（成熟、稳定、有 SLA）
Phase 2（扩展）：等 DeepSeek/GLM 的 API 稳定后再集成
备用方案：Mistral OCR 每 1000 页只需 $1，且处理速度达 2000 页/分钟

### 智能降级"机制

部署复杂度：PaddleOCR-VL 需要两个模型（PP-DocLayoutV2 + PaddleOCR-VL-0.9B）
显存需求：虽然只需 <8GB，但用户的笔记本可能没有 GPU
首次启动慢：下载模型权重可能需要几分钟

解决方案:
```
# 添加一个"智能降级"机制(注意与前文提到的智能路由不同)
def get_ocr_engine():
    if has_gpu() and gpu_memory() > 8GB:
        return PaddleOCRVL()  # 最优方案
    elif has_gpu() and gpu_memory() > 4GB:
        return PaddleOCRVLLite()  # 简化版
    else:
        return TesseractFallback()  # CPU 降级方案
```