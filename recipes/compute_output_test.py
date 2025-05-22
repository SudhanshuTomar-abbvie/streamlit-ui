import os
import logging
import pandas as pd
from io import BytesIO
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class ExcelExtractor:
    """
    Extracts content from Excel files (xlsx, xls) using pandas.
    Can be integrated into the existing document digitization pipeline.
    """
    
    def extract_excel_content(self, file_data: bytes, file_path: str) -> Dict[str, Any]:
        """
        Extract content from Excel files.
        
        Args:
            file_data: Raw bytes of the Excel file
            file_path: Path to the Excel file (used for logging and metadata)
            
        Returns:
            Dict with extracted content:
                - text: Extracted text representation
                - sheets: List of sheet data
                - metadata: File metadata
        """
        try:
            file_name = os.path.basename(file_path)
            logger.info(f"Extracting content from Excel file: {file_name}")
            
            # Create a BytesIO object from file data
            excel_stream = BytesIO(file_data)
            
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(excel_stream)
            sheet_names = excel_file.sheet_names
            
            # Process each sheet
            sheets_data = []
            all_text_content = []
            
            for sheet_name in sheet_names:
                # Read the sheet into a DataFrame
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Handle empty sheets
                if df.empty:
                    sheets_data.append({
                        "sheet_name": sheet_name,
                        "is_empty": True,
                        "text": f"[Sheet '{sheet_name}' is empty]"
                    })
                    all_text_content.append(f"\n--- Sheet: {sheet_name} ---\n[Empty sheet]")
                    continue
                
                # Get sheet content as text
                text_representation = self._dataframe_to_text(df, sheet_name)
                all_text_content.append(text_representation)
                
                # Store sheet data
                sheets_data.append({
                    "sheet_name": sheet_name,
                    "is_empty": False,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                    "text": text_representation
                })
            
            # Create metadata
            metadata = {
                "file_name": file_name,
                "file_path": file_path,
                "file_type": os.path.splitext(file_name)[1].lower(),
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names
            }
            
            # Combine all content
            full_text_content = "\n\n".join(all_text_content)
            
            result = {
                "text": full_text_content,
                "sheets": sheets_data,
                "metadata": metadata
            }
            
            return result
        except Exception as e:
            logger.error(f"Error extracting content from Excel file {file_path}: {e}")
            return {
                "text": f"Error extracting Excel content: {str(e)}",
                "sheets": [],
                "metadata": {"file_name": os.path.basename(file_path), "file_path": file_path, "error": str(e)}
            }
    
    def _dataframe_to_text(self, df: pd.DataFrame, sheet_name: str) -> str:
        """
        Convert a DataFrame to a text representation.
        
        Args:
            df: The pandas DataFrame to convert
            sheet_name: Name of the sheet
            
        Returns:
            str: Text representation of the DataFrame
        """
        # Get dataframe shape
        rows, cols = df.shape
        
        # Start with sheet header
        text_lines = [f"--- Sheet: {sheet_name} ---"]
        text_lines.append(f"Rows: {rows}, Columns: {cols}")
        text_lines.append("")
        
        # Check if DataFrame is too large for complete text extraction
        max_rows = 500
        max_cols = 20
        
        if rows > max_rows or cols > max_cols:
            # For large DataFrames, extract summary and sample data
            text_lines.append("Note: Large sheet - showing sample data and summary")
            text_lines.append("")
            
            # Add column names
            if cols > max_cols:
                # Show truncated column list
                col_sample = list(df.columns[:max_cols])
                text_lines.append(f"Columns (first {max_cols} of {cols}): {', '.join(str(col) for col in col_sample)}...")
            else:
                text_lines.append(f"Columns: {', '.join(str(col) for col in df.columns)}")
            
            # Add sample data (first 50 rows)
            text_lines.append("")
            text_lines.append("Sample data (first rows):")
            
            # Truncate DataFrame for text representation
            sample_df = df.iloc[:min(50, rows), :min(max_cols, cols)]
            
            # Convert sample to string and add to text
            sample_text = sample_df.fillna("").to_string(index=False)
            text_lines.append(sample_text)
            
            # Add data summary
            text_lines.append("")
            text_lines.append("Numerical columns summary:")
            
            # Get summary of numerical columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if not numeric_cols.empty:
                summary_df = df[numeric_cols].describe().round(2)
                summary_text = summary_df.to_string()
                text_lines.append(summary_text)
            else:
                text_lines.append("[No numeric columns found]")
        else:
            # For smaller DataFrames, include full data
            filled_df = df.fillna("")
            text_lines.append(filled_df.to_string(index=False))
        
        return "\n".join(text_lines)


