#include <gtest/gtest.h>
#include "my_package/math_helper.hpp"

// All test cases are defined like so
// Names for test suite and test are arbitrary
TEST(test_suite_name, test1)
{
  ASSERT_EQ(25, square(5));
}

// Main is the same
int main(int argc, char ** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
