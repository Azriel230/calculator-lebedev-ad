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

void nodeFree(Node*);
}

TEST(NodeTest, TestFree)
{
    Node* n = (Node*)malloc(sizeof(Node));
    ASSERT_NE(n, (void*)0);
    n->value = malloc(sizeof(long));
    ASSERT_NE(n->value, (void*)0);

    nodeFree(n);
    // Should be no memory leaks
}

TEST(NodeTest, TestFreeNull)
{
    Node* n = NULL;
    EXPECT_NO_FATAL_FAILURE(nodeFree(n)) << "nodeFree caused crash on NULL";
}
