from fastapi import UploadFile


def validate_solidity_file(file: UploadFile) -> None:
    if not file.filename.endswith(".sol"):
        raise ValueError(f"Unsupported file type for {file.filename}. Only .sol is allowed.")
