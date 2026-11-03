"""Forward previous terminal commands to the English application."""
import runpy

if __name__ == "__main__":
    runpy.run_module("sdg.__main__", run_name="__main__")
