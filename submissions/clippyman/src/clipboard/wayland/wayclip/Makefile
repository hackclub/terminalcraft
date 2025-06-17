.POSIX:
TARGET = libwayclip.a
LIB = -lwayland-client
OBJ_COMMON = protocol/wlr-data-control-unstable-v1.o common.o

DEBUG ?= 1
ifeq ($(DEBUG),1)
	CFLAGS = -g -O0
endif

all: $(TARGET)

$(TARGET): waycopy.o waypaste.o $(OBJ_COMMON)
	$(AR) rcs $(TARGET) waycopy.o waypaste.o $(OBJ_COMMON)
	ranlib $(TARGET)
	mv -f $(TARGET) ../../../../$(BUILDDIR)/$(TARGET)

waycopy.o: waycopy.c common.h protocol/wlr-data-control-unstable-v1-client-protocol.h

waypaste.o: waypaste.c common.h protocol/wlr-data-control-unstable-v1-client-protocol.h

protocol/wlr-data-control-unstable-v1.c: protocol/wlr-data-control-unstable-v1.xml
	wayland-scanner private-code protocol/wlr-data-control-unstable-v1.xml $@

protocol/wlr-data-control-unstable-v1-client-protocol.h: protocol/wlr-data-control-unstable-v1.xml
	wayland-scanner client-header protocol/wlr-data-control-unstable-v1.xml $@

.c.o:
	$(CC) -Wall -Wpedantic $(CFLAGS) -c $< -o $@ -Wl,--whole-archive

install:
	install -Dm755 -t $(DESTDIR)$(PREFIX)/bin $(EXE)

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/waycopy $(DESTDIR)$(PREFIX)/bin/waypaste

clean:
	rm -f *.o $(TARGET) protocol/*.[och]
