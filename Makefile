.PHONY: all install

all:
	@echo
	@echo "To install type 'make install'"
	@echo

install:
	sudo cp commit-generator.py /usr/local/bin/commit
	cp commit-config.json ~/.local/share

uninstall:
	sudo rm /usr/local/bin/commit