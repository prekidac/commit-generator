.PHONY: all install

all:
	@echo
	@echo "To install type 'make install'"
	@echo

install:
	sudo mkdir -p /usr/local/share/commit-generator
	sudo cp commit-generator.py /usr/local/share/commit-generator
	cp commit-config.json ~/.local/share
	sudo ln -s /usr/local/share/commit-generator/commit-generator.py /usr/local/bin/commit