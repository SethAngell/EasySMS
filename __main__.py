import os
import sys
from tabnanny import check
from twilio.rest import Client
from twilio.rest.exceptions import TwilioRestException
import time
from datetime import datetime


#  Make things pretty
# Thanks https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


# Emoji Unicode
moon = "\U0001F315"
rocket = "\U0001F680"
stars = "\U00002728"
smile = "\U0001F604"
wave = "\U0001F44B"

account_sid = None 
auth_token = None
from_number = None
steel_city = False


# Add opt_out message
opt_out = False
opt_out_message = "\nTo stop receiving these messages, reply STOP"
opt_out_list = []

# Running List
results = []

def valid_file(path):
    return os.path.exists(path)

def generate_rich(text, bold=False, selected_color=None):

    if selected_color != None:
        if bold:
            return f"{color.BOLD}{selected_color}{text}{color.END}"
        else:
            return f"{selected_color}{text}{color.END}"
    else:
        if bold:
            return f"{color.BOLD}{text}{color.END}"
        else:
            return f"{text}"

def select_sender():
    print(generate_rich(f'Please select which company this message is for?', True))
    print("1 - Steel City Pizza Company \U0001F355")
    print("2 - Special Forces Administration  \U0001FA96")
    complete = False
    while not complete:
        try:
            response = input(f'Please enter either {color.BOLD}1{color.END} or {color.BOLD}2{color.END} to signal your choice: ')
            response = int(response)
        except:
            print("Oops, your input was invalid. Try again!")

        if response not in [1,2]:
            print("Make sure you enter either 1 or 2!")
        else:
            if response == 1:
                steel_city = True

            complete = True
    
    if steel_city:
        account_sid = os.environ['SCP_TWILIO_ACCOUNT_SID']
        auth_token = os.environ['SCP_TWILIO_AUTH_TOKEN']
        from_number = os.environ['SCP_TWILIO_NUMBER']
        opt_out = True
    else:
        account_sid = os.environ['SFA_TWILIO_ACCOUNT_SID']
        auth_token = os.environ['SFA_TWILIO_AUTH_TOKEN']
        from_number = os.environ['SFA_TWILIO_NUMBER']

def write_results():
    os.makedirs("~/developer/results", exist_ok=True)
    if steel_city:
        opt_out_filename = f'SCP_{time.strftime("%Y-%m-%d_%H-%M-%S")}_opt-out.csv'
        results_filename = f'SCP_{time.strftime("%Y-%m-%d_%H-%M-%S")}_results.csv'
    else:
        opt_out_filename = f'SFA_{time.strftime("%Y-%m-%d_%H-%M-%S")}_opt-out.csv'
        results_filename = f'SFA_{time.strftime("%Y-%m-%d_%H-%M-%S")}_results.csv'

    print(generate_rich(f'Process complete. Writing list of all messages and newly opted out numbers to ~/developer/results/', True))

    with open(f'~/developer/results/{opt_out_filename}', "w") as outfile:
        outfile.write("numbers\n")
        for val in opt_out_list:
            outfile.write(val + '\n')
    
    with open(f'~/developer/results/{results_filename}', "w") as outfile:
        outfile.write("numbers, result\n")
        for val in results:
            outfile.write(",".join(val) + '\n')




def decide_on_input_modality(target):
    print(generate_rich(f'How would you like to input your {target}?', True))
    print(f'1 - Type your {target} into the command line (all in one paragraph/only one number)')
    print(f'2 - Type your {target} into a text file (can be multiple paragraphs/multiple numbers)')
    complete = False
    while not complete:
        try:
            response = input(f'Please enter either {color.BOLD}1{color.END} or {color.BOLD}2{color.END} to signal your choice: ')
            response = int(response)
        except:
            print("Oops, your input was invalid. Try again!")

        if response not in [1,2]:
            print("Make sure you enter either 1 or 2!")
        else:
            return response

def get_message_from_command_line():
    print(generate_rich("Okay, let's get that message figured out", True))
    print("On the following line. Type the message exactly as you'd like it to be sent, and then press enter")
    
    while True:
        message = input('Input your message: ')

        if opt_out:
            message += opt_out_message

        print(f'Your message is: {generate_rich(message, True)}')

        correct = input("Is that message correct? [YES/NO]: ")
        if correct == "YES":
            return message

def get_message_from_text_file():
    print(generate_rich("Okay, let's get that message figured out", True))
    print("On the following line. Drag in the file you'd like to send (.txt only!)")
    
    while True:
        path = input('Input your file: ')
        path = path.strip()

        if (path.split('.')[-1] != 'txt') or not valid_file(path):
            print("Oops! That files doesn't work. Try again!")

        message = ""

        with open(path, 'r') as ifile:
            message = ifile.read()
        
        if opt_out:
            message += opt_out_message

        print(f'Your message is: {message}')

        correct = input("Is that message correct? [YES/NO]: ")
        if correct == "YES":
            return message

