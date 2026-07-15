
from apps.rock_paper_scissors import play_game

result = play_game("rock")
return result 


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


