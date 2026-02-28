# Default values if not provided via command line
REPO ?= .
PDF ?=

.PHONY: detectives graph report help

# 1. Run only the detectives node
detectives:
	uv run python -m src.nodes.run_detectives --repo "$(REPO)" --pdf "$(PDF)"

# 2. Run the full Graph pipeline
graph:
	uv run python -m src.graph "$(REPO)" "$(PDF)"

# 3. Run the full pipeline and save output to a file
report:
	uv run python -m src.graph "$(REPO)" "$(PDF)" > audit_output.log
	@echo "Audit log saved to audit_output.log"

# 4. Helper to see how to use this Makefile
help:
	@echo "Usage examples:"
	@echo "  make graph REPO=. PDF=reports/interim_report.pdf"
	@echo "  make graph REPO=https://github.com/user/repo"
	@echo "  make report REPO=. PDF=reports/interim_report.pdf"
