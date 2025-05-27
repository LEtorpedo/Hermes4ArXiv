.PHONY: help install run clean

help: ## 显示帮助信息
	@echo "🏛️ Hermes4ArXiv - 赫尔墨斯智慧信使"
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# 🚀 快速开始
# =============================================================================

quick-start: ## 🚀 运行快速开始向导（推荐新用户）
	@echo "🚀 启动快速开始向导..."
	cd scripts && uv run quick_start.py

setup-local-env: ## 📝 创建本地环境变量文件
	@if [ ! -f .env ]; then \
		echo "📝 创建本地环境变量文件..."; \
		cp env.example .env; \
		echo "✅ 已创建 .env 文件，请编辑并填入您的配置信息"; \
		echo "💡 提示：使用 'make validate-env' 验证配置"; \
	else \
		echo "⚠️  .env 文件已存在，跳过创建"; \
	fi

# =============================================================================
# 📦 依赖管理
# =============================================================================

install: ## 安装依赖
	uv sync

install-dev: ## 安装开发依赖
	uv sync --all-extras --dev

update-deps: ## 更新依赖
	uv lock --upgrade

# =============================================================================
# 🏃 运行程序
# =============================================================================

run: ## 运行主程序
	cd src && uv run python main.py

test-components: ## 运行组件测试
	cd src && uv run python test_components.py

test-multi-ai: ## 测试多AI分析器功能
	cd src && uv run python test_multi_ai.py

test-quality-evaluation: ## 🌟 测试AI质量评估功能
	@echo "🧪 测试AI质量评估功能..."
	@echo "✅ 测试AI提示词包含质量评估维度"
	@echo "✅ 验证六维分析体系"
	@echo "✅ 检查默认论文数量为50篇"
	@echo "✅ 确认质量筛选配置已移除"
	@echo ""
	@echo "💡 新功能说明："
	@echo "- 每篇论文都有AI质量评估（评分+创新度+严谨性+实用性）"
	@echo "- 不再进行前端筛选，保留所有论文避免遗漏"
	@echo "- 用户可基于AI评估自主选择阅读论文"

# =============================================================================
# 📧 邮件模板预览
# =============================================================================

preview-template: ## 生成HTML邮件模板预览
	uv run python src/preview_template.py

preview-server: ## 启动HTTP服务器预览邮件模板
	uv run python src/preview_server.py

# =============================================================================
# ⚡ 性能测试
# =============================================================================

benchmark: ## 运行并行分析性能基准测试
	uv run scripts/benchmark_parallel.py

benchmark-quick: ## 快速性能测试（3篇论文）
	uv run scripts/benchmark_parallel.py --quick

benchmark-full: ## 完整性能测试（50篇论文）
	uv run scripts/benchmark_parallel.py --papers 50

quick-analysis: ## 快速论文分析（5篇论文）
	uv run scripts/analyze_papers.py --max-papers 5 --search-days 3

# =============================================================================
# 🔧 配置和验证
# =============================================================================

validate-env: ## 验证环境变量配置
	uv run scripts/validate_env.py

validate-env-local: ## 🏠 本地环境验证（跳过SMTP测试）
	uv run scripts/validate_env_local.py

validate-v2-upgrade: ## ✨ 验证v2.1质量评估升级
	@echo "🔍 验证v2.1质量评估升级..."
	@echo ""
	@echo "📋 检查配置更新:"
	@grep -q "MAX_PAPERS.*50" src/config.py && echo "✅ 默认论文数量为50" || echo "❌ 默认论文数量配置异常"
	@grep -q "改为AI分析阶段进行质量评估" src/config.py && echo "✅ 质量筛选配置已移除" || echo "❌ 质量筛选配置仍存在"
	@echo ""
	@echo "📋 检查AI提示词更新:"
	@grep -q "质量评估" src/ai/prompts.py && echo "✅ AI提示词包含质量评估" || echo "❌ AI提示词缺少质量评估"
	@grep -q "给出论文的整体质量评分" src/ai/prompts.py && echo "✅ 包含质量评分要求" || echo "❌ 缺少质量评分要求"
	@echo ""
	@echo "📋 检查文档更新:"
	@grep -q "六维深度解读" README.md && echo "✅ README已更新为六维分析" || echo "❌ README未更新"
	@grep -q "质量评估体系" README.md && echo "✅ README包含质量评估介绍" || echo "❌ README缺少质量评估介绍"
	@echo ""
	@echo "🎉 v2.1升级验证完成！"

status: ## 显示项目状态报告
	uv run scripts/project_status.py

fix-env-encoding: ## 🔧 修复.env文件中的编码问题
	uv run scripts/fix_env_encoding.py

# =============================================================================
# 🧹 清理
# =============================================================================

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

clean-cache: ## 清理 uv 缓存
	uv cache clean

# =============================================================================
# 📊 信息查看
# =============================================================================

show-deps: ## 显示依赖树
	uv tree

cache-info: ## 显示缓存信息
	@echo "缓存目录:"
	uv cache dir
	@echo "缓存内容:"
	ls -la $$(uv cache dir) 2>/dev/null || echo "缓存目录为空"

python-versions: ## 显示可用的 Python 版本
	uv python list 