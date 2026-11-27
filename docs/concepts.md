# 100 概念图鉴 · 内容、视觉与出版规范

这是一套长期维护的财报概念百科：**100 个概念详情页 + 1 个总览页**。每页均生成可独立访问的 HTML 和 XML 合法、可离线查看的 SVG；本次 100 并非统计排名，而是编辑选择的学习路径。

## 为什么放在同一个财报网站

- **概念层**：与任何特定公司无关的财务定义、口径提醒、合成数字例子；
- **证据层**：来源于公司公告/PDF 的真实数字、报告期间、原文页码与审阅状态；
- **研究层**：针对某期公司财报的分析、图表与解释，全部基于证据层。

三个层次必须分别存储和渲染。概念例子不能自动流入 \`data/reports/\`；真实披露也不能反过来随意改变普适的定义。

## 文件与 URL 约定

\`\`\`text
data/concepts.json               # 唯一编辑源：10 categories × 10 concepts
schemas/concepts.schema.json     # 机器验证
src/concepts.py                  # 101 静态页与 100 SVG 的编译器、核验器
src/templates/concept-index.html
src/templates/concept-detail.html
src/static/concepts.css
src/static/concepts.js
scripts/validate_concepts.py
tests/test_concepts.py
dist/concepts/index.html
dist/concepts/<concept-id>/index.html
dist/concepts/<concept-id>/assets/concept.svg
dist/concepts/catalog.json
\`\`\`

Canonical URL: \`https://1998x-stack.github.io/financial-report-viz/concepts/<slug>/\`。稳定的 ASCII 英文 slug 不可随意变更；必要时提供静态重定向或保留旧链接。页面 title 为中文概念名，第二行保留英文术语。

## 固定页面结构

1. **概念信息**：学习序号、所在章节、中文名称、英文名、精确简述；
2. **独立 SVG**：针对该概念选择机制图语法，不要用同一张通用柱状图伪装 100 个不同概念；
3. **公式/勾稽**：简洁表达，并说明适用前提；
4. **示意数值**：公开假设输入和结果，标记 *synthetic / illustrative*；
5. **常见误区**：至少一条该概念独有的错误用法；
6. **关联导航**：相关概念、上一/下一章概念、返回图鉴；
7. **可访问和 SEO**：独立 H1、figure alt、SVG title/desc、JSON-LD DefinedTerm、canonical 链接。

视觉语法根据内容选择：会计等式（\`balance\`）、利润桥（\`bridge\`）、两期比较（\`compare\`）、结构比例（\`stack\`）、分子/分母（\`ratio\`）、时序（\`timeline\`）、说明层级（\`layers\`）、三因素拆解（\`tree\`）。\`balance\` 和 \`bridge\` 必须数值勾稽；分母为零的比率禁止渲染。金额与股数等异质单位不会被画为可比较的同一百分比柱图。

## 10 个章节

报表框架 → 收入与业务 → 利润与费用 → 资产与计量 → 负债与权益 → 现金流与营运 → 回报与每股 → 偿债与风险 → 估值基础 → 比较与质量。

每章初始 10 条；将来超过 100 时，**不要默默打乱已有顺序**，应将新增条目放入 \`extended\` 集合或通过版本化迁移更新规则。目前 100 是站点初始里程碑。

## 审校红线

- 不能把非 IFRS/GAAP 指标（EBITDA、FCF、ROIC 等）的单一公式写成所有公司统一会计准则；
- 现金流与利润、归母与合并利润、百分比与百分点、时点与期间、审阅与审计要明确区分；
- 股价、估值倍数、股息率示例都标为**假设值**，不得显示为实时市场价格；
- 不凭空制造论文/法规页码和出处。若日后新增正式准则引用，应核对版本和段落并增加来源字段；
- 不通过编造财报披露的方式“演示”概念。概念教程的所有数值保持合成教学数据标签；
- 如果概念存在 IFRS、US GAAP 或行业差异，应在定义及误区处注明口径差异，不能夸大公式通用性。

## Agent 工作流与核验

首次编辑先阅读 \`AGENTS.md\` 和 [Financial-Visualization SKILL](https://github.com/1998x-stack/Financial-Visualization/blob/main/skills/financial-visualization/SKILL.md)。执行：

\`\`\`bash
python scripts/validate_concepts.py
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/check_site.py
python scripts/browser_qa.py
\`\`\`

CI 应确认 \`dist/concepts/\` **正好 101 个 HTML**，且内含 **100 张独立 SVG**，总览可搜索、分类按钮可键盘使用，移动端只有图卡局部水平滚动，不能发生页面整体横向溢出。将源数据、验证器、SVG 输出方式纳入 code review；生成的 \`dist/\` 不直接改动。

## 后续教育扩展方向

- 关联“真实财报指标与具体概念”时，用显式验证的映射表，而不是模糊文本匹配；
- 财报用户可以从文章指标跳到解释页，再跳回文章；
- 扩展公式里的交互练习时，必须同时测试负数、零分母、不同期间、单位变换；
- 可按章节发布精读路线；不为了页面数量牺牲财务准确性。
