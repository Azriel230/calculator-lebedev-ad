#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <fcntl.h>
#include <gtest/gtest.h>
#include <unistd.h>
#include <utility>
#include <vector>

extern "C" {
typedef enum EErrors {
    ERR_UNEXPECTED_CHAR = -1,
    ERR_MISMATCHED_PARANTHESES = -2,
    ERR_STACK_FUCKED = -3,
    ERR_EMPTY_INPUT = -4,
    ERR_WRONG_TOKEN_ORDER = -6
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
int parseStdin(Queue* q);
Queue* newQueue();
Node* queuePop(Queue* q);
void queuePrint(Queue*);
void nodeFree(Node*);
void pushIfNumberEnded(int* wasNum, long* number, Queue* q);
}

TEST(ParseStdinTest, PushIfNumberEnded)
{
    Queue* q = newQueue();
    long num = 123;
    int wasNum = 1;
    pushIfNumberEnded(&wasNum, &num, q);
    ASSERT_NE(q->first, (void*)0) << "Didn't insert";
    EXPECT_EQ(*(long*)q->first->value, 123) << "Inserted wrong number";
    num = 50;
    pushIfNumberEnded(&wasNum, &num, q);
    EXPECT_EQ(*(long*)q->last->value, 123) << "Shouln't insert but inserted";
    nodeFree(queuePop(q));
    free(q);
}

bool checkQueue(Queue* q, std::vector<std::pair<long, EType>> expected)
{
    if (q == NULL) {
        return false;
    }

    Node* tmp = q->first;
    int i = 0;
    while (tmp != NULL && i < expected.size()) {
        if (tmp->type != expected[i].second) {
            return false;
        }
        if (tmp->type == OPERATOR && *(char*)tmp->value != expected[i].first) {
            return false;
        }
        if (tmp->type != OPERATOR && *(long*)tmp->value != expected[i].first) {
            return false;
        }
        tmp = tmp->next;
        i++;
    }
    return true;
}

TEST(ParseStdinTest, HandlesSimpleMath)
{
    const char* input = "(1+2 )-3 *4/ 5";
    FILE* instream = fmemopen((void*)input, strlen(input), "r");
    FILE* tmpIn = stdin;
    stdin = instream;
    auto q = newQueue();
    parseStdin(q);
    bool res = checkQueue(q, { { 1, INTEGER }, { 2, INTEGER }, { '+', OPERATOR }, { 3, INTEGER }, { 4, INTEGER }, { '*', OPERATOR }, { 5, INTEGER }, { '/', OPERATOR }, { '-', OPERATOR } });
    fclose(instream);
    EXPECT_EQ(res, true);
    while (q->first != NULL) {
        nodeFree(queuePop(q));
    }
    free(q);
}

TEST(ParseStdinTest, HandlesMoreMath)
{
    const char* input = "(1+2 )-3 *(4/ 5)";
    FILE* instream = fmemopen((void*)input, strlen(input), "r");
    FILE* tmpIn = stdin;
    stdin = instream;
    auto q = newQueue();
    parseStdin(q);
    bool res = checkQueue(q, { { 1, INTEGER }, { 2, INTEGER }, { '+', OPERATOR }, { 3, INTEGER }, { 4, INTEGER }, { 5, INTEGER }, { '/', OPERATOR }, { '*', OPERATOR }, { '-', OPERATOR } });
    fclose(instream);
    EXPECT_EQ(res, true);
    while (q->first != NULL) {
        nodeFree(queuePop(q));
    }

    free(q);
}
