import re
import subprocess
from pathlib import Path


class ConvertError(Exception):
    """Error when convert docx to pdf"""

    pass


def convert_docx_to_pdf(docx_file_path: Path, pdf_file_folder: Path) -> str:
    """
    Convert docx to pdf
    :return pdf file full path
    """
    if not (docx_file_path.exists() and docx_file_path.is_file()):
        raise FileNotFoundError(f"File {docx_file_path} not found")

    if not pdf_file_folder.exists():
        pdf_file_folder.mkdir(parents=True)

        # raise FileNotFoundError(f"Directory {pdf_file_folder} not found")

    completed = subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(pdf_file_folder), str(docx_file_path)],
        check=True,
        text=True,
        capture_output=True,
    )

    if completed.stderr:
        raise ConvertError(completed.stderr)

    # may be needed...
    if completed.returncode != 0:
        raise ConvertError(f"error code: {completed.returncode}")

    # get last file name from stdout
    if completed.stdout:
        stdout_splited = re.search(r"\s*convert\s*(\S+)\s*->\s*(\S+).+:\s*(\S+)", completed.stdout)
        pdf_out_file = stdout_splited[2]

    else:
        pdf_out_file = ""

    return pdf_out_file
