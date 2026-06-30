***credit report generator - takes a json input with company financial data and generates a structured pdf credit report with sections for auditors, financials, annexure and disclaimer***


**how to setup a project :-**
1. clone the repository
2. create and activate virtual environment
3. install requirements from requirements.txt
4. run command ***python -m report_generator*** (here i have already saved the sample_input json in the code itself so by default it will take that path)
4. if file is in another path then run command ***python -m report_generator --input {sample input path} --output {sample output path}***
eg. 
*python -m report_generator --input /Users/ayushchaurasia/Desktop/credit_manager/credit_report_generator/sample_input.json --output /Users/ayushchaurasia/Desktop/credit_manager/credit_report_generator/sample_output.pdf*


**what i have used and how render_report works :-**
1. *pydantic* - used for validating the input json against SampleInputModel schema before passing it to the pdf generator
2. *reportlab* - used for generating the pdf (tables, paragraphs, page layout, table of contents, etc.)
3. *pathlib* - used for handling file paths in a cross platform way
4. *canvas* - 
    a. _PageCanvas extends reportlab canvas to draw header, footer and watermark on every page
    b. showPage saves each page state so total page count is known before drawing, save() loops over all states and draws "Page N of M" on each
    c. _canvas_factory bakes company name and report metadata into the canvas class and passes it to multiBuild as canvasmaker

**render_report(input_json_path, output_pdf_path) :-**
1. takes input json path and output pdf path (both have defaults pointing to sample_input.json and sample_output.pdf inside the project)
2. loads and validates the json using pydantic, if file not found or json is invalid it prints the error and returns None
3. if validation passes it calls generate_pdf with the validated data and the output path
4. returns the output path on success so the caller knows where the file was saved


**file structure :-**
1. *__main__.py* - entry point for python -m report_generator, parses cli arguments and calls render_report
2. *utils.py* - has render_report and load_input_json, also holds the default input and output paths
3. *schemas.py* - all pydantic models that define the shape of the input json (company, auditors, financials, annexure, etc.), used for validation
4. *pdf_generator.py* - core pdf building logic, CreditPdfMaker class builds each section and assembles the final pdf
5. *styles.py* - all styling constants (colours, page dimensions, paragraph styles) used across pdf_generator
6. *settings.py* - holds BASE_DIR (root path of the project)
7. *__init__.py* - marks the folder as a python package
