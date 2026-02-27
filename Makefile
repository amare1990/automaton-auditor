detectives:
	python scripts/run_detectives.py

graph:
	python -m src.graph $(REPO) $(PDF)

report:
	python -m src.graph $(REPO) $(PDF) > audit.md


# Demo easily
# make graph REPO=https://github.com/... PDF=report.pdf
