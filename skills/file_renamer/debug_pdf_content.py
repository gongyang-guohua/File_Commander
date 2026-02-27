import pypdf
import sys

def debug_pdf(filepath):
    print(f"--- Debugging Content of {filepath} ---")
    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for i, page in enumerate(reader.pages[:2]): 
            page_text = page.extract_text()
            print(f"-- Page {i+1} --")
            print(repr(page_text[:500])) # Print representation to see weird chars
            text += page_text + "\n"
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_pdf(sys.argv[1])
