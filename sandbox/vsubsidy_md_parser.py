from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
import json

class Link(BaseModel):
    text: str
    url: str

class ContactInfo(BaseModel):
    organization: Optional[str] = None
    address: Optional[Union[str, List[str]]] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class KeyData(BaseModel):
    status: Optional[str] = None
    deadline: Optional[str] = None
    minimum_contribution: Optional[str] = None
    maximum_contribution: Optional[str] = None
    budget: Optional[str] = None
    application_period: Optional[str] = None
    scope: Optional[str] = None
    submission_procedure: Optional[str] = None

class SubsidyProgram(BaseModel):
    title: str
    abbreviation: Optional[str] = None
    last_update: Optional[str] = None
    key_data: KeyData = Field(default_factory=KeyData)
    summary: Optional[str] = None
    criteria: List[str] = []
    links: List[Link] = []
    contact_info: List[ContactInfo] = []

def extract_json_blocks(markdown_text: str) -> List[dict]:
    """Extract JSON blocks from markdown text."""
    blocks = []
    json_block = ""
    in_json = False
    
    for line in markdown_text.split('\n'):
        if line.strip() == '```json':
            in_json = True
            json_block = ""
        elif line.strip() == '```' and in_json:
            in_json = False
            try:
                blocks.append(json.loads(json_block))
            except json.JSONDecodeError:
                print(f"Failed to parse JSON block: {json_block[:100]}...")
        elif in_json:
            json_block += line + '\n'
            
    return blocks

def parse_contact_info(text: str) -> List[ContactInfo]:
    """Parse contact information from text block."""
    contacts = []
    current_contact = {}
    address_lines = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            if current_contact:
                if address_lines:
                    current_contact['address'] = '\n'.join(address_lines)
                contacts.append(ContactInfo(**current_contact))
                current_contact = {}
                address_lines = []
            continue
            
        if line.startswith('Tel:'):
            current_contact['phone'] = line.replace('Tel:', '').strip()
        elif line.startswith('E-mail:'):
            current_contact['email'] = line.replace('E-mail:', '').strip()
        elif 'NEDERLAND' not in line and not line.startswith(('Tel:', 'E-mail:', 'Postbus')):
            if not current_contact.get('organization'):
                current_contact['organization'] = line
            else:
                address_lines.append(line)
    
    # Add the last contact if exists
    if current_contact:
        if address_lines:
            current_contact['address'] = '\n'.join(address_lines)
        contacts.append(ContactInfo(**current_contact))
    
    return contacts

def parse_markdown_to_subsidies(markdown_text: str) -> List[SubsidyProgram]:
    """Parse markdown text into SubsidyProgram objects."""
    json_blocks = extract_json_blocks(markdown_text)
    subsidies = []
    
    for block in json_blocks:
        if 'title' not in block:
            continue
            
        # Extract links if they exist
        links = []
        if 'links' in block:
            links = [Link(**link) for link in block['links']]
        elif 'related_links' in block:
            links = [Link(text=url, url=url) for url in block['related_links']]
            
        # Create key data
        key_data = {}
        for field in KeyData.__annotations__.keys():
            # Try different possible source fields
            possible_fields = [field, f"min_{field}", f"max_{field}", field.lower()]
            for possible_field in possible_fields:
                if possible_field in block:
                    key_data[field] = block[possible_field]
                    break
                elif 'key_data' in block and possible_field in block['key_data']:
                    key_data[field] = block['key_data'][possible_field]
                    break
        
        # Create subsidy program
        subsidy = SubsidyProgram(
            title=block['title'],
            abbreviation=block.get('abbreviation'),
            last_update=block.get('last_update') or block.get('last_updated'),
            key_data=KeyData(**key_data),
            summary=block.get('summary') or block.get('full_text'),
            criteria=block.get('criteria', []) if isinstance(block.get('criteria'), list) else [block.get('criteria')] if block.get('criteria') else [],
            links=links,
            contact_info=[]
        )
        
        # Add contact info if exists
        if 'contact_info' in block:
            if isinstance(block['contact_info'], list):
                subsidy.contact_info.extend([ContactInfo(**contact) for contact in block['contact_info']])
            else:
                subsidy.contact_info.append(ContactInfo(**block['contact_info']))
                
        subsidies.append(subsidy)
        
    return subsidies

def main():
    # Read markdown file
    with open('../data/two_subsidies.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Parse subsidies
    subsidies = parse_markdown_to_subsidies(markdown_content)
    
    # Open output file
    with open('../data/parsed_subsidies.txt', 'w', encoding='utf-8') as outfile:
        # Print and write formatted output
        for subsidy in subsidies:
            output = []
            output.append("=" * 80)
            output.append(f"Subsidy Program: {subsidy.title}")
            if subsidy.abbreviation:
                output.append(f"Abbreviation: {subsidy.abbreviation}")
            if subsidy.last_update:
                output.append(f"Last Updated: {subsidy.last_update}")
            
            output.append("\nKey Data:")
            for field, value in subsidy.key_data.model_dump(exclude_none=True).items():
                output.append(f"  {field.replace('_', ' ').title()}: {value}")
            
            if subsidy.summary:
                output.append("\nSummary:")
                output.append(subsidy.summary)
            
            if subsidy.criteria:
                output.append("\nCriteria:")
                for criterion in subsidy.criteria[:3]:  # Show first 3 criteria
                    output.append(f"- {criterion[:100]}...")
                if len(subsidy.criteria) > 3:
                    output.append(f"... and {len(subsidy.criteria)-3} more criteria")
            
            if subsidy.contact_info:
                output.append("\nContact Information:")
                for contact in subsidy.contact_info:
                    output.append(f"  Organization: {contact.organization}")
                    if contact.address:
                        output.append(f"  Address: {contact.address}")
                    if contact.phone:
                        output.append(f"  Phone: {contact.phone}")
                    if contact.email:
                        output.append(f"  Email: {contact.email}")
            
            output.append("-" * 80)
            
            # Join all lines with newlines
            formatted_output = '\n'.join(output)
            
            # Print to console
            print(formatted_output)
            
            # Write to file
            outfile.write(formatted_output + '\n')

if __name__ == "__main__":
    main()