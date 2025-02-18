from deliverable2 import URLValidator

# Instantiate the validator
validator = URLValidator()

# Define test inputs
user_prompt = "Is electric vehicle adoption increasing?"
url_to_check = "https://www.iea.org/reports/global-ev-outlook-2023"

# Run the validation function
func_rating = validator.rate_url_validity(user_prompt, url_to_check)
custom_rating = func_rating + 1 if func_rating < 5 else func_rating

# Print the output
print(f"Function Rating: {func_rating}")
print(f"Custom Rating: {custom_rating}")
