CXX	?= g++
SRC 	 = toml.cpp
TARGET   = toml.o
CXXFLAGS = -I../../include -std=$(CXXSTD)

all: $(TARGET)

$(TARGET):
	${CXX} $(SRC) $(CXXFLAGS) -c -o ../../$(BUILDDIR)/$@

clean:
	rm -rf ../../$(BUILDDIR)/toml++/$(TARGET)

.PHONY: $(TARGET) clean all
