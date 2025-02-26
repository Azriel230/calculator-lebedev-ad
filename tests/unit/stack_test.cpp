#include <gtest/gtest.h>
#include "../../src/main.h"

extern "C" {
    typedef union {
        long int_value;
        double float_value;
    } Number;

    typedef struct {
        Number data[STACK_SIZE];
        int top;
    } Stack;

    void initializeStack(Stack* stack);
    int isEmptyStack(Stack* stack);
    int isFullStack(Stack* stack);
    void pushStack(Stack* stack, Number item);
    Number popStack(Stack* stack);
    Number peekStack(Stack* stack);
}

TEST(stackTests, initStack_test)
{
    Stack s;
    initializeStack(&s);
    EXPECT_EQ(-1, s.top);
}

TEST(stackTests, isEmptyStack_test)
{
    Stack s;
    initializeStack(&s);
    EXPECT_EQ(1, isEmptyStack(&s));
    Number item {10};
    pushStack(&s, item);
    EXPECT_EQ(0, isEmptyStack(&s));
}

TEST(stackTests, isFullStack_test)
{
    Stack s;
    initializeStack(&s);
    EXPECT_EQ(0, isFullStack(&s));
    for(int i = 0; i < STACK_SIZE; i++) {
        Number item {i};
        pushStack(&s, item);
    }
    EXPECT_EQ(1, isFullStack(&s));
}

TEST(stackTests, pushStack_test)
{
    Stack s;
    initializeStack(&s);
    EXPECT_EQ(1, isEmptyStack(&s));
    Number item {10};
    pushStack(&s, item);
    EXPECT_EQ(0, isEmptyStack(&s));
    EXPECT_EQ(item.int_value, s.data[s.top].int_value);
}

TEST(stackTests, popStack_test)
{
    Stack s;
    initializeStack(&s);
    EXPECT_EQ(1, isEmptyStack(&s));
    Number item {10};
    pushStack(&s, item);
    EXPECT_EQ(0, isEmptyStack(&s));
    Number poped = popStack(&s);
    EXPECT_EQ(item.int_value, poped.int_value);
    EXPECT_EQ(1, isEmptyStack(&s));
}

TEST(stackTests, peekStack_test)
{
    Stack s;
    initializeStack(&s);
    EXPECT_EQ(1, isEmptyStack(&s));
    Number item {10};
    pushStack(&s, item);
    EXPECT_EQ(0, isEmptyStack(&s));
    Number peeked = peekStack(&s);
    EXPECT_EQ(item.int_value, peeked.int_value);
    EXPECT_EQ(peeked.int_value, s.data[s.top].int_value);
    EXPECT_EQ(0, isEmptyStack(&s));
}