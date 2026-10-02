Question 1: Look at pyproject.toml and uv.lock. What changed?

pyproject.toml: Updated to explicitly list the new project dependencies (mlflow, torch, torchvision, scikit-learn)   

uv.lock: Updated with the dependency graph and resolved versions (including sub-dependencies) to ensure reproducible environment builds across machines. 

