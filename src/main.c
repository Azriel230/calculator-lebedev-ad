#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// #define DEBUG

int IS_FLOAT_MODE = 0;

/////////////////// STRUCTS, ENUMS ////////////////////
typedef enum EErrors {
    ERR_UNEXPECTED_CHAR = -1,
    ERR_MISMATCHED_PARANTHESES = -2,
    ERR_STACK_FUCKED = -3,
    ERR_EMPTY_INPUT = -4,
    ERR_NULL_DIVISION = -5,
    ERR_TOO_MANY_OPERANDS = -6,
    ERR_WRONG_TOKEN_ORDER = -7
} EErrors;

typedef enum EType { INTEGER,
    DOUBLE,
    OPERATOR } EType;

typedef struct Node {
    void* value;
    EType type;
    struct Node* next;
} Node;

typedef struct Stack {
    Node* top;
} Stack;

typedef struct Queue {
    Node* first;
    Node* last;
} Queue;

/////////////////// STACK ////////////////////
Stack* newStack()
{
    Stack* s = (Stack*)malloc(sizeof(Stack));
    if (s == NULL) {
        printf("ERROR allocating memory for Stack");
        return NULL;
    }
    s->top = NULL;
    return s;
}

void stackPush(Stack* s, void* value, EType type)
{
    Node* new = (Node*)malloc(sizeof(Node));
    new->value = value;
    new->next = s->top;
    new->type = type;
    s->top = new;
}

void stackPushNode(Stack* s, Node* new)
{
    new->next = s->top;
    s->top = new;
}

Node* stackPop(Stack* s)
{
    if (s->top == NULL) {
        return NULL;
    }

    Node* res = s->top;
    s->top = s->top->next;
    return res;
}

void stackPrint(Stack* s)
{
    Node* tmp = s->top;
    while (tmp != NULL) {
        switch (tmp->type) {
        case OPERATOR:
            printf("%c\n", *(char*)tmp->value);
            break;
        case INTEGER:
            printf("%ld\n", *(long*)tmp->value);
            break;
        case DOUBLE:
            printf("%0.5f\n", *(double*)tmp->value);
            break;
        }
        tmp = tmp->next;
    }
}

/////////////////// QUEUE ////////////////////
Queue* newQueue()
{
    Queue* q = (Queue*)malloc(sizeof(Queue));
    if (q == NULL) {
        printf("ERROR allocating memory for Stack");
        return NULL;
    }
    q->first = NULL;
    q->last = NULL;
    return q;
}

void queuePush(Queue* q, void* value, EType type)
{
    Node* new = (Node*)malloc(sizeof(Node));
    new->value = value;
    new->type = type;
    new->next = NULL;
    if (q->first == NULL) {
        q->first = new;
        q->last = new;
    } else {
        q->last->next = new;
        q->last = new;
    }
}

void queuePushNode(Queue* q, Node* new)
{
    new->next = NULL;
    if (q->first == NULL) {
        q->first = new;
        q->last = new;
    } else {
        q->last->next = new;
        q->last = new;
    }
}

Node* queuePop(Queue* q)
{
    if (q->first == NULL) {
        return NULL;
    }

    Node* res = q->first;
    q->first = q->first->next;
    return res;
}

void queuePrint(Queue* q)
{
    Node* tmp = q->first;
    while (tmp != NULL) {
        switch (tmp->type) {
        case OPERATOR:
            printf("%c\n", *(char*)tmp->value);
            break;
        case INTEGER:
            printf("%ld\n", *(long*)tmp->value);
            break;
        case DOUBLE:
            printf("%0.5f\n", *(double*)tmp->value);
            break;
        }
        tmp = tmp->next;
    }
}

void nodeFree(Node* n)
{
    if (n == NULL) {
        return;
    }
    free(n->value);
    free(n);
    n = NULL;
}

/////////////////// PARSING ////////////////////

int precedence(char op1, char op2)
{
    if (op1 == '+' || op1 == '-') {
        if (op2 == '+' || op2 == '-') {
            return 0;
        } else { // op2 == '*' || '/'
            return -1;
        }
    } else { // op1 == '*' || '/'
        if (op2 == '+' || op2 == '-') {
            return 1;
        } else {
            return 0;
        }
    }
}

int ExpectedToken = 0;
void pushIfNumberEnded(int* wasNum, long* number, Queue* q)
{
    if (*wasNum) {
        if (IS_FLOAT_MODE) {
            double* val = malloc(sizeof(double));
            *val = *number;
            queuePush(q, val, DOUBLE);
        } else {
            long* val = malloc(sizeof(long));
            *val = *number;
            queuePush(q, val, INTEGER);
        }
        *number = 0;
        *wasNum = 0;
        ExpectedToken = OPERATOR;
    }
}

