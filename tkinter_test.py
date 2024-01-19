import subprocess
import io
import os
import tempfile

# Create a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
    tmp_filename = tmp_file.name

# Take a screenshot and save it to the temporary file
try:
    subprocess.run(["screencapture", "-i", tmp_filename])
except Exception as e:
    print(f"Error occurred: {e}")
    exit(1)

# Read the screenshot from the temporary file into a BytesIO object
try:
    with open(tmp_filename, 'rb') as f:
        img_byte_arr = io.BytesIO(f.read())
    
    # Check if the BytesIO object is not empty
    if img_byte_arr.getbuffer().nbytes > 0:
        print("Screenshot captured and stored in bytes stream.")
    else:
        print("No data captured in the screenshot.")

finally:
    # Clean up the temporary file
    os.remove(tmp_filename)
