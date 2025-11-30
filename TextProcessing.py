import json
import io

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB in bytes

def convert_uploaded_json_to_fileobj(uploaded_file, delimiter="\n\n---\n\n"):
    """
    Parses uploaded JSON/JSONL and returns a list of file objects (BytesIO),
    each guaranteed to be under 50 MB.
    """

    raw = uploaded_file.read().decode("utf-8").strip()

    # Try format 1 — JSON list: [ {recipe}, ... ]
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            recipes = data
        else:
            recipes = [data]
    except json.JSONDecodeError:
        recipes = []

    # Try format 2 — JSONL or multiple objects
    if not recipes:
        recipes = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                recipes.append(obj)
            except json.JSONDecodeError:
                pass

    if not recipes:
        raise ValueError("Uploaded file is not valid JSON or JSONL")

    # Convert to text blocks
    def recipe_to_text(recipe):
        parts = [
            f"Title: {recipe.get('recipe_title', '')}",
            f"Category: {recipe.get('category', '')} / {recipe.get('subcategory', '')}",
            f"Description: {recipe.get('description', '')}",
            "Ingredients:",
            "\n".join(f"- {ing}" for ing in recipe.get("ingredients", [])),
            "Directions:",
            "\n".join(f"{i+1}. {step}" for i, step in enumerate(recipe.get("directions", []))),
        ]
        return "\n".join(parts)

    blocks = [recipe_to_text(r) for r in recipes]

    # -------------------------
    # SPLIT INTO <50MB CHUNKS
    # -------------------------
    files = []
    current_buffer = []
    current_size = 0
    file_index = 1

    for block in blocks:
        block_bytes = (block + delimiter).encode("utf-8")
        block_size = len(block_bytes)

        # If adding this block exceeds 50 MB, finalize current file
        if current_size + block_size > MAX_FILE_SIZE and current_buffer:
            text_output = "".join(current_buffer)
            fileobj = io.BytesIO(text_output.encode("utf-8"))
            fileobj.seek(0)
            fileobj.name = f"recipes_part_{file_index}.txt"
            fileobj.content_type = "text/plain"
            files.append(fileobj)

            # Reset for next file
            file_index += 1
            current_buffer = []
            current_size = 0

        # Add the block to the current file buffer
        current_buffer.append(block + delimiter)
        current_size += block_size

    # Final file
    if current_buffer:
        text_output = "".join(current_buffer)
        fileobj = io.BytesIO(text_output.encode("utf-8"))
        fileobj.seek(0)
        fileobj.name = f"recipes_part_{file_index}.txt"
        fileobj.content_type = "text/plain"
        files.append(fileobj)

    return files
