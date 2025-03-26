#include <cstdlib>
#include <gtest/gtest.h>
extern "C" {
typedef enum EType { INTEGER,
    DOUBLE,
    OPERATOR } EType;

typedef struct Node {
    void* value;
    EType type;
    struct Node* next;
} Node;

typedef struct Queue {
    Node* first;
    Node* last;
} Queue;

Queue* newQueue();
void queuePush(Queue*, void*, EType);
void queuePushNode(Queue*, Node*);
Node* queuePop(Queue*);
void queuePrint(Queue*);
void nodeFree(Node*);
}

TEST(QueueTest, QueueInit)
{
    Queue* q = newQueue();
    EXPECT_EQ(q->first, (void*)0);
    EXPECT_EQ(q->last, (void*)0);
    free(q);
}

TEST(QueueTest, QueuePush)
{
    void *v1 = malloc(sizeof(long)), *v2 = malloc(sizeof(char)), *v3 = malloc(sizeof(double));
    *(long*)v1 = 1;
    *(char*)v2 = 'c';
    *(double*)v3 = 3.0;
    auto q = newQueue();
    queuePush(q, v1, INTEGER);
    queuePush(q, v2, OPERATOR);
    queuePush(q, v3, DOUBLE);
    ASSERT_NE(q->first, (void*)0);
    EXPECT_EQ(q->first->value, v1);
    ASSERT_NE(q->first->next, (void*)0);
    EXPECT_EQ(q->first->next->value, v2);
    ASSERT_NE(q->first->next->next, (void*)0);
    EXPECT_EQ(q->first->next->next->value, v3);
    ASSERT_NE(q->last, (void*)0);
    EXPECT_EQ(q->last->value, v3);

    // Clean up
    nodeFree(queuePop(q));
    nodeFree(queuePop(q));
    nodeFree(queuePop(q));
    free(q);
}

TEST(QueueTest, QueuePop)
{
    void *v1 = malloc(sizeof(long)), *v2 = malloc(sizeof(char)), *v3 = malloc(sizeof(double));
    *(long*)v1 = 1;
    *(char*)v2 = 'c';
    *(double*)v3 = 3.0;
    auto q = newQueue();
    queuePush(q, v1, INTEGER);
    queuePush(q, v2, OPERATOR);
    queuePush(q, v3, DOUBLE);
    auto n1 = queuePop(q);
    auto n2 = queuePop(q);
    auto n3 = queuePop(q);
    queuePushNode(q, n3);
    n3 = queuePop(q);
    EXPECT_EQ(n1->value, v1);
    EXPECT_EQ(n2->value, v2);
    EXPECT_EQ(n3->value, v3);
    EXPECT_EQ(q->first, (void*)0);

    // Clean uo
    free(q);
    nodeFree(n1);
    nodeFree(n2);
    nodeFree(n3);
}

TEST(QueueTest, QueuePushNode)
{
    void *v1 = malloc(sizeof(long)), *v2 = malloc(sizeof(char)), *v3 = malloc(sizeof(double));
    *(long*)v1 = 1;
    *(char*)v2 = 'c';
    *(double*)v3 = 3.0;
    auto q = newQueue();

    // Push to fill queue
    queuePush(q, v1, INTEGER);
    queuePush(q, v2, OPERATOR);
    queuePush(q, v3, DOUBLE);

    // Pop to get nodes
    auto n1 = queuePop(q);
    auto n2 = queuePop(q);
    auto n3 = queuePop(q);

    // Push nodes back to ensure they are correctly borrowed
    queuePushNode(q, n1);
    queuePushNode(q, n2);
    queuePushNode(q, n3);
    ASSERT_EQ(q->first, n1);
    ASSERT_EQ(q->first->next, n2);
    ASSERT_EQ(q->first->next->next, n3);

    // Clean up
    nodeFree(queuePop(q));
    nodeFree(queuePop(q));
    nodeFree(queuePop(q));
    free(q);
}
