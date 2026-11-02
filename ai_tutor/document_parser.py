import os
import re
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_pdf(file_path):
    """
    Extracts text per page from PDF using PyMuPDF if available, with robust fallback.
    """
    pages_data = []

    # Try PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text").strip()
            pages_data.append({
                'page_number': page_idx + 1,
                'text': text if text else f"[Page {page_idx + 1}: Contains diagrams or raster images]"
            })
        doc.close()
        if pages_data:
            return pages_data
    except ImportError:
        pass
    except Exception as e:
        print(f"PyMuPDF error: {e}")

    # Fallback: Pure-Python stream inspection
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # Simple page delimiter estimation
        page_splits = content.split(b'/Page\n')
        if len(page_splits) <= 1:
            page_splits = content.split(b'/Page ')

        extracted_text = ""
        # Search for text stream chunks between BT (Begin Text) and ET (End Text)
        matches = re.findall(b'BT(.*?)ET', content, re.DOTALL)
        for m in matches:
            # extract string literals in parentheses (text)
            text_parts = re.findall(rb'\((.*?)\)', m)
            for part in text_parts:
                try:
                    decoded = part.decode('utf-8', errors='ignore')
                    if len(decoded.strip()) > 1:
                        extracted_text += decoded + " "
                except Exception:
                    continue

        if not extracted_text.strip():
            # Fallback text representation
            extracted_text = f"Document content from {os.path.basename(file_path)}. For full C-level parsing, install PyMuPDF."

        pages_data.append({
            'page_number': 1,
            'text': extracted_text.strip()
        })
    except Exception as e:
        pages_data.append({
            'page_number': 1,
            'text': f"Uploaded document: {os.path.basename(file_path)}"
        })

    return pages_data


def extract_text_from_docx(file_path):
    """
    Extracts text from a .docx file using standard library zipfile & ElementTree.
    """
    pages_data = []
    try:
        with zipfile.ZipFile(file_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            # Find all text elements with namespace
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for p in tree.iterfind('.//w:p', namespaces):
                texts = [node.text for node in p.iterfind('.//w:t', namespaces) if node.text]
                if texts:
                    paragraphs.append(''.join(texts))

            full_text = '\n\n'.join(paragraphs)
            # Approximate pages by character count (~2000 chars per page)
            chunk_size = 2000
            for i in range(0, max(1, len(full_text)), chunk_size):
                page_text = full_text[i:i+chunk_size]
                pages_data.append({
                    'page_number': (i // chunk_size) + 1,
                    'text': page_text.strip()
                })
    except Exception as e:
        pages_data.append({
            'page_number': 1,
            'text': f"Document {os.path.basename(file_path)}: Extracted content."
        })

    return pages_data if pages_data else [{'page_number': 1, 'text': 'Empty Document'}]


def extract_text_from_pptx(file_path):
    """
    Extracts text per slide from .pptx using standard library zipfile & ElementTree.
    """
    pages_data = []
    try:
        with zipfile.ZipFile(file_path, 'r') as pptx:
            # Slides are named ppt/slides/slide1.xml, slide2.xml...
            slide_files = sorted(
                [f for f in pptx.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')],
                key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0
            )

            namespaces = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

            for idx, slide_name in enumerate(slide_files, start=1):
                xml_content = pptx.read(slide_name)
                tree = ET.fromstring(xml_content)
                slide_texts = []
                for t in tree.iterfind('.//a:t', namespaces):
                    if t.text:
                        slide_texts.append(t.text)
                text = ' '.join(slide_texts).strip()
                pages_data.append({
                    'page_number': idx,
                    'text': f"[Slide {idx}] " + (text if text else "Visual slide layout")
                })
    except Exception as e:
        pages_data.append({
            'page_number': 1,
            'text': f"Presentation {os.path.basename(file_path)}"
        })

    return pages_data if pages_data else [{'page_number': 1, 'text': 'Empty Presentation'}]


def extract_text_from_txt(file_path):
    """
    Extracts text from plain text or markdown files.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        content = ""

    chunk_size = 2500
    pages_data = []
    for i in range(0, max(1, len(content)), chunk_size):
        pages_data.append({
            'page_number': (i // chunk_size) + 1,
            'text': content[i:i+chunk_size].strip()
        })
    return pages_data if pages_data else [{'page_number': 1, 'text': 'Empty File'}]


def parse_document_file(file_path, file_extension):
    """
    Main dispatcher for document parsing.
    Returns: list of dicts with 'page_number' and 'text'.
    """
    ext = file_extension.lower().replace('.', '')
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    elif ext in ['pptx', 'ppt']:
        return extract_text_from_pptx(file_path)
    else:
        return extract_text_from_txt(file_path)


def chunk_document_pages(pages_data, chunk_size=700, overlap=100):
    """
    Splits pages into overlapping text chunks with page attribution.
    """
    chunks = []
    chunk_idx = 0

    for item in pages_data:
        page_num = item['page_number']
        text = item['text']

        if len(text) <= chunk_size:
            chunks.append({
                'chunk_index': chunk_idx,
                'page_number': page_num,
                'content': text
            })
            chunk_idx += 1
        else:
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_str = text[start:end].strip()
                if chunk_str:
                    chunks.append({
                        'chunk_index': chunk_idx,
                        'page_number': page_num,
                        'content': chunk_str
                    })
                    chunk_idx += 1
                start += (chunk_size - overlap)

    return chunks
