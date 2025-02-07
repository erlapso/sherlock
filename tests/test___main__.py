import sys
import pytest
import runpy
import types
import importlib
import sherlock_project.__main__
import builtins
from sherlock_project import __main__

def test_python_version_check(monkeypatch, capsys):
    """
    Test that __main__ exits with an error when Python version is below 3.9.
    This simulates an environment running an older version of Python and verifies
    that the appropriate error message is printed and sys.exit(1) is invoked.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 8, 10))
    monkeypatch.setattr(sys, 'version', "3.8.10")
    
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module('sherlock_project.__main__', run_name='__main__', alter_sys=True)
    
    assert excinfo.value.code == 1
    
    captured = capsys.readouterr().out
    assert "Sherlock requires Python 3.9+" in captured
    assert "3.8.10" in captured
def test_main_function_called(monkeypatch, capsys):
    """
    Test that __main__ calls sherlock.main when the Python version is 3.9 or above.
    This is done by simulating a valid Python version and replacing the
    'sherlock_project.sherlock' module with a dummy module that sets a flag
    when its main method is executed.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    assert flag["called"] is True
def test_import_does_not_execute_main(monkeypatch, capsys):
    """
    Test that importing the __main__ module (with __name__ != "__main__")
    does not trigger the version check nor calls sherlock.main().
    This verifies that the guarded block under if __name__ == "__main__": is not executed.
    """
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    importlib.reload(sherlock_project.__main__)
    assert flag["called"] is False
    
    captured = capsys.readouterr().out
    assert captured == ""
def test_missing_sherlock_main(monkeypatch):
    """
    Test that running __main__ raises an AttributeError if the imported
    sherlock module does not define a main function.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    # Create a dummy sherlock module without a main attribute.
    dummy_module = types.SimpleNamespace()  # no main attribute defined
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    with pytest.raises(AttributeError):
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_main_exception_propagates(monkeypatch):
    """
    Test that any exception raised in sherlock.main() is propagated.
    This simulates a scenario where sherlock.main() fails by raising an error,
    ensuring that the __main__ module does not catch or hide the exception.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    def fake_main():
        raise RuntimeError("test error")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    with pytest.raises(RuntimeError, match="test error"):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_missing_sherlock_module(monkeypatch):
    """
    Test that running __main__ raises an ImportError if the imported
    'sherlock_project.sherlock' module is missing.
    This verifies that the __main__ module does not catch the ImportError.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    original_import = builtins.__import__
    
    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "sherlock_project" and "sherlock" in fromlist:
            raise ImportError("No module named 'sherlock'")
        return original_import(name, globals, locals, fromlist, level)
    
    monkeypatch.setattr(builtins, '__import__', fake_import)
    
    with pytest.raises(ImportError, match="No module named 'sherlock'"):
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_python_version_incomplete_string(monkeypatch, capsys):
    """
    Test that __main__ prints the correct error message when sys.version is an
    incomplete version string (e.g., "3.8") and Python version is below 3.9,
    then exits with code 1.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 8, 0))
    monkeypatch.setattr(sys, 'version', "3.8")
    
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module('sherlock_project.__main__', run_name='__main__', alter_sys=True)
    
    assert excinfo.value.code == 1
    captured = capsys.readouterr().out
    assert "Sherlock requires Python 3.9+" in captured
    assert "3.8" in captured
def test_empty_sys_version_raises_index_error(monkeypatch):
    """
    Test that __main__ raises an IndexError if sys.version is an empty string.
    Since the __main__ module attempts to access sys.version.split()[0],
    an empty sys.version will result in an IndexError.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "")
    
    with pytest.raises(IndexError):
         runpy.run_module('sherlock_project.__main__', run_name="__main__", alter_sys=True)
def test_valid_python_version_with_extra_text(monkeypatch, capsys):
    """
    Test that __main__ correctly extracts the Python version when sys.version
    contains extra whitespace and additional text, and that sherlock.main() is called.
    This ensures that even with extra formatting in sys.version, the module runs properly.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 1))
    monkeypatch.setattr(sys, 'version', "  3.9.1 extra data")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert captured == ""
