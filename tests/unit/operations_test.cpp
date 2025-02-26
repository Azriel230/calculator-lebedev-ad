#include <gtest/gtest.h>
#include "../../src/main.h"

extern "C" {
    typedef union {
        long int_value;
        double float_value;
    } Number;

    int priorityOperations(char oper);
    Number applyOperation(Number a, Number b, char oper);
}

TEST(operationsTests, priorityOpers_test)
{
    char plus = '+';
    char minus = '-';
    char mult = '*';
    char div = '/';

    EXPECT_EQ(1, priorityOperations(plus));
    EXPECT_EQ(1, priorityOperations(minus));
    EXPECT_EQ(2, priorityOperations(mult));
    EXPECT_EQ(2, priorityOperations(div));

    char another = ')';
    EXPECT_EQ(0, priorityOperations(another));
}

TEST(operationsTests, applyOper_test)
{
    char plus = '+';
    char minus = '-';
    char mult = '*';
    char division = '/';

    flag_float = 0;
    Number a {0};
    Number b {0};
    a.float_value = 10;
    a.int_value = 10;
    b.float_value = 3;
    b.int_value = 3;
    Number zero {0};
    zero.float_value = 0.0001;
    zero.int_value = 0;

    Number result {0};

    result = applyOperation(a,b,plus);
    EXPECT_EQ(13, result.int_value);
    result = applyOperation(a,b,minus);
    EXPECT_EQ(7, result.int_value);
    result = applyOperation(a,b,mult);
    EXPECT_EQ(30, result.int_value);
    result = applyOperation(a,b,division);
    EXPECT_EQ(3, result.int_value);

    EXPECT_EXIT(applyOperation(a,zero,division), testing::ExitedWithCode(1), "");

    flag_float = 1;

    double abplus = a.float_value + b.float_value;
    double abminus = a.float_value - b.float_value;
    double abmult = a.float_value * b.float_value;
    double abdiv = a.float_value / b.float_value;

    result = applyOperation(a,b,plus);
    EXPECT_EQ(abplus, result.float_value);
    result = applyOperation(a,b,minus);
    EXPECT_EQ(abminus, result.float_value);
    result = applyOperation(a,b,mult);
    EXPECT_EQ(abmult, result.float_value);
    // result = applyOperation(a,b,division);
    // EXPECT_EQ(abdiv, result.float_value);

    EXPECT_EXIT(applyOperation(a,zero,division), testing::ExitedWithCode(1), "");
}

TEST(operationsTests, applyOperDIVISIONfloatNOTZERO_test)
{
    flag_float = 1;
    Number a {0};
    Number b {0};
    a.float_value = 10;
    b.float_value = 3;
    Number result {0};
    char division = '/';

    double abdiv = a.float_value / b.float_value;
    result = applyOperation(a,b,division);
    // EXPECT_EXIT(applyOperation(a,b,div), testing::ExitedWithCode(1), "");

    EXPECT_EQ(abdiv, result.float_value);
}