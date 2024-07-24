import os
import datetime

EXCLUDED_DIRS = {'venv', '.venv', 'history', '__pycache__', 'snapshot', '.old'}


def get_file_info(file_path):
    """Get file information including size and modification time."""
    stats = os.stat(file_path)
    return {
        "size": stats.st_size,
        "modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }


def process_py_files(file_list, output_file, summary_stats):
    """Process Python files in the given file list."""
    for py_file in file_list:
        if not os.path.isfile(py_file):
            print(f"File {py_file} does not exist.")
            continue

        summary_stats['file_count'] += 1
        file_info = get_file_info(py_file)

        output_file.write(f"File: {os.path.basename(py_file)}\n")
        output_file.write(f"Path: {os.path.abspath(py_file)}\n")
        output_file.write(f"Size: {file_info['size']} bytes\n")
        output_file.write(f"Modified: {file_info['modified']}\n\n")

        with open(py_file, 'r') as file:
            lines = file.readlines()
            summary_stats['total_lines'] += len(lines)
            for i, line in enumerate(lines, start=1):
                output_file.write(f"{i:4d}: {line}")

        output_file.write("\n" + "-" * 40 + "\n\n")


def generate_map(root_dir):
    """Generate the project structure map."""
    project_map = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        depth = dirpath.replace(root_dir, "").count(os.sep)
        indent = ' ' * 4 * depth
        project_map.append(f"{indent}{os.path.basename(dirpath)}/")
        subindent = ' ' * 4 * (depth + 1)
        for filename in filenames:
            if filename.endswith('.py'):
                project_map.append(f"{subindent}{filename}")
    return project_map


def write_header(output_file, current_date):
    header = [
        "Application Structure Overview:\n\n",
        "This document contains a snapshot of all Python files in the root directory and specified subdirectories of the application.\n",
        f"Timestamp: {current_date}\n\n"
    ]
    output_file.writelines(header)


def main():
    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    parent_folder = os.path.basename(os.getcwd())
    output_dir = "snapshot"
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, f"{parent_folder}_python_files_{current_date}.txt")

    summary_stats = {
        'file_count': 0,
        'total_lines': 0
    }

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        write_header(output_file, current_date)
        output_file.write("Application Structure Overview:\n\n")
        output_file.write(
            "This document contains a snapshot of all Python files in the root directory and specified subdirectories of the application.\n")
        output_file.write(f"Timestamp: {current_date}\n\n")
        output_file.write("-" * 40 + "\n\n")

        output_file.write("Requirements and IDE Information:\n")
        output_file.write("IDE: Visual Studio Code\n")
        output_file.write("Python version: 3.x\n")
        output_file.write(
            "Project Requirements: Ensure all Python files in specified directories are processed with line numbers and summary statistics.\n\n")
        output_file.write("-" * 40 + "\n\n")

        output_file.write("Project Structure:\n")
        project_map = generate_map(".")
        for line in project_map:
            output_file.write(line + "\n")

        output_file.write("-" * 40 + "\n\n")

        file_paths = [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(".")
                      for filename in filenames if
                      filename.endswith('.py') and not any(excluded in dirpath for excluded in EXCLUDED_DIRS)]
        process_py_files(file_paths, output_file, summary_stats)

        output_file.write("Summary Statistics:\n")
        output_file.write(f"Total number of files processed: {summary_stats['file_count']}\n")
        output_file.write(f"Total number of lines of code: {summary_stats['total_lines']}\n")

    print(f"Python files snapshot has been saved to {output_file_path}")
    print(f"Total number of files processed: {summary_stats['file_count']}")
    print(f"Total number of lines of code: {summary_stats['total_lines']}")


if __name__ == "__main__":
    main()
