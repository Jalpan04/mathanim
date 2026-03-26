import unittest
import subprocess
import os
from pathlib import Path

class TestMathAnimIntegration(unittest.TestCase):
    
    def setUp(self):
        self.scenes_dir = Path("generated_scenes")
        self.scenes_dir.mkdir(exist_ok=True)

    def test_01_docker_hello(self):
        """Test if the Docker container can run basic Python."""
        filename = "test_hello.py"
        filepath = self.scenes_dir / filename
        with open(filepath, "w") as f:
            f.write("print('Hello Integration!')")
            
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{self.scenes_dir.resolve()}:/app/scenes",
            "mathanim-renderer",
            "python3", f"/app/scenes/{filename}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello Integration!", result.stdout)

    def test_02_docker_sympy_support(self):
        """Test if SymPy is installed in the container (Fix Verification)."""
        filename = "test_sympy.py"
        filepath = self.scenes_dir / filename
        with open(filepath, "w") as f:
            f.write("import sympy; print(f'SymPy Version: {sympy.__version__}')")
            
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{self.scenes_dir.resolve()}:/app/scenes",
            "mathanim-renderer",
            "python3", f"/app/scenes/{filename}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"\nSymPy Test Failed. Stderr: {result.stderr}")
            
        self.assertEqual(result.returncode, 0, "SymPy import failed! Docker image might not be built yet.")
        self.assertIn("SymPy Version", result.stdout)

    def test_03_critic_syntax_checker(self):
        """Test the mocked Critic's syntax checking logic."""
        import ast
        
        valid_code = "x = 1\nprint(x)"
        invalid_code = "x = 1\nprint(x" # Missing paren
        
        # Valid should pass
        try:
            ast.parse(valid_code)
        except SyntaxError:
            self.fail("Valid code raised SyntaxError")
            
        # Invalid should look like this
        with self.assertRaises(SyntaxError):
            ast.parse(invalid_code)

if __name__ == '__main__':
    unittest.main()
