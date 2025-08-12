import os
import sys

def create_python_file_with_dynamic_s2_fallback():
    """
    Creates a new Python (.py) file whose content is exactly
    as specified by the user, with a dynamic S2 filename fallback.
    The generated file will be placed in the same directory as this script.
    """
    print("--- Python Script Generator for S2 Runner ---")

    # 1. Ask the user for the S2 file name to be embedded as a fallback
    s2_filename_to_embed = input("Enter the default S2 filename for the *generated* Python script (e.g., my_program.s2): ").strip()
    if not s2_filename_to_embed:
        s2_filename_to_embed = "code.s2" # Default fallback if user enters nothing
        print(f"No S2 filename entered. Using default: '{s2_filename_to_embed}' for the generated script.")

    # Determine the directory where *this* generator script is located
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the name of the Python file that *this* script will create
    # And construct its full path to ensure it's in the same directory
    output_filename_base = "run_s2_script.py" # You can change this output filename
    output_python_filepath = os.path.join(current_script_dir, output_filename_base)

    # 2. Define the exact content for the *new* Python file.
    #    The f-string ensures that the s2_filename_to_embed is placed correctly.
    script_content_lines = [
        "import s2_interpreter",
        "import sys",
        "import os",
        "",
        "if __name__ == \"__main__\":",
        "    if len(sys.argv) > 1:",
        "        filename = sys.argv[1]",
        "    else:",
        f"        filename = \"{s2_filename_to_embed}\"  # Fallback to the user-specified S2 filename",
        "    script_dir = os.path.dirname(os.path.abspath(__file__))",
        "    filepath = os.path.join(script_dir, filename)",
        "    with open(filepath) as f:",
        "        s2_interpreter.run_s_code(f.read().splitlines())"
    ]

    # Prepare content for writing to the file, ensuring each line has a newline
    content_to_write = [line + "\n" for line in script_content_lines]

    # Check if the output Python file already exists and will be overwritten
    if os.path.exists(output_python_filepath):
        print(f"File '{output_filename_base}' already exists in '{current_script_dir}' and will be overwritten.")

    try:
        # Write the content to the new Python file at the determined path
        with open(output_python_filepath, "w") as f:
            f.writelines(content_to_write)
        print(f"\nSuccessfully created '{output_filename_base}' in the same directory: '{current_script_dir}'.")
        print(f"The generated script will use '{s2_filename_to_embed}' as its default S2 file if no argument is provided.")
        print(f"You can now run it: python {output_filename_base} [optional_s2_filename]")
    except IOError as e:
        print(f"Error creating file '{output_filename_base}' at '{output_python_filepath}': {e}")

if __name__ == "__main__":
    create_python_file_with_dynamic_s2_fallback()
