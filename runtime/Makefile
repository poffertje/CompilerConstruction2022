CC      := clang
OBJDIR  ?= ./obj
CFLAGS  := -Wall -Werror -g0 -O0 -c -S -emit-llvm

OBJS    := $(wildcard *.c)
OBJS    := $(patsubst %.c,$(OBJDIR)/%.ll,$(OBJS))


.PHONY: all clean

all: $(OBJS)


$(OBJDIR)/%.ll: %.c | $(OBJDIR)
	$(CC) $(CFLAGS) -o $@ $<

$(OBJDIR):
	mkdir -p $@

clean:
	rm -rf $(OBJDIR)
