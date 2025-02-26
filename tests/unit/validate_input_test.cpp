#include <gtest/gtest.h>
#include "../../src/main.h"

extern "C" {
    int validateInput(char *input);
}

TEST(validateInputTests, validateInput_test)
{
    char input0[] = "((2+3)*4)";
    EXPECT_EQ(1, validateInput(input0));
    char input1[] = "3 + (5 * 2) - (4 / 2)";
    EXPECT_EQ(1, validateInput(input1));
    char input2[] = "1 2 3 4";
    EXPECT_EQ(2, validateInput(input2));
    char input3[] = "1 + (2 (3 + 4))";
    EXPECT_EQ(2, validateInput(input3));
    char input4[] = "1 +- 2";
    EXPECT_EQ(2, validateInput(input4));
    char input5[] = "-1";
    EXPECT_EQ(2, validateInput(input5));
    char input6[] = "1 + 2 /";
    EXPECT_EQ(2, validateInput(input6));
    char input7[] = "((((((((((((((((((((((((((((((((((((((((((((((((((2+((((((((((((((((((((((\n(((((((((((((((((\f(((5+((((((((((((((((((((((((((((((((((((((((((((0+9+(((((((((\n(((((((((((((((((((((((((((((((((((((((((((\n((((((((((((((((((((((((((((((((((((((((((((((((((((((((2*3))))))))))))))))))))))))))))))))))))))))))))))))))))))))\f)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n)))))))))))))))))))))))))))))))))))))))))))))))))))))))\f))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))";
    EXPECT_EQ(1, validateInput(input7));
    char input8[] = "(2+3)+(1+4)*(1-3)";
    EXPECT_EQ(1, validateInput(input8));
}