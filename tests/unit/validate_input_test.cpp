#include <gtest/gtest.h>
#include "../../src/main.h"

extern "C" {
    int validateInput(char *input);
}

TEST(validateInputTests, validateInput_test)
{
    char input[] = "3 + (5 * 2) - (4 / 2)";
    EXPECT_EQ(1, validateInput(input));
    char input2[] = "1 2 3 4";
    EXPECT_EQ(2, validateInput(input2));
    char input3[] = "1 + (2 (3 + 4))";
    EXPECT_EQ(2, validateInput(input3));
    strcmp(input, "1 +- 2");
    char input4[] = "1 +- 2";
    EXPECT_EQ(2, validateInput(input4));
    strcmp(input, "-1");
    char input5[] = "-1";
    EXPECT_EQ(2, validateInput(input5));
    char input6[] = "1 + 2 /";
    EXPECT_EQ(2, validateInput(input6));
}