def test_nonstandard_sys_version_format(monkeypatch, capsys):
    """
    Test that __main__ correctly extracts the first token from sys.version
    even if it is in a nonstandard format (e.g., "foobar extra text"), and then
    prints the correct error message and exits with code 1 when the Python version
    is below 3.9.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 8, 1))
    monkeypatch.setattr(sys, 'version', "foobar extra text")
    
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert excinfo.value.code == 1
    captured = capsys.readouterr().out
    assert "Sherlock requires Python 3.9+" in captured
    assert "foobar" in captured
def test_non_callable_sherlock_main(monkeypatch):
    """
    Test that __main__ raises a TypeError when the 'sherlock.main' attribute exists but is not callable.
    This verifies that the code fails as expected when trying to call a non-callable main attribute.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    dummy_module = types.SimpleNamespace(main="not a callable")
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    with pytest.raises(TypeError):
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_sys_version_not_a_string(monkeypatch):
    """
    Test that __main__ raises an AttributeError when sys.version is not a string.
    This simulates the scenario where sys.version is incorrectly set to a non-string value,
    leading to an error when attempting to call split() on it.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', None)
    
    with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'split'"):
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_sherlock_main_output_propagation(monkeypatch, capsys):
    """
    Test that output printed by sherlock.main() is properly propagated to stdout.
    This ensures that if sherlock.main() prints something, __main__ does not interfere with the output.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    def fake_main():
        print("hello world")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    captured = capsys.readouterr().out
    assert "hello world" in captured
def test_sys_version_whitespace_raises_index_error(monkeypatch):
    """
    Test that __main__ raises an IndexError when sys.version contains only whitespace.
    This simulates a case where sys.version.split() returns an empty list, causing an IndexError
    when the code attempts to access the first element.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "    ")
    
    with pytest.raises(IndexError):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_python_version_with_newlines(monkeypatch, capsys):
    """
    Test that __main__ properly extracts the Python version when sys.version contains
    newlines and extra whitespace, and then calls sherlock.main(). The test simulates a
    sys.version string like "\n3.9.1\nSome extra info" and verifies that the main method
    is invoked and its output is printed.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 1))
    monkeypatch.setattr(sys, 'version', "\n3.9.1\nSome extra info")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("Called main with newline version")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert "Called main with newline version" in captured
def test_extended_sys_version_info(monkeypatch, capsys):
    """
    Test that __main__ correctly handles an extended sys.version_info tuple and
    a custom sys.version string containing extra build info. It verifies that
    the version check passes and that sherlock.main() is invoked.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 2, 'final', 0))
    monkeypatch.setattr(sys, 'version', "3.9.2 custom build")
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert captured == ""
def test_sherlock_main_stderr_output(monkeypatch, capsys):
    """
    Test that output printed to stderr by sherlock.main() is properly propagated.
    This ensures that __main__ does not interfere with stderr output generated
    by sherlock.main().
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    def fake_main():
        print("error occurred", file=sys.stderr)
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    captured_err = capsys.readouterr().err
    assert "error occurred" in captured_err
def test_sherlock_module_not_imported_on_version_failure(monkeypatch):
    """
    Test that if Python version is below 3.9, the sherlock module is not imported.
    This ensures that the version check fails and exits before the import statement
    for "from sherlock_project import sherlock" is executed.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 8, 7))
    monkeypatch.setattr(sys, 'version', "3.8.7")
    
    if "sherlock_project.sherlock" in sys.modules:
        del sys.modules["sherlock_project.sherlock"]
    
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert excinfo.value.code == 1
    assert "sherlock_project.sherlock" not in sys.modules
def test_sys_argv_ignored(monkeypatch):
    """
    Test that extra command-line arguments in sys.argv do not affect the execution of
    sherlock.__main__. The test sets sys.argv with extra arguments, ensuring that
    the main function of the sherlock module is still properly executed.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 1))
    monkeypatch.setattr(sys, 'version', "3.9.1")
    
    original_argv = sys.argv[:]
    monkeypatch.setattr(sys, 'argv', ["__main__.py", "arg1", "arg2"])
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    monkeypatch.setattr(sys, 'argv', original_argv)
    
    assert flag["called"] is True
def test_minimal_sys_version_info(monkeypatch, capsys):
    """
    Test that __main__ executes sherlock.main() correctly when sys.version_info is minimal (tuple of length 2)
    and sys.version contains a simple version string. This ensures that even if the sys.version_info tuple
    is not extended, the version check passes and sherlock.main() is invoked.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9))
    monkeypatch.setattr(sys, 'version', "3.9")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert captured == ""
def test_valid_python_version_inconsistent_version_string(monkeypatch, capsys):
    """
    Test that __main__ executes sherlock.main() correctly even if sys.version string
    is inconsistent with sys.version_info (e.g., sys.version is '3' while sys.version_info
    is (3, 9, 0)). The test ensures that the main method is called and its output is properly
    propagated.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("main executed with inconsistent sys.version")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert "main executed with inconsistent sys.version" in captured
def test_main_module_docstring():
    """
    Test that importing the __main__ module (with __name__ != "__main__")
    does not execute the main block and that the module's docstring is correct.
    This verifies that the module-level documentation is present and mentions 'Sherlock'.
    """
    import sherlock_project.__main__ as main_mod
    assert main_mod.__doc__ is not None, "The __main__ module should have a documentation string."
    assert "Sherlock" in main_mod.__doc__, "The docstring should contain the term 'Sherlock'."
