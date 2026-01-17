"""
Contract Processor Module

Handles PDF file processing and text extraction from contract documents.
Uses PyMuPDF (fitz) for reliable PDF text extraction.
"""

import fitz  # PyMuPDF
import logging
import os

logger = logging.getLogger(__name__)


class ContractProcessor:
    """
    Handles all PDF-related operations for contract analysis.
    
    This class provides methods to:
    - Extract text from PDF files
    - Validate PDF files before processing
    - Handle errors gracefully
    """

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract all text from a PDF contract file.
        
        This method opens the PDF file and extracts text from every page,
        combining them into a single string. Each page is marked with a
        page number for reference.
        
        Args:
            file_path (str): Absolute path to the PDF file
                Example: "/media/contracts/service_agreement.pdf"
        
        Returns:
            str: All extracted text from the PDF
                Example: "--- Page 1 ---\nScope of Services...\n--- Page 2 ---\nPayment Terms..."
        
        Raises:
            ValueError: If file cannot be read or is not a valid PDF
                - File does not exist
                - File is corrupted or not a valid PDF
                - No text could be extracted from the PDF
        
        Example:
            >>> processor = ContractProcessor()
            >>> text = processor.extract_text_from_pdf("/path/to/contract.pdf")
            >>> print(text[:100])  # First 100 characters
            "--- Page 1 ---\nScope of Services..."
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

            # Open PDF file
            doc = fitz.open(file_path)
            
            # Extract text from all pages
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.get_text()
            
            # Close the document
            doc.close()
            
            # Validate that we got some text
            if not text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            # Log success
            char_count = len(text)
            word_count = len(text.split())
            logger.info(
                f"Successfully extracted {char_count} characters "
                f"({word_count} words) from PDF: {file_path}"
            )
            
            return text
            
        except fitz.FileError as e:
            logger.error(f"PDF file error for {file_path}: {str(e)}")
            raise ValueError(f"Invalid PDF file: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def validate_pdf(file_path: str) -> bool:
        """
        Validate that a file is a readable PDF.
        
        This method checks if the file exists, can be opened as a PDF,
        and contains at least one page.
        
        Args:
            file_path (str): Path to the file to validate
        
        Returns:
            bool: True if valid PDF, False otherwise
                - Does not raise exceptions (returns False on error)
                - Safe to use before attempting to extract text
        
        Example:
            >>> processor = ContractProcessor()
            >>> if processor.validate_pdf("/path/to/file.pdf"):
            ...     text = processor.extract_text_from_pdf("/path/to/file.pdf")
            ... else:
            ...     print("File is not a valid PDF")
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                return False
            
            # Try to open as PDF
            doc = fitz.open(file_path)
            
            # Check if it has at least one page
            is_valid = doc.page_count > 0
            
            # Close the document
            doc.close()
            
            if is_valid:
                logger.debug(f"PDF validation passed: {file_path}")
            else:
                logger.warning(f"PDF has no pages: {file_path}")
            
            return is_valid
            
        except Exception as e:
            logger.warning(f"PDF validation failed for {file_path}: {str(e)}")
            return False
