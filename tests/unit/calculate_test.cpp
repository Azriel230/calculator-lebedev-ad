#include <cstdio>
#include <cstdlib>
#include <gtest/gtest.h>
#include <string>
#include <unistd.h>

extern "C" {
typedef enum EErrors {
    ERR_UNEXPECTED_CHAR = -1,
    ERR_MISMATCHED_PARANTHESES = -2,
    ERR_STACK_FUCKED = -3,
    ERR_EMPTY_INPUT = -4
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
Queue* newQueue();
Node* queuePop(Queue* q);
void nodeFree(Node*);
int parseStdin(Queue* q);
double count(Node* opcode, Node* arg1, Node* arg2);
int calculate(Queue* q, void* res);
void queuePrint(Queue* q);
int calculateStdin();
}

TEST(CalculateTest, CountTest)
{
    Node op, arg1, arg2;
    op.value = malloc(sizeof(char));
    *(char*)op.value = '+';
    arg1.value = malloc(sizeof(long));
    *(long*)arg1.value = 10;
    arg2.value = malloc(sizeof(long));
    *(long*)arg2.value = 5;
    auto res = count(&op, &arg1, &arg2);
    EXPECT_EQ(res, 15);
    *(char*)op.value = '-';
    res = count(&op, &arg1, &arg2);
    EXPECT_EQ(res, 5);
    *(char*)op.value = '*';
    res = count(&op, &arg1, &arg2);
    EXPECT_EQ(res, 50);
    *(char*)op.value = '/';
    *(long*)arg1.value = 9;
    *(long*)arg2.value = 2;
    res = count(&op, &arg1, &arg2);
    EXPECT_EQ(res, 4);

    free(op.value);
    free(arg1.value);
    free(arg2.value);
}

TEST(CalculateTest, CalculateFunc)
{
    auto q = newQueue();
    const char* input = "1+2-3*4/5";
    FILE* instream = fmemopen((void*)input, strlen(input), "r");
    FILE* tmp = stdin;
    stdin = instream;
    int err = parseStdin(q);
    ASSERT_EQ(err, 0) << "errors while parsing";
    fclose(instream);
    stdin = tmp;
    void* res = malloc(sizeof(long));
    err = calculate(q, res);
    ASSERT_EQ(err, 0) << "errors while calculating";
    EXPECT_EQ(*(long*)res, 1);
    free(q);
    free(res);
}

TEST(CalculateTest, CalculateStdin)
{
    const char* input = "(1+2 )-3 *4/ 5";
    FILE* instream = fmemopen((void*)input, strlen(input), "r");
    FILE* tmpIn = stdin;
    stdin = instream;
    int saved_stdout = dup(STDOUT_FILENO);
    int pipefd[2];
    pipe(pipefd);

    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);

    calculateStdin();
    fflush(stdout);

    char buffer[1024];
    ssize_t bytes = read(pipefd[0], buffer, sizeof(buffer) - 1);
    close(pipefd[0]);

    dup2(saved_stdout, STDOUT_FILENO);
    std::string res;
    if (bytes > 0) {
        buffer[bytes] = '\0';
        res = std::string(buffer);
    } else {
        res = "";
    }
    stdin = tmpIn;
    EXPECT_STREQ(res.c_str(), "1");
    close(saved_stdout);
    fclose(instream);
}
