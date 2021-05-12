.PHONY: all install

all:
	@echo
	@echo "To install type 'make install'"
	@echo

install:
	pip3 install questionary
	cp commit-generator.py ~/.local/bin/commit
	cp commit-config.json ~/.local/share