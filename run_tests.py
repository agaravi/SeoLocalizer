# run_tests.py
import pytest
import os
import sys

def run_all_tests():
    """
    Ejecuta todos los tests en el directorio de tests e imprime un resumen claro.
    """
    print("Iniciando la ejecución de los tests ...\n")

    # Define el directorio de los tests
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')

    # Añade el directorio 'backend' al PYTHONPATH para que los imports funcionen
    # Esto es crucial cuando ejecutas desde la raíz del proyecto o desde un nivel superior
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # Captura la salida de pytest
    # -v: verbose output
    # -s: allow stdout/stderr to be displayed (for print statements in tests)
    # --tb=no: no traceback for failures (can be overwhelming for screenshots)
    # --reruns 2 --reruns-delay 1: retry failed tests (optional, remove if not desired)
    # --json-report: generate a JSON report (useful for programmatic analysis, not directly for screenshot)
    # --json-report-file=: specify output file for JSON report
    
    # Using pytest.main() to run tests programmatically
    # The return code indicates success (0) or failure (non-zero)
    
    # To get the summary that's easy to screenshot, we'll run it directly.
    # We can suppress intermediate output if needed, but for a clear summary,
    # verbose output is usually good.

    # pytest.main() returns an exit code.
    exit_code = pytest.main([
        tests_dir,
        '-v', # Verbose output
        '-s', # Allow print statements to show
        '--tb=short', # Short traceback for failures
        '--color=yes' # Ensure colored output if terminal supports it
    ])

    print("\n\n--- Resumen de la ejecución de tests ---")
    if exit_code == 0:
        print("✅ Todos los tests han pasado exitosamente")
    else:
        print(f"❌ Se encontraron fallos en los tests. Código de salida: {exit_code}")
    print("------------------------------------------")

    return exit_code

if __name__ == "__main__":
    run_all_tests()