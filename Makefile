SHELL := /bin/bash
GTEST_DIR := googletest/googletest
GTEST_HEADERS := $(GTEST_DIR)/include/gtest/*.h $(GTEST_DIR)/include/gtest/internal/*.h
CC := gcc
CFLAGS := -Wall -Wextra -Wpedantic
VENV_DIR := venv
VENV_ACTIVATE := $(VENV_DIR)/bin/activate
PYTHON := python3
PYTEST = $(VENV_DIR)/bin/pytest

$(shell mkdir -p build/gtest)
$(shell git clone https://github.com/google/googletest &> /dev/null)

.PHONY: all clean run-int run-float run-unit-tests run-integration-tests build/unit-tests

all: build/app.exe venv build/unit-tests

clean:
	@echo "Cleaning..."
	@rm -rf build/
	@rm -rf $(VENV_DIR)
	@rm -rf .pytest_cache
	@rm -rf tests/integration/__pycache__
	@rm -rf googletest/

run-int: build/app.exe
	@build/app.exe

run-float: build/app.exe
	@build/app.exe --float

run-integration-tests: build/app.exe venv tests/integration/integrationTests.py
	@source $(VENV_ACTIVATE); $(PYTEST) tests/integration/integrationTests.py

run-unit-tests: build/unit-tests
	@echo "Running unit-tests"
	@build/node_test.exe
	@build/stack_test.exe
	@build/queue_test.exe
	@build/precedence_test.exe
	@build/parse_test.exe
	@build/calculate_test.exe
	@build/cli_test.exe
	@build/print_test.exe

run-gui: venv src/gui.py
	@source $(VENV_ACTIVATE); $(PYTHON) src/gui.py &

run-server: build/app.exe venv src/server/server.py
	@make --no-print-directory kill-server
	@source $(VENV_ACTIVATE); $(PYTHON) src/server/server.py &

kill-server:
	@SERVER_PID=$$(ps aux | grep "[p]ython.*src/server/server.py" | awk '{print $$2}'); if [ -n "$$SERVER_PID" ]; then \
		echo "Stopping server (PID: $$SERVER_PID)..."; \
		kill $$SERVER_PID; \
	fi

build/app.exe: src/main.c
	@echo "Building app.exe..."
	@$(CC) $(CFLAGS) -o build/app.exe src/main.c

build/app-test.o: src/main.c
	@echo "Building app-test.o..."
	@$(CC) $(CFLAGS) -DGTEST -c src/main.c -o build/app-test.o -g

venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV_DIR)
	@source $(VENV_ACTIVATE); pip install --upgrade pip
	@source $(VENV_ACTIVATE); pip install -U pytest
	@source $(VENV_ACTIVATE); pip install -U structlog
	@source $(VENV_ACTIVATE); pip install -U PySide6
	@source $(VENV_ACTIVATE); pip install -U requests

build/unit-tests: build/precedence_test.exe build/stack_test.exe build/queue_test.exe build/parse_test.exe build/calculate_test.exe build/cli_test.exe build/node_test.exe build/print_test.exe

build/precedence_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/precedence_test.cpp
	@echo "Building precedence unit-tests..."
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/precedence_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/precedence_test.exe

build/stack_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/stack_test.cpp
	@echo "Building stack unit-tests..."
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/stack_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/stack_test.exe

build/node_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/node_test.cpp
	@echo "Building node unit-tests..."
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/node_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/node_test.exe

build/cli_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/cli_test.cpp
	@echo "Building cli unit-tests"
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/cli_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/cli_test.exe

build/calculate_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/calculate_test.cpp
	@echo "Building calculate unit-tests..."
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/calculate_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/calculate_test.exe

build/parse_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/parse_test.cpp
	@echo "Building parse unit-tests"
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/parse_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/parse_test.exe -g

build/queue_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/queue_test.cpp
	@echo "Building queue unit-tests..."
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/queue_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/queue_test.exe

build/print_test.exe: build/gtest/gtest_main.a build/app-test.o tests/unit/print_test.cpp
	@echo "Building print unit-tests..."
	@g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/print_test.cpp \
		build/gtest/gtest_main.a build/app-test.o \
		-o build/print_test.exe

####################################
# BUILD GOOGLE TEST STATIC LIBRARY #
####################################
# Google Test object files
build/gtest/gtest-all.o: $(GTEST_DIR)/src/*.cc $(GTEST_DIR)/src/*.h $(GTEST_HEADERS)
	@echo "Building gtest-all libraries..."
	@g++ -isystem $(GTEST_DIR)/include -I$(GTEST_DIR) -c $(GTEST_DIR)/src/gtest-all.cc -o $@

build/gtest/gtest_main.o: $(GTEST_DIR)/src/*.cc $(GTEST_DIR)/src/*.h $(GTEST_HEADERS)
	@echo "Building gtest-main libraries.."
	@g++ -isystem $(GTEST_DIR)/include -I$(GTEST_DIR) -c $(GTEST_DIR)/src/gtest_main.cc -o $@

# Google Test static libraries
build/gtest/gtest_main.a: build/gtest/gtest-all.o build/gtest/gtest_main.o
	@echo "Building gtest static libraries..."
	@ar rv $@ $^ -o $@
