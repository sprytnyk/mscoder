.PHONY: clean build test icns all

all: build

test:
	uv run pytest

# remake assets/icon.icns, the macOS icon, from assets/icon.ico
icns:
	QT_QPA_PLATFORM=offscreen uv run python scripts/make_icns.py

clean:
	rm -rf build dist __pycache__ icon.iconset
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.spec~" -delete

build:
	uv run pyinstaller mscoder.spec --clean
