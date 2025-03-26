#include <gtest/gtest.h>

extern "C" {
int precedence(char op1, char op2);
}

TEST(PrecedenceTest, Equal)
{
    EXPECT_EQ(0, precedence('+', '-')) << "expected '+' and '-' to be equal, got not equal";
    EXPECT_EQ(0, precedence('*', '/')) << "expected '*' and '/' to be equal, got not equal";
    EXPECT_EQ(-1, precedence('+', '/')) << "expected '+' be after '/', got other result";
}

TEST(PrecedenceTest, More)
{
    EXPECT_EQ(1, precedence('*', '-')) << "expected '*' be before '-', got other result";
    EXPECT_EQ(1, precedence('/', '+')) << "expected '/' be before '+', got other result";
}

TEST(PrecedenceTest, Less)
{
    EXPECT_EQ(-1, precedence('+', '/')) << "expected '+' be after '/', got other result";
    EXPECT_EQ(-1, precedence('-', '*')) << "expected '-' be after '*', got other result";
}
