Question 1: Open the "Models" tab in the mlflow UI. What version number was your model given? What's the difference between a run's logged model artifact and a registered model?

Version number is version 1.  

Difference between Logged Model Artifact and Registered Model:attached to the execution run (/mlruns/...).
 
Registered Model is a logical entity residing in the MLflow Model Registry with a version number, lifecycle, and tag support along with the mutable alias (champion) pointing to the logged artifact.

==============

Question 2: What aliases replaced the old built-in stages in mlflow? Why version a model separately from the run that produced it, and why is an alias more flexible than a fixed stage name?

New aliases replacing old stages: Mutable Aliases (such as champion, challenger...) replaced the deprecated stages (Staging, Production, Archived).   

The training run is an instance of an experiment being attempted, while a registered model version is a validated deployment unit for the software.Aliases are dynamic pointers.Serving systems refer to models:/food11@champion rather than a fixed version number or run ID.The only thing that needs to be changed when deploying a new model is changing who the champion points to.

==============

Question 3: Why load the model through an mlflow model URI (`models:/food11@champion`) instead of pointing directly at the `.pth` file on disk? What would you have to change to serve a newer model version?

Hardcoding a path to a .pth file locks the application to a local file location and raw PyTorch execution.

Models that are loaded using models:/food11@champion separate the application logic from storage mechanisms, offering serialization, dependency, and environment validation automatically. 

Steps for serving an upgraded model: All I need to do is change the champion alias through the MLflow UI to refer to the new model version. I don't need to make any change in the code, just restart or refresh the application.

==============

Question 4: Why copy `pyproject.toml`/`uv.lock` and run `uv sync` *before* copying the rest of the source code, instead of copying everything at once? What happens to the build cache when you only change a line in `serve.py`?           

The process of building Docker images is layer-based and caching each layer depending on the modified files. Dependencies are less prone to changes than the source code. This way, we copy pyproject.toml and uv.lock files first, and Docker will cache our heavy synchronization process of uv files.

if serve.py is changed, docker reuses the cached layers to set up the Python environment and copy only the source code (COPY src/ ./src/).
Rebuilding takes less time because it won't re-download packages.  

==============

Question 5: What's the size difference between a naive single-stage image and your multi-stage one? Use `docker history <image>` to see which layers are the biggest.

Multi-stage: ~1.9 GB, naive: ~3 or 4GB. docker history shows the venv copy (1.75 GB, mostly PyTorch) is by far the biggest layer, the slim base is only ~133 MB and my code is 53 kB

==============

Question 6: What happens to build speed and image size if you forget the `.dockerignore`? Which of the excluded folders would actually break the build if they were sent to the Docker daemon?

Effect of missing .dockerignore: The Docker daemon transfers the entire project including heavy local datasets (data/), experiment caches (mlruns/), and virtual environments (.venv/) to the build process. This will cause slower builds and makes images larger.  

Folders that break the build: Sending a host-compiled local .venv/ into the Docker build will corrupt or conflict with Linux binaries inside the container. 

==============

Question 7: Why can't the container simply use `127.0.0.1:5000` to reach the mlflow server on your host? What does `host.docker.internal` resolve to?

Why container cannot use 127.0.0.1:5000: Because 127.0.0.1 from within a container refers to the loopback interface of the container and not the one of the host operating system.   

host.docker.internal resolves to an internal DNS host name offered by Docker Desktop which will resolve to the internal IP address of the gateway of the host machine.

==============

Question 8: Stop the container and start a new one from the same image. Does the model still load correctly without you rebuilding? What does that tell you about what's baked into the image versus fetched at runtime?

Does model load without rebuilding: Yes, the model loads successfully.   

Baked versus Fetched at runtime: The image bakes code, API routes, and execution dependencies. Model metadata and weights are fetched at runtime over the network from the remote MLflow server via host.docker.internal:5000 during application startup.

==============

Question 9: The Dockerfile and image are versioned differently — one lives in git, the other doesn't (yet). What's still missing before another machine (like a CI runner or a Kubernetes cluster) could reliably pull and run the exact image you just built?

What is lacking before the CI/Kubernetes pulls the image:Container Image Registry Hosting: The built image is available on my machine only. It needs to be tagged and uploaded to a remote registry (like docker hub, GitHub Container Registry). 

MLflow Tracking / Artifact Storage: The container needs access to a remote MLflow tracking server/artifact store rather than using host resources (host.docker.internal).
