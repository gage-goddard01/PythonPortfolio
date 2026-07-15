import random

def play_game(player_choice):   
    choices = ["rock", "paper", "scissors"]
    computer_choice = random.choice(choices)

    winner = 
        if computer_choice == player_choice:
            winner = "tie"
        elif computer_choice == "rock" and player_choice == "scissors":
            winner = "computer"
        elif computer_choice == "paper" and player_choice == "rock":
            winner = "computer"
        elif computer_choice == "scissors" and player_choice == "paper":
            winner = "computer"
        elif player_choice == "rock" and computer_choice == "scissors":
            winner = "player"
        elif player_choice == "paper" and computer_choice == "rock":
            winner = "player"
        elif player_choice == "scissors" and computer_choice == "paper":
            winner = "player"

    game_result= {
        "player_choice": player_choice,
        "computer_choice": computer_choice,
        "winner": winner
    }
    return game_result


#def play_game(choice):
    choices = ["rock", "paper", "scissors"]
    computer_choice = random.choice(choices)
    print(choice)

    if choice == computer_choice:
        print(" You both chose {choice}. It's a tie!")
    elif choice == "rock":
        if computer_choice == "paper":
            print("Paper covers rock. You lose")
        else:
            print("Rock smashes scissors. You win!")
    elif choice == "paper":
        if computer_choice == "rock":
            print("Paper covers rock. You win!")
        else:
            print("Scissors cut paper. You lose.")
    elif choice == "scissors":
        if computer_choice == "paper":
            print("Scissors cut paper. You win!")
        else:
            print("Rock smashes scissors. You lose.")


