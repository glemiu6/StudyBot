import glob
import os


def choose_file(folder: str = "files") -> str | None:
    files = glob.glob(os.path.join(folder, "*"))

    if not files:
        print("No files found.")
        return None

    print("\nAvailable files:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {os.path.basename(f)}")

    while True:
        choice = input("\nChoose a file number or press q to quit: ").strip()

        if choice.lower() == "q":
            return None

        if not choice.isdigit():
            print("Please enter a number.")
            continue

        idx = int(choice)

        if 1 <= idx <= len(files):
            return files[idx - 1]

        print("Invalid choice.")


if __name__ == "__main__":
    choose_file()