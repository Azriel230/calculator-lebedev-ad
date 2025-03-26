#include <cstdlib>
#include <cstring>
#include <gtest/gtest.h>

extern "C" {
int parseArgs(int argc, char** argv);
}

TEST(CLITest, ParseArgs)
{
    int argc = 1;
    char** argv;
    argv = (char**)calloc(2, sizeof(char*));
    argv[0] = (char*)calloc(20, sizeof(char));
    argv[1] = (char*)calloc(20, sizeof(char));
    strcpy(argv[0], "program");
    strcpy(argv[1], "--float");
    int res = parseArgs(argc, (char**)argv);
    EXPECT_EQ(res, 0);
    argc = 2;
    res = parseArgs(argc, (char**)argv);
    free(argv[0]);
    free(argv[1]);
    free(argv);
    EXPECT_EQ(res, 1);
}
