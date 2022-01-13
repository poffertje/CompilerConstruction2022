# Run 'make V=1' for verbose commands (default: V=0)
ifeq ($(V),1)
override V =
else
override V = @
endif

# Run these passes before applying user-specified passes, to normalize IR
OPTPREP := -alloca-hoisting -mem2reg

# All compiled files of the runtime
RUNTIMEDIR := ../runtime
RUNTIME := $(wildcard $(RUNTIMEDIR)/obj/*.ll)

# Binaries for building steps
FRONTEND := frontend
LLINK    := llvm-link
LLC      := llc
OPT      := myopt
LD       := clang

OBJDIR ?= ./obj
BINDIR ?= ./bin
SRCS := $(wildcard *.fc)
BINS := $(patsubst %.fc,$(BINDIR)/%,$(SRCS))

all: $(BINS)

# Disable built-in rules.
.SUFFIXES:

# Preserve all intermediate (.ll) files.
.PRECIOUS: $(OBJDIR)/%-1frontend.ll $(OBJDIR)/%-2prep.ll \
	$(OBJDIR)/%-3opt.ll $(OBJDIR)/%-4runtime.ll $(OBJDIR)/%.o

$(OBJDIR)/%-1frontend.ll: %.fc | $(OBJDIR)
	$(V) $(FRONTEND) -o $@ $< -I $(RUNTIMEDIR)
$(OBJDIR)/%-2prep.ll: $(OBJDIR)/%-1frontend.ll
	$(V) $(OPT) -o $@ $< $(OPTPREP)
$(OBJDIR)/%-3opt.ll: $(OBJDIR)/%-2prep.ll
	$(OPT) -o $@ $< $(PASSES)
$(OBJDIR)/%-4runtime.ll: $(OBJDIR)/%-3opt.ll
	$(V) $(LLINK) -o $@ $< $(RUNTIME)
# TODO: force inlining of runtime (helpers) here?
$(OBJDIR)/%.o: $(OBJDIR)/%-4runtime.ll
	$(V) $(LLC) -filetype=obj -o $@ $<
$(BINDIR)/%: $(OBJDIR)/%.o | $(BINDIR)
	$(V) $(LD) -o $@ $^

$(OBJDIR):
	$(V) mkdir -p $@
$(BINDIR):
	$(V) mkdir -p $@

clean:
	$(V) rm -rf $(OBJDIR) $(BINDIR)