# Integration code for your document processor
def handle_excel_file(file_data, file_path):
    """
    Handler function for Excel files that you can call from your document processor.
    
    Args:
        file_data: Raw bytes of the Excel file
        file_path: Path to the Excel file
        
    Returns:
        Dict with extracted content
    """
    extractor = ExcelExtractor()
    result = extractor.extract_excel_content(file_data, file_path)
    
    # Format result for the combined extracted data format
    combined_data = []
    
    # Add metadata
    metadata = result.get("metadata", {})
    combined_data.append(f"DOCUMENT METADATA:")
    for key, value in metadata.items():
        combined_data.append(f"{key}: {value}")
    combined_data.append("\n")
    
    # Add text content from Excel
    text_content = result.get("text", "")
    if text_content:
        combined_data.append("EXCEL CONTENT:")
        combined_data.append(text_content)
        combined_data.append("\n")
    
    return {
        "text": result.get("text", ""),
        "tables": [{"text": sheet.get("text", ""), "metadata": {"sheet_name": sheet.get("sheet_name", "")}} 
                  for sheet in result.get("sheets", [])],
        "images": [],
        "metadata": result.get("metadata", {})
    }

import os
import platform
import logging
import subprocess
import tempfile
import shutil
import zipfile
import tarfile
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

def download_file(url, destination):
    """Download a file from URL to destination."""
    try:
        logger.info(f"Downloading {url} to {destination}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Successfully downloaded {url}")
        return True
    except Exception as e:
        logger.error(f"Error downloading file from {url}: {e}")
        return False

def extract_archive(archive_path, extract_to, delete_after=True):
    """Extract a zip or tar file and optionally delete it after."""
    try:
        logger.info(f"Extracting {archive_path} to {extract_to}")
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif any(archive_path.endswith(ext) for ext in ['.tar.gz', '.tgz', '.tar.bz2', '.tar.xz', '.tar']):
            with tarfile.open(archive_path) as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            logger.error(f"Unsupported archive format: {archive_path}")
            return False
            
        if delete_after:
            os.remove(archive_path)
        return True
    except Exception as e:
        logger.error(f"Error extracting {archive_path}: {e}")
        return False

