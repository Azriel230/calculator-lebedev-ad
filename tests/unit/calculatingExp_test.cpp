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
    
}