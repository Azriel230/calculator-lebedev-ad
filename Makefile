GTEST_DIR ?= googletest/googletest
GTEST_HEADERS = $(GTEST_DIR)/include/gtest/*.h $(GTEST_DIR)/include/gtest/internal/*.h

$(shell mkdir -p build/gtest)

all: build/app.exe build/unit-tests.exe

clean:
	rm -rf build

# Run the normal C application
run-int: build/app.exe
	build/app.exe

# Run the normal C application with floating point numbers
run-float: build/app.exe
	build/app.exe --float

# Run all tests
run-unit-tests: build/unit-tests.exe
	build/unit-tests.exe

build/app.exe:
	gcc src/main.c -o build/app.exe -Wall -Wextra -Wpedantic -Werror -std=c11

build/app-test.o:
	gcc -DGTEST -c src/main.c -o build/app-test.o

build/unit-tests.exe: build/gtest/gtest_main.a build/app-test.o
	g++ -isystem $(GTEST_DIR)/include -pthread \
		tests/unit/stack_test.cpp \
		tests/unit/operations_test.cpp \
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