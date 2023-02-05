import random


with open("words.txt", "r") as f:
    words = f.read().splitlines()
    
word = random.choice(words)

knowledge = ['_'] * len(word)
lives = 10

while '_' in knowledge:
    if lives == 0:
        print('Game over')
        break
    
    print(f'You have {lives} lives')
    print(*knowledge)
    guess = input()
    if guess not in word:
        lives -= 1
        continue

    for i, x in enumerate(word):
        if x != guess:
            continue
        knowledge[i] = guess
else:
    print('YIPIIEEEEE, you won! Congrats :)')