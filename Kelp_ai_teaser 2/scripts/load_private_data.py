#Imports to circumvent fatal errors
import warnings
warnings.filterwarnings("ignore")

#Function reads .md file to collect data for API
def load_private_data(file_name):
  FILE_TO_READ = file_name
  try:
      with open(FILE_TO_READ, "r", encoding="utf-8") as f:
          file_content = f.read()
  except FileNotFoundError:
      #Fallback if no file found
      print("File not found.")
      return
  return file_content
