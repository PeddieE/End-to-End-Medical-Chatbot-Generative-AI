import os

pdf_file_path = "Data/The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf"

if os.path.exists(pdf_file_path):
    print(f"✅ The file '{pdf_file_path}' exists!")
else:
    print(f"❌ Error: The file '{pdf_file_path}' does NOT exist at this location.")
    print("Please check:")
    print("1. Is there a folder named 'Data' in the same directory as your Python script?")
    print("2. Is the PDF file exactly named 'The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf' (case-sensitive) inside that 'Data' folder?")
    print(f"Your current working directory is: {os.getcwd()}")