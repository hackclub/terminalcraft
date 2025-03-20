def taking_input(message, _description=None):
    main_message = message
    text = message.lower()
    if text == 'help':
        print('''
you should type (note: <word> = what it does)
description = how to play the game
quit = stop playing or leave the current game
score = to see the current points 
''')
        return taking_input(input("> "), _description)  # Recursive call to get a new input
    elif text == 'description':
        if _description is not None:
            _description()
        return taking_input(input("> "), _description)  # Recursive call after showing description
    elif text == 'quit':
        print('Are you sure you want to leave the game')
        print('Type q if you want to stop playing')
        print('Type c if you want to leave the current game only')
        print('Type s if want to continue')
        x = ''
        while True:
            x = input("Enter a character: ").lower().strip()
            if len(x) == 1 and x in ['q', 'c', 's']:  # Fixed 'r' to 's' to match instructions
                break
            print("Invalid input. Please enter a single character, and it must be one of 'q', 'c', or 's'.")
        if x == 'q':
            print("Program terminated.")
            import Multiplayer_CLI  # Import here to avoid circular imports
            Multiplayer_CLI.output_marks()
            exit()
        elif x == 'c':
            return "EXIT_CURRENT_GAME"  # Special return value to signal game exit
        else:  # For 's' - continue
            return taking_input(input("> "), _description)  # Ask for a new input
    elif text == 'score':
        import Multiplayer_CLI  # Import here to avoid circular imports
        Multiplayer_CLI.output_marks()
        return taking_input(input("> "), _description)  # Recursive call after showing score
    return main_message  # Return the original input for normal game processing



def input_processing(input_text,description_func=None):
    # Game setup
    
    
        user_input = input(input_text)
        processed_input = taking_input(user_input, description_func())
        
        if processed_input == "EXIT_CURRENT_GAME":
            return (0, 0)  # Return score tuple to exit
        else:
            return processed_input
        # Process the regular game input
        # ...