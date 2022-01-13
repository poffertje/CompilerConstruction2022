.PHONY: all
all: deps passes

# dependencies

.PHONY: deps
deps: lib/.bootstrapped
	@if ! which frontend; then \
		echo "PATH incorrect - make sure the virtualenv is activated!"; \
		echo "Run 'source shrc' and try running make again"; \
		exit 1; \
	fi

lib/.bootstrapped: | bootstrap.sh
	bash bootstrap.sh
	touch $@

# LLVM passes

.PHONY: passes
passes: deps
	$(MAKE) -C llvm-passes

# Runtime with helper functions

.PHONY: runtime
runtime: deps
	$(MAKE) -C runtime

# tests

.PHONY: check-frontend check-passes
check-frontend: deps
	$(MAKE) -C frontend check

check-passes: passes runtime
	$(MAKE) -C llvm-passes check

# full program examples

.PHONY: examples example-%
examples: passes runtime
	$(MAKE) -BC examples

example-%: passes runtime
	$(MAKE) -BC examples bin/$*

# cleanup

.PHONY: clean
clean:
	rm -f bootstrap.log $(DIST_FILE).tar.gz
	$(MAKE) -C llvm-passes clean
	$(MAKE) -C runtime clean
	$(MAKE) -C examples clean

.PHONY: cleaner
cleaner: clean
	rm -rf lib
	rm -f handin-1.tar.gz handin-2.tar.gz handin-3.tar.gz

.PHONY: handin-1 handin-2 handin-3

handin-1:
	echo "Creating tarball for assignment 1"
	tar -cvz --exclude='__pycache__' --exclude='*.pyc' -f handin-1.tar.gz frontend

handin-2:
	echo "Creating tarball for assignment 2"
	tar -cvz --exclude='*.o' --exclude='obj/' -f handin-2.tar.gz llvm-passes

handin-3:
	echo "Creating tarball for assignment 3"
	tar -cvz --exclude='*.o' --exclude='obj/' -f handin-3.tar.gz llvm-passes runtime
