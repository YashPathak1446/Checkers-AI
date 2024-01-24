import subprocess
from pathlib import Path

def run_game(StudentAI_player: int) -> bool:
    """
    Function to run game where player 1 is randomAI and playuer 2 is Student AI.
    command is the command enetered in terminal operated through subprocess.
    Win condition: Player 2 wins or ties.
    Return: boolean value indicating whether player 2 (Student AI) won or lost.
    """
    cwd = Path.cwd() 
    if not str(cwd).endswith('Tools'):
        cwd += Path('/Tools')

    # Default: StudentAI is second player
    path_first = "./Sample_AIs/Average_AI/main.py"
    path_second = "../src/checkers-python/main.py"
    if StudentAI_player == 1:  # if studentAI goes first
        path_first = "../src/checkers-python/main.py"
        path_second = "./Sample_AIs/Average_AI/main.py"

    command = [
        "python3",
        "{cwd}/AI_Runner.py".format(cwd=cwd),
        "8",
        "8",
        "3",
        "l",
        path_first,
        path_second
    ]
    win = False
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    outputString = output.decode()
    if error:
        print("Error occurred. Terminating.")
        print(error.decode())
        return win
    if 'player {} wins\n'.format(StudentAI_player) in outputString or 'Tie\n' in outputString:
        print('Our AI won.')
        win = True
    return win

def main():
    num_games = 100
    total_black = 0
    total_white = 0

    for i in range(num_games // 2):
        print("Running game (Student AI first) {count}/{num_games}".format(count=i+1, num_games=num_games))
        gameWon = run_game(1)

        if gameWon:
            total_black += 1
        print('Win rate: {}'.format(total_black / (i + 1)))

    print('\n')

    for i in range(num_games // 2):
        print("Running game (Student AI second) {count}/{num_games}".format(count = (num_games // 2) + i + 1, num_games=num_games))
        gameWon = run_game(2)
        
        if gameWon:
            total_white += 1

        print('Win rate: {}'.format(total_white / (i + 1)))
    print('\n')

    average_win_rate = (total_black + total_white) / num_games
    print("\nAverage Win Rate: {average_win_rate}".format(average_win_rate=average_win_rate * 100))

if __name__ == "__main__":
    main()
    