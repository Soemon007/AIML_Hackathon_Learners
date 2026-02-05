import warnings
warnings.filterwarnings("ignore")


def load_private_data(file_name):
  FILE_TO_READ = file_name
  try:
      with open(FILE_TO_READ, "r", encoding="utf-8") as f:
          file_content = f.read()
  except FileNotFoundError:
      print("File not found.")
      return
  return file_content