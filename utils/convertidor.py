#pip install docx2pdf

from docx2pdf import convert
import os

def convierto_docx2pdf(nombre_documento, path_documento):
    docx_path = os.path.join(path_documento, nombre_documento)
    
    if not os.path.isfile(docx_path):
        print(f"Archivo no encontrado: {docx_path}")
        return None
    
    # Nombre para el archivo PDF
    nombre_sin_extension = os.path.splitext(nombre_documento)[0]
    pdf_path = os.path.join(path_documento, f"{nombre_sin_extension}.pdf")
    
    try:
        convert(docx_path, pdf_path)
        print(f"Archivo convertido exitosamente: {pdf_path}")
    except Exception as e:
        print(f"Error al convertir el documento: {e}")
        return None

    nombre_documento_pdf = f"{nombre_sin_extension}.pdf"

    return nombre_documento_pdf
