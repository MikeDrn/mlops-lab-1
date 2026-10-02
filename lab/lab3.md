Question 1: Open the "Models" tab in the mlflow UI. What version number was your model given? What's the difference between a run's logged model artifact and a registered model?

Version Number: Version 1.  

 Difference between Logged Model Artifact and Registered Model:A Logged Model Artifact is a raw, read-only file output (weights, environment configs, structure) tied permanently to a specific execution run (/mlruns/...). 
 
   A Registered Model is a centralized, logical asset managed in the MLflow Model Registry. It provides unique version numbers, lifecycle tracking, tags, and mutable aliases (e.g., champion) pointing to logged artifacts across runs. 

==============

Question 2: What aliases replaced the old built-in stages in mlflow? Why version a model separately from the run that produced it, and why is an alias more flexible than a fixed stage name?

Aliases replacing old stages: Mutable Aliases (such as champion, challenger, or custom tags) replaced the rigid, deprecated stages (Staging, Production, Archived).   Why version separately & why aliases are flexible:A training run records an experiment attempt; a registered model version represents a vetted software deployment unit.   Aliases act as dynamic pointers. Serving systems reference models:/food11@champion instead of static version numbers or run IDs. Switching deployment to a new model simply requires updating where champion points, requiring zero code changes or redeployments in production.

==============

Question 3: Why load the model through an mlflow model URI (`models:/food11@champion`) instead of pointing directly at the `.pth` file on disk? What would you have to change to serve a newer model version?

Why load via models:/food11@champion instead of .pth directly: Hardcoding a path to a .pth file locks the application to a local file location and raw PyTorch execution. Loading via models:/food11@champion decouples application code from storage mechanics, providing automatic serialization checks, dependency validation, and environment isolation.   How to serve a newer model version: Simply update the champion alias in the MLflow Model Registry UI to point to the new model version. Restarting or refreshing the serving application will fetch the updated version automatically without requiring code changes or redeployments.  

==============

Question 4: Why copy `pyproject.toml`/`uv.lock` and run `uv sync` *before* copying the rest of the source code, instead of copying everything at once? What happens to the build cache when you only change a line in `serve.py`?           

Why copy dependency files before source code: Docker builds images layer-by-layer and caches each layer based on file modifications. Dependencies rarely change compared to source code. By copying pyproject.toml and uv.lock first, Docker caches the heavy uv sync step.   What happens when serve.py changes: Docker reuses cached layers for Python setup and dependencies, executing only the fast source copying step (COPY src/ ./src/). Rebuilds take seconds instead of re-downloading packages.  

==============

Question 5: What's the size difference between a naive single-stage image and your multi-stage one? Use `docker history <image>` to see which layers are the biggest.

 "Multi-stage: ~1.9 GB, naive: ~3 or 4GB. docker history shows the venv copy (1.75 GB, mostly PyTorch) is by far the biggest layer; the slim base is only ~133 MB and my code is 53 kB."
==============

Question 6: What happens to build speed and image size if you forget the `.dockerignore`? Which of the excluded folders would actually break the build if they were sent to the Docker daemon?

Effect of missing .dockerignore: The Docker daemon transfers the entire project context—including heavy local datasets (data/), experiment caches (mlruns/), and virtual environments (.venv/)—to the build process. This drastically slows build times and bloats image size.  

Folders that break the build: Sending a host-compiled local .venv/ into the Docker build will corrupt or conflict with Linux binaries inside the container. 
==============

Question 7: Why can't the container simply use `127.0.0.1:5000` to reach the mlflow server on your host? What does `host.docker.internal` resolve to?


Why container cannot use 127.0.0.1:5000: 127.0.0.1 inside a container resolves to the container's isolated loopback network interface, not the host operating system.   What host.docker.internal resolves to: A special DNS host name provided by Docker Desktop that resolves to the host machine's internal gateway IP address, allowing containerized applications to reach host-managed services like the local MLflow tracking server. 
==============

Question 8: Stop the container and start a new one from the same image. Does the model still load correctly without you rebuilding? What does that tell you about what's baked into the image versus fetched at runtime?

Does model load without rebuilding: Yes, the model loads successfully.   Baked versus Fetched at runtime: The image bakes code, API routes, and execution dependencies. Model metadata and weights are fetched at runtime over the network from the remote MLflow server via host.docker.internal:5000 during application startup.
==============

Question 9: The Dockerfile and image are versioned differently — one lives in git, the other doesn't (yet). What's still missing before another machine (like a CI runner or a Kubernetes cluster) could reliably pull and run the exact image you just built?

What is missing before remote runners (CI / Kubernetes) can pull the image:Container Image Registry Hosting: The built image exists only on your local machine daemon. It must be tagged and pushed to a remote registry (such as Docker Hub, GitHub Container Registry ghcr.io, Amazon ECR, or Google Artifact Registry).   Remote MLflow Tracking / Artifact Storage: The container requires access to a shared MLflow tracking server and artifact store (like S3/GCS) instead of referencing local host resources (host.docker.internal). 

