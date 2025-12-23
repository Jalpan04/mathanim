import numpy
print(f"Numpy version: {numpy.__version__}")
try:
    print(f"Nextafter test: {numpy.nextafter(0, 1)}")
    import fastapi
    print("FastAPI imported")
except Exception as e:
    print(f"Error: {e}")
