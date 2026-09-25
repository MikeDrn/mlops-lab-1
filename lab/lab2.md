Question 1: Look at pyproject.toml and uv.lock. What changed?

pyproject.toml: Now it lists also the new project dependencies (mlflow, torch, torchvision, scikit-learn) with their constraints.   

uv.lock: Updated with the complete dependency graph and resolved versions (including sub-dependencies). 

=========================

Question 2: What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata mlflow stores and the artifacts it stores?

--backend-store-uri: Contains the storage location for metadata (like the run IDs, hyperparameter values, metric logs per epoch, execution status). In this case, it uses an SQLite database

--default-artifact-root: Contains the directory path where MLflow stores artifacts (heavy output files like trained model, images, or plots).

The difference between Metadata and Artifacts is that Metadata is structured, lightweight tabular data (parameters and scalars like loss values) it acts like the description of the experiment, whereas artifacts are heavy, unstructured binary files produced during training (like the model weights and plots).

=========================

Question 3: Why shouldn't `mlflow.db` and `mlruns/` be tracked by git, and why shouldn't they be tracked by dvc either?

mlflow.db and mlruns/ represent machine-local execution logs and binary outputs, not source code (so they do not belong in Git) nor raw/processed datasets (so they do not belong in DVC). Tracking them in Git would make the repository huge, while MLflow already manages artifact location and retrieval without needing DVC pointers.

=========================

Question 4: What happens the first time you call `set_experiment` with a name that doesn't exist yet? Check the mlflow UI.

Calling mlflow.set_experiment("food11") for the first time automatically registers a new experiment named "food11" in MLflow, assigning it a new unique Experiment ID which is "1" in my case.

=========================

Question 5: What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?

mlflow.log_param logs static, fixed configurations set before the execution (--lr or --batch-size).

mlflow.log_metric logs dynamic scalar values produced during or after execution (for example loss or accuracy). log_metric accepts a step parameter to allow plotting scalar changes over time/epochs.

=========================

Question 6: Open the run in the mlflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?

The model artifact is stored under the local MLflow artifact directory ./mlruns, inside the artifact directory associated with that specific run.
For example mine is in: C:\Users\User\Documents\mlops-lab-1\mlruns\1\models

=========================

Question 7: In the mlflow UI, open the `food11` experiment. Select these runs and click "Compare". Which learning rate gave the best `val_accuracy`? Is higher always better?

Best Learning Rate: 0.0001 (for validation accuracy equal to 0.710).

No, a higher learning rate is not always better. For example, the learning rate 0.01 resulted in a much lower validation accuracy of 0.151.

=========================

Question 8: Use the parallel coordinates plot on the compare page to look at `lr`, `batch_size` and `val_accuracy` together. What pattern do you see?

Lower learning rate drives higher performance: The lines ending at the top of the val_accuracy axis all originate from lr = 0.0001. 
Higher learning rates (lr = 0.001 and lr = 0.01) are going down towards lower accuracy.

Smaller batch size performs better at low lr: Holding lr = 0.0001 constant, batch_size = 32 reached higher accuracy (0.710) compared to batch_size = 64 (0.568).

Optimal Path: The top performing path in red connects:

batch_size =32 -> lr=0.0001 -> val_accuracy = 0.710

=========================

Question 9: Sort the runs table by `val_accuracy` descending. Which run is the best one? Note its run ID, you'll need it in the next lab.

Best run ID: 3fd29c1c943c40a98a9df727291a4992
Best run name: amazing-frog-464
Validation accuracy: 0.710

ID: 72b9b6db5a5a4f0e8200dbaa51362728
validation accuracy: 0.5693430656934306

ID: d14590b9c75a44d28a5dd3b9c36fc971
validation accuracy: 0.5684306569343066

ID: 6548ad30e48c411b94ef169f84fd4ac5
validation accuracy: 0.15054744525547445
