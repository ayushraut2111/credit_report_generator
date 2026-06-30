how to setup a project :-
1. clone the repository
2. create and activate virtual environment
3. install requirements from requirements.txt
4. run command python -m report_generator (here i have already saved the sample_input json in the code itself so by default it will take that path)
4. if file is in another path then run command python -m report_generator --input {sample input path} --output {sample output path}
eg. 
python -m report_generator --input /Users/ayushchaurasia/Desktop/credit_manager/credit_report_generator/sample_input.json --output /Users/ayushchaurasia/Desktop/credit_manager/credit_report_generator/sample_output.pdf