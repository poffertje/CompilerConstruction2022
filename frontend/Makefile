CFLAGS :=
LDFLAGS :=

.PHONY: all check clean
.SUFFIXES:

all:

%: %.o
	clang -o $@ $< $(LDFLAGS)

%.o: %.ll
	llc -filetype=obj -o $@ $<

%.ll: %.fc
	frontend $(CFLAGS) -o $@ $<

# Run 'TIMEOUT=<timeout_in_seconds> make check' to kill tests with infinite
# loops. The default is 3 seconds.
check:
	@python3 runtests.py

clean:
	rm -rf parsetab.py parser.out __pycache__ test/tmp*
