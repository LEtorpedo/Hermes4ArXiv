.PHONY: help install run clean validate-env

help: ## 显示帮助信息
	@echo "🚀 Hermes4ArXiv - ArXiv论文自动追踪器"
	@echo "GitHub Actions专用配置"
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# 📦 依赖管理
# =============================================================================

install: ## 安装依赖
	uv sync

update-deps: ## 更新依赖
	uv lock --upgrade

# =============================================================================
# 🔧 配置和验证
# =============================================================================

validate-env: ## 验证环境变量配置
	uv run scripts/validate_env.py

configure: ## 运行配置助手
	uv run scripts/configure_analysis.py

# =============================================================================
# 🏃 程序运行（主要用于GitHub Actions）
# =============================================================================

run: ## 运行论文分析（GitHub Actions中使用）
	cd src && uv run python main.py

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