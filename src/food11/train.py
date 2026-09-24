import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


# ---------------------------------------------------------
# Command-line arguments
# ---------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Train ResNet18 on Food-11")

    parser.add_argument(
        "--dataset",
        type=str,
        choices=["mini", "processed"],
        default="mini",
        help="Dataset to use: mini or processed",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs",
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size",
    )

    return parser.parse_args()


# ---------------------------------------------------------
# Evaluate model
# ---------------------------------------------------------
def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    average_loss = total_loss / total
    accuracy = correct / total

    return average_loss, accuracy


# ---------------------------------------------------------
# Main training function
# ---------------------------------------------------------
def main():
    args = parse_args()

    # Choose CPU or GPU automatically
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"Using device: {device}")

    # -----------------------------------------------------
    # Dataset paths
    # -----------------------------------------------------
    if args.dataset == "mini":
        data_dir = Path("data/food11_processed_mini")
    else:
        data_dir = Path("data/food11_processed")

    train_dir = data_dir / "training"
    val_dir = data_dir / "validation"
    test_dir = data_dir / "evaluation"

    # -----------------------------------------------------
    # Image transforms
    # -----------------------------------------------------
    transform = transforms.Compose(
        [
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    # -----------------------------------------------------
    # Load datasets
    # -----------------------------------------------------
    train_dataset = datasets.ImageFolder(
        train_dir,
        transform=transform,
    )

    val_dataset = datasets.ImageFolder(
        val_dir,
        transform=transform,
    )

    test_dataset = datasets.ImageFolder(
        test_dir,
        transform=transform,
    )

    # -----------------------------------------------------
    # DataLoaders
    # -----------------------------------------------------
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
    )

    print(f"Training images: {len(train_dataset)}")
    print(f"Validation images: {len(val_dataset)}")
    print(f"Evaluation images: {len(test_dataset)}")
    print(f"Classes: {train_dataset.classes}")

    # -----------------------------------------------------
    # Load pretrained ResNet18
    # -----------------------------------------------------
    model = models.resnet18(
        weights=models.ResNet18_Weights.DEFAULT
    )

    # Replace final layer:
    # original ResNet18 -> 1000 classes
    # Food-11 -> 11 classes
    number_of_features = model.fc.in_features
    model.fc = nn.Linear(number_of_features, 11)

    model = model.to(device)

    # -----------------------------------------------------
    # Loss function and optimizer
    # -----------------------------------------------------
    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    # -----------------------------------------------------
    # MLflow setup
    # -----------------------------------------------------
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    # -----------------------------------------------------
    # Start MLflow run
    # -----------------------------------------------------
    with mlflow.start_run():

        # Log fixed hyperparameters
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
            }
        )

        # -------------------------------------------------
        # Training loop
        # -------------------------------------------------
        for epoch in range(args.epochs):

            model.train()

            running_loss = 0.0
            total_training_samples = 0

            for images, labels in train_loader:

                images = images.to(device)
                labels = labels.to(device)

                # Clear old gradients
                optimizer.zero_grad()

                # Forward pass
                outputs = model(images)

                # Calculate loss
                loss = criterion(outputs, labels)

                # Backpropagation
                loss.backward()

                # Update model weights
                optimizer.step()

                running_loss += loss.item() * images.size(0)
                total_training_samples += images.size(0)

            # Average training loss
            train_loss = running_loss / total_training_samples

            # ---------------------------------------------
            # Validation
            # ---------------------------------------------
            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            # ---------------------------------------------
            # Log epoch metrics to MLflow
            # ---------------------------------------------
            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Accuracy: {val_accuracy:.4f}"
            )

        # -------------------------------------------------
        # Final evaluation
        # -------------------------------------------------
        _, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        print(f"Final Test Accuracy: {test_accuracy:.4f}")

        # Log final test accuracy
        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        # -------------------------------------------------
        # Save trained model in MLflow
        # -------------------------------------------------
        mlflow.pytorch.log_model(
            model,
            "model",
            serialization_format="pickle",
        )
        

        

        print("Training completed and results logged to MLflow.")


if __name__ == "__main__":
    main()