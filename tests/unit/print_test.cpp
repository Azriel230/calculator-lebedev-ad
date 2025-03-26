#include <cstdio>
#include <cstdlib>
#include <gtest/gtest.h>
#include <string>
#include <unistd.h>

extern "C" {
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

Stack* newStack();
Queue* newQueue();
void stackPush(Stack*, void*, EType);
void queuePush(Queue* q, void* value, EType type);
void stackPushNode(Stack*, Node*);
Node* stackPop(Stack*);
Node* queuePop(Queue* q);
void nodeFree(Node*);
void stackPrint(Stack* s);
void queuePrint(Queue* q);
}

TEST(PrintTest, PrintStack3)
{
    auto s = newStack();
    int saved_stdout = dup(STDOUT_FILENO);
    int pipefd[2];
    pipe(pipefd);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);

    long* v1 = (long*)malloc(sizeof(long));
    *v1 = 10;
    stackPush(s, v1, INTEGER);
    double* v2 = (double*)malloc(sizeof(double));
    *v2 = 15;
    stackPush(s, v2, DOUBLE);
    char* v3 = (char*)malloc(sizeof(char));
    *v3 = '+';
    stackPush(s, v3, OPERATOR);
    stackPrint(s);
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
    EXPECT_STREQ(res.c_str(), "+\n15.00000\n10\n");
    close(saved_stdout);
    nodeFree(stackPop(s));
    nodeFree(stackPop(s));
    nodeFree(stackPop(s));
    free(s);
}

TEST(PrintTest, PrintStack1)
{
    auto s = newStack();
    int saved_stdout = dup(STDOUT_FILENO);
    int pipefd[2];
    pipe(pipefd);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);

    long* v1 = (long*)malloc(sizeof(long));
    *v1 = 10;
    stackPush(s, v1, INTEGER);
    stackPrint(s);
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
    EXPECT_STREQ(res.c_str(), "10\n");
    close(saved_stdout);
    nodeFree(stackPop(s));
    free(s);
}

TEST(PrintTest, PrintQueue1)
{
    auto s = newQueue();
    int saved_stdout = dup(STDOUT_FILENO);
    int pipefd[2];
    pipe(pipefd);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);

    long* v1 = (long*)malloc(sizeof(long));
    *v1 = 10;
    queuePush(s, v1, INTEGER);
    queuePrint(s);
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
    EXPECT_STREQ(res.c_str(), "10\n");
    close(saved_stdout);
    nodeFree(queuePop(s));
    free(s);
}

TEST(PrintTest, PrintQueue3)
{
    auto s = newQueue();
    int saved_stdout = dup(STDOUT_FILENO);
    int pipefd[2];
    pipe(pipefd);
    dup2(pipefd[1], STDOUT_FILENO);
    close(pipefd[1]);

    long* v1 = (long*)malloc(sizeof(long));
    *v1 = 10;
    queuePush(s, v1, INTEGER);
    double* v2 = (double*)malloc(sizeof(double));
    *v2 = 15;
    queuePush(s, v2, DOUBLE);
    char* v3 = (char*)malloc(sizeof(char));
    *v3 = '+';
    queuePush(s, v3, OPERATOR);
    queuePrint(s);
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
    EXPECT_STREQ(res.c_str(), "10\n15.00000\n+\n");
    close(saved_stdout);
    nodeFree(queuePop(s));
    nodeFree(queuePop(s));
    nodeFree(queuePop(s));
    free(s);
}
