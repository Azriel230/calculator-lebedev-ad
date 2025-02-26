#include <gtest/gtest.h>
#include "../../src/main.h"

extern "C" {
    typedef union {
        long int_value;
        double float_value;
    } Number;

    Number calculatingExpression(char *input);
}

TEST(calculatingExpTestss, calculatingExp_test)
{
    flag_float = 0;
    char input1[] = "(2+3)+(1+4)*(1-3)";
    Number result = calculatingExpression(input1);
    EXPECT_EQ(-5, result.int_value);
}