int parseStdin(Queue* q)
{
    ExpectedToken = 0;
    long number = 0;
    int wasNum = 0;
    char ch;
    void* vp;
    Node* tmp = NULL;
    Stack* s = newStack();

    do {
        switch (ch = getchar()) {
        case '(':
            vp = malloc(sizeof(char));
            *(char*)vp = '(';
            stackPush(s, vp, OPERATOR);
            break;
        case ')':
            pushIfNumberEnded(&wasNum, &number, q);
            while (s->top != NULL && *(char*)s->top->value != '(') {
                tmp = stackPop(s);
                queuePushNode(q, tmp);
            }
            if (s->top == NULL) {
                return ERR_MISMATCHED_PARANTHESES;
            }
            if (*(char*)s->top->value == '(') {
                nodeFree(stackPop(s));
            }
            break;
        case '+':
        case '-':
        case '*':
        case '/':
            pushIfNumberEnded(&wasNum, &number, q);
            if (ExpectedToken != OPERATOR) {
                exit(ERR_WRONG_TOKEN_ORDER);
            }
            ExpectedToken = 0;
            while (s->top != NULL && *(char*)s->top->value != '(' && precedence(*(char*)s->top->value, ch) != -1) {
                tmp = stackPop(s);
                queuePushNode(q, tmp);
            }
            vp = malloc(sizeof(char));
            *(char*)vp = ch;
            stackPush(s, vp, OPERATOR);
            break;
        case EOF:
            pushIfNumberEnded(&wasNum, &number, q);
            while (s->top != NULL) {
                tmp = stackPop(s);
                queuePushNode(q, tmp);
            }
            break;
        case ' ':
        case '\n':
        case '\f':
        case '\v':
        case '\t':
        case '\r':
            pushIfNumberEnded(&wasNum, &number, q);
            break;
        default:
            if (ch >= '0' && ch <= '9') {
                if (ExpectedToken == OPERATOR) {
                    exit(ERR_WRONG_TOKEN_ORDER);
                }
                wasNum = 1;
                number = number * 10 + ch - '0';
            } else {
                return ERR_UNEXPECTED_CHAR;
            }
        }
#ifdef DEBUG
        printf("\nQUEUE FRAME:\n");
        queuePrint(q);
        printf("STACK FRAME:\n");
        stackPrint(s);
#endif /* ifdef DEBUG */
    } while (ch != EOF);
    if (q->first == NULL) {
      return ERR_EMPTY_INPUT;
    }

    free(s);
    return 0;
}

//////////////////// CALCULATING ///////////////////

double count(Node* opcode, Node* arg1, Node* arg2)
{
    double res = 0;
    int i1, i2;
    double d1, d2;
    if (IS_FLOAT_MODE) {
        d1 = *(double*)arg1->value;
        d2 = *(double*)arg2->value;
        switch (*(char*)opcode->value) {
        case '+':
            res = d1 + d2;
            break;
        case '-':
            res = d1 - d2;
            break;
        case '*':
            res = d1 * d2;
            break;
        case '/':
            if (d2 == 0) {
                exit(ERR_NULL_DIVISION);
            }
            res = d1 / d2;
            break;
        }
        return res;
    }

    i1 = *(long*)arg1->value;
    i2 = *(long*)arg2->value;
    switch (*(char*)opcode->value) {
    case '+':
        res = i1 + i2;
        break;
    case '-':
        res = i1 - i2;
        break;
    case '*':
        res = i1 * i2;
        break;
    case '/':
        if (i2 == 0) {
            exit(ERR_NULL_DIVISION);
        }
        res = i1 / i2;
        break;
    }
    return res;
}

int calculate(Queue* q, void* res)
{
    Stack* s = newStack();

    while (q->first != NULL) {
        void* vp;
        Node* nextToken = queuePop(q);
        if (nextToken->type == INTEGER || nextToken->type == DOUBLE) {
            stackPushNode(s, nextToken);
        } else {
            if (s->top == NULL || s->top->next == NULL) {
                return ERR_STACK_FUCKED;
            }
            Node* arg2 = stackPop(s);
            Node* arg1 = stackPop(s);
            double value = count(nextToken, arg1, arg2);
            nodeFree(arg2);
            nodeFree(arg1);
            nodeFree(nextToken);
            if (IS_FLOAT_MODE) {
                vp = malloc(sizeof(double));
                *(double*)vp = value;
                stackPush(s, vp, DOUBLE);
            } else {
                vp = malloc(sizeof(long));
                *(long*)vp = value;
                stackPush(s, vp, INTEGER);
            }
        }
    }

    if (s->top->next != NULL) {
        exit(ERR_TOO_MANY_OPERANDS);
    }
    if (IS_FLOAT_MODE) {
        *(double*)res = *(double*)s->top->value;
    } else {
        *(long*)res = *(long*)s->top->value;
    }
    nodeFree(stackPop(s));
    free(s);
    return 0;
}

int calculateStdin()
{
    void* res;
    if (IS_FLOAT_MODE) {
        res = malloc(sizeof(double));
    } else {
        res = malloc(sizeof(long));
    }

    Queue* resultQueue = newQueue();

    int err = parseStdin(resultQueue);
    switch (err) {
    case ERR_MISMATCHED_PARANTHESES:
        printf("ERROR: mismatched parantheses in expression");
        return ERR_MISMATCHED_PARANTHESES;
        break;
    case ERR_EMPTY_INPUT:
        printf("ERROR: no meaningfull characters in input");
        return ERR_EMPTY_INPUT;
    case ERR_UNEXPECTED_CHAR:
        printf("ERROR: unexpected character");
        return ERR_UNEXPECTED_CHAR;
    }
#ifdef DEBUG
    queuePrint(resultQueue);
#endif /* ifdef DEBUG */

    err = calculate(resultQueue, res);
    free(resultQueue);
    if (err == ERR_STACK_FUCKED) {
        printf("ERROR: stack corrupted during evaluation. Expression must be "
               "incorrect");
        return ERR_STACK_FUCKED;
    }

    if (IS_FLOAT_MODE) {
        printf("%f", *(double*)res);
    } else {
        printf("%ld", *(long*)res);
    }
    free(res);

    return 0;
}

///////////////// CLI /////////////////
int parseArgs(int argc, char** argv)
{
    if (argc == 1) {
        return 0;
    }
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--float") || !strcmp(argv[i], "-f")) {
            return 1;
        }
        printf("Unnown command line option %s\n", argv[i]);
    }
    return 0;
}

#ifndef GTEST
int main(int argc, char** argv)
{
    IS_FLOAT_MODE = parseArgs(argc, argv);
    return calculateStdin();
}
#endif
