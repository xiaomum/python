import os
height = 7
stars = 1
for i in range(height):
    print((' ' * (height-i)) + ('*' * stars))
    stars += 2
print((' ' * height) + 2 * '|')
print((' ' * height + 2 * '|'))