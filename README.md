# calculator-lebedev-ad

This project is a simple calculator program written in C. It reads an arithmetic expression from standard input, parses
it, and prints the result. The program supports the following operators on integers: `+`, `-`, `*`, `/`, `(`, and `)`.

## Building the Program

To build the program, you need a C compiler such as `gcc` or `clang`. Follow these steps:

1. Open a terminal.
2. Navigate to the directory containing the source code (`main.c`).
3. Run the following command to compile the program:

```sh
gcc main.c -o calculator.exe
```

This will create an executable file named `calculator.exe`.

## Running the Program

To run the program, use the following command:

```sh
./calculator.exe
```

The program will prompt you to enter an arithmetic expression. After entering the expression, press `Enter` and then
`Ctrl+D` to see the result.

## Formatting the C Code

To format the C code according to the WebKit style, you can use `clang-format`, follow these steps:

1. Ensure you have `clang-format` installed. If not, install it using your package manager.
2. Run the following command to format the code:

```sh
clang-format -i main.c
```

This will format the `main.c` file in place according to the WebKit style.