def test_sys_version_as_int_raises_attribute_error(monkeypatch):
    """
    Test that __main__ raises an AttributeError when sys.version is an integer.
    This simulates a scenario where sys.version is incorrectly set to an integer value,
    leading to an error when attempting to call split() on it.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', 39)
    
    with pytest.raises(AttributeError, match="has no attribute 'split'"):
         runpy.run_module('sherlock_project.__main__', run_name='__main__', alter_sys=True)
def test_sys_version_info_list_raises_type_error(monkeypatch):
    """
    Test that if sys.version_info is set as a list instead of a tuple, 
    a TypeError is raised during the version check due to an unsupported comparison.
    """
    monkeypatch.setattr(sys, 'version_info', [3, 9, 0])
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    with pytest.raises(TypeError):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_runpy_without_alter_sys(monkeypatch, capsys):
    """
    Test that running sherlock_project.__main__ with alter_sys=False still properly calls
    sherlock.main() and outputs to stdout. This verifies that the module works correctly even
    when not altering sys.argv and other system variables.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 10, 0))
    monkeypatch.setattr(sys, 'version', "3.10.0")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("main executed with alter_sys False")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=False)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert "main executed with alter_sys False" in captured
def test_sherlock_main_system_exit(monkeypatch):
    """
    Test that if sherlock.main() calls sys.exit(), the SystemExit exception is propagated
    and the exit code is preserved.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    def fake_main():
        sys.exit(2)
    
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    with pytest.raises(SystemExit) as excinfo:
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    assert excinfo.value.code == 2
def test_sys_argv_restored_after_runpy(monkeypatch):
    """
    Test that running sherlock_project.__main__ with alter_sys=True restores sys.argv
    to its original value after execution. This ensures that any changes made to sys.argv
    during module execution do not persist afterward.
    """
    original_argv = ["original", "value"]
    monkeypatch.setattr(sys, "argv", original_argv.copy())
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert sys.argv == original_argv
    assert flag["called"] is True
def test_sherlock_main_returns_value(monkeypatch, capsys):
    """
    Test that if sherlock.main() returns a value, __main__ does not propagate or print it.
    This verifies that the return value from main() is ignored and does not affect the output.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        return "foo"
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert captured == ""
def test_non_numeric_sys_version_valid_info(monkeypatch, capsys):
    """
    Test that __main__ executes sherlock.main successfully even if sys.version's
    first token is non-numeric, provided that sys.version_info indicates a valid version.
    This ensures that the version check solely relies on sys.version_info and does not misinterpret
    a non-numeric sys.version string when determining if Python is supported.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 1))
    monkeypatch.setattr(sys, 'version', "foobar extra data")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("non-numeric version test")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert "non-numeric version test" in captured
def test_sys_version_preserved(monkeypatch, capsys):
    """
    Test that executing sherlock_project.__main__ does not modify sys.version
    or sys.version_info. This ensures that the __main__ module only reads these
    attributes and does not alter them during execution.
    """
    original_version = sys.version
    original_version_info = sys.version_info
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("main executed without modifying sys.version")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    assert sys.version == "3.9.0"
    assert sys.version_info == (3, 9, 0)
def test_main_prints_then_raises(monkeypatch, capsys):
    """
    Test that if sherlock.main() prints output to stdout and then raises an exception,
    the output is correctly captured before the exception is propagated.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    def fake_main():
        print("Log before exception")
        raise RuntimeError("error occurred in main")
    
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    with pytest.raises(RuntimeError, match="error occurred in main"):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
        
    captured = capsys.readouterr().out
    assert "Log before exception" in captured
def test_main_with_tabs_in_sys_version(monkeypatch, capsys):
    """
    Test that __main__ correctly extracts the Python version when sys.version
    contains tab characters and extra formatting (e.g., parentheses), ensuring that
    sherlock.main() is invoked as expected.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 1))
    monkeypatch.setattr(sys, 'version', "\t3.9.0\t(some build info)")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("main executed with tab formatted sys.version")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert "main executed with tab formatted sys.version" in captured
def test_custom_version_info_with_custom_object(monkeypatch, capsys):
    """
    Test that __main__ correctly handles a custom version_info object (not a tuple)
    that implements __lt__ and __eq__. This simulates an environment where the Python
    version information is provided by a non-tuple object. The test ensures that the
    version check passes and sherlock.main() is called.
    """
    class FakeVersion:
        def __init__(self, major, minor, patch=0):
            self.major = major
            self.minor = minor
            self.patch = patch
        def __lt__(self, other):
            return (self.major, self.minor, self.patch) < other
        def __eq__(self, other):
            return (self.major, self.minor, self.patch) == other
        def __repr__(self):
            return f"FakeVersion({self.major}, {self.minor}, {self.patch})"
    
    fake_version = FakeVersion(3, 9, 2)
    monkeypatch.setattr(sys, 'version_info', fake_version)
    monkeypatch.setattr(sys, 'version', "3.9.2 custom build")
    
    flag = {"called": False}
    def fake_main():
        flag["called"] = True
        print("custom version_info object accepted")
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert flag["called"] is True
    captured = capsys.readouterr().out
    assert "custom version_info object accepted" in captured
def test_python_version_non_numeric_token(monkeypatch, capsys):
    """
    Test that __main__ prints the correct error message when sys.version starts
    with a non-numeric token (e.g. "Python 3.8.0") and sys.version_info is below 3.9.
    This ensures that the extracted token is used in the error message.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 8, 0))
    monkeypatch.setattr(sys, 'version', "Python 3.8.0")
    
    with pytest.raises(SystemExit) as excinfo:
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    assert excinfo.value.code == 1
    
    captured = capsys.readouterr().out
    assert "Sherlock requires Python 3.9+" in captured
    assert "Python" in captured
