#!/bin/bash

# --- Configuration ---
# Set the desired name for the virtual environment directory
VENV_NAME="my_project_venv"

# Set the path where the virtual environment will be created
# e.g., use '.' for the current directory, or a specific path
VENV_PATH="." # Creates the VENV_NAME directory in the current location
VENV_DIR="$VENV_PATH/$VENV_NAME"

# Set the name of the requirements file
REQUIREMENTS_FILE="requirements.txt"
# --- End Configuration ---


# 1. Check if the requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: Requirements file '$REQUIREMENTS_FILE' not found!"
    echo "Please create this file and list your dependencies (e.g., requests, numpy==1.22.0) inside it."
    exit 1
fi

echo "--- Setting up Environment ---"

# 2. Create the virtual environment
echo "Creating virtual environment at: $VENV_DIR"
python3 -m venv "$VENV_DIR"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment."
    exit 1
fi

# 3. Activate the virtual environment
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

echo "Activating virtual environment..."
# Source the activation script to set up the environment in the script's shell
source "$ACTIVATE_SCRIPT"

# 4. Install dependencies from the requirements file
echo "Installing packages from $REQUIREMENTS_FILE..."
# The -r flag tells pip to read the list of packages from the specified file
python3 -m pip install -r "$REQUIREMENTS_FILE"

# 5. Check for installation success
if [ $? -eq 0 ]; then
    echo ""
    echo "SUCCESS: All dependencies installed successfully."
else
    echo ""
    echo "ERROR: Package installation failed. Check the logs above for specific package errors."
    # Exit the script with an error code
    exit 1
fi

echo ""
echo "--- Next Steps ---"
echo "The virtual environment '$VENV_NAME' has been created and packages are installed."
echo "To manually activate it in your current terminal, run:"
echo "source $ACTIVATE_SCRIPT"
echo "------------------"
