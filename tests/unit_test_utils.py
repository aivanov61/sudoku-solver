# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import unittest
import sys

sys.path.insert(0, '.')


class UnitTestUtils:
    """
    Utility for Unit Tests.
    Use the unittest decorator to register test cases with the test runner.
    Example:
        test = UnitTestUtils()

        @test.unittest()
        def test_case0:
            ...
    Test cases can be individually disabled by setting unittest(disabled=True).
    Tear down between test cases should happen in the teardown() method.
    Run all registered tests by calling the run method on the test runner instance.
    """

    def __init__(self):
        super().__init__()
        self.tests = []
        self.test_names = set()
        self.tasks = []

    def unittest(self, disabled=False):
        # Decorator to register test cases with the test runner.
        def decorator(test):
            def wrapper():
                if disabled:
                    print("[ DISABLED TEST ]: " + test.__name__)
                else:
                    print("\n[ RUNNING TEST ]: " + test.__name__)
                    test()
                    print("[ TEST COMPLETE ]: " + test.__name__ + "\n")

            if test.__name__ not in self.test_names:
                self.tests.append(wrapper)
                self.test_names.add(test.__name__)
            else:
                raise Exception(f"Test with name '{test.__name__}' already registered")

            return test

        return decorator

    def setup(self):
        """
        Setup the test environment before running each test case. Example:
            class ExampleTest(UnitTestUtils):
                def __init__(self, dut):
                    super.__init__()
                    self.dut = dut

                def setup(self):
                    dut.write(data=0xabc, addr=0x1)
                    dut.write(data=0xdef, addr=0x2)

            ...

            @test.unittest()
            def test_case0:
                expect_equal(dut.read(addr=0x1), 0xabc)

            @test.unittest()
            def test_case1:
                expect_equal(dut.read(addr=0x2), 0xdef)
        """
        pass

    def teardown(self):
        """
        Reset the test environment between test cases. Example:
            class ExampleTest(UnitTestUtils):
                def __init__(self, dut):
                    super.__init__()
                    self.dut = dut

                def teardown(self):
                    self.dut.clear_data()

            ...

            @test.unittest()
            def test_case0:
                dut.write(data=0xabc, addr=0x1)
                expect_equal(dut.read(addr=0x1), 0xabc)

            @test.unittest()
            def test_case1:
                expect_equal(dut.read(addr=0x1), 0x0)
        """
        pass

    def run(self):
        # Run all tests registered to the test runner
        for t in self.tests:
            self.__execute_test(t)
        print("[ ALL TESTS COMPLETED ]")

    def __execute_test(self, t):
        print("\n[ SETUP ]")
        self.setup()
        t()
        print("[ TEARDOWN ]")
        self.teardown()
