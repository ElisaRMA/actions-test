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
        
        # Determine if value needs quotes
        needs_quotes = False
        if isinstance(value, str):
            # Only quote string values that aren't numbers, booleans, or dates
            if (value.lower() not in ['true', 'false'] and 
                not value.replace('-', '').isdigit() and
                not value.isdigit()):
                needs_quotes = True
        
        # Format the line - using single quotes when needed
        if needs_quotes:
            line = f"{name} = '{value}'"  # Using single quotes
        else:
            line = f"{name} = {value}"
        
        output_lines.append(line)
    
    return "\n".join(output_lines)
    
def format_for_slack(parameters_text):
    """Format parameters text for safe inclusion in Slack JSON"""
    # Escape backticks and quotes
    escaped = parameters_text.replace('`', '\\`').replace('"', '\\"')
    # Convert to single line with \n markers
    return escaped.replace('\n', '\\n')


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
slack_safe_params = format_for_slack(params_text)

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
    f.write(f"slack_safe_parameters={slack_safe_params}\n")