def compile_from_source(source_dir, build_dir, install_dir, configure_cmd, make_cmd=None):
    """Compile and install software from source."""
    try:
        # Create build directory
        os.makedirs(build_dir, exist_ok=True)
        
        # Configure
        logger.info(f"Running configure command: {configure_cmd}")
        subprocess.run(configure_cmd, cwd=build_dir, check=True)
        
        # Make and install
        if make_cmd:
            logger.info(f"Running make command: {make_cmd}")
            subprocess.run(make_cmd, cwd=build_dir, check=True)
        else:
            # Default make commands
            logger.info("Running make")
            subprocess.run(["make"], cwd=build_dir, check=True)
            
            logger.info("Running make install")
            subprocess.run(["make", "install"], cwd=build_dir, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during compilation: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during compilation: {e}")
        return False

def install_build_dependencies():
    """Try to install build dependencies for compiling software."""
    system = platform.system().lower()
    
    if system != "linux":
        # We only handle Linux build dependencies for now
        return False
    
    try:
        # Check for common Linux package managers
        if os.path.exists("/etc/debian_version"):
            # Debian/Ubuntu
            try:
                packages = [
                    "build-essential", "cmake", "pkg-config", "libpng-dev", 
                    "libjpeg-dev", "libtiff-dev", "libopenjp2-7-dev",
                    "libfreetype6-dev", "libfontconfig1-dev", "libcairo2-dev"
                ]
                subprocess.run(["apt-get", "update"], check=True)
                subprocess.run(["apt-get", "install", "-y"] + packages, check=True)
                return True
            except Exception as e:
                logger.warning(f"Failed to install build dependencies with apt: {e}")
        
        elif os.path.exists("/etc/redhat-release"):
            # Red Hat/CentOS/Fedora
            try:
                packages = [
                    "gcc", "gcc-c++", "make", "cmake", "pkgconfig", "libpng-devel",
                    "libjpeg-devel", "libtiff-devel", "openjpeg2-devel",
                    "freetype-devel", "fontconfig-devel", "cairo-devel"
                ]
                subprocess.run(["yum", "install", "-y"] + packages, check=True)
                return True
            except Exception as e:
                logger.warning(f"Failed to install build dependencies with yum: {e}")
    
    except Exception as e:
        logger.warning(f"Failed to install build dependencies: {e}")
    
    return False

def install_poppler_from_source():
    """Install poppler by compiling from source."""
    try:
        # Set up directories
        base_dir = os.path.join(os.getcwd(), "poppler_build")
        source_dir = os.path.join(base_dir, "source")
        build_dir = os.path.join(base_dir, "build")
        install_dir = os.path.join(os.getcwd(), "poppler")
        
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(install_dir, exist_ok=True)
        
        # Download poppler source
        poppler_version = "23.08.0"
        poppler_url = f"https://poppler.freedesktop.org/poppler-{poppler_version}.tar.xz"
        archive_path = os.path.join(tempfile.gettempdir(), "poppler.tar.xz")
        
        if not download_file(poppler_url, archive_path):
            # Try alternative mirror
            poppler_url = f"https://sourceforge.net/projects/poppler/files/poppler/{poppler_version}/poppler-{poppler_version}.tar.xz"
            if not download_file(poppler_url, archive_path):
                logger.error("Failed to download poppler source")
                return False
        
        # Extract source
        if not extract_archive(archive_path, source_dir):
            return False
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
        if not extracted_dirs:
            logger.error("Could not find extracted poppler source directory")
            return False
        
        poppler_source_dir = os.path.join(source_dir, extracted_dirs[0])
        
        # Configure and build
        configure_cmd = [
            "cmake",
            poppler_source_dir,
            f"-DCMAKE_INSTALL_PREFIX={install_dir}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DENABLE_UNSTABLE_API_ABI_HEADERS=ON"
        ]
        
        if compile_from_source(poppler_source_dir, build_dir, install_dir, configure_cmd):
            # Add to PATH
            bin_dir = os.path.join(install_dir, "bin")
            logger.info(f"Adding poppler bin directory to PATH: {bin_dir}")
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error installing poppler from source: {e}")
        return False

def install_leptonica_from_source():
    """Install Leptonica library (dependency for Tesseract) from source."""
    try:
        # Set up directories
        base_dir = os.path.join(os.getcwd(), "leptonica_build")
        source_dir = os.path.join(base_dir, "source")
        build_dir = os.path.join(base_dir, "build")
        install_dir = os.path.join(os.getcwd(), "leptonica")
        
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(install_dir, exist_ok=True)
        
        # Download leptonica source
        leptonica_version = "1.83.0"
        leptonica_url = f"https://github.com/DanBloomberg/leptonica/releases/download/{leptonica_version}/leptonica-{leptonica_version}.tar.gz"
        archive_path = os.path.join(tempfile.gettempdir(), "leptonica.tar.gz")
        
        if not download_file(leptonica_url, archive_path):
            logger.error("Failed to download leptonica source")
            return False
        
        # Extract source
        if not extract_archive(archive_path, source_dir):
            return False
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
        if not extracted_dirs:
            logger.error("Could not find extracted leptonica source directory")
            return False
        
        leptonica_source_dir = os.path.join(source_dir, extracted_dirs[0])
        
        # Configure and build
        os.chdir(leptonica_source_dir)
        configure_cmd = [
            "./configure",
            f"--prefix={install_dir}"
        ]
        
        if compile_from_source(leptonica_source_dir, leptonica_source_dir, install_dir, configure_cmd):
            # Set environment variables for Tesseract to find Leptonica
            os.environ["PKG_CONFIG_PATH"] = f"{install_dir}/lib/pkgconfig:{os.environ.get('PKG_CONFIG_PATH', '')}"
            os.environ["LD_LIBRARY_PATH"] = f"{install_dir}/lib:{os.environ.get('LD_LIBRARY_PATH', '')}"
            os.environ["LIBLEPT_HEADERSDIR"] = f"{install_dir}/include"
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error installing leptonica from source: {e}")
        return False

def install_tesseract_from_source():
    """Install Tesseract OCR by compiling from source."""
    try:
        # First install Leptonica (dependency)
        if not install_leptonica_from_source():
            logger.warning("Failed to install Leptonica, Tesseract installation may fail")
        
        # Set up directories
        base_dir = os.path.join(os.getcwd(), "tesseract_build")
        source_dir = os.path.join(base_dir, "source")
        build_dir = os.path.join(base_dir, "build")
        install_dir = os.path.join(os.getcwd(), "tesseract")
        
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(install_dir, exist_ok=True)
        
        # Download tesseract source
        tesseract_version = "5.3.2"
        tesseract_url = f"https://github.com/tesseract-ocr/tesseract/archive/refs/tags/{tesseract_version}.tar.gz"
        archive_path = os.path.join(tempfile.gettempdir(), "tesseract.tar.gz")
        
        if not download_file(tesseract_url, archive_path):
            logger.error("Failed to download tesseract source")
            return False
        
        # Extract source
        if not extract_archive(archive_path, source_dir):
            return False
        
        # Find the extracted directory
        extracted_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
        if not extracted_dirs:
            logger.error("Could not find extracted tesseract source directory")
            return False
        
        tesseract_source_dir = os.path.join(source_dir, extracted_dirs[0])
        
        # Generate configure script (needed for source tarball)
        try:
            logger.info("Running ./autogen.sh")
            subprocess.run(["./autogen.sh"], cwd=tesseract_source_dir, check=True)
        except Exception as e:
            logger.warning(f"Error running autogen.sh: {e}")
            # Continue anyway, it might work with the existing configure script
        
        # Configure and build
        leptonica_dir = os.path.join(os.getcwd(), "leptonica")
        configure_cmd = [
            "./configure",
            f"--prefix={install_dir}",
            f"--with-extra-libraries={leptonica_dir}/lib",
            f"--with-extra-includes={leptonica_dir}/include"
        ]
        
        if compile_from_source(tesseract_source_dir, tesseract_source_dir, install_dir, configure_cmd):
            # Download language data
            lang_dir = os.path.join(install_dir, "share", "tessdata")
            os.makedirs(lang_dir, exist_ok=True)
            
            # Download English language data
            eng_url = "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata"
            eng_path = os.path.join(lang_dir, "eng.traineddata")
            download_file(eng_url, eng_path)
            
            # Add to PATH and set TESSDATA_PREFIX
            bin_dir = os.path.join(install_dir, "bin")
            logger.info(f"Adding tesseract bin directory to PATH: {bin_dir}")
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
            os.environ["TESSDATA_PREFIX"] = lang_dir
            
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error installing tesseract from source: {e}")
        return False

def get_portable_poppler():
    """Download a portable version of poppler based on platform."""
    system = platform.system().lower()
    poppler_path = os.path.join(os.getcwd(), "poppler")
    os.makedirs(poppler_path, exist_ok=True)
    
    if system == "windows":
        # Windows portable version
        poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.07.0-0/Release-23.07.0-0.zip"
    elif system == "linux":
        # Try a more reliable Linux binary build
        poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.07.0-0/Release-23.07.0-0.zip"
    elif system == "darwin":  # macOS
        poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.07.0-0/Release-23.07.0-0.zip"
    else:
        logger.warning(f"Unsupported platform for portable poppler: {system}")
        return False
    
    archive_path = os.path.join(tempfile.gettempdir(), "poppler_portable.zip")
    
    if download_file(poppler_url, archive_path) and extract_archive(archive_path, poppler_path):
        # Find the bin directory (might be nested)
        bin_dir = None
        for root, dirs, files in os.walk(poppler_path):
            if any(f.startswith('pdfinfo') or f.startswith('pdfinfo.exe') for f in files):
                bin_dir = root
                break
        
        # If bin directory not found, try common locations
        if not bin_dir:
            potential_paths = [
                os.path.join(poppler_path, "Library", "bin"),
                os.path.join(poppler_path, "bin"),
                os.path.join(poppler_path, "poppler-23.07.0", "Library", "bin")
            ]
            for path in potential_paths:
                if os.path.exists(path):
                    bin_dir = path
                    break
        
        if bin_dir:
            logger.info(f"Adding poppler bin directory to PATH: {bin_dir}")
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
            return True
    
    logger.warning("Failed to install portable poppler")
    return False

def get_portable_tesseract():
    """Download a portable version of tesseract based on platform."""
    system = platform.system().lower()
    tesseract_path = os.path.join(os.getcwd(), "tesseract")
    os.makedirs(tesseract_path, exist_ok=True)
    
    # Only Windows has readily available portable versions
    if system == "windows":
        tesseract_url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-portable-5.3.1.20230401.zip"
        archive_path = os.path.join(tempfile.gettempdir(), "tesseract_portable.zip")
        
        if download_file(tesseract_url, archive_path) and extract_archive(archive_path, tesseract_path):
            # Find the bin directory
            bin_dir = None
            for root, dirs, files in os.walk(tesseract_path):
                if "tesseract.exe" in files:
                    bin_dir = root
                    break
            
            if bin_dir:
                logger.info(f"Adding tesseract bin directory to PATH: {bin_dir}")
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                
                # Set TESSDATA_PREFIX if tessdata directory exists
                for root, dirs, _ in os.walk(tesseract_path):
                    if "tessdata" in dirs:
                        tessdata_dir = os.path.join(root, "tessdata")
                        logger.info(f"Setting TESSDATA_PREFIX to {tessdata_dir}")
                        os.environ["TESSDATA_PREFIX"] = tessdata_dir
                        break
                
                return True
    
    logger.warning(f"No portable tesseract available for {system}")
    return False

def check_poppler_installed():
    """Check if poppler is installed and in PATH."""
    try:
        system = platform.system().lower()
        check_commands = {
            "windows": ["pdfinfo", "-v"],
            "linux": ["pdfinfo", "-v"],
            "darwin": ["pdfinfo", "-v"] 
        }
        
        command = check_commands.get(system, ["pdfinfo", "-v"])
        
        # Try running the command
        logger.info(f"Checking if poppler is installed using command: {' '.join(command)}")
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        is_installed = result.returncode == 0 or "pdfinfo version" in (result.stdout + result.stderr)
        logger.info(f"Poppler installed: {is_installed}")
        return is_installed
    except Exception as e:
        logger.warning(f"Error checking poppler installation: {e}")
        return False

def check_tesseract_installed():
    """Check if tesseract is installed and in PATH."""
    try:
        logger.info("Checking if tesseract is installed")
        result = subprocess.run(
            ["tesseract", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        is_installed = result.returncode == 0
        logger.info(f"Tesseract installed: {is_installed}")
        return is_installed
    except Exception as e:
        logger.warning(f"Error checking tesseract installation: {e}")
        return False

def install_poppler():
    """Install poppler using the best available method."""
    logger.info("Installing poppler...")
    
    # Try portable version first (easier)
    if get_portable_poppler():
        return True
    
    # Try compiling from source (harder but more likely to work)
    return install_poppler_from_source()

def install_tesseract():
    """Install tesseract using the best available method."""
    logger.info("Installing tesseract OCR...")
    
    # Try portable version first (easier, but limited platforms)
    if get_portable_tesseract():
        return True
    
    # Try compiling from source (harder but more likely to work)
    return install_tesseract_from_source()

def ensure_dependencies_installed():
    """Ensure all dependencies (pandoc, poppler, tesseract) are installed."""
    results = {}
    
    # Check for pandoc
    try:
        import pypandoc
        pandoc_installed = pypandoc.get_pandoc_version() is not None
        logger.info(f"Pandoc installed: {pandoc_installed}")
        
        if not pandoc_installed:
            logger.info("Downloading pandoc binaries...")
            try:
                # Assuming this is from your existing module
                pandoc_tmp_directory = os.getcwd()
                pypandoc.ensure_pandoc_installed(targetfolder=pandoc_tmp_directory)
                pandoc_installed = True
                logger.info("Pandoc binaries downloaded successfully")
            except Exception as e:
                logger.warning(f"Failed to download pandoc binaries: {e}")
        
        results["pandoc"] = pandoc_installed
    except ImportError:
        logger.warning("pypandoc module not available")
        results["pandoc"] = False
    
    # Check for poppler
    poppler_installed = check_poppler_installed()
    if not poppler_installed:
        poppler_installed = install_poppler()
        if poppler_installed:
            logger.info("Poppler installed successfully")
        else:
            logger.warning("Failed to install poppler")
    
    results["poppler"] = poppler_installed
    
    # Check for tesseract
    tesseract_installed = check_tesseract_installed()
    if not tesseract_installed:
        tesseract_installed = install_tesseract()
        if tesseract_installed:
            logger.info("Tesseract OCR installed successfully")
        else:
            logger.warning("Failed to install tesseract OCR")
    
    results["tesseract"] = tesseract_installed
    
    return results

def set_library_environment_variables(base_dir=None):
    """
    Set all necessary environment variables to use poppler, leptonica, and tesseract.
    
    Args:
        base_dir (str, optional): Base directory where libraries are installed.
                                 If None, uses current working directory.
    
    Returns:
        dict: Dictionary of set environment variables and their values
    """
    if base_dir is None:
        base_dir = os.getcwd()
    
    logger.info(f"Setting environment variables for installed libraries in {base_dir}")
    env_vars = {}
    
    # Poppler environment variables
    poppler_dir = os.path.join(base_dir, "poppler")
    if os.path.exists(poppler_dir):
        # Find bin directory
        bin_dir = None
        for potential_bin in [
            os.path.join(poppler_dir, "bin"),
            os.path.join(poppler_dir, "Library", "bin")
        ]:
            if os.path.exists(potential_bin):
                bin_dir = potential_bin
                break
        
        # If still not found, search for it
        if not bin_dir:
            for root, dirs, files in os.walk(poppler_dir):
                if any(f.startswith('pdfinfo') or f.startswith('pdfinfo.exe') for f in files):
                    bin_dir = root
                    break
        
        if bin_dir:
            logger.info(f"Adding poppler bin directory to PATH: {bin_dir}")
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            env_vars["POPPLER_PATH"] = bin_dir
    
    # Leptonica environment variables
    leptonica_dir = os.path.join(base_dir, "leptonica")
    if os.path.exists(leptonica_dir):
        lib_dir = os.path.join(leptonica_dir, "lib")
        include_dir = os.path.join(leptonica_dir, "include")
        pkgconfig_dir = os.path.join(lib_dir, "pkgconfig")
        
        if os.path.exists(lib_dir):
            logger.info(f"Setting Leptonica library paths: {lib_dir}")
            os.environ["LD_LIBRARY_PATH"] = lib_dir + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
            env_vars["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
            
            if os.path.exists(pkgconfig_dir):
                os.environ["PKG_CONFIG_PATH"] = pkgconfig_dir + os.pathsep + os.environ.get("PKG_CONFIG_PATH", "")
                env_vars["PKG_CONFIG_PATH"] = os.environ["PKG_CONFIG_PATH"]
        
        if os.path.exists(include_dir):
            os.environ["LIBLEPT_HEADERSDIR"] = include_dir
            env_vars["LIBLEPT_HEADERSDIR"] = include_dir
    
    # Tesseract environment variables
    tesseract_dir = os.path.join(base_dir, "tesseract")
    if os.path.exists(tesseract_dir):
        # Find bin directory
        bin_dir = os.path.join(tesseract_dir, "bin")
        
        # If standard bin doesn't exist, search for it
        if not os.path.exists(bin_dir):
            for root, dirs, files in os.walk(tesseract_dir):
                if "tesseract" in files or "tesseract.exe" in files:
                    bin_dir = root
                    break
        
        if os.path.exists(bin_dir):
            logger.info(f"Adding tesseract bin directory to PATH: {bin_dir}")
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
            env_vars["TESSERACT_PATH"] = bin_dir
        
        # Find tessdata directory
        tessdata_dir = None
        potential_paths = [
            os.path.join(tesseract_dir, "share", "tessdata"),
            os.path.join(tesseract_dir, "tessdata")
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                tessdata_dir = path
                break
        
        # If still not found, search for it
        if not tessdata_dir:
            for root, dirs, _ in os.walk(tesseract_dir):
                if "tessdata" in dirs:
                    tessdata_dir = os.path.join(root, "tessdata")
                    break
        
        if tessdata_dir:
            logger.info(f"Setting TESSDATA_PREFIX to {tessdata_dir}")
            os.environ["TESSDATA_PREFIX"] = tessdata_dir
            env_vars["TESSDATA_PREFIX"] = tessdata_dir
    
    # Print summary of set environment variables
    logger.info("Environment variables set:")
    for var, value in env_vars.items():
        logger.info(f"  {var} = {value}")
    
    return env_vars

# Example usage:
# env_vars = set_library_environment_variables()
# Example usage
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     results = ensure_dependencies_installed()
#     print(f"Dependencies installed: {results}")

import os
import logging
from io import BytesIO
import base64
import pandas as pd
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple

import dataiku
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title
from unstructured.staging.base import elements_to_json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseDigitizer:
    """
    Base class for document digitization that handles file reading from a Dataiku Folder.
    """
    def __init__(self, folder_id: str):
        """
        Initialize the digitizer with a Dataiku folder.
        
        Args:
            folder_id: The ID of the Dataiku folder containing the documents
        """
        self.data_source = dataiku.Folder(folder_id)
    
    def get_file_data(self, file_path: str) -> bytes:
        """
        Reads file data from the Dataiku Folder.
        
        Args:
            file_path: Path to the file within the Dataiku folder
            
        Returns:
            bytes: The file content as bytes
        """
        with self.data_source.get_download_stream(file_path) as f:
            return f.read()

class UnstructuredDigitizer(BaseDigitizer):
    """
    Digitizes documents using the Unstructured library to extract content.
    """
    def __init__(self, folder_id: str, llm_model_id: str = "custom:iliad-plugin-conn-prod:Claude_3_5_Sonnet"):
        """
        Initialize the Unstructured digitizer.
        
        Args:
            folder_id: The ID of the Dataiku folder containing the documents
            llm_model_id: The ID of the LLM model to use for image description
        """
        super().__init__(folder_id)
        self.llm_model_id = llm_model_id
        
        # Initialize Dataiku LLM client
        self.client = dataiku.api_client()
        self.project = self.client.get_default_project()
        try:
            self.llm_model = self.project.get_llm(self.llm_model_id)
            logger.info(f"Successfully initialized LLM model: {self.llm_model_id}")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM model: {e}")
            self.llm_model = None
    
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract all content from a document using Unstructured.
        
        Args:
            file_path: Path to the file within the Dataiku folder
            
        Returns:
            Dict with keys:
                - text: Extracted text content
                - tables: Extracted tables
                - images: List of extracted images with descriptions
                - metadata: Document metadata
        """
        try:
            file_data = self.get_file_data(file_path)
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Handle Excel files separately
            if file_ext in ['.xlsx', '.xls']:
                #from excel_extractor import handle_excel_file  # Import the module you added
                return handle_excel_file(file_data, file_path)
            
            # Create a BytesIO object from the file data
            file_stream = BytesIO(file_data)
            
            # Extract elements using Unstructured
            elements = partition(
                file=file_stream,
                file_filename=file_name,
                strategy="auto",
                include_metadata=True,
                extract_images_in_pdf=True,
                extract_image_block_types=["Image"],
                extract_tables=True
            )
            
            # Process extracted elements
            text_elements = []
            table_elements = []
            image_elements = []
            
            for element in elements:
                element_type = element.category
                
                if element_type == "Table":
                    table_elements.append(element)
                elif element_type == "Image":
                    image_elements.append(element)
                elif element_type in ["Title", "NarrativeText", "Text", "ListItem", "Header"]:
                    text_elements.append(element)
            
            # Process text content
            text_content = "\n".join([element.text for element in text_elements])
            
            # Process tables
            tables = []
            for table_element in table_elements:
                tables.append({
                    "text": table_element.text,
                    "metadata": table_element.metadata.to_dict() if hasattr(table_element, "metadata") else {}
                })
            
            # Process images and get descriptions using Dataiku LLM
            images = []
            for image_element in image_elements:
                image_data = {}
                if hasattr(image_element, "metadata") and hasattr(image_element.metadata, "image_base64"):
                    image_data["image_base64"] = image_element.metadata.image_base64
                    if self.llm_model:
                        image_data["description"] = self._describe_image(image_element.metadata.image_base64)
                    else:
                        image_data["description"] = "Image description not available (LLM model not configured)"
                images.append(image_data)
            
            # Get document metadata
            metadata = {
                "file_name": file_name,
                "file_path": file_path,
                "file_type": file_ext,
                "page_count": len(set([e.metadata.page_number for e in elements if hasattr(e, "metadata") and hasattr(e.metadata, "page_number")])),
            }
            
            # Create structured output
            result = {
                "text": text_content,
                "tables": tables,
                "images": images,
                "metadata": metadata
            }
            
            return result
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return {
                "text": f"Error extracting content: {str(e)}",
                "tables": [],
                "images": [],
                "metadata": {"file_name": os.path.basename(file_path), "file_path": file_path, "error": str(e)}
            }
    
    def _describe_image(self, image_base64: str) -> str:
        """
        Generate a description for an image using Dataiku's LLM integration.
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            str: Description of the image
        """
        try:
            if not self.llm_model:
                return "Image description not available (LLM model not configured)"
            
            # Create a completion request
            completion = self.llm_model.new_completion()
            mp_message = completion.new_multipart_message()
            
            # Add text instructions and image data
            mp_message.with_text("Please provide a detailed description of this image, including all visible text, elements, and context.")
            mp_message.with_text(f"Here is the image in base64 format:\n{image_base64}")
            mp_message.add()
            
            # Execute the completion request
            logger.info("Executing LLM request for image description...")
            resp = completion.execute()
            
            # Extract response text
            if resp.success and hasattr(resp, "text"):
                return resp.text
            else:
                logger.warning(f"LLM request failed or unexpected response format: {resp}")
                return "Unable to generate image description"
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return f"Error generating image description: {str(e)}"
    
    def combine_extracted_data(self, extracted_data: Dict[str, Any]) -> str:
        """
        Combine all extracted data into a single text column.
        
        Args:
            extracted_data: Dictionary containing text, tables, and images
            
        Returns:
            str: Combined extracted data as a single text string
        """
        combined = []
        
        # Add metadata
        metadata = extracted_data.get("metadata", {})
        combined.append(f"DOCUMENT METADATA:")
        for key, value in metadata.items():
            combined.append(f"{key}: {value}")
        combined.append("\n")
        
        # Add text content
        text_content = extracted_data.get("text", "")
        if text_content:
            combined.append("TEXT CONTENT:")
            combined.append(text_content)
            combined.append("\n")
        
        # Add tables
        tables = extracted_data.get("tables", [])
        if tables:
            combined.append("TABLE CONTENT:")
            for i, table in enumerate(tables):
                combined.append(f"Table {i+1}:")
                combined.append(table.get("text", ""))
                combined.append("")
            combined.append("\n")
        
        # Add images with descriptions
        images = extracted_data.get("images", [])
        if images:
            combined.append("IMAGE CONTENT:")
            for i, image in enumerate(images):
                combined.append(f"Image {i+1} Description:")
                combined.append(image.get("description", "No description available"))
                combined.append("")
        
        return "\n".join(combined)


class DocumentProcessor:
    """
    Processes documents in a folder by extracting content using the UnstructuredDigitizer.
    """
    def __init__(self, input_folder_id: str, llm_model_id: str = "custom:iliad-plugin-conn-prod:Claude_3_5_Sonnet", 
                 max_workers: int = 10):
        """
        Initialize the document processor.
        
        Args:
            input_folder_id: The ID of the Dataiku folder containing the documents
            llm_model_id: The ID of the LLM model to use for image description
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.input_folder_id = input_folder_id
        self.digitizer = UnstructuredDigitizer(input_folder_id, llm_model_id)
        self.max_workers = max_workers or os.cpu_count()
        logger.info(f"Initialized DocumentProcessor with {self.max_workers} workers")
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single document file.
        
        Args:
            file_path: Path to the file within the Dataiku folder
            
        Returns:
            Dict: Processed document data
        """
        try:
            file_name = os.path.basename(file_path)
            logger.info(f"Processing file: {file_name}")
            
            # Extract content using the digitizer
            extracted_data = self.digitizer.extract_content(file_path)
            
            # Combine all extracted data into a single text field
            combined_data = self.digitizer.combine_extracted_data(extracted_data)
            
            # Prepare result
            result = {
                "file_name": file_name,
                "file_path": file_path,
                "extracted_data": combined_data,
                "metadata": str(extracted_data.get("metadata", {})),
                "processing_status": "success"
            }
            
            logger.info(f"Completed processing file: {file_name}")
            return result
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "extracted_data": f"Error processing file: {str(e)}",
                "metadata": "{}",
                "processing_status": "error"
            }
    
    def process_all_files(self, file_list: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Process all files in the input folder in parallel.
        
        Args:
            file_list: List of file paths to process. If None, all files in the folder are processed.
            
        Returns:
            pd.DataFrame: DataFrame containing the extracted data
        """
        # If no file list is provided, get all files from the folder
        if file_list is None:
            data_source = dataiku.Folder(self.input_folder_id)
            file_list = data_source.list_paths_in_partition()
        
        logger.info(f"Starting parallel processing of {len(file_list)} files with {self.max_workers} workers")
        processed_data = []
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {executor.submit(self.process_file, file_path): file_path 
                             for file_path in file_list}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    data = future.result()
                    processed_data.append(data)
                    logger.info(f"Added results for {os.path.basename(file_path)}")
                except Exception as e:
                    logger.error(f"Exception processing {file_path}: {e}")
                    # Add error information to the results
                    processed_data.append({
                        "file_name": os.path.basename(file_path),
                        "file_path": file_path,
                        "extracted_data": f"Error in parallel processing: {str(e)}",
                        "metadata": "{}",
                        "processing_status": "error"
                    })
        
        logger.info(f"Completed processing all {len(file_list)} files")
        return pd.DataFrame(processed_data)


def main():
    """
    Main function to run the document digitization pipeline.
    Example usage in a Dataiku recipe.
    """
    logging.basicConfig(level=logging.INFO)
    results = ensure_dependencies_installed()
    print(f"Dependencies installed: {results}")
    set_library_environment_variables()
    # Get input and output datasets from Dataiku
    input_folder = "Input" #dataiku.get_custom_variables().get("input_folder", "input_documents")
    output_dataset = "output_test" #dataiku.get_custom_variables().get("output_dataset", "extracted_document_data")
    
    # Get LLM model ID from custom variables or use default
    llm_model_id = "custom:iliad-plugin-conn-prod:Claude_3_5_Sonnet" #dataiku.get_custom_variables().get("llm_model_id", "custom:iliad-plugin-conn-prod:Claude_3_5_Sonnet")
    
    # Configure parallel processing
    max_workers = 10 #int(dataiku.get_custom_variables().get("max_workers", 10))
    
    # Initialize the document processor
    processor = DocumentProcessor(
        input_folder_id=input_folder,
        llm_model_id=llm_model_id,
        max_workers=max_workers
    )
    
    # Process all documents
    results_df = processor.process_all_files()
    print(results_df)
    # Write results to the output dataset
    output = dataiku.Dataset(output_dataset)
    output.write_with_schema(results_df)
    
    logger.info(f"Document digitization pipeline completed. Processed {len(results_df)} files.")


if __name__ == "__main__":
    main()
    