def test_sys_version_info_as_string_raises_type_error(monkeypatch):
    """
    Test that if sys.version_info is set to a string instead of a tuple,
    a TypeError is raised during the version comparison in __main__.
    """
    monkeypatch.setattr(sys, 'version_info', "3.8.0")
    monkeypatch.setattr(sys, 'version', "3.8.0")
    with pytest.raises(TypeError):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_sys_version_missing(monkeypatch):
    """
    Test that __main__ raises an AttributeError when sys.version attribute is missing.
    This simulates a scenario where sys.version is deleted so that sys.version.split() fails.
    """
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.delattr(sys, 'version', raising=False)
    
    with pytest.raises(AttributeError, match="module 'sys' has no attribute 'version'"):
         runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_missing_sys_version_info(monkeypatch):
    """
    Test that __main__ raises an AttributeError when sys.version_info is missing.
    This simulates an environment where the system version information is unavailable,
    and verifies that the code errors out as expected.
    """
    # Remove the sys.version_info attribute
    monkeypatch.delattr(sys, 'version_info', raising=True)
    # Set sys.version to a proper value, so that the split() call in __main__ does not fail.
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    with pytest.raises(AttributeError, match="module 'sys' has no attribute 'version_info'"):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_multiple_reload_no_side_effects(monkeypatch):
    """
    Test that reloading the __main__ module multiple times (when __name__ != "__main__")
    does not trigger sherlock.main(). This verifies that the guarded block is only run
    when the module is executed as __main__.
    """
    call_count = {"count": 0}
    def fake_main():
        call_count["count"] += 1
    # Set up a dummy sherlock module with our fake_main.
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    # Set valid Python version values.
    monkeypatch.setattr(sys, 'version_info', (3, 9, 1))
    monkeypatch.setattr(sys, 'version', "3.9.1")
    # Import and reload the __main__ module multiple times.
    import sherlock_project.__main__ as main_mod
    importlib.reload(main_mod)
    importlib.reload(main_mod)
    # Assert that fake_main was never called since __name__ is not "__main__".
    assert call_count["count"] == 0
def test_sys_version_split_error(monkeypatch):
    """
    Test that __main__ propagates an exception raised by sys.version.split().
    This simulates a scenario where sys.version is a custom object whose split() method fails.
    """
    class DummyVersion:
        def split(self):
            raise ValueError("split failure")
    monkeypatch.setattr(sys, "version", DummyVersion())
    monkeypatch.setattr(sys, "version_info", (3, 9, 0))
    
    # Provide a dummy sherlock module so that once the version check passes,
    # the call to sherlock.main() would not mask the error raised by sys.version.split()
    dummy_module = types.SimpleNamespace(main=lambda: None)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    with pytest.raises(ValueError, match="split failure"):
        runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
def test_sherlock_main_unicode_output(monkeypatch, capsys):
    """
    Test that __main__ correctly propagates Unicode output from sherlock.main().
    This verifies that if sherlock.main() prints non-ASCII characters (e.g., Japanese text)
    to stdout, they are captured and output as expected.
    """
    # Set a valid Python version.
    monkeypatch.setattr(sys, 'version_info', (3, 9, 0))
    monkeypatch.setattr(sys, 'version', "3.9.0")
    
    # Define a fake main function that prints Unicode text.
    def fake_main():
        print("こんにちは世界")  # "Hello World" in Japanese.
    
    # Insert the dummy module for sherlock.
    dummy_module = types.SimpleNamespace(main=fake_main)
    sys.modules["sherlock_project.sherlock"] = dummy_module
    
    # Run the __main__ module to trigger the execution.
    runpy.run_module("sherlock_project.__main__", run_name="__main__", alter_sys=True)
    
    # Capture and assert that the Unicode output is correctly printed.
    captured = capsys.readouterr().out
    assert "こんにちは世界" in captured