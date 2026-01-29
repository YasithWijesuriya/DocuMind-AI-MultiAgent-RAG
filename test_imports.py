#!/usr/bin/env python3
"""
test_imports.py - Verify all Starlette + LangChain + dependent imports work correctly
Run this before deploying to Vercel to catch import errors early
"""

import sys
import traceback

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(msg):
    print(f"\n{BOLD}{msg}{RESET}")
    print("=" * 60)

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def test_import(module_name, import_path):
    """Test if a module can be imported"""
    try:
        module = __import__(import_path, fromlist=[""])
        print_success(f"{module_name}")
        return True
    except ImportError as e:
        print_error(f"{module_name}: {e}")
        return False
    except Exception as e:
        print_error(f"{module_name}: {type(e).__name__}: {e}")
        return False

def main():
    print_header("Python Environment Check")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    # Test 1: Web Framework
    print_header("1. Web Framework")
    tests = [
        ("Starlette", "starlette"),
        ("Uvicorn", "uvicorn"),
        ("Pydantic", "pydantic"),
    ]
    for name, path in tests:
        if test_import(name, path):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(name)
    
    # Test 2: LangChain Core
    print_header("2. LangChain Core Modules")
    tests = [
        ("LangChain", "langchain"),
        ("LangChain Core", "langchain_core"),
        ("LangChain Community", "langchain_community"),
        ("LangChain OpenAI", "langchain_openai"),
        ("LangChain Pinecone", "langchain_pinecone"),
        ("LangChain Text Splitters", "langchain_text_splitters"),
        ("LangSmith", "langsmith"),
        ("LangGraph", "langgraph"),
    ]
    for name, path in tests:
        if test_import(name, path):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(name)
    
    # Test 3: Document Processing
    print_header("3. Document Processing")
    tests = [
        ("UnstructuredPDFLoader", "langchain_community.document_loaders"),
        ("PyPDF", "pypdf"),
        ("BeautifulSoup", "bs4"),
        ("Pandas", "pandas"),
        ("Numpy", "numpy"),
    ]
    for name, path in tests:
        if test_import(name, path):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(name)
    
    # Test 4: Vector Store & Embeddings
    print_header("4. Vector Store & Embeddings")
    tests = [
        ("Pinecone Client", "pinecone"),
        ("OpenAI Embeddings", "langchain_openai.embeddings"),
    ]
    for name, path in tests:
        if test_import(name, path):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(name)
    
    # Test 5: Environment & Configuration
    print_header("5. Environment & Config")
    tests = [
        ("python-dotenv", "dotenv"),
        ("Requests", "requests"),
        ("Packaging", "packaging"),
        ("Pillow", "PIL"),
    ]
    for name, path in tests:
        if test_import(name, path):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(name)
    
    # Test 6: Critical Imports (Deep)
    print_header("6. Critical Deep Imports")
    critical_imports = [
        ("ChatOpenAI", lambda: __import__("langchain_openai", fromlist=["ChatOpenAI"]).ChatOpenAI),
        ("UnstructuredPDFLoader", lambda: __import__("langchain_community.document_loaders", fromlist=["UnstructuredPDFLoader"]).UnstructuredPDFLoader),
        ("PineconeVectorStore", lambda: __import__("langchain_pinecone", fromlist=["PineconeVectorStore"]).PineconeVectorStore),
        ("Pinecone", lambda: __import__("pinecone", fromlist=["Pinecone"]).Pinecone),
    ]
    for name, fn in critical_imports:
        try:
            fn()
            print_success(f"{name}")
            results["passed"] += 1
        except Exception as e:
            print_error(f"{name}: {type(e).__name__}: {str(e)[:100]}")
            results["failed"] += 1
            results["errors"].append(name)
    
    # Test 7: Versions
    print_header("7. Version Info")
    version_checks = [
        ("pydantic", "pydantic", "__version__"),
        ("langchain", "langchain", "__version__"),
        ("langchain-core", "langchain_core", "__version__"),
        ("langsmith", "langsmith", "__version__"),
    ]
    for display_name, module_name, attr in version_checks:
        try:
            module = __import__(module_name, fromlist=[attr])
            version = getattr(module, attr, "unknown")
            print_success(f"{display_name}: {version}")
        except Exception as e:
            print_warning(f"{display_name}: Could not determine version ({e})")
    
    # Summary
    print_header("Summary")
    total = results["passed"] + results["failed"]
    percentage = (results["passed"] / total * 100) if total > 0 else 0
    print(f"Total tests: {total}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success rate: {percentage:.1f}%")
    
    if results["failed"] == 0:
        print(f"\n{GREEN}{BOLD}✅ All imports successful! Safe to deploy.{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}❌ {results['failed']} import(s) failed:{RESET}")
        for error in results["errors"]:
            print(f"  - {error}")
        print(f"\n{YELLOW}Fix the errors above before deploying to Vercel.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
