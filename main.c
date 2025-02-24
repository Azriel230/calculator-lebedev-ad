#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define STACK_SIZE 100

int flag_float = 0; // 0 - long, 1 - double

typedef union {
    long int_value;
    double float_value;
} Number;

typedef struct {
    Number data[STACK_SIZE];
    int top;
} Stack;

void initializeStack(Stack* stack) {
    stack->top = -1;
}

int isEmptyStack(Stack* stack) {
    return stack->top == -1;
}

int isFullStack(Stack* stack) {
    return stack->top == STACK_SIZE - 1;
}

void pushStack(Stack* stack, Number item) {
    if (!isFullStack(stack)) {
        stack->top++;
        stack->data[stack->top] = item;
    } else {
        printf("Push error! Stack is full.\n");
    }
}

Number popStack(Stack* stack) {
    if (!isEmptyStack(stack)) {
        Number top_item = stack->data[stack->top];
        stack->top--;
        return top_item;
    } else {
        printf("Pop error! Stack is empty.\n");
        Number empty = {0};
        return empty;
    }
}

Number peekStack(Stack* stack) {
    if (!isEmptyStack(stack)) {
        return stack->data[stack->top];
    } else {
        printf("Peek error! Stack is empty.\n");
        Number empty = {0};
        return empty;
    }
}

int priorityOperations(char oper) {
    switch (oper) {
        case '+':
        case '-':
            return 1;
        case '*':
        case '/':
            return 2;
        default:
            return 0;
    }
}

Number applyOperation(Number a, Number b, char oper) {
    Number result = {0};
    if (flag_float) {
        switch (oper) {
            case '+': result.float_value = a.float_value + b.float_value; break;
            case '-': result.float_value = a.float_value - b.float_value; break;
            case '*': result.float_value = a.float_value * b.float_value; break;
            case '/':
                if (b.float_value != 0) {
                    result.float_value = a.float_value / b.float_value;
                } else {
                    printf("Operation error! Division by zero!\n");
                }
                break;
        }
    } else {
        switch (oper) {
            case '+': result.int_value = a.int_value + b.int_value; break;
            case '-': result.int_value = a.int_value - b.int_value; break;
            case '*': result.int_value = a.int_value * b.int_value; break;
            case '/':
                if (b.int_value != 0) {
                    result.int_value = a.int_value / b.int_value;
                } else {
                    printf("Operation error! Division by zero!\n");
                }
                break;
        }
    }
    return result;
}

Number calculatingExpression(char* input) {
    Stack numbers;
    initializeStack(&numbers);
    Stack operations;
    initializeStack(&operations);

    for (int i = 0; input[i] != '\0'; i++) {
        if (isspace(input[i])) continue;

        if (isdigit(input[i])) {
            Number number = {0};
            if (flag_float) {
                double value = 0;
                while (isdigit(input[i])) {
                    value = value * 10 + (input[i] - '0');
                    i++;
                }
                number.float_value = value;
            } else {
                long value = 0;
                while (isdigit(input[i])) {
                    value = value * 10 + (input[i] - '0');
                    i++;
                }
                number.int_value = value;
            }
            pushStack(&numbers, number);
            i--;
        } else if (input[i] == '(') {
            Number op = {0};
            op.int_value = '(';
            pushStack(&operations, op);
        } else if (input[i] == ')') {
            while (!isEmptyStack(&operations) && peekStack(&operations).int_value != '(') {
                Number b = popStack(&numbers);
                Number a = popStack(&numbers);
                char oper = (char)popStack(&operations).int_value;
                pushStack(&numbers, applyOperation(a, b, oper));
            }
            popStack(&operations);
        } else {
            while (!isEmptyStack(&operations) && priorityOperations((char)peekStack(&operations).int_value) >= priorityOperations(input[i])) {
                Number b = popStack(&numbers);
                Number a = popStack(&numbers);
                char oper = (char)popStack(&operations).int_value;
                pushStack(&numbers, applyOperation(a, b, oper));
            }
            Number op = {0};
            op.int_value = input[i];
            pushStack(&operations, op);
        }
    }

    while (!isEmptyStack(&operations)) {
        Number b = popStack(&numbers);
        Number a = popStack(&numbers);
        char oper = (char)popStack(&operations).int_value;
        pushStack(&numbers, applyOperation(a, b, oper));
    }

    return popStack(&numbers);
}

int validateInput(char* input) {
    while (*input) {
        char c = *input;

        if (isdigit(c)) {
            input++;
            continue;
        }

        if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
            input++;
            continue;
        }

        if (c == '(' || c == ')' || c == '+' || c == '-' || c == '*' || c == '/') {
            input++;
            continue;
        }

        return -1;
    }

    return 0;
}

int main(int argc, char** argv) {
    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = %s\n", i, argv[i]);
        if (strcmp(argv[i], "--float") == 0) {
            flag_float = 1;
        }
    }

    char* input = malloc(1024);
    if (input == NULL) {
        printf("Memory allocation error!\n");
        return -1;
    }

    fgets(input, 1024, stdin);

    int error_flag = validateInput(input);
    if (error_flag == -1) {
        free(input);
        return -12345; // input error
    }

    Number result = calculatingExpression(input);
    if (flag_float) {
        printf("%.4lf\n", result.float_value);
    } else {
        printf("%ld\n", result.int_value);
    }

    free(input);
    return 0;
}
