import sys

def get_error_message(error, error_detail:sys):
    _,_,exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = f"The exception occured in a script {file_name} at line {line_number} with an error message {error_message}"
    return error_message

class CustomException(Exception):
    def __init__(self, error_message, error_detail):
        super().__init__(error_message)
        self.error_message = get_error_message(error_message=error_message, error_detail=error_detail)

    def __str__(self) -> str:
        return self.error_message