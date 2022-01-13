LLVMCONF ?= llvm-config
CXX     := g++
PREFIX  := $(shell $(LLVMCONF) --prefix)
CFLAGS  := -Wall -Werror -g3 -fPIC $(subst $(PREFIX),'$(PREFIX)',$(shell $(LLVMCONF) --cxxflags)) -O0
UNAME_S := $(shell uname -s)
LDFLAGS := -g3 -shared $(subst $(PREFIX),'$(PREFIX)',$(shell $(LLVMCONF) --ldflags))
ifeq ($(UNAME_S), Darwin)
LDFLAGS += -Wl,-headerpad_max_install_names -undefined dynamic_lookup
endif
OBJDIR  ?= ./obj

OBJS    := $(wildcard *.cpp)
OBJS    := $(patsubst %.cpp,$(OBJDIR)/%.o,$(OBJS))

LIB     := libllvm-passes.so


.PHONY: all clean passes check

passes: $(OBJDIR)/$(LIB)

all: passes

check: passes
	@bash tests/run.sh

$(OBJDIR)/$(LIB): $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $^

$(OBJDIR)/%.o: %.cpp | $(OBJDIR)
	$(CXX) -c $(CFLAGS) -o $@ $<

$(OBJDIR):
	mkdir -p $@

clean:
	rm -rf $(OBJDIR)
