import yaml
import os
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO

yaml_file_path = 'resources/job_parameters.yml'  # Update this path

def parse_parameters_to_output(parameters):
    """Convert parameters list to the desired output format"""
    output_lines = []
    for param in parameters:
        name = param['name']
        value = param['default']
        # Format the line based on value type
        if isinstance(value, bool):
            line = f"{name} = {str(value).lower()}"
        elif isinstance(value, (int, float)) or (isinstance(value, str) and not value.isdigit() and value not in ['true', 'false']):
            line = f"{name} = {value}"
        else:
            line = f"{name} = \"{value}\""
        output_lines.append(line)
    return "\n".join(output_lines)

# Calculate next Monday's date
today = datetime.now()
next_monday = today + relativedelta(weekday=MO(+1))
next_monday_str = next_monday.strftime('%Y-%m-%d')

print(f"Next Monday's date: {next_monday_str}")

# Read the YAML file
with open(yaml_file_path, 'r') as file:
    content = file.read()

# Parse the YAML content
try:
    yaml_data = yaml.safe_load(content)
except yaml.YAMLError as e:
    print(f"Error parsing YAML: {e}")
    sys.exit(1)

# Get parameters before updating (for the output)
parameters = yaml_data.get('variables', {}).get('parameters_credit', {}).get('default', [])
parameters_output = parse_parameters_to_output(parameters)

updated = False
for param in parameters:
    if param.get('name') == 'REFERENCE_DATE':
        old_date = param.get('default')
        param['default'] = next_monday_str.strip("'")
        updated = True
        print(f"Updated REFERENCE_DATE from {old_date} to {next_monday_str}")
        break

if not updated:
    print("Could not find REFERENCE_DATE in the YAML structure")
    sys.exit(1)

# Write back to the file without quotes on strings
with open(yaml_file_path, 'w') as file:
    yaml.dump(yaml_data, file, default_flow_style=False, sort_keys=False)

# Create outputs for GitHub Actions
with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f"next_monday={next_monday_str}\n")
    f.write(f"branch_name=update-reference-date-{next_monday_str}\n")
    f.write(f"old_date={old_date}\n")
    f.write(f"file_changed={yaml_file_path}\n")
    # Add the formatted parameters as a new output
    f.write(f"formatted_parameters<<EOF\n{parameters_output}\nEOF\n")
