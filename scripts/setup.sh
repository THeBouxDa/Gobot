#!/bin/bash


TARGET_FILE="./private/secrets.json"

# Create the folder (and parents) if it doesn't exist
echo "Creating any missing directories and files.."
mkdir -p "./data/raw/characters"
mkdir -p "./private"
mkdir -p "./logs"


if [ ! -f "$TARGET_FILE" ]; then
    cat << EOF > "$TARGET_FILE" 
{
    "token": "INSERT YOUR TOKEN HERE",
    "test_guild_ids": {},
    "authorized_users": {}
}
EOF
fi


if ! command -v uv &> /dev/null; then
        echo "'uv' is not installed or not added to your PATH."
        echo "Attempting install:"
        curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "Synchronizing project dependencies..."
uv sync

echo "Locking dependencies..."
uv lock

echo "Setup complete."