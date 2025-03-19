
import json, os# stored in file so user doesnt get asked for it again and again
import google.generativeai as genai
import argparse# module that parses argument from cmd line terminl shell
text='this is the start of proj txt to cli, idea is to pass cmds to terminal then have gemnini respond to it will probalbly have to refer to my brother for this'


configuration='config.json'
# os=input("your os:")
# terminal=input("yout termoinal ")

def config_exits_in_sys(configuration):
    if os.path.exists(configuration):
        with open("config.json")as f:
            return json.load(f) 
    else:
        print(f"create new config files")
        return create_config(configuration)

def create_config(configuration):
    os_name=input(f"type in your os:")
    terminal=input(f"type in your terminal type: ")
    api_key=input(f'your api key-(can get this from "https://aistudio.google.com/prompts/new_chat") for free:')
    config_dict={
        'os':os_name,
        'terminal':terminal,
        'api_key':api_key
    }
    with open("config.json",'w') as f:
        json.dump(config_dict,f,indent=4)
        print("saved successfully")
    return config_dict
    
config=config_exits_in_sys(configuration)
os_name=config['os']
terminal=config['terminal']
api_key=config['api_key']


parser = argparse.ArgumentParser(description=text)
# parser.add_argument('api_key',help='will be used for communjcation can get this from "https://aistudio.google.com/prompts/new_chat" for free')
parser.add_argument("string_text",nargs="+",help='pass normal text here, for this to work run this app initiallty')
args=parser.parse_args()



# print(f"{args.string_text} passed for processing")


char_string=" ".join(args.string_text)
# print(char_string)



def gen_ai_ans(char_string, os_name, terminal, api_key):

    genai.configure(api_key=api_key, transport="rest")
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Fixed the  comn typos before sending to AI
    fixed_input = char_string.lower().replace("cretae", "create").replace("foldr", "folder").replace("extensiom", "extension")
    
    prompt = f"""
    You are a command-line interpreter expert. Convert "{fixed_input}" into the exact {os_name} {terminal} command.

    CRITICAL PARSING RULES:
    1. For "create folder X" commands, ALWAYS extract X as the folder name
    2. For "count files with extension X", ALWAYS extract X as the extension
    3. Always identify command structure first, then extract parameters
    
    EXAMPLES:
    - Input: "create folder documents" → COMMAND: New-Item -ItemType Directory -Path "documents"
    - Input: "count files with extension py" → COMMAND: Get-ChildItem -Filter "*.py" -File | Measure-Object | Select-Object -ExpandProperty Count
    - Input: "delete file old_logs.txt" → COMMAND: Remove-Item -Path "old_logs.txt"
    
    REMEMBER: Always output your response in this exact format:
    COMMAND: [the exact command to execute]
    Explanation: [brief explanation of what the command does]
    
    DO NOT include any additional text, only the COMMAND and Explanation.
    """

    try:
        response = model.generate_content(prompt)
        if response and response.candidates:
            response_text = response.candidates[0].content.parts[0].text.strip()
            
            # Extract command if present
            if "COMMAND:" in response_text:
                command_parts = response_text.split("COMMAND:")[1].split("Explanation:")
                if len(command_parts) > 0:
                    command = command_parts[0].strip()
                    explanation = command_parts[1].strip() if len(command_parts) > 1 else "No explanation provided."
                    return f"COMMAND: {command}\nExplanation: {explanation}"
            
            # If no command found but we have text, return it
            return response_text
            
    except Exception as e:
        return f"Error: {str(e)}"
    
    return "Unable to generate command"
#output = gen_ai_ans(char_string) - parametera were are missing , i forgot to call them judt did thaty
output=gen_ai_ans(char_string, os_name,terminal,api_key)
print(f"the corresponding command is:{output}")
