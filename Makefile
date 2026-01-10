.PHONY: clean build all

all: build

clean:
	rm -rf build dist __pycache__ icon.iconset
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.spec~" -delete

build:
	pyinstaller mscoder.spec
