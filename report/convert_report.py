import pypandoc
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
source_file = os.path.join(script_dir, 'report.md')

# ODT conversion
odt_file = os.path.join(script_dir, 'report.odt')
odt_args = ['--toc']
reference_odt = os.path.join(script_dir, 'reference.odt')
if os.path.exists(reference_odt):
    print(f"Using reference doc from: {reference_odt}")
    odt_args.append(f'--reference-doc={reference_odt}')

print(f"Converting to {odt_file}...")
try:
    pypandoc.convert_file(source_file, 'odt', outputfile=odt_file, extra_args=odt_args)
    print(f"Created {odt_file}")
except Exception as e:
    print(f"ODT conversion failed: {e}")

# DOCX conversion
docx_file = os.path.join(script_dir, 'report.docx')
docx_args = ['--toc']
reference_docx = os.path.join(script_dir, 'reference.docx')
if os.path.exists(reference_docx):
    print(f"Using reference doc from: {reference_docx}")
    docx_args.append(f'--reference-doc={reference_docx}')

print(f"Converting to {docx_file}...")
try:
    pypandoc.convert_file(source_file, 'docx', outputfile=docx_file, extra_args=docx_args)
    print(f"Created {docx_file}")
except Exception as e:
    print(f"DOCX conversion failed: {e}")