def send_twilio_message(body, to_number):
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
                                    body=body,
                                    from_=from_number,
                                    to=to_number
                                )
        
        results.append([to_number, message.status])

    except TwilioRestException as e:
        if str(message.error_code) == "21610":
            opt_out_list.append(to_number]



def send_test_message(body):
    print(generate_rich(f'Lets test your message. Sending to {os.environ["TEST_NUMBER"]}', True))
    send_twilio_message(body, os.environ["TEST_NUMBER"])

    decision = input("Are you satisfied with your message? [YES/NO]: ")

    if decision == 'YES':
        return True
    else:
        print("Sorry about that :( Go ahead and start this script over")
        sys.exit(1)

def check_number_validity(number):
    if (number[0] != "+") or (number[1] != "1") or (len(number) != 12):
        return False
    else:
        return True


def get_number_from_command_line():
    while True:
        print(generate_rich("Lets get that phone number", True))
        print("Below, please enter the number you'd like to text in the following format: +10000000000")
        number = input("Enter the number here: ")

        if not check_number_validity(number):
            print("Sorry, that number doesn't work. Let's try again!")
            continue

        decision = input(f'You\'d like to text {number}? [YES/NO]: ')

        if decision == 'YES':
            return [number]
        else:
            print("Sorry about that :( Go ahead and start this script over")
            sys.exit(1)

def get_numbers_from_file():
    print(generate_rich("Okay, let's get those numbers figured out", True))
    print("On the following line. Drag in the file containing the numbers you want to message (.txt only!)")
    
    while True:
        path = input('Input your file: ')
        path = path.strip()

        if (path.split('.')[-1] != 'txt') or not valid_file(path):
            print("Oops! That files doesn't work. Try again!")
            continue

        numbers = []
        raw = []
        rejects = []

        with open(path, 'r') as ifile:
            raw = ifile.readlines()

        for number in raw:
            if len(number) < 3:
                continue
            if check_number_validity(number.strip()):
                numbers.append(number.strip())
            else:
                rejects.append(number.strip())
        
        print("We extracted all available numbers")
        if len(rejects) > 0:
            if len(rejects) > 10:
                print(f'During the validation process, {len(rejects)} numbers were found to be invalid. They will not be contacted. These numbers have been saved to ~/Developer/results/rejects/')
                with open(f'~/Developer/results/rejects/{time.strftime("%Y-%m-%d_%H-%M-%S")}_rejects.txt', 'w') as outfile:
                    outfile.writelines(rejects)
            print("The following numbers were invalid. Please fix and resubmit just these numbers")
            for number in rejects:
                print(number)
        
        return numbers

def validate_numbers(numbers):
    print(generate_rich("We're almost ready to send out that message!"))
    print(f'This message will be sent to {len(numbers)} numbers')

    decision = input("Would you like to move forward with sending your messages? [YES/NO]: ")

    if decision == 'YES':
        return True
    else:
        print("Sorry :( Please try again!")
        sys.exit(1)

def send_messages(message, numbers):
    if len(numbers) < 10:
        raw = True
    else:
        raw = False

    checkpoints = []
    if not raw:
        for val in range(1,11):
            checkpoint = len(numbers) * (val/10)
            checkpoint = int(checkpoint)
            checkpoints.append(checkpoint)


    counter = 0
    checkpoint = 1

    for number in numbers:
        send_twilio_message(message, number)
        counter += 1

        if raw:
            print(f'Successfully messaged {number}')
        else:
            if counter in checkpoints:
                print(f'{checkpoint * 10}% of recipients have been messaged')
                checkpoint += 1

    

# Intro
print(generate_rich("Hello! Welcome To EasySMS. Your premier texting tool", True, color.BLUE))
print("Lets get started!\n")
time.sleep(2)

# Determine which company we're working with
select_sender()

# Message Decision
modality = decide_on_input_modality("message")

if modality == 1:
    message = get_message_from_command_line()
else:
    message = get_message_from_text_file()

# Test Message
send_test_message(message)

# Get Phone Numbers
modality = decide_on_input_modality("phone numbers")

if modality == 1:
    numbers = get_number_from_command_line()
else:
    numbers = get_numbers_from_file()

validate_numbers(numbers)

# Send Messages
send_messages(message, numbers)

# Record results
write_results()

# Goodbye
print(generate_rich("Thanks for using EasySMS. See you next time!", True, color.BLUE))
