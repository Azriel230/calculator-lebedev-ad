GTEST_DIR ?= googletest/googletest
GTEST_HEADERS = $(GTEST_DIR)/include/gtest/*.h $(GTEST_DIR)/include/gtest/internal/*.h
PYTHON := python3
PIP := pip3
VENV_NAME := venv
VENV_ACTIVATE := $(VENV_NAME)/bin/activate
VENV_PYTHON := $(VENV_NAME)/bin/python
VENV_PIP := $(VENV_NAME)/bin/pip
PYTEST := $(VENV_NAME)/bin/pytest
BUILD := build

$(shell mkdir -p build/gtest)
$(shell git clone https://github.com/google/googletest &> /dev/null)

.PHONY: all clean run-int run-float run-unit-test run-integration-tests

all: build/app.exe build/unit-tests.exe

clean:
	rm -rf build
	rm -rf $(VENV_NAME)

# Run the normal C application
run-int: build/app.exe
	build/app.exe

# Run the normal C application with floating point numbers
run-float: build/app.exe
	build/app.exe --float

# Run all tests
run-unit-tests: build/app.exe build/unit-tests.exe
	build/unit-tests.exe

# Create virtual environment if it doesn't exist
venv: check-venv
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_NAME); \
	fi

run-integration-tests: build/app.exe install-deps
	source $(VENV_NAME)/bin/activate; $(PYTEST) tests/integration/integrationTests.py

# Check if venv module is available
check-venv:
	@$(PYTHON) -c "import venv" 2>/dev/null || (echo "python3-venv not found. Installing..." && sudo apt update && sudo apt install -y python3-venv)

# Install dependencies in virtual environment
install-deps: venv
	@echo "Installing dependencies..."
	@. $(VENV_ACTIVATE) && $(VENV_PIP) install --upgrade pip
	@. $(VENV_ACTIVATE) && $(VENV_PIP) install pytest

build/app.exe:
	gcc src/main.c -o build/app.exe -Wall -Wextra -Wpedantic -Werror -std=c11

build/app-test.o:
	gcc -DGTEST -c src/main.c -o build/app-test.o

build/unit-tests.exe: build/gtest/gtest_main.a build/app-test.o
	g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/validate_input_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/unit-tests.exe

####################################
# BUILD GOOGLE TEST STATIC LIBRARY #
####################################

# Google Test object files
build/gtest/gtest-all.o: $(GTEST_DIR)/src/*.cc $(GTEST_DIR)/src/*.h $(GTEST_HEADERS)
	g++ -isystem $(GTEST_DIR)/include -I$(GTEST_DIR) -c $(GTEST_DIR)/src/gtest-all.cc -o $@

build/gtest/gtest_main.o: $(GTEST_DIR)/src/*.cc $(GTEST_DIR)/src/*.h $(GTEST_HEADERS)
	g++ -isystem $(GTEST_DIR)/include -I$(GTEST_DIR) -c $(GTEST_DIR)/src/gtest_main.cc -o $@

# Google Test static libraries
build/gtest/gtest_main.a: build/gtest/gtest-all.o build/gtest/gtest_main.o
	ar rv $@ $^ -o $@