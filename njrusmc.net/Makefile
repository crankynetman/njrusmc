# File:    Makefile
# Version: GNU Make 3.81
# Author:  Nick Russo (http://njrusmc.net)
# Purpose: Makefile simplifies all manual regression testing operations.
#          It's useful to run "make" locally before making any commits.

# "make" or "make all" do the same thing, running all targets in sequence
.DEFAULT_GOAL := all
.PHONY: all
all: lint hash atom link

# Perform linting, security checking, and formatting on code files
.PHONY: lint
lint:
	@echo "*** Starting  lint ***"
	ci_scripts/html_lint.sh
	find . -name "*.py" | xargs pylint --jobs 5
	find . -name "*.py" | xargs bandit --verbose
	find . -name "*.py" | xargs black --verbose --line-length 80
	@echo "*** Completed lint ***"

# Published SHA-256 checksums for everything on the site, excluding hidden
# files and website source files (HTML/CSS)
.PHONY: hash
hash:
	@echo "*** Starting  hash ***"
	rm -f ci_scripts/hashes.txt
	find . -type f ! -path "*/\.*" ! -path "./r/*" ! -name "*.html" ! -name "*.css" \
	| xargs sha256sum | tee ci_scripts/hashes.txt
	@echo "*** Completed hash ***"

# Generate Atom XML file for feed subscribers
.PHONY: atom
atom:
	@echo "*** Starting  atom ***"
	python ci_scripts/make_atom.py
	@echo "*** Completed atom ***"

# Test all hyperlinks in the HTML files to ensure they respond
.PHONY: link
link:
	@echo "*** Starting  link ***"
	python ci_scripts/check_links.py "index.html"
	@echo "*** Completed link ***"
