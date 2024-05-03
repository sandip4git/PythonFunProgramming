def format_strings_with_single_quotes(input_string):
    # Split the input string by commas
    string_list = input_string.split(',')

    # Add single quotes around each string
    formatted_list = [f"'{s.strip()}'" for s in string_list]

    # Join the formatted strings with commas
    formatted_string = ', '.join(formatted_list)

    return formatted_string

# Example usage:
def main():    
    input_strings = "APPLE, BANANA,ORANGE,GRAPE"

    input_strings=input_strings.split(", ")

    lowercase_list = [s.lower() for s in input_strings]

    result = ', '.join(lowercase_list)

    formatted_result = format_strings_with_single_quotes(result)    
        
    print(formatted_result)  # Output: 'apple', 'banana', 'orange', 'grape'

main()
