#Imports to circumvent fatal errors
import warnings
warnings.filterwarnings("ignore")

#Function reads .md file to collect data for API
def load_private_data(file_name):
  try:
      with open(file_name, "r", encoding="utf-8") as f:
          file_content = f.read().strip()

  #Fallbacks for errors
  except FileNotFoundError:
      print(f"Error: File '{file_name}' not found.")
      return None
  except PermissionError:
      print(f"Error: Permission denied to read '{file_name}'.")
      return None
  except UnicodeDecodeError:
      print(f"Error: Unable to decode '{file_name}'. File may not be UTF-8 encoded.")
      return None
  except Exception as e:
      print(f"Error reading file: {str(e)}")
      return None
    
  return file_content
